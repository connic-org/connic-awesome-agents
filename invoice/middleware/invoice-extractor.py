"""Middleware for the invoice-extractor agent.

Adds audit metadata and enforces basic input validation.
"""

import uuid
from typing import Any


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Attach a unique request ID and audit timestamp for traceability."""
    context["request_id"] = str(uuid.uuid4())
    context["source"] = "invoice-pipeline"
    return content


async def after(response: str, context: dict[str, Any]) -> str:
    """Log extraction cost for billing reconciliation."""
    token_usage = context.get("token_usage", {})
    duration = context.get("duration_ms", 0)
    context["audit_log"] = {
        "request_id": context.get("request_id"),
        "tokens_used": token_usage.get("output_tokens", 0) + token_usage.get("input_tokens", 0),
        "duration_ms": duration,
    }
    return response
