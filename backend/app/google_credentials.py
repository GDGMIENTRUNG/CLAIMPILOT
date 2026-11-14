"""Shared client factory: preserve the token file and validate granted scopes."""
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.config import settings
from app.services.errors import IntegrationError
from app.services.gmail import save_token

class GoogleClientFactory:
    @staticmethod
    def get_client(write=False):
        try:
            path=settings.token_path
            if not path.is_file():raise IntegrationError('gmail_not_authorized')
            data=json.loads(path.read_text());declared=data.get('scopes',[])
            if isinstance(declared,str):declared=declared.split()
            if write and not any(s.endswith('/gmail.compose') or s.endswith('/gmail.modify') for s in declared):raise IntegrationError('gmail_compose_consent_required')
            creds=Credentials.from_authorized_user_file(str(path))
            if not creds.valid:
                if not creds.refresh_token:raise IntegrationError('gmail_authorization_invalid_reauthorize')
                creds.refresh(Request());save_token(creds)
            return build('gmail','v1',credentials=creds,cache_discovery=False)
        except IntegrationError:raise
        except Exception as exc:raise IntegrationError('gmail_authorization_invalid_reauthorize') from exc
