"""Payment and dunning tools."""

import math


def calculate_retry_delay(attempt_number: int, base_delay_hours: int = 24) -> dict[str, int]:
    """Calculate exponential backoff delay for payment retry.

    Uses exponential backoff with jitter to space out retry attempts,
    capped at 7 days.

    Args:
        attempt_number: Which retry attempt this is (1-based)
        base_delay_hours: Base delay in hours before first retry

    Returns:
        Dict with delay_hours and next_attempt_timestamp_offset
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
