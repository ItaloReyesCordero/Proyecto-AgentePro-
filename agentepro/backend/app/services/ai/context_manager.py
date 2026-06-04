from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.message import Message
from app.utils.helpers import sanitize_for_prompt


async def get_conversation_context(
    conversation_id: str,
    db: AsyncSession,
    max_messages: int = 20,
    max_chars: int = 8000,
) -> list[dict[str, str]]:
    """
    Recupera el contexto de conversación en formato compatible con Claude API.

    Args:
        conversation_id: UUID de la conversación.
        db: Sesión de base de datos.
        max_messages: Máximo de mensajes a recuperar.
        max_chars: Límite de caracteres totales en el contexto.

    Returns:
        Lista de dicts con 'role' y 'content' para la API de Claude.
    """
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(max_messages)
    )
    messages = list(reversed(result.scalars().all()))

    context: list[dict[str, str]] = []
    total_chars = 0

    for msg in messages:
        content = msg.transcription or msg.content or ""
        if not content:
            continue

        content = sanitize_for_prompt(content, 500)
        total_chars += len(content)

        if total_chars > max_chars:
            break

        role = "user" if msg.direction == "inbound" else "assistant"
        context.append({"role": role, "content": content})

    return context


def build_context_summary(messages: list[dict[str, str]], max_chars: int = 2000) -> str:
    """
    Construye un resumen textual del contexto de conversación para incluir en prompts.

    Args:
        messages: Lista de mensajes en formato {'role': ..., 'content': ...}.
        max_chars: Límite de caracteres del resumen.

    Returns:
        String con el resumen de la conversación.
    """
    if not messages:
        return "Sin historial de conversación previo."

    lines = []
    for msg in messages[-10:]:  # Últimos 10 mensajes
        role_label = "Cliente" if msg["role"] == "user" else "Asistente"
        content = msg["content"][:200]
        lines.append(f"{role_label}: {content}")

    summary = "\n".join(lines)
    if len(summary) > max_chars:
        summary = summary[:max_chars] + "..."

    return summary


def trim_context_to_token_limit(
    messages: list[dict[str, str]],
    system_prompt_chars: int,
    max_total_chars: int = 50000,
) -> list[dict[str, str]]:
    """
    Recorta el contexto para no exceder el límite de tokens de Claude.

    Args:
        messages: Lista de mensajes del contexto.
        system_prompt_chars: Caracteres ya usados por el system prompt.
        max_total_chars: Límite total estimado de caracteres.

    Returns:
        Lista recortada de mensajes.
    """
    available_chars = max_total_chars - system_prompt_chars
    total = 0
    result = []

    # Procesar desde el más reciente hacia el más antiguo
    for msg in reversed(messages):
        content_len = len(msg.get("content", ""))
        if total + content_len > available_chars:
            break
        total += content_len
        result.insert(0, msg)

    return result


def ensure_alternating_roles(
    messages: list[dict[str, str]],
) -> list[dict[str, str]]:
    """
    Asegura que los mensajes alternen entre 'user' y 'assistant'.
    Claude API requiere esta alternancia.

    Combina mensajes consecutivos del mismo rol.
    """
    if not messages:
        return []

    result: list[dict[str, str]] = []
    for msg in messages:
        if result and result[-1]["role"] == msg["role"]:
            # Combinar con el mensaje anterior
            result[-1]["content"] += "\n" + msg["content"]
        else:
            result.append({"role": msg["role"], "content": msg["content"]})

    return result
