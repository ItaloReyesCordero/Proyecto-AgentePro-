from __future__ import annotations

from app.services.culqi_service import CulqiService
from app.utils.helpers import derive_lead_stage, lead_stage_to_contact_status
from app.webhooks.retell import _parse_event


def test_parse_retell_event() -> None:
    body = {
        "event": "call_ended",
        "call": {
            "call_id": "call_123",
            "from_number": "+51999",
            "to_number": "+51900",
            "direction": "inbound",
            "transcript": "Hola, quiero una cita",
            "duration_ms": 65000,
        },
    }
    event = _parse_event(body)
    assert event.event == "call_ended"
    assert event.call_id == "call_123"
    assert event.duration_ms == 65000
    assert "cita" in event.transcript


def test_culqi_event_classification() -> None:
    assert (
        CulqiService.handle_webhook_event({"type": "charge.creation.success"})
        == "renew_subscription"
    )
    assert (
        CulqiService.handle_webhook_event({"type": "charge.creation.failed"})
        == "notify_payment_failed"
    )
    assert (
        CulqiService.handle_webhook_event({"type": "subscription.cancel"})
        == "deactivate_tenant"
    )
    assert CulqiService.handle_webhook_event({"type": "other.event"}) == "ignore"


def test_derive_lead_stage() -> None:
    assert derive_lead_stage("customer", 10) == "customer"
    assert derive_lead_stage("blocked", 90) == "lost"
    assert derive_lead_stage("lead", 80) == "hot"
    assert derive_lead_stage("lead", 50) == "warm"
    assert derive_lead_stage("lead", 10) == "cold"


def test_lead_stage_roundtrip() -> None:
    assert lead_stage_to_contact_status("customer") == "customer"
    assert lead_stage_to_contact_status("hot") == "prospect"
    assert lead_stage_to_contact_status("cold") == "lead"
