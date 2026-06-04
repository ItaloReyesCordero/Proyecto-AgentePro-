from __future__ import annotations
import json
import httpx
from anthropic import AsyncAnthropic
from dataclasses import dataclass
from typing import Any
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

FAL_API_URL = "https://fal.run/fal-ai/flux/schnell"

CONTENT_SYSTEM_PROMPT = """Eres un experto en marketing digital para negocios latinoamericanos.
Tu tarea es generar contenido atractivo para Instagram que conecte con audiencias peruanas y latinoamericanas.

Responde SIEMPRE con un JSON con este formato exacto (sin texto adicional):
{
  "caption": "Caption completo del post (máximo 2200 caracteres, incluye saltos de línea con \\n)",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
  "image_prompt": "Prompt detallado en inglés para generar la imagen con IA",
  "cta": "Llamada a la acción del post",
  "post_type": "product|service|educational|promotional|testimonial|behind_scenes"
}

REGLAS:
- Caption en español peruano natural
- Incluir emojis relevantes en el caption
- Máximo 15 hashtags (mezcla de grandes, medianos y pequeños)
- image_prompt en inglés, muy descriptivo para generar imagen profesional
- CTA claro y directo al final del caption"""


@dataclass
class GeneratedPost:
    caption: str
    hashtags: list[str]
    image_prompt: str
    image_url: str | None
    cta: str
    post_type: str
    tokens_used: int


class InstagramContentGenerator:
    def __init__(self) -> None:
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_post(
        self,
        topic: str,
        business_name: str,
        business_type: str,
        services: list[dict[str, Any]] | None = None,
        tone: str = "profesional",
        generate_image: bool = True,
        extra_instructions: str = "",
    ) -> GeneratedPost:
        """
        Genera un post de Instagram completo con caption, hashtags e imagen.

        Args:
            topic: Tema del post (ej: "promoción de verano", "nuevo servicio").
            business_name: Nombre del negocio.
            business_type: Tipo de negocio.
            services: Lista de servicios disponibles.
            tone: Tono del contenido (profesional, divertido, inspirador, etc).
            generate_image: Si debe generar imagen con fal.ai.
            extra_instructions: Instrucciones adicionales del usuario.
        """
        services_str = ""
        if services:
            services_str = "\nServicios:\n" + "\n".join(
                f"- {s.get('name', '')}: {s.get('description', '')} (S/. {s.get('price', 'consultar')})"
                for s in services[:5]
            )

        user_prompt = f"""Genera un post de Instagram para:
Negocio: {business_name}
Tipo de negocio: {business_type}
Tema del post: {topic}
Tono: {tone}
{services_str}
{f"Instrucciones adicionales: {extra_instructions}" if extra_instructions else ""}

El post debe ser auténtico, engaging y adaptado al mercado peruano."""

        tokens_used = 0
        image_url = None

        # Generar caption con Claude
        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL_DEFAULT,
                max_tokens=1024,
                system=CONTENT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw_text = response.content[0].text.strip()
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            logger.error("instagram_json_error", error=str(exc))
            data = {
                "caption": f"✨ {business_name} tiene algo especial para ti hoy.\n\n¡Contáctanos para más información!",
                "hashtags": ["peru", "negocio", "emprendimiento"],
                "image_prompt": f"Professional business photo for {business_name}, clean modern aesthetic",
                "cta": "¡Escríbenos ahora!",
                "post_type": "promotional",
            }
        except Exception as exc:
            logger.error("instagram_claude_error", error=str(exc))
            raise

        # Generar imagen con fal.ai
        if generate_image and settings.FAL_KEY:
            image_url = await self._generate_image(data.get("image_prompt", ""))

        return GeneratedPost(
            caption=data.get("caption", ""),
            hashtags=data.get("hashtags", []),
            image_prompt=data.get("image_prompt", ""),
            image_url=image_url,
            cta=data.get("cta", ""),
            post_type=data.get("post_type", "promotional"),
            tokens_used=tokens_used,
        )

    async def _generate_image(self, prompt: str) -> str | None:
        """Genera una imagen usando fal.ai Flux."""
        if not prompt:
            return None

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    FAL_API_URL,
                    headers={
                        "Authorization": f"Key {settings.FAL_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "prompt": prompt,
                        "image_size": "square_hd",
                        "num_inference_steps": 4,
                        "num_images": 1,
                    },
                )
                response.raise_for_status()
                result = response.json()
                images = result.get("images", [])
                if images:
                    return images[0].get("url")
        except Exception as exc:
            logger.error("fal_image_generation_error", error=str(exc), prompt=prompt[:100])

        return None

    async def generate_story_caption(
        self,
        post_caption: str,
        business_name: str,
    ) -> str:
        """Genera un caption corto para Stories de Instagram basado en el post."""
        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL_DEFAULT,
                max_tokens=128,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Crea un texto muy corto (máximo 2 líneas) para una Story de Instagram "
                            f"basado en este post de {business_name}:\n\n{post_caption[:300]}\n\n"
                            "Solo el texto, sin explicaciones. Incluye máximo 2 emojis."
                        ),
                    }
                ],
            )
            return response.content[0].text.strip()
        except Exception:
            return f"¡Nuevo contenido de {business_name}! 🔥 Ver más en el feed."
