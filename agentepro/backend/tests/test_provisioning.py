from __future__ import annotations

from app.models.tenant import BusinessType, PlanType
from app.services.provisioning.tenant_provisioner import (
    _DEFAULT_FAQS,
    _business_enum,
    _plan_enum,
    _slugify,
)


def test_slugify_is_unique_and_clean() -> None:
    s1 = _slugify("Clínica San José!!")
    s2 = _slugify("Clínica San José!!")
    assert s1 != s2  # sufijo aleatorio
    assert " " not in s1
    assert s1.startswith("cl")


def test_plan_enum_defaults_to_basic() -> None:
    assert _plan_enum("professional") == PlanType.PROFESSIONAL
    assert _plan_enum("invalid") == PlanType.BASIC


def test_business_enum_defaults_to_other() -> None:
    assert _business_enum("healthcare") == BusinessType.HEALTHCARE
    assert _business_enum("nope") == BusinessType.OTHER


def test_default_faqs_exist_for_each_known_type() -> None:
    for key in ("healthcare", "education", "retail", "services"):
        assert key in _DEFAULT_FAQS
        assert len(_DEFAULT_FAQS[key]) >= 1
        assert "question" in _DEFAULT_FAQS[key][0]
