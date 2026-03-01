"""Payment and dunning tools."""

import math
from datetime import datetime, timezone
from connic.tools import db_insert, db_find


async def get_customer_history(customer_email: str) -> list[dict]:
    """Retrieve payment event history for a customer.

    Args:
        customer_email: The customer's email address.

    Returns:
        List of payment event records, most recent first.
    """
    result = await db_find(
        "payment_events",
        filter={"customer_email": customer_email},
        sort={"recorded_at": -1},
        limit=10,
    )
    return result.get("documents", [])


async def record_payment_event(
    customer_email: str,
    event_type: str,
    dunning_stage: str,
    amount_cents: int = 0,
    currency: str = "usd",
    attempt_number: int = 1,
    failure_reason: str = "",
    notes: str = "",
) -> dict:
    """Record a payment event for dunning history tracking.

    Each call inserts a new record so the full timeline is preserved.

    Args:
        customer_email: Customer's email address.
        event_type: Stripe event type (e.g. "invoice.payment_failed").
        dunning_stage: Current dunning stage (friendly_reminder, urgent_notice,
                       final_warning, service_paused, win_back).
        amount_cents: Payment amount in smallest currency unit.
        currency: ISO 4217 currency code.
        attempt_number: Which payment attempt this is.
        failure_reason: Why the payment failed (card_declined, insufficient_funds, etc.).
        notes: Additional context about the event and decision made.

    Returns:
        The inserted payment event document.
    """
    result = await db_insert("payment_events", {
        "customer_email": customer_email,
        "event_type": event_type,
        "dunning_stage": dunning_stage,
        "amount_cents": amount_cents,
        "currency": currency,
        "attempt_number": attempt_number,
        "failure_reason": failure_reason,
        "notes": notes,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    })
    return result["inserted"][0] if result.get("inserted") else result


def calculate_retry_delay(attempt_number: int, base_delay_hours: int = 24) -> dict[str, int]:
    """Calculate exponential backoff delay for payment retry.

    Uses exponential backoff capped at 7 days.

    Args:
        attempt_number: Which retry attempt this is (1-based)
        base_delay_hours: Base delay in hours before first retry

    Returns:
        Dict with delay_hours, delay_days, and attempt number
    """
    delay = min(base_delay_hours * (2 ** (attempt_number - 1)), 168)
    return {
        "delay_hours": delay,
        "delay_days": math.ceil(delay / 24),
        "attempt": attempt_number,
    }


def format_amount(amount_cents: int, currency: str = "usd") -> str:
    """Format a Stripe amount (in cents) to a human-readable string.

    Args:
        amount_cents: Amount in smallest currency unit (cents for USD/EUR)
        currency: ISO 4217 currency code

    Returns:
        Formatted amount string like "$49.99" or "49,99 EUR"
    """
    amount = amount_cents / 100
    symbols = {"usd": "$", "eur": "\u20ac", "gbp": "\u00a3"}
    symbol = symbols.get(currency.lower(), currency.upper() + " ")

    if currency.lower() in ("usd", "gbp"):
        return f"{symbol}{amount:,.2f}"
    return f"{amount:,.2f} {symbol}"
