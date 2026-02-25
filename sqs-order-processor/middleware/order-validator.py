"""Middleware for order-validator.

Extracts order metadata into context and rejects obviously invalid payloads
before the LLM processes them.
"""

import json
from typing import Any

try:
    from connic.exceptions import StopProcessing
except ImportError:
    class StopProcessing(Exception):
        pass


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Extract order metadata and reject empty/malformed orders."""
    parts = content.get("parts", [])
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            try:
                payload = json.loads(part["text"])
                if "order_id" not in payload:
                    raise StopProcessing(
                        '{"error": "Missing order_id", "status": "rejected"}'
                    )
                context["order_id"] = payload["order_id"]
                context["customer_id"] = payload.get("customer_id", "unknown")

                items = payload.get("items", [])
                if not items:
                    raise StopProcessing(
                        '{"error": "Order has no items", "status": "rejected", '
                        f'"order_id": "{payload["order_id"]}"' + '}'
                    )
            except json.JSONDecodeError:
                raise StopProcessing(
                    '{"error": "Invalid JSON payload", "status": "rejected"}'
                )
    return content


async def after(response: str, context: dict[str, Any]) -> str:
    return response
