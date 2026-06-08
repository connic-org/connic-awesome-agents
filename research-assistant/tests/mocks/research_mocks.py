"""Mocks for the research_tools custom tools.

Keeps the suite deterministic and free of side effects: the agents still reach
for the real tools (the calls are recorded and asserted), but the runner
substitutes these return values instead of executing them.
"""


def mock_research_tools_search_internal_knowledge(tool_name, params, context):
    return [{
        "entry_id": "kb_data_retention_policy",
        "content": (
            "Internal Data Retention Policy (v3, 2025): customer PII is retained "
            "for 24 months then anonymized; financial records for 10 years per "
            "HGB; application logs for 90 days. Policy owner: DPO. Last reviewed "
            "2025-11. This is the authoritative, current internal source."
        ),
        "score": 0.95,
    }]


def mock_research_tools_save_research_report(tool_name, params, context):
    return {"entry_id": "rr_test_1"}


def mock_research_tools_assess_confidence(tool_name, params, context):
    return {"confidence_level": "medium", "confidence_score": 0.6, "factors": {}}


def mock_research_tools_format_citation(tool_name, params, context):
    return "[1] Example Source (web)"
