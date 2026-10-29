from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    database_url: str = "postgresql+psycopg://claimpilot:claimpilot@localhost:5432/claimpilot"
    ai_provider: Literal["gemini", "groq"] = "gemini"
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    groq_timeout_seconds: int = Field(default=20, ge=5, le=120)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8080/"
    gmail_token_path: str = ".secrets/gmail-token.json"
    gmail_query: str = 'in:inbox newer_than:30d {complaint issue problem refund return replacement damaged broken defective missing lost "not received" late delayed wrong incorrect overcharged "khiếu nại" "phàn nàn" "vấn đề" "hoàn tiền" "đổi trả" "thay thế" "hư hỏng" "thất lạc" "chưa nhận" "giao trễ" "giao sai" "tính phí sai"}'
    gmail_batch_size: int = Field(default=25, ge=1, le=100)
    gmail_retry_failed: bool = True
    gemini_timeout_seconds: int = Field(default=30, ge=5, le=120)
    frontend_origin: str = "http://localhost:5173"
    @property
    def token_path(self):
        p = Path(self.gmail_token_path)
        return p if p.is_absolute() else ROOT / p
settings = Settings()
