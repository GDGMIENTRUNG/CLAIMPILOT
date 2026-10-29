from app.config import settings
from app.services.gemini import GeminiService
from app.services.groq_service import GroqService


def get_ai_service():
    """Explicit selection; never silently send an email to a fallback provider."""
    return GroqService() if settings.ai_provider == "groq" else GeminiService()
