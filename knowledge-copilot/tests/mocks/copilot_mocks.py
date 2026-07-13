"""Mocks for the copilot_tools custom tools.

Keeps the suite deterministic and free of side effects: the copilot still
reaches for the real tools (the calls are recorded and asserted), but the
runner substitutes these return values instead of executing them, so no
knowledge base or database is touched.
"""


def mock_copilot_tools_list_topics(tool_name, params, context):
    if params.get("parent"):
        return {
            "parent": {"name": params["parent"], "entry_count": 4, "has_children": True},
            "namespaces": [
                {"name": f"{params['parent']}.deploys", "entry_count": 6, "has_children": False},
                {"name": f"{params['parent']}.oncall", "entry_count": 3, "has_children": False},
            ],
        }
    return [
        {"name": "engineering", "entry_count": 4, "total_entry_count": 13, "has_children": True},
        {"name": "policies", "entry_count": 9, "total_entry_count": 21, "has_children": True},
        {"name": "onboarding", "entry_count": 5, "total_entry_count": 5, "has_children": False},
    ]


def mock_copilot_tools_search_docs(tool_name, params, context):
    # Nothing about office pets exists, so the gap-reporting case gets an empty result.
    if "dog" in params.get("query", "").lower() or "pet" in params.get("query", "").lower():
        return []
    return [
        {
            "content": "Rollback procedure: run `deploy rollback <release-id>` from the "
                       "release channel, confirm the previous release is healthy in the "
                       "dashboard, then post a summary in the incident thread.",
            "entry_id": "deploy-rollback",
            "namespace": "engineering.deploys",
            "score": 0.91,
            "metadata": {},
        }
    ]


def mock_copilot_tools_report_gap(tool_name, params, context):
    return {
        "_id": "gap_test_1",
        "question": params.get("question"),
        "summary": params.get("summary"),
    }
