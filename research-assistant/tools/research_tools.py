"""Research assistant tools for synthesis and quality assessment."""

from typing import Any
from connic.tools import query_knowledge, store_knowledge


async def search_internal_knowledge(query: str) -> list[dict]:
    """Search the internal research knowledge base for existing findings.

    Args:
        query: Topic or question to search for.

    Returns:
        List of matching knowledge entries with content and relevance score.
    """
    result = await query_knowledge(query, namespace="research", max_results=5)
    return result.get("results", [])


async def save_research_report(
    content: str,
    report_id: str | None = None,
) -> dict:
    """Store a completed research report in the knowledge base for future reference.

    Args:
        content: The research report or summary.
        report_id: Optional stable ID (e.g. "market-research-saas-2025-q1").

    Returns:
        Store result with entry_id.
    """
    return await store_knowledge(content, namespace="research", entry_id=report_id)


def assess_confidence(
    source_count: int,
    sources_agree: bool,
    has_primary_sources: bool,
    information_age_days: int | None = None,
) -> dict[str, Any]:
    """Assess the confidence level of research findings.

    Produces a structured confidence assessment based on source quality
    indicators.

    Args:
        source_count: Number of distinct sources consulted
        sources_agree: Whether sources generally agree on key facts
        has_primary_sources: Whether primary/official sources were found
        information_age_days: How old the newest relevant source is (None if unknown)

    Returns:
        Dict with confidence level, score, and reasoning
    """
    score = 0

    if source_count >= 3:
        score += 30
    elif source_count >= 1:
        score += 15

    if sources_agree:
        score += 30
    else:
        score += 5

    if has_primary_sources:
        score += 25

    if information_age_days is not None:
        if information_age_days <= 30:
            score += 15
        elif information_age_days <= 180:
            score += 10
        elif information_age_days <= 365:
            score += 5

    if score >= 75:
        level = "high"
    elif score >= 45:
        level = "medium"
    else:
        level = "low"

    return {
        "confidence_level": level,
        "confidence_score": min(score, 100),
        "factors": {
            "source_count": source_count,
            "sources_agree": sources_agree,
            "has_primary_sources": has_primary_sources,
            "information_age_days": information_age_days,
        },
    }


def format_citation(
    title: str,
    url: str | None = None,
    source_type: str = "web",
    date: str | None = None,
) -> str:
    """Format a citation for inclusion in a research report.

    Args:
        title: Title of the source
        url: URL if available
        source_type: Type of source (web, knowledge_base, official_docs)
        date: Publication or retrieval date

    Returns:
        Formatted citation string
    """
    parts = [f"[{source_type.upper()}]", title]
    if url:
        parts.append(f"({url})")
    if date:
        parts.append(f"- {date}")
    return " ".join(parts)
