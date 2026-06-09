"""Tests unitarios de los módulos de IA puros (sin red ni BD).

Cubre: intent_detector, lead_scorer, response_formatter, context_manager
(funciones sin sesión), voice_prompt_builder y context_manager helpers.
"""
from __future__ import annotations

from app.services.ai import (
    context_manager,
    intent_detector,
    lead_scorer,
    response_formatter,
)
from app.services.ai.intent_detector import Intent
from app.services.ai.voice_prompt_builder import (
    build_outbound_call_script,
    build_voice_system_prompt,
)


# ----------------------------- intent_detector -----------------------------

def test_detect_intent_priority_escalation():
    assert intent_detector.detect_intent("Es urgente, necesito ayuda") == Intent.ESCALATION


def test_detect_intent_appointment():
    assert intent_detector.detect_intent("Quiero agendar una cita") == Intent.APPOINTMENT


def test_detect_intent_price():
    assert intent_detector.detect_intent("¿Cuál es el precio?") == Intent.PRICE_INQUIRY


def test_detect_intent_greeting_short():
    assert intent_detector.detect_intent("Hola") == Intent.GREETING


def test_detect_intent_greeting_long_becomes_lead():
    # saludo + más de 5 palabras => LEAD
    assert (
        intent_detector.detect_intent("Hola quisiera saber algo importante por favor ahora")
        == Intent.LEAD
    )


def test_detect_intent_followup():
    assert intent_detector.detect_intent("Es de seguimiento de lo conversado") == Intent.FOLLOWUP


def test_detect_intent_faq():
    assert intent_detector.detect_intent("¿Qué es esto exactamente?") == Intent.FAQ


def test_detect_intent_unknown():
    assert intent_detector.detect_intent("zzz qqq www") == Intent.UNKNOWN


def test_detect_multiple_intents():
    found = intent_detector.detect_multiple_intents(
        "Hola, es urgente, quiero una cita y el precio"
    )
    assert Intent.ESCALATION in found
    assert Intent.APPOINTMENT in found
    assert Intent.PRICE_INQUIRY in found
    assert Intent.GREETING in found


def test_detect_multiple_intents_followup_and_faq():
    found = intent_detector.detect_multiple_intents(
        "seguimiento, qué es esto, cuéntame más"
    )
    assert Intent.FOLLOWUP in found
    assert Intent.FAQ in found


def test_detect_multiple_intents_unknown():
    assert intent_detector.detect_multiple_intents("zzz qqq") == [Intent.UNKNOWN]


def test_has_buying_signals_true():
    assert intent_detector.has_buying_signals("quiero comprar ahora")


def test_has_buying_signals_false():
    assert not intent_detector.has_buying_signals("solo estoy mirando opciones varias")


def test_extract_phone_numbers():
    nums = intent_detector.extract_phone_numbers("Mi número es +51 987654321")
    assert nums


def test_extract_names_found():
    assert intent_detector.extract_names("Hola, me llamo Carlos") == "Carlos"
    assert intent_detector.extract_names("soy Ana") == "Ana"
    assert intent_detector.extract_names("mi nombre es Pedro") == "Pedro"
    assert intent_detector.extract_names("habla Luis") == "Luis"


def test_extract_names_not_found():
    assert intent_detector.extract_names("no hay nombre aqui") is None


# ----------------------------- lead_scorer -----------------------------

def test_calculate_lead_score_cold():
    score, stage = lead_scorer.calculate_lead_score(
        messages_count=1,
        has_price_inquiry=False,
        has_appointment_request=False,
        has_personal_info=False,
    )
    assert stage == "cold"
    assert score < 34


def test_calculate_lead_score_hot_capped():
    score, stage = lead_scorer.calculate_lead_score(
        messages_count=20,
        has_price_inquiry=True,
        has_appointment_request=True,
        has_personal_info=True,
        response_speed_minutes=1,
    )
    assert score == 100
    assert stage == "hot"


def test_calculate_lead_score_warm():
    score, stage = lead_scorer.calculate_lead_score(
        messages_count=3,
        has_price_inquiry=True,
        has_appointment_request=False,
        has_personal_info=False,
        response_speed_minutes=4,
    )
    assert stage == "warm"


def test_calculate_lead_score_speed_buckets():
    # cubre los tres tramos de velocidad
    assert lead_scorer.calculate_lead_score(0, False, False, False, 1)[0] == 20
    assert lead_scorer.calculate_lead_score(0, False, False, False, 4)[0] == 17
    assert lead_scorer.calculate_lead_score(0, False, False, False, 10)[0] == 13
    assert lead_scorer.calculate_lead_score(0, False, False, False, 60)[0] == 10


def test_calculate_lead_score_from_conversation_data():
    score, stage = lead_scorer.calculate_lead_score_from_conversation_data(
        {"messages_count": 7, "has_price_inquiry": True}
    )
    assert score > 0
    assert stage in ("cold", "warm", "hot")


def test_calculate_lead_score_from_empty_data():
    score, stage = lead_scorer.calculate_lead_score_from_conversation_data({})
    assert stage == "cold"


def test_merge_lead_scores():
    assert lead_scorer.merge_lead_scores(80, 40) == int(80 * 0.7 + 40 * 0.3)
    assert lead_scorer.merge_lead_scores(200, 200) == 100
    assert lead_scorer.merge_lead_scores(-50, -50) == 0


def test_get_stage_label():
    assert lead_scorer.get_stage_label(70) == "hot"
    assert lead_scorer.get_stage_label(40) == "warm"
    assert lead_scorer.get_stage_label(10) == "cold"


