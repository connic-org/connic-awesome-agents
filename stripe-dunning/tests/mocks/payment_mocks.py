"""Mocks for payment-analyzer's custom tools.

Keeps the suite deterministic and free of side effects: the analyzer reaches for
the real tools (the calls are still recorded and asserted), but the runner
substitutes these return values instead of touching the database.
"""


def mock_payment_tools_get_customer_history(tool_name, params, context):
    return []


def mock_payment_tools_record_payment_event(tool_name, params, context):
    return {"recorded": True, "event_type": params.get("event_type")}


def mock_payment_tools_calculate_retry_delay(tool_name, params, context):
    return {
        "delay_hours": 24,
        "delay_days": 1,
        "attempt": params.get("attempt_number", 1),
    }
