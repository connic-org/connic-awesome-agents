"""Middleware for payment-analyzer.

Filters irrelevant Stripe events and extracts key fields into context
so downstream agents and tools can access them.

The Stripe inbound connector delivers the full Stripe event JSON:
{id, object, type, data: {object: {...}}, created}
"""

import json
from typing import Any

from connic.core import StopProcessing

RELEVANT_EVENTS = {
    "invoice.payment_failed",
    "customer.subscription.updated",
    "customer.subscription.deleted",
}


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Filter to relevant Stripe events and extract customer metadata."""
    parts = content.get("parts", [])
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            try:
                payload = json.loads(part["text"])
                event_type = payload.get("type", "")
                if event_type not in RELEVANT_EVENTS:
                    raise StopProcessing(
                        f"Ignoring irrelevant Stripe event: {event_type}"
                    )
                context["stripe_event_type"] = event_type

                data_obj = payload.get("data", {}).get("object", {})
                context["stripe_customer_id"] = data_obj.get("customer", "")
                context["customer_email"] = (
                    data_obj.get("customer_email")
                    or data_obj.get("receipt_email")
                    or ""
                )
                context["customer_name"] = data_obj.get("customer_name", "")
            except (json.JSONDecodeError, AttributeError):
                pass
    return content


async def after(response: str, context: dict[str, Any]) -> str:
    return response
