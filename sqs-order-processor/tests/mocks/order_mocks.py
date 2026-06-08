"""Mocks for order-validator's custom tools.

Keeps the suite deterministic and free of side effects: the validator reaches
for the real tools (the calls are still recorded and asserted), but the runner
substitutes these return values instead of executing them. Mirrors the real
math so assertions stay realistic.
"""


def mock_order_tools_calculate_order_total(tool_name, params, context):
    items = params.get("items", [])
    shipping = params.get("shipping_cost", 0.0)
    rate = params.get("tax_rate", 0.0)
    subtotal = sum(i.get("price", 0) * i.get("quantity", 1) for i in items)
    tax = round(subtotal * rate, 2)
    return {
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "shipping": shipping,
        "total": round(subtotal + tax + shipping, 2),
        "item_count": sum(i.get("quantity", 1) for i in items),
    }


def mock_order_tools_check_inventory(tool_name, params, context):
    items = params.get("items", [])
    return {
        "all_available": True,
        "items": [
            {
                "sku": i.get("sku", "unknown"),
                "requested": i.get("quantity", 1),
                "in_stock": 100,
                "available": True,
            }
            for i in items
        ],
    }
