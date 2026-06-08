"""Invoice processing tools for extraction and validation."""

from typing import Any


def add(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: The first number
        b: The second number

    Returns:
        The sum of a and b
    """
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers.

    Args:
        a: The first number
        b: The second number

    Returns:
        The product of a and b
    """
    return a * b


def calculate_tax(amount: float, rate: float = 0.19) -> dict[str, float]:
    """Calculate tax for a given amount.

    Args:
        amount: The base amount to calculate tax on
        rate: The tax rate as a decimal (default: 0.19 for 19% VAT)

    Returns:
        Dict with net, tax, and gross amounts
    """
    tax = round(amount * rate, 2)
    return {"net": amount, "tax": tax, "gross": round(amount + tax, 2)}


def validate_totals(
    payload: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate that invoice totals are mathematically correct.

    Runs as a tool agent after invoice-extractor, so it receives the extracted
    invoice as its payload.

    Args:
        payload: The extracted invoice, with keys: subtotal, tax_amount, total,
            and optional tax_rate (default 0.19) and tolerance (default 0.02).
        context: Auto-injected run context.

    Returns:
        Dict with valid (bool), checks performed, and any discrepancies
    """
    payload = payload or {}
    subtotal = payload.get("subtotal", 0.0)
    tax_amount = payload.get("tax_amount", 0.0)
    total = payload.get("total", 0.0)
    tax_rate = payload.get("tax_rate", 0.19)
    tolerance = payload.get("tolerance", 0.02)

    expected_tax = round(subtotal * tax_rate, 2)
    expected_total = round(subtotal + expected_tax, 2)

    tax_ok = abs(tax_amount - expected_tax) <= tolerance
    total_ok = abs(total - expected_total) <= tolerance
    line_total_ok = abs(total - (subtotal + tax_amount)) <= tolerance

    checks = {
        "tax_matches_rate": tax_ok,
        "total_matches_calculation": total_ok,
        "line_total_consistent": line_total_ok,
    }

    if all(checks.values()):
        return {"valid": True, "checks": checks, "message": "All totals verified"}

    discrepancies = []
    if not tax_ok:
        discrepancies.append(
            f"Tax: expected {expected_tax} at {tax_rate*100}%, got {tax_amount}"
        )
    if not total_ok:
        discrepancies.append(
            f"Total: expected {expected_total}, got {total}"
        )
    if not line_total_ok:
        discrepancies.append(
            f"Subtotal + tax ({subtotal + tax_amount}) != total ({total})"
        )

    return {"valid": False, "checks": checks, "discrepancies": discrepancies}
