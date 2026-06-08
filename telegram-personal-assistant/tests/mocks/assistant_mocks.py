"""Mocks for the assistant_tools custom tools.

Keeps the suite deterministic and free of side effects: the assistant still
reaches for the real tools (the calls are recorded and asserted), but the runner
substitutes these return values instead of executing them, so no database,
knowledge base, or scheduled trigger is touched.
"""


def mock_assistant_tools_save_note(tool_name, params, context):
    return {"_id": "note_test_1", "title": params.get("title")}


def mock_assistant_tools_find_notes(tool_name, params, context):
    return [{"_id": "note_test_1", "title": "Groceries"}]


def mock_assistant_tools_delete_note(tool_name, params, context):
    return {"deleted": True}


def mock_assistant_tools_search_knowledge(tool_name, params, context):
    return [{"content": "Stored fact", "score": 0.8}]


def mock_assistant_tools_remember_knowledge(tool_name, params, context):
    return {"entry_id": "kb_test_1"}


def mock_assistant_tools_schedule_followup(tool_name, params, context):
    return {"scheduled_at": "2026-06-08T10:00:00Z", "task": params.get("task")}
