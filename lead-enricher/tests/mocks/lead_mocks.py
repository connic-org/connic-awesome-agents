"""Mocks for lead-enricher's custom tools.

Keeps the suite deterministic and side-effect free: the agent still reaches for
get_lead / get_icp_criteria / save_lead (the calls are recorded and asserted),
but the runner substitutes these return values instead of touching the database
or knowledge base. web_search is a predefined tool and runs for real.
"""


def mock_lead_tools_get_lead(tool_name, params, context):
    return None


def mock_lead_tools_get_icp_criteria(tool_name, params, context):
    return {"source": "kb", "criteria": ["B2B SaaS", "50+ employees"]}


def mock_lead_tools_save_lead(tool_name, params, context):
    return {
        "email": params.get("email"),
        "score": params.get("score"),
        "status": "qualified",
    }
