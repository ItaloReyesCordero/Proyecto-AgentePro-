from __future__ import annotations
import json
from anthropic import AsyncAnthropic
from dataclasses import dataclass
from typing import Any
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CallSummary:
    summary: str
    key_points: list[str]
    sentiment: str  # positive, neutral, negative
    intent: str
    next_action: str
    appointment_requested: bool
    appointment_details: str | None
    lead_score: int
    lead_stage: str
    contact_info_extracted: dict[str, Any]
    tokens_used: int


SUMMARIZER_SYSTEM_PROMPT = """Eres un asistente especializado en analizar transcripciones de llamadas de ventas y atención al cliente en español peruano.

Tu tarea: analizar la transcripción de una llamada y devolver un JSON con el siguiente formato EXACTO (sin texto adicional):

{
  "summary": "Resumen ejecutivo de la llamada en 2-3 oraciones",
  "key_points": ["Punto clave 1", "Punto clave 2", "Punto clave 3"],
  "sentiment": "positive|neutral|negative",
  "intent": "appointment|inquiry|complaint|purchase|followup|unknown",
  "next_action": "Descripción de la acción recomendada",
  "appointment_requested": true|false,
  "appointment_details": "Fecha/hora mencionada o null",
  "lead_score": 0,
  "lead_stage": "cold|warm|hot",
  "contact_info_extracted": {
    "name": "nombre si mencionó",
    "phone": "teléfono si mencionó",
    "email": "email si mencionó",
    "budget": "presupuesto si mencionó"
  }
}

CRITERIOS DE CALIFICACIÓN:
- lead_score 0-33 (cold): Solo preguntó información general
- lead_score 34-66 (warm): Mostró interés, preguntó precios o disponibilidad
- lead_score 67-100 (hot): Quiere comprar/agendar pronto, tiene urgencia o presupuesto

SENTIMENT:
- positive: Cliente satisfecho, interesado, agradecido
- neutral: Llamada informativa, sin emoción clara
- negative: Cliente molesto, frustrante, queja

Responde SOLO con el JSON, sin markdown, sin explicaciones."""


class CallSummarizerService:
    def __init__(self) -> None:
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def summarize(
        self,
        transcript: str,
        call_duration_seconds: int | None = None,
        call_direction: str = "inbound",
        agent_name: str = "Agente",
    ) -> CallSummary:
        """
        Analiza la transcripción de una llamada y retorna un resumen estructurado.

        Args:
            transcript: Texto completo de la transcripción.
            call_duration_seconds: Duración en segundos.
            call_direction: 'inbound' o 'outbound'.
            agent_name: Nombre del agente de voz.
        """
        if not transcript or not transcript.strip():
            return CallSummary(
                summary="Llamada sin transcripción disponible.",
                key_points=[],
                sentiment="neutral",
                intent="unknown",
                next_action="Revisar grabación manualmente.",
                appointment_requested=False,
                appointment_details=None,
                lead_score=0,
                lead_stage="cold",
                contact_info_extracted={},
                tokens_used=0,
            )

        # Construir contexto adicional
        context_parts = []
        if call_duration_seconds:
            minutes = call_duration_seconds // 60
            seconds = call_duration_seconds % 60
            context_parts.append(f"Duración: {minutes}m {seconds}s")
        if call_direction:
            context_parts.append(
                f"Tipo: {'Llamada entrante' if call_direction == 'inbound' else 'Llamada saliente'}"
            )
        if agent_name:
            context_parts.append(f"Agente de IA: {agent_name}")

        context_str = " | ".join(context_parts)
        user_content = f"CONTEXTO: {context_str}\n\nTRANSCRIPCIÓN:\n{transcript}"

        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL_DEFAULT,
                max_tokens=1024,
                system=SUMMARIZER_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_content}],
            )
            raw_text = response.content[0].text.strip()
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            # Parsear JSON
            data = json.loads(raw_text)

            return CallSummary(
                summary=data.get("summary", "Sin resumen disponible."),
                key_points=data.get("key_points", []),
                sentiment=data.get("sentiment", "neutral"),
                intent=data.get("intent", "unknown"),
                next_action=data.get("next_action", "Ninguna acción recomendada."),
                appointment_requested=bool(data.get("appointment_requested", False)),
                appointment_details=data.get("appointment_details"),
                lead_score=int(data.get("lead_score", 0)),
                lead_stage=data.get("lead_stage", "cold"),
                contact_info_extracted=data.get("contact_info_extracted", {}),
                tokens_used=tokens_used,
            )

        except json.JSONDecodeError as exc:
            logger.error("call_summarizer_json_error", error=str(exc), raw=raw_text[:200])
            return CallSummary(
                summary="Error al parsear resumen de IA.",
                key_points=[],
                sentiment="neutral",
                intent="unknown",
                next_action="Revisar transcripción manualmente.",
                appointment_requested=False,
                appointment_details=None,
                lead_score=0,
                lead_stage="cold",
                contact_info_extracted={},
                tokens_used=0,
            )
        except Exception as exc:
            logger.error("call_summarizer_error", error=str(exc))
            return CallSummary(
                summary="No se pudo generar el resumen automáticamente.",
                key_points=[],
                sentiment="neutral",
                intent="unknown",
                next_action="Revisar transcripción manualmente.",
                appointment_requested=False,
                appointment_details=None,
                lead_score=0,
                lead_stage="cold",
                contact_info_extracted={},
                tokens_used=0,
            )

    async def generate_followup_message(
        self,
        summary: CallSummary,
        contact_name: str,
        business_name: str,
    ) -> str:
        """Genera un mensaje de seguimiento post-llamada para enviar por WhatsApp."""
        prompt = f"""Genera un mensaje de WhatsApp de seguimiento post-llamada.

Resumen de la llamada: {summary.summary}
Puntos clave: {', '.join(summary.key_points[:3])}
Próxima acción acordada: {summary.next_action}
Cliente: {contact_name}
Empresa: {business_name}

El mensaje debe:
- Ser cálido y profesional
- Máximo 3 oraciones
- Confirmar lo hablado en la llamada
- Indicar los próximos pasos
- Terminar con una pregunta o llamada a la acción

Responde SOLO con el mensaje, sin encabezados ni explicaciones."""

        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL_DEFAULT,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        except Exception as exc:
            logger.error("followup_message_error", error=str(exc))
            return (
                f"Hola {contact_name}, gracias por tu llamada. "
                f"Fue un placer hablar contigo. ¿Tienes alguna pregunta adicional?"
            )
