"""Tests unitarios de las propiedades de cobro/estado del modelo Tenant.

Se construyen Tenants en memoria (sin BD). OJO: SQLAlchemy NO aplica los
`default=` de columna hasta el INSERT, así que cada test fija explícitamente
los atributos de los que depende la propiedad bajo prueba.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.models.tenant import PlanType, Tenant


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _tenant(**kwargs) -> Tenant:
    """Tenant en memoria con los campos de cobro en valores neutros por defecto."""
    base = dict(
        name="N",
        slug="n",
        plan=PlanType.TRIAL,
        trial_ends_at=None,
        next_payment_due=None,
        billing_suspended=False,
        monthly_amount_pen=None,
    )
    base.update(kwargs)
    return Tenant(**base)


# --- is_trial_expired --------------------------------------------------------


def test_trial_expired_when_past():
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=_now() - timedelta(days=1))
    assert t.is_trial_expired is True


def test_trial_not_expired_when_future():
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=_now() + timedelta(days=5))
    assert t.is_trial_expired is False


def test_trial_not_expired_when_no_end_date():
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=None)
    assert t.is_trial_expired is False


@pytest.mark.parametrize("plan", [PlanType.BASIC, PlanType.PROFESSIONAL, PlanType.ENTERPRISE])
def test_paid_plan_never_trial_expired(plan):
    t = _tenant(plan=plan, trial_ends_at=_now() - timedelta(days=100))
    assert t.is_trial_expired is False


def test_trial_expired_handles_naive_datetime():
    # trial_ends_at sin tzinfo se asume UTC.
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=datetime.utcnow() - timedelta(days=2))
    assert t.is_trial_expired is True


# --- payment_due_at ----------------------------------------------------------


def test_payment_due_at_uses_trial_end_when_trial():
    end = _now() + timedelta(days=3)
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=end)
    assert t.payment_due_at == end


def test_payment_due_at_uses_next_due_when_paid():
    due = _now() + timedelta(days=10)
    t = _tenant(plan=PlanType.BASIC, next_payment_due=due)
    assert t.payment_due_at == due


# --- payment_state -----------------------------------------------------------


def test_state_suspended_takes_priority():
    t = _tenant(plan=PlanType.BASIC, billing_suspended=True, next_payment_due=_now() + timedelta(days=30))
    assert t.payment_state == "suspended"


def test_state_trial_with_no_due_is_trial():
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=None)
    assert t.payment_state == "trial"


def test_state_active_when_paid_no_due():
    t = _tenant(plan=PlanType.BASIC, next_payment_due=None)
    assert t.payment_state == "active"


def test_state_overdue_when_due_in_past():
    t = _tenant(plan=PlanType.BASIC, next_payment_due=_now() - timedelta(days=1))
    assert t.payment_state == "overdue"


def test_state_due_soon_within_3_days():
    t = _tenant(plan=PlanType.BASIC, next_payment_due=_now() + timedelta(days=2))
    assert t.payment_state == "due_soon"


def test_state_active_when_far_in_future():
    t = _tenant(plan=PlanType.BASIC, next_payment_due=_now() + timedelta(days=20))
    assert t.payment_state == "active"


def test_state_trial_due_soon_near_trial_end():
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=_now() + timedelta(days=1))
    assert t.payment_state == "due_soon"


def test_state_trial_overdue_when_trial_passed():
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=_now() - timedelta(hours=2))
    assert t.payment_state == "overdue"


def test_state_trial_active_when_far_from_end():
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=_now() + timedelta(days=10))
    assert t.payment_state == "trial"


@pytest.mark.parametrize(
    "days,expected",
    [
        (-5, "overdue"),
        (-1, "overdue"),
        (1, "due_soon"),
        (3, "due_soon"),
        (4, "active"),
        (15, "active"),
    ],
)
def test_state_thresholds_for_paid_plan(days, expected):
    t = _tenant(plan=PlanType.BASIC, next_payment_due=_now() + timedelta(days=days))
    assert t.payment_state == expected


# --- service_blocked ---------------------------------------------------------


def test_service_blocked_when_suspended():
    t = _tenant(plan=PlanType.BASIC, billing_suspended=True)
    assert t.service_blocked is True


def test_service_blocked_when_trial_expired():
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=_now() - timedelta(days=1), billing_suspended=False)
    assert t.service_blocked is True


def test_service_not_blocked_when_active_paid():
    t = _tenant(plan=PlanType.BASIC, billing_suspended=False, next_payment_due=_now() + timedelta(days=30))
    assert t.service_blocked is False


def test_service_not_blocked_during_valid_trial():
    t = _tenant(plan=PlanType.TRIAL, trial_ends_at=_now() + timedelta(days=7), billing_suspended=False)
    assert t.service_blocked is False


# --- enum y repr -------------------------------------------------------------


def test_plan_enum_values():
    assert PlanType.TRIAL.value == "trial"
    assert PlanType.BASIC.value == "basic"
    assert PlanType.PROFESSIONAL.value == "professional"
    assert PlanType.ENTERPRISE.value == "enterprise"


def test_due_soon_days_constant():
    assert Tenant.PAYMENT_DUE_SOON_DAYS == 3
