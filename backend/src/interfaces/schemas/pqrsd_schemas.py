"""
Canonical PQRSD schema — single source of truth.
Every router, use case, and seed script must import from here.

Supports BOTH the new canonical format (usuario, ubicacion, contenido, metadata)
and the legacy format (ciudadano, descripcion_detallada, asunto_principal) for
backward compatibility with existing S3 records.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ── Enumerations (as string literals) ────────────────────────────────────────

TIPOS_PERSONA   = Literal["natural", "juridica", "Natural", "Juridica"]
TIPOS_DOCUMENTO = Literal["cedula_ciudadania", "cedula_extranjeria", "tarjeta_identidad", "pasaporte", "nit"]
GENEROS         = Literal["masculino", "femenino", "no_binario", "prefiero_no_decirlo", "otro",
                          "Masculino", "Femenino"]
CANALES         = Literal["PORTAL", "WEB", "FB_DM", "IG_DM", "MAIL", "EMAIL", "WHATSAPP",
                          "IN_PERSON", "PHONE", "PRESENCIAL", "META_DM", "APP"]
ASUNTOS         = Literal["peticion", "queja", "reclamo", "solicitud", "denuncia",
                          "Peticion", "Queja", "Reclamo", "Solicitud", "Denuncia"]
ATENCIONES      = Literal["ninguna", "adulto_mayor", "persona_con_discapacidad",
                          "mujer_embarazada", "victima_conflicto", "otro",
                          "Ninguna", "Adulto mayor", "Persona con discapacidad"]
ESTADOS         = Literal["abierto", "respondido", "PENDIENTE_TRIAGE", "PENDIENTE_RESPUESTA"]


# ── Usuario (nuevo formato canónico) ─────────────────────────────────────────

class Usuario(BaseModel):
    nombre:    str | None = None
    documento: str | None = None
    telefono:  str | None = None
    email:     str | None = None


# ── Ubicación (nuevo formato canónico) ────────────────────────────────────────

class Ubicacion(BaseModel):
    pais:            str = "Colombia"
    departamento:    str | None = None
    ciudad:          str | None = None
    direccion:       str | None = None
    direccion_hecho: str | None = None


# ── Metadata canónica ─────────────────────────────────────────────────────────

class PQRSDMetadata(BaseModel):
    persona:                str | None = None
    genero:                 str | None = None
    atencion_preferencial:  str | None = None
    es_solicitud_informacion: str | None = None
    autoriza_notificacion:  str | None = None
    # Legacy fields (from raw/social media ingests)
    post_id:                str | None = None
    created_time:           str | None = None


# ── Análisis IA (se adjunta en background, nunca en el POST inicial) ──────────

class AnalisisIA(BaseModel):
    sentimiento:      str | None = None
    is_offensive:     bool = False
    toxicity_warning: str | None = None
    offensive_words:  list[str] = Field(default_factory=list)
    tipo_sugerido:    str | None = None
    secretaria_asignada: str | None = None
    texto_mejorado:   str | None = None


# ── Ciudadano (legacy, kept for backward compat reads) ────────────────────────

class Ciudadano(BaseModel):
    tipo_persona:     str | None = None
    tipo_documento:   str | None = None
    numero_documento: str | None = None
    nombres:          str | None = None
    apellidos:        str | None = None
    genero:           str | None = None
    pais:               str = "Colombia"
    departamento:       str | None = None
    ciudad:             str | None = None
    direccion:          str | None = None
    correo_electronico: str | None = None
    telefono:           str | None = None
    id_meta:            str | None = None


# ── Helpers: extract data supporting both old and new schemas ─────────────────

def get_citizen_email(record: dict) -> str | None:
    """Get citizen email from either new or legacy format."""
    # New format
    usuario = record.get("usuario")
    if isinstance(usuario, dict) and usuario.get("email"):
        return usuario["email"]
    # Legacy format
    ciudadano = record.get("ciudadano")
    if isinstance(ciudadano, dict) and ciudadano.get("correo_electronico"):
        return ciudadano["correo_electronico"]
    return None


def get_citizen_name(record: dict) -> str:
    """Get citizen display name from either new or legacy format."""
    # New format
    usuario = record.get("usuario")
    if isinstance(usuario, dict) and usuario.get("nombre"):
        return usuario["nombre"]
    # Legacy format
    ciudadano = record.get("ciudadano")
    if isinstance(ciudadano, dict):
        nombres = (ciudadano.get("nombres") or "").strip()
        apellidos = (ciudadano.get("apellidos") or "").strip()
        full = f"{nombres} {apellidos}".strip()
        if full:
            return full
    return "ciudadano/a"


def get_contenido(record: dict) -> str:
    """Get the main text content from either new or legacy format."""
    return (
        record.get("contenido")
        or record.get("descripcion_detallada")
        or ""
    )


def get_tipo(record: dict) -> str:
    """Get PQRSD type from either field."""
    return (
        record.get("tipo")
        or record.get("asunto_principal")
        or "peticion"
    )


def get_autoriza_notificacion(record: dict) -> bool:
    """Check if citizen authorized notifications, supporting both schemas."""
    # New format
    metadata = record.get("metadata")
    if isinstance(metadata, dict):
        val = metadata.get("autoriza_notificacion")
        if val is not None:
            return str(val).lower() in ("si", "sí", "true", "yes")
    # Legacy format
    legacy = record.get("autoriza_notificacion_correo")
    if legacy is not None:
        if isinstance(legacy, bool):
            return legacy
        return str(legacy).lower() in ("si", "sí", "true", "yes")
    return False


def is_anonymous(record: dict) -> bool:
    """Check if the record is anonymous. Treats None as not anonymous."""
    val = record.get("anonima")
    if val is None:
        return False
    return bool(val)
