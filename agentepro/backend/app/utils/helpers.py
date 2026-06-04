from __future__ import annotations
import re
from datetime import datetime
import phonenumbers


def normalize_phone(phone: str) -> str:
    try:
        parsed = phonenumbers.parse(phone, "PE")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return phone


def get_peru_now() -> datetime:
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo("America/Lima"))


def is_within_business_hours(business_hours: dict, dt: datetime | None = None) -> bool:
    if dt is None:
        dt = get_peru_now()
    day_names = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    day_key = day_names[dt.weekday()]
    day_config = business_hours.get(day_key, {})
    if not day_config.get("active", False):
        return False
    open_time = day_config.get("open", "00:00")
    close_time = day_config.get("close", "23:59")
    current_time = dt.strftime("%H:%M")
    return open_time <= current_time <= close_time


def sanitize_for_prompt(text: str, max_length: int = 2000) -> str:
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = text[:max_length]
    return text.strip()


def normalize_phone_number(phone: str) -> str:
    """Normaliza un número de teléfono eliminando espacios y caracteres especiales."""
    return re.sub(r"[^\d+]", "", phone)


def phone_matches_any(phone: str | None, candidates: list[str] | None) -> bool:
    """True si `phone` coincide con alguno de `candidates`, de forma tolerante.

    Compara solo dígitos y por los últimos 9 (largo de móvil peruano), así
    ``+51 999 888 777``, ``51999888777`` y ``999888777`` se consideran iguales.
    """
    if not phone or not candidates:
        return False

    def _digits(p: str) -> str:
        d = re.sub(r"\D", "", p or "")
        return d[-9:] if len(d) >= 9 else d

    target = _digits(phone)
    if not target:
        return False
    return any(_digits(c) == target for c in candidates if c)


def format_currency_soles(amount: float) -> str:
    """Formatea un monto en soles peruanos."""
    return f"S/. {amount:.2f}"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Trunca texto a una longitud máxima."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def derive_lead_stage(contact_status: str | None, score: int) -> str:
    """Mapea el estado del contacto + score a la etapa de lead del dashboard.

    Etapas del frontend: cold | warm | hot | customer | lost.
    """
    status = (contact_status or "").lower()
    if status == "customer":
        return "customer"
    if status in {"inactive", "blocked"}:
        return "lost"
    if score >= 67:
        return "hot"
    if score >= 34:
        return "warm"
    return "cold"


def lead_stage_to_contact_status(lead_stage: str) -> str:
    """Inverso de derive_lead_stage para actualizar el contacto desde el dashboard."""
    mapping = {
        "cold": "lead",
        "warm": "prospect",
        "hot": "prospect",
        "customer": "customer",
        "lost": "inactive",
    }
    return mapping.get((lead_stage or "").lower(), "lead")


def enum_value(value: object) -> str:
    """Devuelve el `.value` de un Enum o el str del valor."""
    return getattr(value, "value", value) if value is not None else ""
