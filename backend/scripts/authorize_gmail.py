import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import urllib.request
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from google.oauth2.credentials import Credentials
from app.config import settings
from app.services.gmail import SCOPES, save_token

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            OAuthCallbackHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
            <html>
            <head><title>Xac thuc thanh cong</title></head>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px; background-color: #f0fdf4;">
                <h1 style="color: #166534;">&#9989; X&aacute;c th&#7921;c Gmail th&agrave;nh c&ocirc;ng!</h1>
                <p style="color: #374151; font-size: 18px;">H&#7879; th&#7889;ng ClaimPilot &#273;&atilde; k&#7871;t n&#7889;i th&agrave;nh c&ocirc;ng v&#7899;i Gmail c&#7911;a b&#7841;n.</p>
                <p style="color: #6b7280;">B&#7841;n c&oacute; th&#7875; &#273;&oacute;ng tab n&agrave;y v&agrave; quay l&#7841;i trang ClaimPilot.</p>
            </body>
            </html>
            """)
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            error_desc = params.get("error", ["Khong tim thay ma xac thuc"])[0]
            self.wfile.write(f"<h3>Loi xac thuc: {error_desc}</h3>".encode("utf-8"))

    def log_message(self, format, *args):
        pass


def exchange_code_for_tokens(code: str) -> dict:
    url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.google_redirect_uri
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    if not settings.google_client_id or not settings.google_client_secret:
        raise SystemExit("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env")

    uri = urllib.parse.urlparse(settings.google_redirect_uri)
    port = uri.port or 8080

    auth_params = urllib.parse.urlencode({
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    })
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{auth_params}"

    print(f"\n=======================================================")
    print(f"Mo trinh duyet xac thuc Gmail tai:")
    print(auth_url)
    print(f"=======================================================\n")

    server = HTTPServer(("127.0.0.1", port), OAuthCallbackHandler)
    server.timeout = 180

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    while not OAuthCallbackHandler.auth_code:
        server.handle_request()

    server.server_close()

    print("Dang lay token tu Google...")
    token_info = exchange_code_for_tokens(OAuthCallbackHandler.auth_code)

    creds = Credentials(
        token=token_info["access_token"],
        refresh_token=token_info.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES
    )
    save_token(creds)
    print("✅ Gmail authorized! Token saved successfully to .secrets/gmail-token.json.")


if __name__ == "__main__":
    main()
