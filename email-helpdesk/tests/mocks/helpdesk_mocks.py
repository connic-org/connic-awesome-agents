"""Mocks for the email-responder's helpdesk tools.

Keeps the suite deterministic and free of side effects: the responder reaches
for the real tools (the calls are still recorded and asserted), but the runner
substitutes these return values instead of touching the knowledge base.
"""


def mock_helpdesk_tools_search_helpdesk_knowledge(tool_name, params, context):
    return [{"content": "Reset your password under Settings", "score": 0.9}]


def mock_helpdesk_tools_save_helpdesk_solution(tool_name, params, context):
    return {"entry_id": "hd_test_1"}


def mock_helpdesk_tools_remove_stale_entry(tool_name, params, context):
    return {"removed": True}
