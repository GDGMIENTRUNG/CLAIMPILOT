from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.static import SPAStaticFiles
from app.config import settings
from app.services.gmail import save_token


def test_spa_does_not_swallow_api_missing_assets_or_unsafe_paths(tmp_path):
    (tmp_path / 'index.html').write_text('<html>ClaimPilot</html>')
    (tmp_path / 'assets').mkdir()
    (tmp_path / 'assets/app.js').write_text('const ready = true;')
    app = FastAPI()
    app.mount('/', SPAStaticFiles(directory=tmp_path, html=True))
    with TestClient(app) as client:
        for path in ('/', '/cases/1'):
            assert client.get(path).status_code == 200
            assert 'text/html' in client.get(path).headers['content-type']
        assert client.get('/assets/app.js').status_code == 200
        for path in ('/api', '/api/missing', '/assets/missing.js', '/.env', '/%2e%2e/secret.txt'):
            assert client.get(path).status_code == 404
        assert client.post('/cases/1').status_code == 405


def test_readonly_token_refresh_does_not_write_secret(monkeypatch, tmp_path):
    class Credentials:
        def to_json(self):
            raise AssertionError('Read-only token should never be serialized')
    monkeypatch.setattr(settings, 'gmail_token_read_only', True)
    monkeypatch.setattr(settings, 'gmail_token_path', str(tmp_path / 'token.json'))
    save_token(Credentials())
    assert not settings.token_path.exists()
