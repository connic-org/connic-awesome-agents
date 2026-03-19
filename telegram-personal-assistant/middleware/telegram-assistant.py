"""Middleware for telegram-assistant.

Before:
  Puts the chat_id from the connector payload into context so the session
  key (context.telegram_chat_id) resolves correctly.
  Injects the current UTC time so the agent can calculate relative delays.

After:
  Wraps the agent reply in {"chat_id": ..., "text": "..."} for the outbound
  Telegram connector.
"""
import json
from datetime import datetime, timezone
from typing import Any


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    payload = context.get("payload") or {}
    chat_id = payload.get("chat_id") if isinstance(payload, dict) else None
    context["telegram_chat_id"] = chat_id

    now = datetime.now(timezone.utc)
    time_part = {"text": f"[Current time: {now.strftime('%Y-%m-%d %H:%M UTC (%A)')}]"}
    content["parts"].insert(0, time_part)

    return content


async def after(response: str, context: dict[str, Any]) -> str:
    chat_id = context.get("telegram_chat_id")
    return json.dumps({"chat_id": chat_id, "text": response.strip()})
