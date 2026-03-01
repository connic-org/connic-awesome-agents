"""Helpdesk knowledge tools - domain wrappers over knowledge primitives."""

from connic.tools import query_knowledge, store_knowledge, delete_knowledge


async def search_helpdesk_knowledge(query: str) -> list[dict]:
    """Search the helpdesk knowledge base for relevant answers.

    Args:
        query: Customer question or keywords from the email.

    Returns:
        List of matching entries with content and relevance score.
    """
    result = await query_knowledge(query, namespace="helpdesk", max_results=3)
    return result.get("results", [])


async def save_helpdesk_solution(
    content: str,
    entry_id: str | None = None,
) -> dict:
    """Store a reusable answer in the helpdesk knowledge base.

    Args:
        content: The answer or solution. Include the original question for better retrieval.
        entry_id: Optional stable ID for future updates (e.g. "returns-policy").

    Returns:
        Store result with entry_id.
    """
    return await store_knowledge(content, namespace="helpdesk", entry_id=entry_id)


async def remove_stale_entry(entry_id: str) -> dict:
    """Remove an outdated entry from the helpdesk knowledge base.

    Args:
        entry_id: The ID of the entry to remove.

    Returns:
        Deletion result.
    """
    return await delete_knowledge(entry_id=entry_id, namespace="helpdesk")
