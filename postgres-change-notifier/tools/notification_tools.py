"""Notification tools for database change events."""

from typing import Any


def classify_change(
    table: str,
    operation: str,
    changed_fields: list[str] | None = None,
) -> dict[str, Any]:
    """Classify the significance of a database change.

    Provides a rule-based initial classification that the LLM can
    override with more nuanced analysis.

    Args:
        table: Database table name
        operation: INSERT, UPDATE, or DELETE
        changed_fields: List of column names that were modified

    Returns:
        Dict with significance level and suggested channels
    """
    high_sig_tables = {"orders", "payments", "users", "permissions", "subscriptions"}
    sensitive_fields = {"status", "amount", "role", "permissions", "email", "password_hash"}

    significance = "low"
    channels = []

    if table in high_sig_tables:
        significance = "medium"
        if operation == "DELETE":
            significance = "high"
            channels.append("security-team")
        elif changed_fields:
            if any(f in sensitive_fields for f in changed_fields):
                significance = "high"

    if table in ("orders", "payments"):
        channels.append("ops-team")
    if table == "users" and operation == "INSERT":
        channels.append("sales-team")

    if not channels and significance != "low":
        channels.append("ops-team")

    return {
        "significance": significance,
        "suggested_channels": channels,
        "table": table,
        "operation": operation,
    }


def dispatch(
    channel: str,
    title: str,
    message: str,
    severity: str = "info",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Format a notification payload for webhook delivery.

    The outbound HTTP webhook connector will deliver this to the
    configured endpoint (Slack, Teams, PagerDuty, etc.).

    Args:
        channel: Target channel (ops-team, security-team, sales-team)
        title: Notification title
        message: Notification body
        severity: info, warning, or critical
        metadata: Additional context (table, operation, record IDs)

    Returns:
        Structured notification ready for outbound webhook delivery
    """
    return {
        "channel": channel,
        "title": title,
        "message": message,
        "severity": severity,
        "metadata": metadata or {},
    }
