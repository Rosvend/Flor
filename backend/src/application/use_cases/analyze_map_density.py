"""
Analyze Map Density — Caso de uso para el mapa de calor de comunas de Medellín.

Agrupa las PQRS por la ciudad/barrio declarado en 'ubicacion' y las mapea
a las 16 comunas de Medellín.  Si Gemini está disponible, genera una explicación
corta de las problemáticas dominantes por comuna.  Si no, devuelve solo conteos.
"""
from __future__ import annotations

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ── Mapeo estático barrio/palabra-clave → comuna ─────────────────────────────
# Cubre los barrios / nombres más comunes.  Orden importa: más específico primero.
_KEYWORD_TO_COMMUNE: list[tuple[str, int, str]] = [
    # (patrón-lower, id_comuna, nombre_comuna)
    ("popular", 1, "Popular"),
    ("santa cruz", 2, "Santa Cruz"),
    ("santacruz", 2, "Santa Cruz"),
    ("manrique", 3, "Manrique"),
    ("aranjuez", 4, "Aranjuez"),
    ("castilla", 5, "Castilla"),
    ("doce de octubre", 6, "Doce de Octubre"),
    ("12 de octubre", 6, "Doce de Octubre"),
    ("robledo", 7, "Robledo"),
    ("villa hermosa", 8, "Villa Hermosa"),
    ("villahermosa", 8, "Villa Hermosa"),
    ("buenos aires", 9, "Buenos Aires"),
    ("la candelaria", 10, "La Candelaria"),
    ("candelaria", 10, "La Candelaria"),
    ("laureles", 11, "Laureles-Estadio"),
    ("estadio", 11, "Laureles-Estadio"),
    ("la america", 12, "La América"),
    ("america", 12, "La América"),
    ("san javier", 13, "San Javier"),
    ("el poblado", 14, "El Poblado"),
    ("poblado", 14, "El Poblado"),
    ("guayabal", 15, "Guayabal"),
    ("belen", 16, "Belén"),
    ("belén", 16, "Belén"),
    ("belen rincon", 16, "Belén"),
    # Estaciones de metro como referencias geográficas
    ("la floresta", 7, "Robledo"),
    ("suramericana", 11, "Laureles-Estadio"),
    ("industriales", 15, "Guayabal"),
    ("centro", 10, "La Candelaria"),
    ("parque berrio", 10, "La Candelaria"),
    ("alpujarra", 10, "La Candelaria"),
    ("universidad", 10, "La Candelaria"),
    ("hospital", 10, "La Candelaria"),
    ("prado", 4, "Aranjuez"),
    ("tricentenario", 5, "Castilla"),
    ("caribe", 4, "Aranjuez"),
    ("niquía", 5, "Castilla"),
]

_ALL_COMMUNES: dict[int, str] = {
    1: "Popular", 2: "Santa Cruz", 3: "Manrique", 4: "Aranjuez",
    5: "Castilla", 6: "Doce de Octubre", 7: "Robledo", 8: "Villa Hermosa",
    9: "Buenos Aires", 10: "La Candelaria", 11: "Laureles-Estadio",
    12: "La América", 13: "San Javier", 14: "El Poblado", 15: "Guayabal", 16: "Belén",
}


def _infer_commune(pqr: dict) -> tuple[int, str] | None:
    """Intenta inferir la comuna de Medellín desde los campos de ubicación."""
    ubicacion = pqr.get("ubicacion") or {}
    # Buscar en ciudad, dirección, dirección del hecho y contenido (último recurso)
    search_fields = [
        str(ubicacion.get("ciudad") or ""),
        str(ubicacion.get("barrio") or ""),
        str(ubicacion.get("direccion") or ""),
        str(ubicacion.get("direccion_hecho") or ""),
        str(pqr.get("contenido") or "")[:300],
    ]
    text = " ".join(search_fields).lower()

    for keyword, commune_id, commune_name in _KEYWORD_TO_COMMUNE:
        if keyword in text:
            return (commune_id, commune_name)

    # Si la ciudad dice "Medellín" sin barrio específico, asignamos al centro
    if "medell" in text:
        return (10, "La Candelaria")

    return None


class AnalyzeMapDensity:
    """
    Lee todas las PQRS del Curated Data Lake, las agrupa por comuna y,
    opcionalmente, pide a Gemini una explicación breve de la problemática.
    """

    def __init__(self, curated_data_lake, generation=None):
        self._lake = curated_data_lake
        self._generation = generation  # GenerationPort | None

    def execute(self, organization_id: int = 1) -> dict:
        all_pqrs = self._lake.get_all()
        filtered = [p for p in all_pqrs if p.get("organization_id", 1) == organization_id]

        # ── 1. Agrupar por comuna ─────────────────────────────────────────────
        commune_data: dict[int, dict] = {}

        for pqr in filtered:
            result = _infer_commune(pqr)
            if not result:
                continue
            commune_id, commune_name = result

            if commune_id not in commune_data:
                commune_data[commune_id] = {
                    "id": commune_id,
                    "name": commune_name,
                    "count": 0,
                    "tipos": {},
                    "sample_texts": [],
                }

            commune_data[commune_id]["count"] += 1

            # Contar por tipo
            tipo = (pqr.get("tipo") or "Sin tipo").upper()
            commune_data[commune_id]["tipos"][tipo] = commune_data[commune_id]["tipos"].get(tipo, 0) + 1

            # Guardar hasta 3 extractos de contenido para el prompt de IA
            contenido = pqr.get("contenido") or pqr.get("descripcion_detallada") or ""
            if contenido and len(commune_data[commune_id]["sample_texts"]) < 3:
                commune_data[commune_id]["sample_texts"].append(contenido[:200])

        # ── 2. Generar explicaciones con Gemini (si disponible) ──────────────
        communes_list = list(commune_data.values())

        if self._generation and communes_list:
            communes_list = self._enrich_with_ai(communes_list)

        # ── 3. Construir respuesta ────────────────────────────────────────────
        total_mapped = sum(c["count"] for c in communes_list)
        return {
            "total_pqrs": len(filtered),
            "total_mapped": total_mapped,
            "communes": communes_list,
        }

    def _enrich_with_ai(self, communes: list[dict]) -> list[dict]:
        """Genera un resumen corto por cada comuna con PQRS usando Gemini."""
        # Solo enriquecer comunas con al menos 1 PQRS para ahorrar cuota
        for c in communes:
            if not c["sample_texts"]:
                c["ai_summary"] = None
                continue
            try:
                samples = "\n- ".join(c["sample_texts"])
                prompt = (
                    f"Eres un analista de la Alcaldía de Medellín. "
                    f"En la comuna {c['name']} se han radicado {c['count']} PQRS. "
                    f"Estos son algunos extractos:\n- {samples}\n\n"
                    f"Escribe una conclusión de máximo 2 oraciones que explique "
                    f"la problemática principal de esta zona. Sé directo y concreto."
                )
                summary = self._generation.generate(
                    system="Eres un analista de la Alcaldía de Medellín.",
                    user=prompt
                )
                c["ai_summary"] = summary.strip() if summary else None
            except Exception as exc:
                logger.warning("No se pudo generar resumen IA para %s: %s", c["name"], exc)
                c["ai_summary"] = None
        return communes
