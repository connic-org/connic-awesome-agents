"""Middleware for knowledge-copilot.

Before:
  Resolves the portal user ID from the WebSocket payload into context so the
  session key (context.user_id) resolves. Rejects messages without one via
  StopProcessing, since an anonymous message cannot be attached to a session.

After:
  Appends a provenance footer naming the doc topics the answer was built from
  (recorded in context by search_docs). Guardrail rejections skip this footer
  because the agent sets guardrails.run_after_on_block: false.
"""

from typing import Any

from connic import StopProcessing


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    payload = context.get("payload") or {}
    client_ctx = payload.get("context") if isinstance(payload.get("context"), dict) else {}
    user_id = client_ctx.get("user_id") or payload.get("user_id")

    if not user_id:
        raise StopProcessing(
            "Missing user_id: include it in the message context so your "
            "conversation history can be restored."
        )

    context["user_id"] = str(user_id)
    return content


async def after(response: str, context: dict[str, Any]) -> str:
    reply = response.strip()
    topics = context.get("topics_consulted") or []
    if topics:
        reply += "\n\n[Sources: " + ", ".join(sorted(set(topics))) + "]"
    else:
        reply += "\n\n[No knowledge base sources consulted]"
    return reply
