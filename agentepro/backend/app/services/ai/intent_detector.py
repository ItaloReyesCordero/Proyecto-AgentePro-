from __future__ import annotations
import re
from enum import Enum


class Intent(str, Enum):
    APPOINTMENT = "appointment"
    FAQ = "faq"
    LEAD = "lead"
    ESCALATION = "escalation"
    GREETING = "greeting"
    FOLLOWUP = "followup"
    PRICE_INQUIRY = "price_inquiry"
    UNKNOWN = "unknown"


APPOINTMENT_KEYWORDS = [
    "cita", "agendar", "reservar", "turno", "cuándo puedo", "disponibilidad",
    "horario disponible", "quiero una cita", "necesito una cita", "cuando tienen",
    "pueden atenderme", "hay turno",
]

PRICE_KEYWORDS = [
    "precio", "costo", "cuánto", "tarifa", "cuánto cuesta", "vale", "cuesta",
    "cuanto vale", "cuanto es", "me puedes dar un precio", "cotización", "cotizar",
    "presupuesto", "cobran", "cobras",
]

ESCALATION_KEYWORDS = [
    "urgente", "emergencia", "queja", "hablar con", "hablar con alguien",
    "quiero hablar", "necesito un agente", "con una persona", "con un humano",
    "problema grave", "muy urgente", "es urgente", "es una emergencia",
    "no me estás ayudando", "esto no sirve",
]

GREETING_KEYWORDS = [
    "hola", "buenos días", "buenas tardes", "buenas noches", "hi", "hello",
    "buenas", "buen día", "oe", "ola", "hey",
]

FOLLOWUP_KEYWORDS = [
    "ya te contacté", "ya llamé", "como quedamos", "según lo conversado",
    "hablamos antes", "es de seguimiento", "seguimiento",
]

FAQ_KEYWORDS = [
    "cómo funciona", "qué es", "me puedes explicar", "qué hacen",
    "a qué se dedican", "información", "cuéntame más", "más info",
]


def detect_intent(text: str) -> Intent:
    """
    Detecta la intención principal de un mensaje de texto.

    Prioridad: ESCALATION > APPOINTMENT > PRICE_INQUIRY > GREETING > FOLLOWUP > FAQ > UNKNOWN
    """
    text_lower = text.lower().strip()

    if any(kw in text_lower for kw in ESCALATION_KEYWORDS):
        return Intent.ESCALATION

    if any(kw in text_lower for kw in APPOINTMENT_KEYWORDS):
        return Intent.APPOINTMENT

    if any(kw in text_lower for kw in PRICE_KEYWORDS):
        return Intent.PRICE_INQUIRY

    if any(kw in text_lower for kw in GREETING_KEYWORDS):
        # Si el saludo va acompañado de otra cosa, puede ser lead
        if len(text_lower.split()) > 5:
            return Intent.LEAD
        return Intent.GREETING

    if any(kw in text_lower for kw in FOLLOWUP_KEYWORDS):
        return Intent.FOLLOWUP

    if any(kw in text_lower for kw in FAQ_KEYWORDS):
        return Intent.FAQ

    return Intent.UNKNOWN


def detect_multiple_intents(text: str) -> list[Intent]:
    """Detecta todas las intenciones presentes en un mensaje (puede haber varias)."""
    text_lower = text.lower().strip()
    found: list[Intent] = []

    if any(kw in text_lower for kw in ESCALATION_KEYWORDS):
        found.append(Intent.ESCALATION)
    if any(kw in text_lower for kw in APPOINTMENT_KEYWORDS):
        found.append(Intent.APPOINTMENT)
    if any(kw in text_lower for kw in PRICE_KEYWORDS):
        found.append(Intent.PRICE_INQUIRY)
    if any(kw in text_lower for kw in GREETING_KEYWORDS):
        found.append(Intent.GREETING)
    if any(kw in text_lower for kw in FOLLOWUP_KEYWORDS):
        found.append(Intent.FOLLOWUP)
    if any(kw in text_lower for kw in FAQ_KEYWORDS):
        found.append(Intent.FAQ)

    if not found:
        found.append(Intent.UNKNOWN)

    return found


def has_buying_signals(text: str) -> bool:
    """Detecta señales de compra en el texto."""
    buying_signals = [
        "quiero comprar", "me interesa", "voy a llevar", "me lo llevo",
        "lo quiero", "lo necesito", "puedo pagar", "tengo el dinero",
        "cuándo puedo pagar", "cómo pago", "formas de pago", "acepta tarjeta",
        "puede ser hoy", "para mañana", "lo más pronto", "urgente",
        "ya decidí", "me decidí", "contratar",
    ]
    text_lower = text.lower()
    return any(signal in text_lower for signal in buying_signals)


def extract_phone_numbers(text: str) -> list[str]:
    """Extrae números de teléfono del texto."""
    pattern = r"(?:\+51\s?)?(?:9\d{8}|\d{2,3}[-.\s]?\d{4,})"
    return re.findall(pattern, text)


def extract_names(text: str) -> str | None:
    """Intenta extraer el nombre del cliente del texto."""
    name_patterns = [
        r"me llamo (\w+ ?\w*)",
        r"soy (\w+ ?\w*)",
        r"mi nombre es (\w+ ?\w*)",
        r"habla (\w+ ?\w*)",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text.lower())
        if match:
            name = match.group(1).strip()
            return name.title()
    return None