def test_get_stage_display():
    assert lead_scorer.get_stage_display("cold") == "Frío"
    assert lead_scorer.get_stage_display("warm") == "Tibio"
    assert lead_scorer.get_stage_display("hot") == "Caliente"
    assert lead_scorer.get_stage_display("???") == "Desconocido"


# ----------------------------- response_formatter -----------------------------

def test_format_for_whatsapp_markdown_and_html():
    out = response_formatter.format_for_whatsapp(
        "<b>Hola</b> **negrita** __sub__\n# Título"
    )
    assert "<b>" not in out
    assert "*negrita*" in out
    assert "_sub_" in out
    assert "Título" in out


def test_format_for_whatsapp_limits_paragraphs():
    text = "\n\n".join(f"p{i}" for i in range(6))
    out = response_formatter.format_for_whatsapp(text)
    assert out.count("\n\n") == 2  # 3 párrafos


def test_format_for_whatsapp_truncates_long():
    out = response_formatter.format_for_whatsapp("a" * 5000)
    assert len(out) <= 4096
    assert out.endswith("...")


def test_format_for_voice_strips_markdown_emoji_url():
    out = response_formatter.format_for_voice(
        "**Hola** _mundo_\n- item\n1. uno\nhttps://x.com 😀"
    )
    assert "**" not in out
    assert "http" not in out
    assert "el enlace compartido" in out
    assert out.endswith(".")


def test_format_for_voice_keeps_terminal_punctuation():
    out = response_formatter.format_for_voice("Hola mundo!")
    assert out.endswith("!")


def test_split_long_message_short():
    assert response_formatter.split_long_message("corto") == ["corto"]


def test_split_long_message_by_paragraphs():
    text = "\n\n".join(["x" * 800, "y" * 800])
    parts = response_formatter.split_long_message(text, max_length=1000)
    assert len(parts) >= 2


def test_split_long_message_by_sentences():
    long_para = ". ".join(["frase" * 100 for _ in range(5)])
    parts = response_formatter.split_long_message(long_para, max_length=300)
    assert len(parts) > 1


def test_add_typing_delay_suggestion():
    assert response_formatter.add_typing_delay_suggestion("hola") == 4 * 30
    assert response_formatter.add_typing_delay_suggestion("a" * 1000) == 3000


# ----------------------------- context_manager (puro) -----------------------------

def test_build_context_summary_empty():
    assert context_manager.build_context_summary([]) == "Sin historial de conversación previo."


def test_build_context_summary_labels():
    msgs = [
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "¿En qué ayudo?"},
    ]
    out = context_manager.build_context_summary(msgs)
    assert "Cliente: Hola" in out
    assert "Asistente:" in out


def test_build_context_summary_truncates():
    msgs = [{"role": "user", "content": "x" * 300}]
    out = context_manager.build_context_summary(msgs, max_chars=50)
    assert out.endswith("...")


def test_trim_context_to_token_limit():
    msgs = [{"role": "user", "content": "a" * 100} for _ in range(10)]
    out = context_manager.trim_context_to_token_limit(msgs, system_prompt_chars=0, max_total_chars=250)
    # solo caben 2 mensajes de 100 chars dentro de 250
    assert len(out) == 2


def test_ensure_alternating_roles_empty():
    assert context_manager.ensure_alternating_roles([]) == []


def test_ensure_alternating_roles_merges():
    msgs = [
        {"role": "user", "content": "a"},
        {"role": "user", "content": "b"},
        {"role": "assistant", "content": "c"},
    ]
    out = context_manager.ensure_alternating_roles(msgs)
    assert len(out) == 2
    assert out[0]["content"] == "a\nb"


# ----------------------------- voice_prompt_builder -----------------------------

class _VoiceCfg:
    agent_name = "Lucía"
    language = "es"
    outbound_calling_hours = {}
    welcome_message = None
    max_call_duration_seconds = None
    escalation_phone = None


class _AgentCfg:
    services = [
        {"name": "Corte", "description": "rápido", "price": 25},
        {"name": "Color", "description": "tinte", "price": "S/50"},
        {"name": "Otro", "description": "x", "price": None},
    ]
    faqs = [{"question": "¿Horario?", "answer": "9-6"}]


def test_build_voice_system_prompt_inbound_defaults():
    out = build_voice_system_prompt(_VoiceCfg(), _AgentCfg(), call_direction="inbound")
    assert "Lucía" in out
    assert "LLAMADA ENTRANTE" in out
    assert "S/. 25.00" in out
    assert "S/50" in out
    assert "precio a consultar" in out


def test_build_voice_system_prompt_outbound_with_contact_and_escalation():
    cfg = _VoiceCfg()
    cfg.escalation_phone = "+51999"
    cfg.welcome_message = "Hola!"
    cfg.max_call_duration_seconds = 1200
    out = build_voice_system_prompt(
        cfg,
        _AgentCfg(),
        call_direction="outbound",
        contact_context={"full_name": "Juan", "previous_interactions": 3},
    )
    assert "LLAMADA SALIENTE" in out
    assert "Juan" in out
    assert "+51999" in out
    assert "3 interacciones" in out


def test_build_voice_system_prompt_no_agent_config_other_language():
    cfg = _VoiceCfg()
    cfg.language = "en"
    out = build_voice_system_prompt(cfg, None)
    assert "en" in out
    assert "Consultar con el equipo." in out


def test_build_outbound_call_script_with_services():
    out = build_outbound_call_script(
        "Ana", "MiNegocio", "Bot", "recordar cita", services=[{"name": "Spa"}]
    )
    assert "Ana" in out
    assert "Spa" in out


def test_build_outbound_call_script_no_services():
    out = build_outbound_call_script("Ana", "MiNegocio", "Bot", "recordar cita")
    assert "Ana" in out
