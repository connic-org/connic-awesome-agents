"""Search customer knowledge in Connic Retrieval and return simulated ticket receipts."""

import hashlib
import json
import re
from typing import Any, Literal

from connic.tools import retrieval_query


async def search_knowledge_base(query: str) -> dict[str, Any]:
    """Search customer knowledge in the environment's support Retrieval namespace.

    Args:
        query: A concise description of the customer's question or issue.

    Returns:
        The Retrieval response, including up to three matching passages with
        source IDs, relevance scores, and metadata. An empty results list means
        no matching passages; an error field means the lookup failed.
    """
    return await retrieval_query(query, namespace="support", max_results=3)


def create_mock_ticket(
    summary: str,
    description: str,
    customer_email: str,
    priority: Literal["low", "normal", "high"] = "normal",
    confirmed: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a demo receipt without saving a ticket or contacting a support team.

    Args:
        summary: Short description of the issue, confirmed by the caller.
        description: Caller-supplied details and troubleshooting already attempted.
        customer_email: Fictional contact email read back and confirmed by the caller.
        priority: low for questions, normal for individual issues, high for a blocked team.
        confirmed: True only after the caller agrees to the summary, email, and demo-only action.
        context: Automatically injected Connic run context; never supplied by the caller.

    Returns:
        Explicitly simulated receipt, or an error if confirmation or details are missing.
        The same request within the same run produces the same demo reference.
    """
    if confirmed is not True:
        return {"error": "caller_confirmation_required", "mock": True}
    if not summary.strip() or not description.strip():
        return {"error": "summary_and_description_required", "mock": True}
    customer_email = customer_email.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", customer_email):
        return {"error": "valid_contact_email_required", "mock": True}
    if priority not in {"low", "normal", "high"}:
        return {"error": "invalid_priority", "mock": True}

    ticket = {
        "summary": summary.strip(),
        "description": description.strip(),
        "customer_email": customer_email,
        "priority": priority,
        "run_id": (context or {}).get("run_id"),
    }
    fingerprint = json.dumps(ticket, sort_keys=True).encode("utf-8")
    return {
        "ticket_id": f"DEMO-{hashlib.sha256(fingerprint).hexdigest()[:8].upper()}",
        "status": "mock_created",
        "mock": True,
        "persisted": False,
        "dispatched": False,
        "message": "Demo receipt only. No helpdesk ticket was saved and no support team was notified.",
        **ticket,
    }
