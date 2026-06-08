"""Order processing tools for validation and fulfillment."""

import uuid
import time
import zlib
from typing import Any


def calculate_order_total(
    items: list[dict[str, Any]],
    shipping_cost: float = 0.0,
    tax_rate: float = 0.0,
) -> dict[str, Any]:
    """Calculate the expected order total from line items.

    Independently verifies order math so the LLM can detect discrepancies
    with the stated total.

    Args:
        items: List of items, each with "price" and "quantity" keys
        shipping_cost: Shipping fee
        tax_rate: Tax rate as decimal (e.g. 0.19 for 19%)

    Returns:
        Dict with subtotal, tax, shipping, and total breakdown
    """
    subtotal = sum(
        item.get("price", 0) * item.get("quantity", 1)
        for item in items
    )
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax + shipping_cost, 2)

    return {
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "shipping": shipping_cost,
        "total": total,
        "item_count": sum(item.get("quantity", 1) for item in items),
    }


def check_inventory(
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Check inventory availability for all order items.

    Args:
        items: List of items with "sku" and "quantity" keys

    Returns:
        Dict with all_available flag and per-item availability
    """
    availability = []
    all_available = True

    for item in items:
        sku = item.get("sku", "unknown")
        quantity = item.get("quantity", 1)
        available = True
        # Deterministic per-SKU stock (crc32, not hash() which varies per process).
        stock = 50 + zlib.crc32(sku.encode()) % 200

        if stock < quantity:
            available = False
            all_available = False

        availability.append({
            "sku": sku,
            "requested": quantity,
            "in_stock": stock,
            "available": available,
        })

    return {
        "all_available": all_available,
        "items": availability,
    }


def create_fulfillment(
    payload: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a fulfillment record for an approved order.

    Runs as a tool agent after order-validator, so it receives the validation
    result as its payload. Only creates a record if the order was approved;
    rejected or needs_review orders are returned with instructions.

    Args:
        payload: The validation result, with keys: order_id, validation_status
            (approved, needs_review, or rejected), items, and shipping_address.
        context: Auto-injected run context.

    Returns:
        Fulfillment record or rejection notice
    """
    payload = payload or {}
    order_id = payload.get("order_id")
    validation_status = payload.get("validation_status")
    items = payload.get("items")
    shipping_address = payload.get("shipping_address")

    if validation_status != "approved":
        return {
            "fulfilled": False,
            "order_id": order_id,
            "reason": f"Order status is '{validation_status}', not approved",
            "action": "manual_review" if validation_status == "needs_review" else "notify_customer",
        }

    return {
        "fulfilled": True,
        "fulfillment_id": str(uuid.uuid4()),
        "order_id": order_id,
        "status": "pending_shipment",
        "items_to_pick": len(items) if items else 0,
        "shipping_address": shipping_address,
        "created_at": time.time(),
    }
