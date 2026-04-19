from typing import List, Dict, Any
from datetime import datetime, timezone
from src.domain.ports.email_connector_port import EmailConnectorPort
from src.application.use_cases.process_pqrs import ProcessPQRS
from src.application.dtos.pqrs_dtos import ProcessPQRSInput
from src.application.use_cases.ingest_curated_messages import IngestCuratedMessages
from src.application.dtos.ingest_curated_dtos import IngestCuratedMessagesInput

class IngestEmailPQRS:
    """
    Caso de Uso: Ingestión Automática desde Gmail.
    Recupera correos no leídos, los procesa (IA) y los guarda en el Curated Data Lake.
    """
    def __init__(
        self, 
        email_connector: EmailConnectorPort,
        process_pqrs: ProcessPQRS,
        ingest_curated: IngestCuratedMessages
    ):
        self._connector = email_connector
        self._process_pqrs = process_pqrs
        self._ingest_curated = ingest_curated

    def execute(self, query: str = "is:unread") -> Dict[str, Any]:
        # 1. Recuperar correos
        emails = self._connector.fetch_unread_messages(query=query)
        if not emails:
            return {"status": "success", "count": 0, "message": "No hay correos nuevos"}

        curated_records = []
        
        for email in emails:
            # 2. Validar si es una PQRS (Filtro de Spam/Irrelevantes)
            text_to_analyze = f"Asunto: {email['subject']}\n\nCuerpo: {email['body']}"
            
            # Accedemos al pre_classifier a través de process_pqrs
            is_valid = self._process_pqrs._pre_classifier.is_pqrs(text_to_analyze)
            
            if not is_valid:
                # Si no es una PQRS, simplemente la marcamos como leída y saltamos
                self._connector.mark_as_read(email['id'])
                continue

            # 3. Procesar con IA (Toxicidad, Sentimiento, Pre-Clasificación)
            ai_result = self._process_pqrs.execute(ProcessPQRSInput(text=text_to_analyze))
            
            # Generar un radicado automático para el registro curado
            import uuid
            radicado = f"RAD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Extraer email del remitente
            sender_email = email.get('sender', '')
            # Try to extract email from "Name <email>" format
            if '<' in sender_email and '>' in sender_email:
                sender_email_clean = sender_email.split('<')[1].split('>')[0]
            else:
                sender_email_clean = sender_email

            # 4. Formatear para el Curated Data Lake — formato canónico
            curated_record = {
                "radicado":             radicado,
                "timestamp_radicacion": datetime.now(timezone.utc).isoformat(),
                "tipo":                 (ai_result.tipo_sugerido or "Peticion").capitalize(),
                "canal":                "EMAIL",
                "anonima":              None,
                "estado":               "abierto",
                "organization_id":      1,
                "usuario": {
                    "nombre":    email.get('sender_name') or sender_email,
                    "documento": None,
                    "telefono":  None,
                    "email":     sender_email_clean,
                },
                "ubicacion": {
                    "pais":            "Colombia",
                    "departamento":    None,
                    "ciudad":          None,
                    "direccion":       None,
                    "direccion_hecho": None,
                },
                "contenido":            email['body'],
                "metadata": {
                    "persona":                None,
                    "genero":                 None,
                    "atencion_preferencial":  None,
                    "es_solicitud_informacion": None,
                    "autoriza_notificacion":  "Si",
                    "asunto_original":        email.get('subject'),
                },
                "analisis_ia": {
                    "sentimiento":        ai_result.sentiment,
                    "is_offensive":       ai_result.is_offensive,
                    "toxicity_warning":   ai_result.toxicity_warning,
                    "offensive_words":    ai_result.offensive_words,
                    "tipo_sugerido":      ai_result.tipo_sugerido,
                    "secretaria_asignada": ai_result.secretaria_asignada,
                    "texto_mejorado":     ai_result.improved_text,
                },
                # Pipeline fields — initially empty
                "resumen_ia":           None,
                "borrador_respuesta":   None,
                "tipo_confirmado":      None,
                "respuesta":            None,
                "timestamp_respuesta":  None,
                "respondido_por":       None,
            }
            curated_records.append(curated_record)
            
            # 5. Marcar como leído en Gmail
            self._connector.mark_as_read(email['id'])

        # 6. Guardar en el Data Lake
        if curated_records:
            self._ingest_curated.execute(IngestCuratedMessagesInput(records=curated_records))

        return {
            "status": "success",
            "count": len(curated_records),
            "radicados": [r['radicado'] for r in curated_records]
        }
