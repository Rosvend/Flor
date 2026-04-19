from pydantic import BaseModel
import uuid
from datetime import datetime, timezone

from src.domain.ports.raw_data_lake import RawDataLakePort
from src.domain.ports.curated_data_lake import CuratedDataLakePort
from src.domain.ports.classification_port import ClassificationPort
from src.application.dtos.ingest_curated_dtos import IngestCuratedMessagesInput
from src.application.use_cases.ingest_curated_messages import IngestCuratedMessages


class MigrationResult(BaseModel):
    total_raw_processed: int
    pqrs_found: int
    keys_migrated: list[str]


class MigrateRawToCurated:
    def __init__(
        self,
        raw_data_lake: RawDataLakePort,
        curated_data_lake: CuratedDataLakePort,
        classifier: ClassificationPort,
        ingest_curated: IngestCuratedMessages
    ) -> None:
        self._raw_data_lake = raw_data_lake
        self._curated_data_lake = curated_data_lake
        self._classifier = classifier
        self._ingest_curated = ingest_curated

    def execute(self) -> MigrationResult:
        # 1. Obtener todos los registros crudos
        raw_data = self._raw_data_lake.get_all()
        
        migrated_keys = []
        curated_records_to_insert = []
        keys_to_delete = []

        for key, raw_record in raw_data.items():
            # Extraer contenido (manejando varios formatos posibles)
            contenido = raw_record.get("contenido") or raw_record.get("text") or raw_record.get("message")
            if not contenido:
                # No hay texto, marcamos para borrar y seguimos
                keys_to_delete.append(key)
                continue

            # 2. Usar NLP para saber si es PQRSD
            if self._classifier.is_pqrs(contenido):
                # Es una PQRS! La mapeamos al formato CuratedRecord
                
                # Extraer info del usuario si existe
                raw_user = raw_record.get("usuario", {})
                usuario = {
                    "nombre": raw_user.get("nombre") or raw_user.get("name") or "Anónimo",
                    "id_meta": raw_user.get("id_meta") or raw_user.get("id"),
                }
                
                # Mapear metadatos
                raw_metadata = raw_record.get("metadata", {})
                
                # Clasificar el tipo
                classification_result = self._classifier.pre_classify(contenido)
                tipo = classification_result.tipo
                
                # Construir el diccionario validado para IngestCuratedMessages
                raw_user = raw_record.get("usuario", {})
                tipo_map = {"peticion": "peticion", "queja": "queja", "reclamo": "reclamo",
                            "solicitud": "solicitud", "denuncia": "denuncia"}
                asunto = tipo_map.get((tipo or "").lower(), "peticion")

                curated_dict = {
                    "radicado":                    None,  # assigned by data lake
                    "timestamp_radicacion":        datetime.now(timezone.utc).isoformat(),
                    "canal":                       raw_record.get("canal", "META_DM"),
                    "estado":                      "abierto",
                    "anonima":                     True,  # raw social media: always anonymous
                    "ciudadano": {
                        "pais":               "Colombia",
                        "departamento":       None,
                        "ciudad":             None,
                        "direccion":          None,
                        "correo_electronico": None,
                        "telefono":           raw_user.get("telefono"),
                        "id_meta":            raw_user.get("id_meta") or raw_user.get("id"),
                    },
                    "asunto_principal":            asunto,
                    "atencion_preferencial":       "ninguna",
                    "autoriza_notificacion_correo": False,
                    "descripcion_detallada":       contenido,
                    "metadata": {
                        "post_id":      raw_metadata.get("post_id"),
                        "created_time": raw_metadata.get("created_time"),
                    },
                }
                curated_records_to_insert.append(curated_dict)
                migrated_keys.append(key)
                keys_to_delete.append(key)
            else:
                # No es PQRS (spam o charlar), solo lo borramos
                keys_to_delete.append(key)

        # 3. Guardar los que sí son PQRS en curated
        if curated_records_to_insert:
            self._ingest_curated.execute(IngestCuratedMessagesInput(records=curated_records_to_insert))

        # 4. Limpiar el raw data lake
        for key in keys_to_delete:
            self._raw_data_lake.delete(key)

        return MigrationResult(
            total_raw_processed=len(raw_data),
            pqrs_found=len(migrated_keys),
            keys_migrated=migrated_keys
        )
