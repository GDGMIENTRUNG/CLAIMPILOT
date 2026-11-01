from types import SimpleNamespace
from unittest.mock import MagicMock
import httpx
import pytest
from groq import APITimeoutError
from app.config import settings
from app.schemas import Analysis
from app.services.ai import get_ai_service
from app.services.gemini import GeminiService
from app.services.groq_service import GroqService
from app.services.errors import IntegrationError


def setup_client(monkeypatch, content=None, reason='stop'):
    monkeypatch.setattr(settings,'groq_api_key','test-key-never-sent')
    client=MagicMock()
    client.__enter__.return_value=client
    data=Analysis(is_complaint=True,complaint_type='late_delivery',order_id='DH001',requested_action='shipping_fee_refund',summary='Customer reports late delivery.',missing_information=[],priority='medium')
    client.chat.completions.create.return_value=SimpleNamespace(choices=[SimpleNamespace(finish_reason=reason,message=SimpleNamespace(content=data.model_dump_json() if content is None else content))])
    factory=MagicMock(return_value=client)
    monkeypatch.setattr('app.services.groq_service.Groq',factory)
    return client,factory


def test_groq_strict_extraction_and_config(monkeypatch):
    client,factory=setup_client(monkeypatch)
    result=GroqService().analyze('Test subject','Actual provided body')
    assert result.order_id=='DH001'
    args=client.chat.completions.create.call_args.kwargs
    assert args['model']==settings.groq_model
    assert 'Actual provided body' in args['messages'][1]['content']
    assert args['response_format']['json_schema']['strict'] is True
    assert args['response_format']['json_schema']['schema']==Analysis.model_json_schema()
    assert args['reasoning_effort']=='low'
    assert factory.call_args.kwargs['max_retries']==0


@pytest.mark.parametrize('content,reason',[('invalid','stop'),('{}','stop'),('', 'length')])
def test_groq_bad_output_is_not_used(monkeypatch,content,reason):
    setup_client(monkeypatch,content,reason)
    with pytest.raises(IntegrationError,match='invalid_ai_output'):
        GroqService().analyze('subject','body')


def test_groq_key_missing(monkeypatch):
    monkeypatch.setattr(settings,'groq_api_key','')
    with pytest.raises(IntegrationError,match='groq_not_configured'):
        GroqService().analyze('subject','body')


def test_groq_timeout(monkeypatch):
    client,_=setup_client(monkeypatch)
    client.chat.completions.create.side_effect=APITimeoutError(request=httpx.Request('POST','https://api.groq.com/openai/v1/chat/completions'))
    with pytest.raises(IntegrationError,match='groq_timeout_retry_sync'):
        GroqService().analyze('subject','body')


@pytest.mark.parametrize('code,expected',[(400,'groq_request_invalid'),(401,'groq_api_key_invalid'),(403,'groq_access_denied'),(404,'groq_model_not_found'),(429,'groq_rate_limited'),(503,'groq_service_unavailable')])
def test_groq_errors_are_sanitized(monkeypatch,code,expected):
    client,_=setup_client(monkeypatch)
    exc=RuntimeError('private provider payload')
    exc.status_code=code
    client.chat.completions.create.side_effect=exc
    with pytest.raises(IntegrationError,match=expected) as caught:
        GroqService().analyze('subject','body')
    assert 'private' not in str(caught.value)


def test_provider_switch_preserves_gemini(monkeypatch):
    monkeypatch.setattr(settings,'ai_provider','groq')
    assert isinstance(get_ai_service(),GroqService)
    monkeypatch.setattr(settings,'ai_provider','gemini')
    assert isinstance(get_ai_service(),GeminiService)


def test_status_reports_selected_provider_without_secrets(client,monkeypatch):
    monkeypatch.setattr(settings,'ai_provider','groq')
    monkeypatch.setattr(settings,'groq_api_key','private-test-key')
    response=client.get('/api/integrations/status')
    assert response.json()['ai_provider']=='groq'
    assert response.json()['ai_configured'] is True
    assert response.json()['ai_model']==settings.groq_model
    assert 'private-test-key' not in response.text
