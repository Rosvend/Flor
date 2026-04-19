"""
Canonical PQRSD schema — single source of truth.
Every router, use case, and seed script must import from here.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ── Enumerations (as string literals) ────────────────────────────────────────

TIPOS_PERSONA   = Literal["natural", "juridica"]
TIPOS_DOCUMENTO = Literal["cedula_ciudadania", "cedula_extranjeria", "tarjeta_identidad", "pasaporte", "nit"]
GENEROS         = Literal["masculino", "femenino", "no_binario", "prefiero_no_decirlo", "otro"]
CANALES         = Literal["PORTAL", "FB_DM", "IG_DM", "MAIL", "WHATSAPP", "IN_PERSON", "PHONE"]
ASUNTOS         = Literal["peticion", "queja", "reclamo", "solicitud", "denuncia"]
ATENCIONES      = Literal["ninguna", "adulto_mayor", "persona_con_discapacidad", "mujer_embarazada", "victima_conflicto", "otro"]
ESTADOS         = Literal["abierto", "respondido"]


# ── Ciudadano ─────────────────────────────────────────────────────────────────

class Ciudadano(BaseModel):
    # Present only when anonima=False
    tipo_persona:     TIPOS_PERSONA   | None = None
    tipo_documento:   TIPOS_DOCUMENTO | None = None
    numero_documento: str | None = None
    nombres:          str | None = None
    apellidos:        str | None = None
    genero:           GENEROS | None = None
    # Always present
    pais:               str = "Colombia"
    departamento:       str | None = None
    ciudad:             str | None = None
    direccion:          str | None = None
    correo_electronico: str | None = None
    telefono:           str | None = None
    id_meta:            str | None = None


# ── Metadata de canal ─────────────────────────────────────────────────────────

class PQRSDMetadata(BaseModel):
    post_id:      str | None = None
    created_time: str | None = None


# ── Análisis IA (se adjunta en background, nunca en el POST inicial) ──────────

class AnalisisIA(BaseModel):
    sentimiento:      str | None = None
    is_offensive:     bool = False
    toxicity_warning: str | None = None
    offensive_words:  list[str] = Field(default_factory=list)
    tipo_sugerido:    str | None = None
    secretaria_asignada: str | None = None
    texto_mejorado:   str | None = None


# ── Schema principal ──────────────────────────────────────────────────────────

class PQRSDCurada(BaseModel):
    radicado:             str
    timestamp_radicacion: str
    canal:                str
    estado:               ESTADOS = "abierto"
    anonima:              bool
    ciudadano:            Ciudadano
    asunto_principal:     ASUNTOS
    atencion_preferencial: str = "ninguna"
    autoriza_notificacion_correo: bool
    descripcion_detallada: str
    metadata:   PQRSDMetadata = Field(default_factory=PQRSDMetadata)
    analisis_ia: AnalisisIA | None = None

    @model_validator(mode="after")
    def _check_ciudadano_no_anonimo(self) -> "PQRSDCurada":
        if not self.anonima:
            required = ["tipo_persona", "tipo_documento", "numero_documento", "nombres", "apellidos", "genero"]
            missing = [f for f in required if getattr(self.ciudadano, f) is None]
            if missing:
                raise ValueError(f"ciudadano requiere {missing} cuando anonima=False")
        return self
