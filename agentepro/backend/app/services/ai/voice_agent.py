from __future__ import annotations

from anthropic import AsyncAnthropic

from app.config import settings
from app.models.agent_config import AgentConfig
from app.models.voice_config import VoiceConfig
from app.services.ai.response_formatter import format_for_voice
from app.services.ai.voice_prompt_builder import build_voice_system_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceAgentService:
    """Genera respuestas de voz con Claude.

    Retell normalmente usa su propio motor LLM; este servicio sirve para
    flujos custom-LLM (websocket) o pruebas de guión.
    """

    def __init__(self) -> None:
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_response(
        self,
        user_utterance: str,
        history: list[dict[str, str]],
        voice_config: VoiceConfig,
        agent_config: AgentConfig,
        call_direction: str = "inbound",
    ) -> str:
        system_prompt = build_voice_system_prompt(
            voice_config=voice_config,
            agent_config=agent_config,
            call_direction=call_direction,
        )
        messages = [*history, {"role": "user", "content": user_utterance}]
        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL_COMPLEX,
                max_tokens=256,
                system=system_prompt,
                messages=messages,
            )
            return format_for_voice(response.content[0].text)
        except Exception as exc:
            logger.error("voice_agent_error", error=str(exc))
            return "Disculpe, no le escuché bien. ¿Me puede repetir, por favor?"
