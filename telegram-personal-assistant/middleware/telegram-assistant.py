"""Middleware for telegram-assistant.

Before:
  Extracts chat_id, sender name, and message text from the Telegram Update
  payload. Sets context.telegram_chat_id for persistent session keying.

After:
  Wraps the agent reply in {"chat_id": ..., "text": "..."} for the outbound
  Telegram connector.
"""
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    parts = content.get("parts", [])
    raw_text = ""
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            raw_text += part["text"]

    try:
        payload = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError):
        payload = {}

    chat_id = payload.get("chat_id")
    message_text = payload.get("text", "").strip()

    msg = payload.get("message", {})
    first_name = msg.get("from_first_name", "")
    username = msg.get("from_username", "")
    sender = f"@{username}" if username else first_name or "User"

    logger.info(
        f"[telegram-assistant] chat_id={chat_id!r} sender={sender!r} "
        f"text={message_text[:80]!r}"
    )

    context["telegram_chat_id"] = chat_id
    context["telegram_sender"] = sender

    content["parts"] = [{"text": message_text or "(no text)"}]
    return content


async def after(response: str, context: dict[str, Any]) -> str:
    chat_id = context.get("telegram_chat_id")
    return json.dumps({"chat_id": chat_id, "text": response.strip()})
