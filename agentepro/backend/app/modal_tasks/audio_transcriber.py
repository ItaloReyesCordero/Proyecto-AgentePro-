from __future__ import annotations

import modal

from app.modal_tasks.app import app, image, secrets

transcribe_image = image.apt_install("ffmpeg").pip_install("openai>=1.40.0")


@app.function(image=transcribe_image, secrets=secrets)
async def transcribe_whatsapp_audio(audio_url: str, message_id: str, tenant_id: str) -> str:
    """Descarga el audio de WhatsApp, lo transcribe con Whisper y actualiza el mensaje."""
    import asyncio
    import os
    import tempfile
    import uuid

    import httpx
    from openai import OpenAI
    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.message import Message
    from app.models.tenant import Tenant
    from app.services.whatsapp.sender import build_client_for_tenant

    text = ""
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tenant_id))
        if tenant is None:
            return ""
        client = build_client_for_tenant(tenant)
        audio_bytes = None
        if client and not audio_url.startswith("http"):
            media_url = await client.get_media_url(audio_url)
            if media_url:
                audio_bytes = await client.download_media(media_url)
        elif audio_url.startswith("http"):
            async with httpx.AsyncClient(timeout=30.0) as http:
                resp = await http.get(audio_url)
                audio_bytes = resp.content

        if not audio_bytes:
            return ""

        # El escritura del temporal, la lectura del archivo y la llamada SÍNCRONA
        # de OpenAI son bloqueantes; se ejecutan en un hilo aparte (asyncio.to_thread,
        # stdlib) para no bloquear el event loop de esta función async.
        def _transcribe(data: bytes) -> str:
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
                f.write(data)
                tmp_path = f.name
            try:
                openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
                with open(tmp_path, "rb") as audio_file:
                    transcription = openai_client.audio.transcriptions.create(
                        model="whisper-1", file=audio_file, language="es"
                    )
                return transcription.text
            finally:
                os.unlink(tmp_path)

        text = await asyncio.to_thread(_transcribe, audio_bytes)

        msg = (
            await db.execute(select(Message).where(Message.wa_message_id == message_id))
        ).scalar_one_or_none()
        if msg:
            msg.transcription = text
            await db.commit()

    return text
