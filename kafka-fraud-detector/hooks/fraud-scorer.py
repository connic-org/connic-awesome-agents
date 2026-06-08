"""Tool hooks for fraud-scorer.

Runs around every tool call: enforces admin-only overrides as a second line of
defense behind the conditional tool gate, normalises ids, and logs results to
the project Logs tab.
"""

from typing import Any

from connic import AbortTool


async def before(tool_name: str, params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "admin_override" and not context.get("is_admin"):
        raise AbortTool({"error": "admin_override requires an internal admin context"})

    # Normalise transaction ids so alert keys stay consistent regardless of casing.
    if isinstance(params.get("transaction_id"), str):
        params["transaction_id"] = params["transaction_id"].upper()

    return params


async def after(tool_name: str, params: dict[str, Any], result: Any, context: dict[str, Any]) -> Any:
    print(f"[fraud-hook] {tool_name} -> {result}")
    return result
