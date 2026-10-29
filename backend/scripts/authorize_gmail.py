from urllib.parse import urlparse
from google_auth_oauthlib.flow import InstalledAppFlow
from app.config import settings
from app.services.gmail import SCOPES, save_token

def main():
    if not settings.google_client_id or not settings.google_client_secret:
        raise SystemExit("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET from a Desktop app OAuth client in backend/.env")
    uri = urlparse(settings.google_redirect_uri)
    if uri.hostname != "localhost" or uri.scheme != "http":
        raise SystemExit("Use an http://localhost:<port>/ redirect for the local authorization command")
    config = {"installed": {"client_id": settings.google_client_id, "client_secret": settings.google_client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "redirect_uris": [settings.google_redirect_uri]}}
    flow = InstalledAppFlow.from_client_config(config, SCOPES)
    creds = flow.run_local_server(host="localhost", port=uri.port or 8080, access_type="offline", prompt="select_account consent", timeout_seconds=180)
    save_token(creds)
    print("Gmail authorized. Token saved locally; do not commit it.")
if __name__ == "__main__":
    main()
