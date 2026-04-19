from pydantic import BaseModel
from typing import Optional
from src.domain.ports.curated_data_lake import CuratedDataLakePort
from src.domain.ports.pqrs_analyzer_port import SimilarityAnalyzerPort

class DraftIntelligentResponseOutput(BaseModel):
    draft_text: str
    precedent_id: Optional[str]
    similarity_score: float

class DraftIntelligentResponse:
    def __init__(
        self,
        curated_data_lake: CuratedDataLakePort,
        similarity_analyzer: SimilarityAnalyzerPort
    ) -> None:
        self._curated_data_lake = curated_data_lake
        self._similarity_analyzer = similarity_analyzer

    def execute(self, radicado: str, organization_id: int) -> DraftIntelligentResponseOutput:
        # 1. Obtener la PQRS objetivo
        target_pqr = self._curated_data_lake.get_by_radicado(radicado)
        if not target_pqr:
            raise ValueError(f"PQR con radicado {radicado} no encontrada.")

        # Verificar permisos de organización
        if target_pqr.get("organization_id", 1) != organization_id:
            raise ValueError(f"No tiene permisos para acceder a la PQR {radicado}.")

        target_text = target_pqr.get("contenido", "")

        # 2. Obtener todas las PQRS de la organización, excepto la actual
        all_pqrs = self._curated_data_lake.get_all()
        candidates = [
            p for p in all_pqrs 
            if p.get("organization_id", 1) == organization_id and p.get("radicado") != radicado
        ]

        if not candidates:
            return DraftIntelligentResponseOutput(
                draft_text="No hay suficientes casos históricos en la base de datos para generar una sugerencia basada en precedentes.",
                precedent_id=None,
                similarity_score=0.0
            )

        # 3. Buscar la más similar
        result = self._similarity_analyzer.find_most_similar(target_text, candidates)
        
        if not result or result[1] < 0.15: # Umbral mínimo de similitud
            return DraftIntelligentResponseOutput(
                draft_text="No se encontró un precedente suficientemente similar para generar una sugerencia.",
                precedent_id=None,
                similarity_score=result[1] if result else 0.0
            )

        best_pqr, score = result
        precedent_id = best_pqr.get("radicado")
        secretaria = best_pqr.get("secretaria_asignada") or "competencia general"
        
        # 4. Construir la respuesta sugerida basada en el precedente (sin Gemini)
        # Si el precedente ya tenía una respuesta de un funcionario, la usamos como base.
        respuesta_previa = best_pqr.get("respuesta_funcionario")
        
        if respuesta_previa:
            draft_text = f"[Sugerencia basada en precedente {precedent_id}]\n{respuesta_previa}"
        else:
            draft_text = f"[Basado en Precedente Sugerido {precedent_id}]\nRespuesta estándar sugerida para solicitudes de {secretaria}."

        return DraftIntelligentResponseOutput(
            draft_text=draft_text,
            precedent_id=precedent_id,
            similarity_score=round(score * 100, 1) # Porcentaje
        )
