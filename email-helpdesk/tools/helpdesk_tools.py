"""Helpdesk knowledge tools - domain wrappers over retrieval primitives."""

from connic.tools import retrieval_query, retrieval_store, retrieval_delete


async def search_helpdesk_knowledge(query: str) -> list[dict]:
    """Search helpdesk Retrieval for relevant answers.

    Args:
        query: Customer question or keywords from the email.

    Returns:
        List of matching entries with content and relevance score.
    """
    result = await retrieval_query(query, namespace="helpdesk", max_results=3)
    return result.get("results", [])


async def save_helpdesk_solution(
    content: str,
    entry_id: str | None = None,
) -> dict:
    """Store a reusable answer in helpdesk Retrieval.

    Args:
        content: The answer or solution. Include the original question for better retrieval.
        entry_id: Optional stable ID for future updates (e.g. "returns-policy").

    Returns:
        Store result with entry_id.
    """
    return await retrieval_store(content, namespace="helpdesk", entry_id=entry_id)


async def remove_stale_entry(entry_id: str) -> dict:
    """Remove an outdated entry from helpdesk Retrieval.

    Args:
        entry_id: The ID of the entry to remove.

    Returns:
        Deletion result.
    """
    return await retrieval_delete(entry_id=entry_id, namespace="helpdesk")
