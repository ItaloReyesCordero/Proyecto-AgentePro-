from __future__ import annotations


def calculate_lead_score(
    messages_count: int,
    has_price_inquiry: bool,
    has_appointment_request: bool,
    has_personal_info: bool,
    response_speed_minutes: float | None = None,
) -> tuple[int, str]:
    """
    Calcula el puntaje de calificación del lead.

    Args:
        messages_count: Número de mensajes en la conversación.
        has_price_inquiry: Si el cliente preguntó por precios.
        has_appointment_request: Si el cliente solicitó una cita.
        has_personal_info: Si el cliente compartió datos personales (nombre, teléfono, etc).
        response_speed_minutes: Minutos que tardó el cliente en responder.

    Returns:
        Tupla (score: int 0-100, stage: str cold|warm|hot).
    """
    score = 10  # Puntaje base por haber contactado

    # Engagement por cantidad de mensajes
    if messages_count >= 3:
        score += 15
    if messages_count >= 7:
        score += 10
    if messages_count >= 15:
        score += 5

    # Señales de interés
    if has_price_inquiry:
        score += 20  # Preguntar precio es señal fuerte de intención
    if has_appointment_request:
        score += 25  # Solicitar cita es la señal más fuerte
    if has_personal_info:
        score += 10  # Dar datos personales muestra confianza

    # Velocidad de respuesta (respuesta rápida = mayor interés)
    if response_speed_minutes is not None:
        if response_speed_minutes < 2:
            score += 10  # Responde casi inmediatamente
        elif response_speed_minutes < 5:
            score += 7
        elif response_speed_minutes < 15:
            score += 3

    # Limitar a máximo 100
    score = min(score, 100)

    # Determinar etapa
    if score >= 67:
        stage = "hot"
    elif score >= 34:
        stage = "warm"
    else:
        stage = "cold"

    return score, stage


def calculate_lead_score_from_conversation_data(
    data: dict,
) -> tuple[int, str]:
    """
    Calcula el lead score desde un diccionario de datos de conversación.

    Args:
        data: Diccionario con claves opcionales:
            - messages_count (int)
            - has_price_inquiry (bool)
            - has_appointment_request (bool)
            - has_personal_info (bool)
            - response_speed_minutes (float)
    """
    return calculate_lead_score(
        messages_count=data.get("messages_count", 0),
        has_price_inquiry=data.get("has_price_inquiry", False),
        has_appointment_request=data.get("has_appointment_request", False),
        has_personal_info=data.get("has_personal_info", False),
        response_speed_minutes=data.get("response_speed_minutes"),
    )


def merge_lead_scores(ai_score: int, rule_score: int, ai_weight: float = 0.7) -> int:
    """
    Combina el score de la IA con el score calculado por reglas.

    Args:
        ai_score: Score asignado por Claude (0-100).
        rule_score: Score calculado por reglas (0-100).
        ai_weight: Peso del score de IA (default 70%).

    Returns:
        Score combinado (0-100).
    """
    combined = int(ai_score * ai_weight + rule_score * (1 - ai_weight))
    return max(0, min(combined, 100))


def get_stage_label(score: int) -> str:
    """Retorna la etiqueta del stage basada en el score."""
    if score >= 67:
        return "hot"
    elif score >= 34:
        return "warm"
    return "cold"


def get_stage_display(stage: str) -> str:
    """Retorna la etiqueta legible del stage."""
    labels = {
        "cold": "Frío",
        "warm": "Tibio",
        "hot": "Caliente",
    }
    return labels.get(stage, "Desconocido")
