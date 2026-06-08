"""Mocks for support-responder's custom tools.

Keeps the suite deterministic and side-effect free: the responder still reaches
for search_solutions / save_solution / format_escalation (the calls are recorded
and asserted), but the runner substitutes these return values instead of
touching the knowledge base or emitting an escalation.
"""


def mock_support_tools_search_solutions(tool_name, params, context):
    return [{"content": "Reset via Settings > Security", "score": 0.9}]


def mock_support_tools_save_solution(tool_name, params, context):
    return {"entry_id": "sol_test_1", "ok": True}


def mock_support_tools_format_escalation(tool_name, params, context):
    return {"escalated": True, "priority": params.get("priority")}
