"""Support tools for escalation and knowledge management."""

from typing import Any
from connic.tools import query_knowledge, store_knowledge


async def search_solutions(query: str) -> list[dict]:
    """Search the support knowledge base for solutions matching the query.

    Args:
        query: Describe the customer's issue (e.g. "password reset not working").

    Returns:
        List of matching solution entries with content and relevance score.
    """
    result = await query_knowledge(query, namespace="solutions", max_results=3)
    return result.get("results", [])


async def save_solution(
    content: str,
    entry_id: str | None = None,
) -> dict:
    """Store a reusable solution in the knowledge base for future tickets.

    Args:
        content: The solution text. Include the problem description for better retrieval.
        entry_id: Optional stable ID for future updates (e.g. "password-reset-steps").

    Returns:
        Store result with entry_id.
    """
    return await store_knowledge(content, namespace="solutions", entry_id=entry_id)


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
