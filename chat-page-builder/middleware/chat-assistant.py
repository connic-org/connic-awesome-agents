"""Middleware for chat-assistant.

The chat app sends {"message": ..., "conversation_id": ...} over the
assistant-chat connector, and connic sets context["end_user"] from the
signed-in visitor. The session key joins both, so a conversation ID alone
never opens someone else's history. The model gets the message with a short
note on who is signed in and today's date, for periods like "last month".
"""

from datetime import datetime, timezone
from typing import Any

from connic import StopProcessing


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    user = context.get("end_user") or {}
    payload = context.get("payload")
    payload = payload if isinstance(payload, dict) else {}
    message = payload.get("message")
    conversation = payload.get("conversation_id")
    if not user.get("id") or not isinstance(message, str) or not isinstance(conversation, str) or not conversation:
        raise StopProcessing("Open this assistant through the chat app.")

    context["conversation_key"] = f"{user['id']}:{conversation}"
    who = user.get("name") or user.get("email") or "a visitor"
    today = datetime.now(timezone.utc).strftime("%A, %d %B %Y")
    content["parts"] = [{"text": f"[Signed in: {who}. Today is {today}.]"}, {"text": message}]
    return content
