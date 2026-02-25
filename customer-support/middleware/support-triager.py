"""Middleware for support-triager.

Enforces rate limiting per customer and enriches context with customer metadata.
Demonstrates StopProcessing for graceful early exits.
"""

from typing import Any

try:
    from connic.exceptions import StopProcessing
except ImportError:
    class StopProcessing(Exception):
        pass

BLOCKED_DOMAINS = {"spam.example.com", "throwaway.mail"}


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Filter spam and enrich with customer metadata before triage.

    Raises StopProcessing for blocked senders so the LLM never runs,
    saving tokens and latency.
    """
    parts = content.get("parts", [])
    text = ""
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            text += part["text"]

    text_lower = text.lower()
    for domain in BLOCKED_DOMAINS:
        if domain in text_lower:
            raise StopProcessing(
                "This message has been automatically filtered. "
                "Please contact support through our official channels."
            )

    context["channel"] = "websocket" if context.get("connector_id", "").startswith("ws-") else "async"

    return content


async def after(response: str, context: dict[str, Any]) -> str:
    """Pass triage result through unchanged."""
    return response
