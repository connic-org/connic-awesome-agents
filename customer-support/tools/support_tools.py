"""Support tools for escalation and ticket management."""

from typing import Any


def format_escalation(
    ticket_summary: str,
    priority: str,
    category: str,
    reason: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Format an escalation payload for human handoff.

    Args:
        ticket_summary: Brief summary of the customer issue
        priority: Ticket priority (low/medium/high/critical)
        category: Ticket category (billing/technical/account/onboarding/general)
        reason: Why the agent is escalating (no knowledge found, complex issue, etc.)
        context: Auto-injected run context

    Returns:
        Structured escalation payload ready for webhook delivery
    """
    return {
        "escalation": True,
        "summary": ticket_summary,
        "priority": priority,
        "category": category,
        "reason": reason,
        "run_id": context.get("run_id") if context else None,
        "connector_id": context.get("connector_id") if context else None,
    }
