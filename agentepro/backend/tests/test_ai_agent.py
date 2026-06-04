from __future__ import annotations

from app.models.agent_config import AgentConfig
from app.services.ai.agent import AIAgentService
from app.services.ai.prompt_builder import build_whatsapp_system_prompt


def _config() -> AgentConfig:
    cfg = AgentConfig(
        tenant_id=None,
        agent_name="María",
        faqs=[{"question": "¿Horario?", "answer": "9 a 6"}],
        services=[{"name": "Consulta", "description": "30 min", "price": 80.0}],
        escalation_keywords=["urgente", "queja"],
    )
    return cfg


def test_prompt_contains_identity_and_services() -> None:
    prompt = build_whatsapp_system_prompt(_config())
    assert "María" in prompt
    assert "Consulta" in prompt
    assert "S/. 80.00" in prompt
    assert "urgente" in prompt


def test_parse_meta_extracts_fields() -> None:
    agent = AIAgentService()
    raw = (
        "Claro, con gusto.\n"
        '<!--META:{"intent":"appointment","confidence":0.9,"lead_score":80,'
        '"lead_stage":"hot","actions":["book_appointment"],"appointment_date":null,'
        '"key_info_extracted":{"service_interest":"consulta"}}-->'
    )
    meta = agent._parse_meta(raw)
    assert meta["intent"] == "appointment"
    assert meta["lead_score"] == 80
    assert meta["lead_stage"] == "hot"


def test_parse_meta_fallback_on_missing_block() -> None:
    agent = AIAgentService()
    meta = agent._parse_meta("Respuesta sin metadatos")
    assert meta["intent"] == "unknown"
    assert meta["lead_stage"] == "cold"


def test_clean_response_removes_meta_and_action() -> None:
    agent = AIAgentService()
    raw = "Hola 👋<!--ACTION:ESCALATE--><!--META:{\"intent\":\"x\"}-->"
    cleaned = agent._clean_response(raw)
    assert "META" not in cleaned
    assert "ACTION" not in cleaned
    assert cleaned.startswith("Hola")
