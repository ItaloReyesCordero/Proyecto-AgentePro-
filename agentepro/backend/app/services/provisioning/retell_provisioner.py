from __future__ import annotations

from app.models.agent_config import AgentConfig
from app.models.voice_config import VoiceConfig
from app.services.ai.voice_prompt_builder import build_voice_system_prompt
from app.services.voice.retell_client import RetellClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def provision_voice_agent(
    voice_config: VoiceConfig, agent_config: AgentConfig, webhook_url: str | None = None
) -> tuple[str | None, str | None]:
    """Crea el LLM + agente de voz en Retell.

    `webhook_url` es la URL de nuestro backend (`/webhooks/retell/{slug}`) a la que
    Retell avisa cuando empieza/termina/analiza la llamada — sin ella, las llamadas
    no se guardan en nuestra base.

    Devuelve (agent_id, llm_id). (None, None) si Retell no está habilitado.
    """
    client = RetellClient()
    if not client._enabled:
        logger.info("retell_provision_skipped")
        return None, None

    system_prompt = build_voice_system_prompt(voice_config, agent_config, "inbound")
    llm = await client.create_retell_llm(system_prompt)
    if not llm or not llm.get("llm_id"):
        return None, None
    llm_id = llm["llm_id"]

    agent = await client.create_agent(
        agent_name=voice_config.agent_name,
        llm_id=llm_id,
        voice_id=voice_config.voice_id,
        webhook_url=webhook_url,
    )
    agent_id = agent.get("agent_id") if agent else None
    return agent_id, llm_id


async def rollback_voice_agent(agent_id: str | None) -> None:
    if not agent_id:
        return
    client = RetellClient()
    if client._enabled:
        await client.delete_agent(agent_id)
