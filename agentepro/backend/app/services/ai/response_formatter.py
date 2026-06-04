from __future__ import annotations
import re


def format_for_whatsapp(text: str) -> str:
    """
    Asegura que el texto esté bien formateado para WhatsApp.
    - Limita a 3 párrafos máximo
    - Convierte markdown a formato WhatsApp (*negrita*, _cursiva_)
    - Elimina HTML tags
    """
    text = text.strip()

    # Eliminar tags HTML si los hubiera
    text = re.sub(r"<[^>]+>", "", text)

    # Convertir **negrita** a *negrita* (formato WhatsApp)
    text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)

    # Convertir _cursiva_ ya está en formato WhatsApp, mantener
    # Pero convertir __subrayado__ que no existe en WhatsApp
    text = re.sub(r"__(.*?)__", r"_\1_", text)

    # Eliminar encabezados markdown
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Limpiar múltiples líneas en blanco
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Limitar a 3 párrafos
    paragraphs = text.split("\n\n")
    if len(paragraphs) > 3:
        text = "\n\n".join(paragraphs[:3])

    # Asegurar que no supere 4096 caracteres (límite de WhatsApp)
    if len(text) > 4096:
        text = text[:4093] + "..."

    return text.strip()


def format_for_voice(text: str) -> str:
    """
    Remueve markdown y formatos no hablables para síntesis de voz.
    - Elimina asteriscos, guiones, almohadillas
    - Convierte listas a oraciones
    - Elimina emojis complejos
    - Normaliza puntuación
    """
    # Eliminar negrita y cursiva markdown
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)

    # Eliminar encabezados
    text = re.sub(r"#{1,6}\s+", "", text)

    # Convertir listas con guiones a frases
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)

    # Eliminar listas numeradas
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    # Eliminar URLs
    text = re.sub(r"https?://\S+", "el enlace compartido", text)

    # Eliminar emojis (rango básico y extendido)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub("", text)

    # Limpiar espacios múltiples
    text = re.sub(r"  +", " ", text)
    text = re.sub(r"\n{2,}", ". ", text)
    text = re.sub(r"\n", " ", text)

    # Asegurar que las oraciones terminen correctamente
    text = text.strip()
    if text and not text[-1] in ".!?":
        text += "."

    return text


def split_long_message(text: str, max_length: int = 1500) -> list[str]:
    """
    Divide mensajes largos en partes más pequeñas para WhatsApp.
    Intenta dividir en puntos o saltos de párrafo.
    """
    if len(text) <= max_length:
        return [text]

    parts = []
    paragraphs = text.split("\n\n")
    current_part = ""

    for paragraph in paragraphs:
        if len(current_part) + len(paragraph) + 2 <= max_length:
            current_part = (current_part + "\n\n" + paragraph).strip()
        else:
            if current_part:
                parts.append(current_part.strip())
            # Si el párrafo solo ya excede el límite, dividir por oraciones
            if len(paragraph) > max_length:
                sentences = re.split(r"(?<=[.!?])\s+", paragraph)
                current_part = ""
                for sentence in sentences:
                    if len(current_part) + len(sentence) + 1 <= max_length:
                        current_part = (current_part + " " + sentence).strip()
                    else:
                        if current_part:
                            parts.append(current_part)
                        current_part = sentence
            else:
                current_part = paragraph

    if current_part:
        parts.append(current_part.strip())

    return parts if parts else [text[:max_length]]


def add_typing_delay_suggestion(text: str) -> int:
    """
    Sugiere el tiempo de delay en ms antes de enviar el mensaje
    para simular tipeo natural.
    """
    # Aproximadamente 50ms por carácter con variación
    base_delay = min(len(text) * 30, 3000)  # Máximo 3 segundos
    return base_delay
