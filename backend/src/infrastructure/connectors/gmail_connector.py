import os
import base64
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.domain.ports.email_connector_port import EmailConnectorPort

# Si modificas estos SCOPES, elimina el archivo token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailConnector(EmailConnectorPort):
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None

    def authenticate(self) -> None:
        """
        Maneja la autenticación OAuth2. 
        Si no hay token.json, abre el navegador para autorizar.
        """
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"No se encontró {self.credentials_path}. "
                        "Descárgalo desde Google Cloud Console -> APIs & Services -> Credentials."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

    def fetch_unread_messages(self, query: str = "is:unread") -> List[Dict[str, Any]]:
        if not self.service:
            self.authenticate()

        try:
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            parsed_messages = []
            for msg in messages:
                msg_data = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                
                # Extraer Headers
                headers = msg_data.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "Sin Asunto")
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Desconocido")
                
                # Extraer Cuerpo (Body)
                parts = msg_data.get('payload', {}).get('parts', [])
                body = ""
                
                if not parts: # Mensaje simple
                    body_data = msg_data.get('payload', {}).get('body', {}).get('data', '')
                else: # Mensaje multipart
                    # Buscamos la parte text/plain
                    body_part = next((p for p in parts if p['mimeType'] == 'text/plain'), parts[0])
                    body_data = body_part.get('body', {}).get('data', '')

                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')

                parsed_messages.append({
                    "id": msg['id'],
                    "sender": sender,
                    "subject": subject,
                    "body": body,
                    "timestamp": msg_data.get('internalDate')
                })
            
            return parsed_messages

        except HttpError as error:
            print(f"Error en Gmail API: {error}")
            return []

    def mark_as_read(self, message_id: str) -> None:
        if not self.service:
            self.authenticate()
        
        try:
            # Eliminar la etiqueta 'UNREAD' para marcarlo como leído
            self.service.users().messages().batchModify(
                userId='me',
                body={
                    'ids': [message_id],
                    'removeLabelIds': ['UNREAD']
                }
            ).execute()
        except HttpError as error:
            print(f"Error marcando como leído: {error}")
