from enum import Enum


class PQRSDType(str, Enum):
    PETITION = "PETICION"
    COMPLAINT = "QUEJA"
    CLAIM = "RECLAMO"
    SUGGESTION = "SUGERENCIA"
    DENUNCIA = "DENUNCIA"
