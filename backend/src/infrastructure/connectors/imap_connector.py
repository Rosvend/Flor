import imaplib
import email
import email.message
import logging
import os
from datetime import datetime, timedelta, timezone
from email.header import decode_header, make_header
from email.utils import parseaddr
from typing import Any, Dict, List

from src.domain.ports.email_connector_port import EmailConnectorPort

logger = logging.getLogger(__name__)


class ImapEmailConnector(EmailConnectorPort):
    """
    Adaptador IMAP para leer bandeja de entrada de Gmail usando App Password.
    Reutiliza el mismo App Password que ya se usa para SMTP.

    Requiere IMAP habilitado en la cuenta de Gmail
    (Ajustes -> Reenvío y correo POP/IMAP -> Habilitar IMAP).
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        mailbox: str = "INBOX",
    ):
        self.host = host or os.getenv("IMAP_HOST", "imap.gmail.com")
        self.port = int(port or os.getenv("IMAP_PORT", "993"))
        self.user = user or os.getenv("IMAP_USER") or os.getenv("SMTP_USER")
        raw_pwd = password or os.getenv("IMAP_PASSWORD") or os.getenv("SMTP_PASSWORD") or ""
        self.password = raw_pwd.replace(" ", "")
        self.mailbox = mailbox
        self.since_days = int(os.getenv("IMAP_SINCE_DAYS", "1"))
        self.max_per_fetch = int(os.getenv("IMAP_MAX_PER_FETCH", "10"))
        self._conn: imaplib.IMAP4_SSL | None = None

    def authenticate(self) -> None:
        if not self.user or not self.password:
            raise RuntimeError(
                "IMAP credentials missing. Define IMAP_USER/IMAP_PASSWORD "
                "(or reuse SMTP_USER/SMTP_PASSWORD) in .env."
            )
        self._conn = imaplib.IMAP4_SSL(self.host, self.port, timeout=30)
        self._conn.login(self.user, self.password)
        self._conn.select(self.mailbox)

    def _ensure(self) -> imaplib.IMAP4_SSL:
        if self._conn is None:
            self.authenticate()
        assert self._conn is not None
        return self._conn

    def _close(self) -> None:
        if self._conn is None:
            return
        try:
            self._conn.close()
        except Exception:
            pass
        try:
            self._conn.logout()
        except Exception:
            pass
        self._conn = None

    @staticmethod
    def _decode_header(value: str | None) -> str:
        if not value:
            return ""
        try:
            return str(make_header(decode_header(value)))
        except Exception:
            return value

    @staticmethod
    def _extract_body(msg: email.message.Message) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition") or "")
                if ctype == "text/plain" and "attachment" not in disp.lower():
                    return ImapEmailConnector._decode_payload(part)
            # fallback a text/html si no hay text/plain
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    return ImapEmailConnector._decode_payload(part)
            return ""
        return ImapEmailConnector._decode_payload(msg)

    @staticmethod
    def _decode_payload(part: email.message.Message) -> str:
        payload = part.get_payload(decode=True)
        if not payload:
            return ""
        charset = part.get_content_charset() or "utf-8"
        try:
            return payload.decode(charset, errors="replace")
        except LookupError:
            return payload.decode("utf-8", errors="replace")

    def fetch_unread_messages(self, query: str = "is:unread") -> List[Dict[str, Any]]:
        conn = self._ensure()
        try:
            # SINCE <DD-Mon-YYYY> — IMAP sólo acepta mes en inglés
            since_dt = datetime.now(timezone.utc) - timedelta(days=max(0, self.since_days - 1))
            since_str = since_dt.strftime("%d-%b-%Y")
            typ, data = conn.uid("search", None, "UNSEEN", "SINCE", since_str)
            if typ != "OK":
                logger.warning("IMAP SEARCH falló: %s", data)
                return []
            uids = data[0].split() if data and data[0] else []
            if not uids:
                return []
            # Tope por corrida para no atascar el scheduler en bandejas grandes
            if self.max_per_fetch > 0 and len(uids) > self.max_per_fetch:
                logger.info(
                    "IMAP: %s unread encontrados, procesando sólo %s en este tick",
                    len(uids), self.max_per_fetch,
                )
                uids = uids[-self.max_per_fetch:]

            messages: List[Dict[str, Any]] = []
            for uid in uids:
                typ, msg_data = conn.uid("fetch", uid, "(BODY.PEEK[])")
                if typ != "OK" or not msg_data or not msg_data[0]:
                    continue
                raw_bytes = msg_data[0][1]
                if not isinstance(raw_bytes, (bytes, bytearray)):
                    continue
                msg = email.message_from_bytes(raw_bytes)

                subject = self._decode_header(msg.get("Subject"))
                from_raw = self._decode_header(msg.get("From"))
                sender_name, sender_email = parseaddr(from_raw)
                body = self._extract_body(msg)
                date_hdr = msg.get("Date") or ""

                messages.append({
                    "id": uid.decode() if isinstance(uid, bytes) else str(uid),
                    "sender": from_raw,
                    "sender_name": sender_name or None,
                    "sender_email": sender_email or None,
                    "subject": subject or "Sin Asunto",
                    "body": body or "",
                    "timestamp": date_hdr,
                })
            return messages
        except Exception as exc:
            logger.error("Error en IMAP fetch: %s", exc)
            self._close()
            return []

    def mark_as_read(self, message_id: str) -> None:
        conn = self._ensure()
        try:
            conn.uid("store", message_id, "+FLAGS", "(\\Seen)")
        except Exception as exc:
            logger.error("Error marcando IMAP como leído (uid=%s): %s", message_id, exc)
            self._close()
