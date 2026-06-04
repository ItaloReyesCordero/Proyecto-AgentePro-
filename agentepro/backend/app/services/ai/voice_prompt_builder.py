from __future__ import annotations
from datetime import datetime
from typing import Any, TYPE_CHECKING
from app.utils.helpers import is_within_business_hours, get_peru_now

if TYPE_CHECKING:
    from app.models.voice_config import VoiceConfig
    from app.models.agent_config import AgentConfig


def build_voice_system_prompt(
    voice_config: VoiceConfig,
    agent_config: AgentConfig | None = None,
    call_direction: str = "inbound",
    contact_context: dict[str, Any] | None = None,
) -> str:
    """
    Construye el system prompt para el agente de voz (Retell AI).

    Args:
        voice_config: Configuración del agente de voz del tenant.
        agent_config: Configuración del agente de chat (para reutilizar FAQs y servicios).
        call_direction: 'inbound' o 'outbound'.
        contact_context: Datos del contacto (nombre, historial, etc).
    """
    current_datetime = get_peru_now()

    # Determinar si está en horario
    calling_hours = voice_config.outbound_calling_hours or {}
    within_hours = is_within_business_hours(calling_hours, current_datetime)

    # Nombre del contacto
    contact_name = ""
    contact_history = ""
    if contact_context:
        contact_name = contact_context.get("full_name") or contact_context.get("name") or ""
        prev_interactions = contact_context.get("previous_interactions", 0)
        if prev_interactions:
            contact_history = f"\nEste cliente ha tenido {prev_interactions} interacciones previas."

    # Saludo personalizado
    greeting_name = f", {contact_name}" if contact_name else ""

    # Servicios del agente de chat
    services_str = ""
    if agent_config and agent_config.services:
        for svc in agent_config.services:
            price_val = svc.get("price")
            # El precio puede venir como número (25) o como texto ("S/25", "consultar").
            if price_val in (None, ""):
                price_str = "precio a consultar"
            elif isinstance(price_val, (int, float)):
                price_str = f"S/. {price_val:.2f}"
            else:
                price_str = str(price_val)
            services_str += f"  - {svc.get('name', '')}: {svc.get('description', '')} ({price_str})\n"

    # FAQs resumidas
    faqs_str = ""
    if agent_config and agent_config.faqs:
        for faq in agent_config.faqs[:5]:  # Máximo 5 FAQs para voz
            faqs_str += f"  P: {faq.get('question', '')}\n  R: {faq.get('answer', '')}\n\n"

    # Mensaje de bienvenida
    welcome = voice_config.welcome_message or "Hola, gracias por llamar. ¿En qué puedo ayudarte?"

    # Duración máxima
    max_duration_min = (voice_config.max_call_duration_seconds or 600) // 60

    # Teléfono de escalación
    escalation_phone = voice_config.escalation_phone or ""
    escalation_str = (
        f"Si el cliente solicita hablar con un humano, indícale que le transferirás y di: "
        f"'Por favor espera, voy a transferirte con un agente. "
        f"También puedes llamar directamente al {escalation_phone}.' "
        if escalation_phone
        else "Si el cliente solicita hablar con un humano, indícale que le transferirás con el equipo."
    )

    # Instrucciones específicas por dirección de llamada
    if call_direction == "outbound":
        direction_instructions = f"""## LLAMADA SALIENTE
Estás llamando proactivamente al cliente{greeting_name}.
- Preséntate INMEDIATAMENTE: "{welcome}"
- Sé conciso y directo — el cliente no te estaba esperando
- Pregunta si es buen momento antes de continuar
- Si no contesta o está ocupado, ofrece llamar en otro horario
- Máximo {max_duration_min} minutos de llamada
{contact_history}"""
    else:
        direction_instructions = f"""## LLAMADA ENTRANTE
El cliente está llamando y tú eres el primero en responder.
- Saluda con: "{welcome}"
- Escucha activamente qué necesita
- No interrumpas — deja que termine de hablar
- Máximo {max_duration_min} minutos de llamada
{contact_history}"""

    prompt = f"""## IDENTIDAD
Eres {voice_config.agent_name}, agente de voz de la empresa.
Idioma: {'Español' if voice_config.language == 'es' else voice_config.language}

## CONTEXTO DE LA LLAMADA
{direction_instructions}

## REGLAS DE CONVERSACIÓN PARA VOZ
1. Habla de forma NATURAL — usa pausas, confirmaciones ("entiendo", "claro", "por supuesto")
2. NO uses markdown, listas con guiones ni asteriscos — solo texto hablado
3. Las respuestas deben ser CORTAS (máximo 2-3 oraciones por turno)
4. Confirma siempre que entendiste: "Entonces me dice que..."
5. Deletrea números y fechas claramente
6. No repitas el mismo texto dos veces

## CAPACIDADES
- Responder preguntas sobre servicios y precios
- Agendar citas y recordatorios
- Calificar el interés del cliente
- Tomar mensajes para el equipo

## CATÁLOGO DE SERVICIOS
{services_str if services_str else "Consultar con el equipo."}

## PREGUNTAS FRECUENTES
{faqs_str if faqs_str else "Responde con información general del negocio."}

## TRANSFERENCIA A HUMANO
{escalation_str}
Palabras clave para transferir: urgente, emergencia, queja, hablar con persona, supervisor

## CIERRE DE LLAMADA
Antes de terminar:
1. Resume lo acordado
2. Confirma próximos pasos
3. Agradece la llamada: "Fue un placer atenderle. Que tenga un excelente día."

## GRABACIÓN Y PRIVACIDAD
Informa al inicio si la llamada será grabada.
Nunca pidas información de tarjetas de crédito por teléfono."""

    return prompt


def build_outbound_call_script(
    contact_name: str,
    business_name: str,
    agent_name: str,
    purpose: str,
    services: list[dict[str, Any]] | None = None,
) -> str:
    """Genera un script específico para llamadas outbound de seguimiento."""
    services_mention = ""
    if services:
        service_names = [s.get("name", "") for s in services[:3]]
        services_mention = f"Tenemos disponible: {', '.join(service_names)}."

    return f"""## SCRIPT LLAMADA OUTBOUND
Eres {agent_name} de {business_name}.
Llamando a: {contact_name}
Propósito: {purpose}

APERTURA:
"Buenos días/tardes, ¿hablo con {contact_name}? Soy {agent_name} de {business_name}.
¿Tiene un momento? Le llamo porque {purpose}."

SI ACEPTA HABLAR:
- Desarrolla el propósito de la llamada
- {services_mention}
- Ofrece resolver dudas
- Intenta agendar siguiente paso

SI ESTÁ OCUPADO:
"Entiendo perfectamente. ¿Cuándo sería un buen momento para llamarle?
Le puedo llamar mañana en la mañana o en la tarde, lo que prefiera."

SI NO CONTESTA:
Deja mensaje de voz breve: "Hola {contact_name}, le habla {agent_name} de {business_name}.
Le llamé por {purpose}. Por favor comuníquese al número que aparece en su pantalla. ¡Gracias!"

CIERRE POSITIVO:
"Perfecto, entonces quedamos en [ACCIÓN]. Muchas gracias por su tiempo. ¡Que tenga excelente día!"
"""
