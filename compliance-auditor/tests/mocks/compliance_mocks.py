"""Mocks for the compliance tools.

Keeps the suite deterministic and free of side effects: the scanner reaches for
the real tools (the calls are still recorded and asserted), but the runner
substitutes these return values instead of touching the knowledge base or
database. web_search and the MCP server still run for real.
"""


def mock_compliance_tools_list_policy_areas(tool_name, params, context):
    return [{"name": "policies.data-retention", "entry_count": 3, "has_children": False}]


def mock_compliance_tools_get_policies(tool_name, params, context):
    return [{"content": "Data retention max 14 days", "score": 0.8}]


def mock_compliance_tools_get_audit_history(tool_name, params, context):
    return []


def mock_compliance_tools_store_audit_finding(tool_name, params, context):
    return {"stored": True}
