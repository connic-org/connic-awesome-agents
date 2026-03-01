"""Lead enrichment tools - domain wrappers over db_* and knowledge primitives.

Agents work with leads in business terms (save_lead, get_icp_criteria) rather
than constructing filter dicts or managing collection names and namespaces.
"""

from connic.tools import db_insert, db_find, query_knowledge

LeadStatus = str  # "qualified" | "nurture" | "low"


async def save_lead(
    email: str,
    name: str,
    company: str,
    score: int,
    industry: str = "",
    company_size: str = "",
    funding_stage: str = "",
    notes: str = "",
) -> dict:
    """Save an enriched lead to the leads database.

    Args:
        email: Signup email address.
        name: Contact name.
        company: Company name.
        score: ICP fit score (0-100). 70+ = qualified, 40-69 = nurture, <40 = low.
        industry: Detected industry vertical.
        company_size: Estimated employee range (e.g. "50-200").
        funding_stage: Funding stage if found (e.g. "Series A", "Bootstrapped").
        notes: Research summary and score reasoning (2-4 sentences).

    Returns:
        The inserted lead document including its system-assigned id.
    """
    status: LeadStatus = (
        "qualified" if score >= 70 else "nurture" if score >= 40 else "low"
    )
    result = await db_insert("leads", {
        "email":         email,
        "name":          name,
        "company":       company,
        "score":         score,
        "status":        status,
        "industry":      industry,
        "company_size":  company_size,
        "funding_stage": funding_stage,
        "notes":         notes,
    })
    return result["inserted"][0]


async def get_lead(email: str) -> dict | None:
    """Look up an existing lead by email to avoid duplicate enrichment.

    Args:
        email: The signup email to look up.

    Returns:
        The lead document, or None if not found.
    """
    result = await db_find("leads", filter={"email": email}, limit=1)
    docs = result["documents"]
    return docs[0] if docs else None


async def get_icp_criteria(industry: str | None = None) -> dict:
    """Retrieve the ideal customer profile (ICP) scoring criteria.

    Reads from the knowledge base (namespace "icp"). Seed it once with
    store_knowledge to describe your target customer, e.g.:

        store_knowledge(
            "Target: B2B SaaS companies with 20-500 employees, Series A or later,
             using modern cloud infra. High fit: fintech, HR tech, devtools.",
            namespace="icp",
            entry_id="icp-criteria",
        )

    Falls back to a generic rubric if nothing is stored yet.

    Args:
        industry: Optional industry to narrow the criteria query.

    Returns:
        Dict with source ("knowledge_base" or "default") and criteria list.
    """
    query = f"ideal customer profile scoring criteria {industry or ''}".strip()
    result = await query_knowledge(query, namespace="icp", max_results=3)
    items = result.get("results", [])
    if items:
        return {"source": "knowledge_base", "criteria": [r["content"] for r in items]}
    return {
        "source": "default",
        "criteria": [
            "B2B company with 10-500 employees",
            "Software, fintech, or e-commerce industry",
            "Clear automation or AI adoption signals",
        ],
    }
