"""Compliance audit tools for risk scoring and finding formatting."""

from typing import Any

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
