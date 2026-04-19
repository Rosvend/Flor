import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.domain.ports.notification_port import NotificationPort

logger = logging.getLogger(__name__)

_ASUNTO_LABELS = {
    "peticion": "Petición",
    "queja": "Queja",
    "reclamo": "Reclamo",
    "solicitud": "Solicitud",
    "denuncia": "Denuncia",
}

_FIRMA = """
Atentamente,
Secretaría de Desarrollo Económico
Alcaldía de Medellín
NIT: 890.905.211-1 | Línea de Atención: 444 4144
www.medellin.gov.co
"""


def _send(to: str, subject: str, body: str) -> None:
    host     = os.environ["SMTP_HOST"]
    port     = int(os.getenv("SMTP_PORT", "587"))
    user     = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    from_    = os.getenv("EMAIL_FROM", user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Alcaldía de Medellín <{from_}>"
    msg["To"]      = to
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.sendmail(from_, to, msg.as_string())


class GmailSMTPAdapter(NotificationPort):

    def notify_created(self, record: dict) -> None:
        correo = record.get("ciudadano", {}).get("correo_electronico")
        if not correo or not record.get("autoriza_notificacion_correo"):
            return

        radicado  = record.get("radicado", "N/A")
        asunto    = _ASUNTO_LABELS.get(record.get("asunto_principal", ""), "Solicitud")
        canal     = record.get("canal", "N/A")
        fecha     = record.get("timestamp_radicacion", "N/A")[:10]
        ciudadano = record.get("ciudadano", {})
        nombre    = f"{ciudadano.get('nombres','')} {ciudadano.get('apellidos','')}".strip() or "ciudadano/a"

        body = f"""\
Estimado/a {nombre},

Su {asunto.lower()} ha sido recibida y radicada exitosamente en el sistema de la
Secretaría de Desarrollo Económico de la Alcaldía de Medellín.

══════════════════════════════════════════════
 NÚMERO DE RADICADO : {radicado}
 ESTADO             : ABIERTO
══════════════════════════════════════════════

Detalles de su solicitud:
  • Tipo de solicitud : {asunto}
  • Canal             : {canal}
  • Fecha radicación  : {fecha}

Su solicitud será atendida en el plazo establecido por la Ley 1755 de 2015
(máximo 15 días hábiles a partir de la fecha de radicación).

Conserve su número de radicado para cualquier consulta o seguimiento.
{_FIRMA}"""

        try:
            _send(correo, f"[Alcaldía de Medellín] PQRSD Radicada – {radicado}", body)
            logger.info("Notificación 'creada' enviada a %s para radicado %s", correo, radicado)
        except Exception as exc:
            logger.error("Error enviando notificación 'creada': %s", exc)

    def notify_resolved(self, record: dict) -> None:
        correo = record.get("ciudadano", {}).get("correo_electronico")
        if not correo or not record.get("autoriza_notificacion_correo"):
            return

        radicado  = record.get("radicado", "N/A")
        asunto    = _ASUNTO_LABELS.get(record.get("asunto_principal", ""), "Solicitud")
        fecha_rad = record.get("timestamp_radicacion", "N/A")[:10]
        fecha_res = record.get("timestamp_respuesta", "N/A")[:10]
        ciudadano = record.get("ciudadano", {})
        nombre    = f"{ciudadano.get('nombres','')} {ciudadano.get('apellidos','')}".strip() or "ciudadano/a"

        body = f"""\
Estimado/a {nombre},

Su {asunto.lower()} radicada bajo el número {radicado} ha sido atendida y respondida
por la Secretaría de Desarrollo Económico de la Alcaldía de Medellín.

══════════════════════════════════════════════
 NÚMERO DE RADICADO : {radicado}
 ESTADO             : RESPONDIDO
══════════════════════════════════════════════

Detalles:
  • Tipo de solicitud  : {asunto}
  • Fecha radicación   : {fecha_rad}
  • Fecha de respuesta : {fecha_res}

Si considera que su solicitud no fue resuelta de forma satisfactoria, puede presentar
una nueva PQRSD o comunicarse con nosotros a través de los canales oficiales.
{_FIRMA}"""

        try:
            _send(correo, f"[Alcaldía de Medellín] PQRSD Respondida – {radicado}", body)
            logger.info("Notificación 'respondida' enviada a %s para radicado %s", correo, radicado)
        except Exception as exc:
            logger.error("Error enviando notificación 'respondida': %s", exc)
