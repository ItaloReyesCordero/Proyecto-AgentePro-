from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from app.utils.helpers import is_within_business_hours, get_peru_now

if TYPE_CHECKING:
    from app.models.agent_config import AgentConfig


def build_whatsapp_system_prompt(
    agent_config: AgentConfig,
    current_datetime: datetime | None = None,
    channel: str = "whatsapp",
) -> str:
    if current_datetime is None:
        current_datetime = get_peru_now()

    within_hours = is_within_business_hours(
        agent_config.business_hours or {}, current_datetime
    )

    # Instrucciones de personalidad
    personality_instructions: dict[str, str] = {
        "formal": (
            "Usa SIEMPRE 'usted'. Lenguaje profesional y cortés. "
            "Sin emojis excesivos. Respuestas estructuradas."
        ),
        "amigable": (
            "Usa 'tú'. Tono cálido y cercano. Usa emojis moderadamente "
            "(máximo 2-3 por mensaje). Muy accesible."
        ),
        "profesional": (
            "Equilibra lo formal y lo cercano. 'usted' para primeros contactos, "
            "'tú' si el cliente tutea. Pocos emojis."
        ),
        "energico": (
            "¡Muy dinámico! Usa exclamaciones. Emojis energéticos. "
            "Muy entusiasta y motivador."
        ),
    }
    personality = getattr(agent_config, "personality", "profesional") or "profesional"
    personality_instruction = personality_instructions.get(personality, personality_instructions["profesional"])

    # Horario formateado
    day_names = {
        "lunes": "Lunes",
        "martes": "Martes",
        "miercoles": "Miércoles",
        "jueves": "Jueves",
        "viernes": "Viernes",
        "sabado": "Sábado",
        "domingo": "Domingo",
    }
    business_hours_str = ""
    for day_key, day_name in day_names.items():
        day_config = (agent_config.business_hours or {}).get(day_key, {})
        if day_config.get("active", False):
            business_hours_str += (
                f"  - {day_name}: {day_config.get('open', '09:00')} "
                f"- {day_config.get('close', '18:00')}\n"
            )
        else:
            business_hours_str += f"  - {day_name}: Cerrado\n"

    # Servicios formateados
    services_str = ""
    for svc in agent_config.services or []:
        price_val = svc.get("price")
        # El precio puede venir como número (25) o como texto ("S/25", "consultar").
        if price_val in (None, ""):
            price_str = "Consultar precio"
        elif isinstance(price_val, (int, float)):
            price_str = f"S/. {price_val:.2f}"
        else:
            price_str = str(price_val)
        services_str += (
            f"  - {svc.get('name', '')}: {svc.get('description', '')} | {price_str}\n"
        )

    # FAQs formateadas
    faqs_str = ""
    for faq in agent_config.faqs or []:
        faqs_str += (
            f"  P: {faq.get('question', '')}\n"
            f"  R: {faq.get('answer', '')}\n\n"
        )

    # Escalation keywords
    escalation_keywords = ", ".join(
        agent_config.escalation_keywords or ["urgente", "emergencia", "queja", "hablar con"]
    )

    # Nombre del negocio (puede estar en agent_name o en un campo extra)
    business_name = getattr(agent_config, "business_name", None) or agent_config.agent_name
    agent_name = agent_config.agent_name

    # Citas habilitadas
    appointment_enabled = getattr(agent_config, "appointment_enabled", False)

    # Mensaje fuera de horario
    outside_hours_message = getattr(agent_config, "outside_hours_message", None) or ""

    # Teléfono de escalación
    escalation_phone = agent_config.escalation_phone or ""

    # Instrucciones personalizadas
    custom_instructions = getattr(agent_config, "custom_instructions", None) or "Ninguna instrucción adicional."

    # Bloque de escalación
    if escalation_phone:
        escalation_action_msg = (
            f"Voy a conectarte con nuestro equipo ahora mismo. "
            f"También puedes llamar al {escalation_phone}."
        )
    else:
        escalation_action_msg = "Voy a conectarte con nuestro equipo ahora mismo."

    # Fecha formateada en español
    date_formatted = current_datetime.strftime("%A %d de %B de %Y, %H:%M")

    prompt = f"""## IDENTIDAD Y ROL
Eres {agent_name}, el asistente virtual de {business_name}.
Canal de atención: {'WhatsApp' if channel == 'whatsapp' else 'Instagram Direct'}

PERSONALIDAD: {personality.upper()}
{personality_instruction}

## FUNCIONES PRINCIPALES
1. Responder preguntas frecuentes con la información EXACTA del negocio
2. Presentar servicios y precios cuando pregunten
3. Calificar leads (detectar intención de compra, urgencia, presupuesto)
4. Agendar citas {'(SÍ habilitado)' if appointment_enabled else '(NO habilitado - solo informar)'}
5. Hacer seguimiento de interés
6. Escalar a humano cuando sea necesario

## HORARIO ACTUAL
Fecha y hora en Perú: {date_formatted}
Horario de atención:
{business_hours_str}
Estado actual: {'✅ DENTRO del horario de atención' if within_hours else '⚠️ FUERA del horario de atención'}
{f"Mensaje fuera de horario: {outside_hours_message}" if not within_hours and outside_hours_message else ""}

## CATÁLOGO DE SERVICIOS
{services_str if services_str else "Consultar directamente con el equipo."}

## BASE DE CONOCIMIENTO — PREGUNTAS FRECUENTES
{faqs_str if faqs_str else "Responde con información general del negocio."}

## SISTEMA DE CALIFICACIÓN DE LEADS
Evalúa mentalmente en cada mensaje:
- Interés: ¿está buscando activamente? (0-33 frío, 34-66 tibio, 67-100 caliente)
- Urgencia: ¿necesita el servicio pronto?
- Presupuesto: ¿puede pagar? ¿mencionó precio?
- Autoridad: ¿es quien decide?

## CUÁNDO ESCALAR A HUMANO
Escala INMEDIATAMENTE si el cliente dice: {escalation_keywords}
También escala si:
- Pregunta algo crítico que no sabes
- Expresa molestia o frustración
- Lleva más de 5 mensajes sin resolver
- La consulta es legal, médica o muy técnica

Al escalar, di: "{escalation_action_msg}"
Y agrega al final: <!--ACTION:ESCALATE-->

## METADATOS DE RESPUESTA (OBLIGATORIO)
Al final de CADA respuesta, agrega este bloque (NO visible para el cliente):
<!--META:{{"intent":"faq|appointment|lead|escalation|greeting|followup","confidence":0.95,"lead_score":50,"lead_stage":"cold","actions":[],"appointment_date":null,"key_info_extracted":{{}}}}-->

REGLA DE CITAS: cuando el cliente quiera AGENDAR/RESERVAR una cita (o pida hora), pon
`"intent":"appointment"`. Si mencionó día/hora, pon `"appointment_date"` en formato
ISO `YYYY-MM-DDTHH:MM` (usa la fecha/hora actual de Perú como referencia para "mañana",
"el viernes", etc.; si solo dijo el día, usa la hora 00:00). En `key_info_extracted`
incluye `"service"` (el servicio pedido) y `"name"` (nombre del cliente) si los sabes.

## INSTRUCCIONES ESPECIALES
{custom_instructions}

## REGLAS ABSOLUTAS
1. Nunca inventes precios que no están en tu lista
2. Nunca hagas promesas que el negocio no puede cumplir
3. No digas que eres una IA a menos que insistan 3+ veces
4. Respuestas máximo 3 párrafos — WhatsApp es conversación, no email
5. Si mandan audio: "Hola 😊 Por ahora solo puedo leer texto. ¿Puedes escribirme?"
6. Usa el nombre del cliente si lo sabes
7. Termina siempre con una pregunta para mantener la conversación
8. NUNCA incluyas el bloque META en el texto visible de tu respuesta"""

    return prompt
