import base64
import os
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.config import settings
from app.services.errors import IntegrationError

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose"
]
def save_token(credentials):
    # Secret Manager volumes are read-only. Refreshed access tokens remain in
    # memory; the durable refresh token is still read from the mounted secret.
    if settings.gmail_token_read_only:
        return
    path = settings.token_path
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.chmod(path, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write(credentials.to_json())

def parse_message(message):
    try:
        raw = message["raw"]
        email = BytesParser(policy=policy.default).parsebytes(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
        sender = parseaddr(str(email.get("From", "")))[1]
        if not sender or "@" not in sender:
            raise ValueError("Missing sender")
        part = email.get_body(preferencelist=("plain", "html"))
        body = part.get_content() if part else ""
        if part and part.get_content_type() == "text/html":
            soup = BeautifulSoup(body, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            body = soup.get_text("\n", strip=True)
        if not body.strip():
            raise ValueError("No readable body")
        return dict(gmail_message_id=message["id"], sender_email=sender,
                    email_subject=str(email.get("Subject", "(no subject)")), email_body=body,
                    received_at=datetime.fromtimestamp(int(message["internalDate"]) / 1000, timezone.utc))
    except Exception as exc:
        raise IntegrationError("malformed_email") from exc

class GmailService:
    def __init__(self):
        if not settings.token_path.is_file():
            raise IntegrationError("gmail_not_authorized_run_authorize_command")
        try:
            creds = Credentials.from_authorized_user_file(str(settings.token_path), SCOPES)
            if not creds.valid:
                if not creds.refresh_token:
                    raise ValueError("No refresh token")
                creds.refresh(Request())
                save_token(creds)
            self.client = build("gmail", "v1", credentials=creds, cache_discovery=False)
        except Exception as exc:
            raise IntegrationError("gmail_authorization_invalid_reauthorize") from exc
    def list_ids(self, known_ids=None):
        try:
            result = []
            token = None
            known_ids = known_ids or set()
            unseen = 0
            # Continue past saved messages so repeated sync can drain the backlog.
            while unseen < settings.gmail_batch_size and len(result) < 1000:
                page = self.client.users().messages().list(userId="me", q=settings.gmail_query,
                    maxResults=min(100, settings.gmail_batch_size - unseen), pageToken=token).execute()
                ids = [m["id"] for m in page.get("messages", [])]
                result.extend(ids)
                unseen += sum(ident not in known_ids for ident in ids)
                token = page.get("nextPageToken")
                if not token:
                    break
            return result
        except Exception as exc:
            raise IntegrationError("gmail_read_failed_check_permissions_or_quota") from exc
    def get_message(self, message_id):
        try:
            message = self.client.users().messages().get(userId="me", id=message_id, format="raw").execute()
        except Exception as exc:
            raise IntegrationError("gmail_message_fetch_failed") from exc
        return parse_message(message)
