"""Knowledge copilot tools - topic discovery, scoped search, and gap reporting."""

from typing import Any

from connic.tools import db_insert, kb_list_namespaces, query_knowledge

GAPS_COLLECTION = "knowledge_gaps"


async def list_topics(parent: str | None = None) -> Any:
    """List knowledge base topics to discover where documentation lives.

    Topics are hierarchical namespaces separated by dots (e.g.
    "engineering.deploys"). Call without arguments to see the top level,
    then drill into a topic to see its sub-topics and entry counts.

    Args:
        parent: Optional topic to list the children of (e.g. "engineering").
                Omit to list top-level topics.

    Returns:
        Topic entries with name, entry_count, and has_children.
    """
    return await kb_list_namespaces(parent=parent)


async def search_docs(
    query: str,
    topic: str | None = None,
    context: dict[str, Any] | None = None,
) -> list[dict]:
    """Search the internal documentation for content matching the query.

    Args:
        query: What you are looking for (e.g. "rollback procedure for a bad deploy").
        topic: Optional topic from list_topics to scope the search
               (e.g. "engineering.deploys"). Sub-topics are included.
               Omit to search the whole knowledge base.
        context: Auto-injected run context.

    Returns:
        Matching doc chunks with content, source topic, and relevance score.
    """
    result = await query_knowledge(query, namespace=topic, max_results=5)
    hits = result.get("results", [])

    # Record consulted topics so the after middleware can build the provenance footer.
    if context is not None:
        consulted = context.setdefault("topics_consulted", [])
        for hit in hits:
            consulted.append(hit.get("namespace") or topic or "general")

    return hits


async def report_gap(
    question: str,
    summary: str,
    context: dict[str, Any] | None = None,
) -> dict:
    """Record a question the documentation could not answer so the docs team can fill the gap.

    Only call this after searching and finding nothing relevant.

    Args:
        question: The user's question, reworded to stand on its own.
        summary: One or two sentences on what was searched and what was missing.

    Returns:
        The recorded gap document.
    """
    result = await db_insert(GAPS_COLLECTION, {
        "question": question,
        "summary": summary,
        "user_id": (context or {}).get("user_id"),
        "run_id": (context or {}).get("run_id"),
    })
    return result["inserted"][0]
