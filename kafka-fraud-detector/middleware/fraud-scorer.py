"""Middleware for fraud-scorer.

Enriches context with metadata from the Kafka message headers
and sets the is_admin flag for conditional tool access.
"""

import json
from typing import Any


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Extract Kafka metadata and set admin flag for conditional tools."""
    parts = content.get("parts", [])
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            try:
                payload = json.loads(part["text"])
                context["is_admin"] = payload.get("source") == "admin-dashboard"
                if "customer_id" in payload.get("data", {}):
                    context["customer_id"] = payload["data"]["customer_id"]
            except (json.JSONDecodeError, AttributeError):
                context["is_admin"] = False
    return content


async def after(response: str, context: dict[str, Any]) -> str:
    """Log fraud scoring metrics."""
    return response
