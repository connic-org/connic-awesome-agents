"""Compliance audit tools for risk scoring and finding formatting."""

from typing import Any
from connic.tools import query_knowledge, db_insert, db_find


async def get_policies(topic: str) -> list[dict]:
    """Retrieve internal compliance policies relevant to the given topic.

    Searches the knowledge base semantically - describe what you're looking
    for in natural language.

    Args:
        topic: Regulatory area or topic (e.g. "data retention", "GDPR", "access control").

    Returns:
        List of matching policy entries from the knowledge base.
    """
    result = await query_knowledge(topic, namespace="policies", max_results=5)
    return result.get("results", [])


async def get_audit_history(
    framework: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Retrieve previous audit findings for trend comparison.

    Args:
        framework: Filter by compliance framework (e.g. "GDPR", "SOC2", "HIPAA").
                   Omit to get findings across all frameworks.
        limit: Maximum number of records to return.

    Returns:
        List of previous audit finding records, most recent first.
    """
    filter_dict = {}
    if framework:
        filter_dict["framework"] = framework
    result = await db_find(
        "audit_findings",
        filter=filter_dict if filter_dict else None,
        sort={"audit_date": -1},
        limit=limit,
    )
    return result.get("documents", [])


async def store_audit_finding(
    framework: str,
    audit_date: str,
    overall_posture: str,
    compliance_percentage: float,
    findings: list[dict],
    summary: str = "",
) -> dict:
    """Persist an audit report for trend tracking.

    Each call inserts a new record so the full audit history is preserved.

    Args:
        framework: Compliance framework (e.g. "GDPR", "SOC2", "HIPAA").
        audit_date: Date of the audit (YYYY-MM-DD).
        overall_posture: green, yellow, or red.
        compliance_percentage: Compliance score 0-100.
        findings: List of individual finding dicts from format_finding.
        summary: Executive summary of the audit.

    Returns:
        The inserted audit finding document.
    """
    result = await db_insert("audit_findings", {
        "framework": framework,
        "audit_date": audit_date,
        "overall_posture": overall_posture,
        "compliance_percentage": compliance_percentage,
        "finding_count": len(findings),
        "findings": findings,
        "summary": summary,
    })
    return result["inserted"][0] if result.get("inserted") else result


SEVERITY_WEIGHTS = {"critical": 25, "high": 15, "medium": 8, "low": 3, "info": 0}


def calculate_risk_score(
    findings: list[dict[str, Any]],
    max_score: int = 100,
) -> dict[str, Any]:
    """Calculate an overall compliance risk score from audit findings.

    Higher score means higher risk. A score of 0 means fully compliant.

    Args:
        findings: List of finding dicts, each with a "severity" key
        max_score: Maximum possible risk score

    Returns:
        Dict with risk_score, posture (green/yellow/red), and breakdown
    """
    total_penalty = 0
    breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

    for finding in findings:
        severity = finding.get("severity", "info").lower()
        if severity in breakdown:
            breakdown[severity] += 1
            total_penalty += SEVERITY_WEIGHTS.get(severity, 0)

    risk_score = min(total_penalty, max_score)

    if risk_score >= 50 or breakdown["critical"] > 0:
        posture = "red"
    elif risk_score >= 20 or breakdown["high"] > 0:
        posture = "yellow"
    else:
        posture = "green"

    compliance_pct = max(0, 100 - risk_score)

    return {
        "risk_score": risk_score,
        "compliance_percentage": compliance_pct,
        "posture": posture,
        "finding_counts": breakdown,
        "total_findings": sum(breakdown.values()),
    }


def format_finding(
    title: str,
    severity: str,
    area: str,
    regulation: str,
    description: str,
    remediation: str,
) -> dict[str, Any]:
    """Format a single compliance finding into a structured record.

    Args:
        title: Short finding title
        severity: critical, high, medium, low, or info
        area: Affected business area (e.g. "data-storage", "access-control")
        regulation: Specific regulation reference (e.g. "GDPR Art. 32")
        description: What the issue is
        remediation: How to fix it

    Returns:
        Structured finding dict
    """
    return {
        "title": title,
        "severity": severity.lower(),
        "area": area,
        "regulation": regulation,
        "description": description,
        "remediation": remediation,
        "status": "open",
    }
