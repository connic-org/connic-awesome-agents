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
    subtotal: float,
    tax_amount: float,
    total: float,
    tax_rate: float = 0.19,
    tolerance: float = 0.02,
) -> dict[str, Any]:
    """Validate that invoice totals are mathematically correct.

    Args:
        subtotal: The subtotal before tax
        tax_amount: The tax amount on the invoice
        total: The total amount on the invoice
        tax_rate: Expected tax rate as decimal
        tolerance: Acceptable rounding difference in currency units

    Returns:
        Dict with valid (bool), checks performed, and any discrepancies
    """
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
