"""Fraud detection and scoring tools."""

import time
from typing import Any
from connic.tools import query_knowledge, store_knowledge


async def search_fraud_patterns(query: str) -> list[dict]:
    """Search stored fraud patterns for matches relevant to the current transaction.

    Args:
        query: Transaction characteristics to match against known patterns
               (e.g. "card-not-present high-value merchant-mismatch").

    Returns:
        List of matching fraud pattern entries with relevance scores.
    """
    result = await query_knowledge(query, namespace="fraud-patterns", max_results=5)
    return result.get("results", [])


async def store_fraud_pattern(
    content: str,
    pattern_id: str | None = None,
) -> dict:
    """Store a novel fraud pattern for future detection.

    Args:
        content: Description of the pattern including transaction characteristics
                 and why it was flagged as suspicious.
        pattern_id: Optional stable ID for this pattern type.

    Returns:
        Store result with entry_id.
    """
    return await store_knowledge(content, namespace="fraud-patterns", entry_id=pattern_id)


_velocity_store: dict[str, list[float]] = {}


def calculate_velocity(
    customer_id: str,
    transaction_timestamp: float,
    window_minutes: int = 60,
) -> dict[str, Any]:
    """Calculate transaction velocity for a customer.

    Tracks how many transactions a customer has made within a time window.
    High velocity can indicate card testing or automated fraud.

    Args:
        customer_id: Unique customer identifier
        transaction_timestamp: Unix timestamp of the current transaction
        window_minutes: Time window to count transactions in

    Returns:
        Dict with count, velocity_per_hour, and is_anomalous flag
    """
    window_seconds = window_minutes * 60
    cutoff = transaction_timestamp - window_seconds

    if customer_id not in _velocity_store:
        _velocity_store[customer_id] = []

    _velocity_store[customer_id] = [
        ts for ts in _velocity_store[customer_id] if ts > cutoff
    ]
    _velocity_store[customer_id].append(transaction_timestamp)

    count = len(_velocity_store[customer_id])
    velocity = count / (window_minutes / 60)

    return {
        "customer_id": customer_id,
        "transaction_count": count,
        "window_minutes": window_minutes,
        "velocity_per_hour": round(velocity, 2),
        "is_anomalous": velocity > 10,
    }


def check_geo_anomaly(
    customer_id: str,
    current_country: str,
    current_timestamp: float,
    last_country: str | None = None,
    last_timestamp: float | None = None,
) -> dict[str, Any]:
    """Detect impossible travel patterns between transactions.

    If a customer transacts in two countries within an implausibly short
    time, it may indicate stolen credentials.

    Args:
        customer_id: Unique customer identifier
        current_country: ISO country code of current transaction
        current_timestamp: Unix timestamp of current transaction
        last_country: ISO country code of previous transaction
        last_timestamp: Unix timestamp of previous transaction

    Returns:
        Dict with is_anomalous flag and details
    """
    if not last_country or not last_timestamp:
        return {
            "customer_id": customer_id,
            "is_anomalous": False,
            "reason": "No previous transaction to compare",
        }

    if current_country == last_country:
        return {
            "customer_id": customer_id,
            "is_anomalous": False,
            "reason": "Same country as last transaction",
        }

    hours_between = (current_timestamp - last_timestamp) / 3600
    if hours_between < 2:
        return {
            "customer_id": customer_id,
            "is_anomalous": True,
            "reason": f"Transaction in {current_country} only {hours_between:.1f}h after {last_country}",
            "hours_between": round(hours_between, 2),
        }

    return {
        "customer_id": customer_id,
        "is_anomalous": False,
        "reason": f"Sufficient time ({hours_between:.1f}h) between {last_country} and {current_country}",
    }


def create_alert(
    customer_id: str,
    risk_score: int,
    risk_level: str,
    reason: str,
    transaction_id: str | None = None,
) -> dict[str, Any]:
    """Create a fraud alert for the security team.

    Args:
        customer_id: Customer who triggered the alert
        risk_score: Numeric risk score 0-100
        risk_level: low, medium, high, or critical
        reason: Human-readable explanation of why this is suspicious
        transaction_id: The specific transaction that triggered the alert

    Returns:
        Structured alert payload
    """
    return {
        "alert_type": "fraud",
        "customer_id": customer_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reason": reason,
        "transaction_id": transaction_id,
        "created_at": time.time(),
        "requires_action": risk_level in ("high", "critical"),
    }


def admin_override(
    transaction_id: str,
    decision: str,
    reason: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Override a fraud decision (admin only, conditionally available).

    Args:
        transaction_id: Transaction to override
        decision: "approve" or "block"
        reason: Why the admin is overriding
        context: Auto-injected run context

    Returns:
        Override confirmation
    """
    return {
        "overridden": True,
        "transaction_id": transaction_id,
        "decision": decision,
        "reason": reason,
        "admin_run_id": context.get("run_id") if context else None,
    }


def format_escalation(
    alert: dict[str, Any],
) -> dict[str, Any]:
    """Format a fraud alert for Kafka outbound delivery.

    Args:
        alert: The fraud alert payload from create_alert

    Returns:
        Kafka-ready message with routing key and payload
    """
    risk_level = alert.get("risk_level", "medium")
    return {
        "topic": f"fraud-alerts-{risk_level}",
        "key": alert.get("customer_id", "unknown"),
        "payload": alert,
    }
