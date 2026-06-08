"""Mocks for the change-analyzer's custom tools.

Keeps the suite deterministic and free of side effects: the analyzer reaches for
the real tools (the calls are still recorded and asserted), but the runner
substitutes these return values instead of touching the database. trigger_agent
still runs for real.
"""


def mock_notification_tools_classify_change(tool_name, params, context):
    return {"significance": "high", "suggested_channels": ["ops-team"]}


def mock_notification_tools_log_audit_event(tool_name, params, context):
    return {"logged": True}
