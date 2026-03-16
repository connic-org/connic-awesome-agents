"""Middleware for telegram-assistant.

Before:
  Puts the chat_id from the connector payload into context so the session
  key (context.telegram_chat_id) resolves correctly.

After:
  Wraps the agent reply in {"chat_id": ..., "text": "..."} for the outbound
  Telegram connector.
"""
import json
from typing import Any


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    payload = context.get("payload") or {}
    chat_id = payload.get("chat_id") if isinstance(payload, dict) else None
    context["telegram_chat_id"] = chat_id
    return content


async def after(response: str, context: dict[str, Any]) -> str:
    chat_id = context.get("telegram_chat_id")
    return json.dumps({"chat_id": chat_id, "text": response.strip()})
