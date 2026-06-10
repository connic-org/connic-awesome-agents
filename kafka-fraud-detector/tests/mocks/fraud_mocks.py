"""Mocks for fraud-scorer's custom tools.

Keeps the suite deterministic and free of side effects: the scorer reaches for
the real tools (the calls are still recorded and asserted), but the runner
substitutes these return values instead of touching the velocity store, the
knowledge base, or the alert pipeline.
"""


def mock_fraud_tools_calculate_velocity(tool_name, params, context):
    return {"count": 5, "velocity_per_hour": 5, "is_anomalous": False}


def mock_fraud_tools_check_geo_anomaly(tool_name, params, context):
    # Mirrors the real logic so the answer stays consistent with the payload;
    # a contradictory canned answer makes the model distrust and retry the tool.
    last_country = params.get("last_country")
    current_country = params.get("current_country")
    if not last_country:
        return {"is_anomalous": False, "reason": "No previous transaction to compare"}
    if last_country == current_country:
        return {"is_anomalous": False, "reason": "Same country as last transaction"}
    return {
        "is_anomalous": True,
        "reason": f"Transaction in {current_country} shortly after {last_country}",
    }


def mock_fraud_tools_search_fraud_patterns(tool_name, params, context):
    return []


def mock_fraud_tools_create_alert(tool_name, params, context):
    return {"alert_id": "al_test_1", "risk_level": params.get("risk_level")}


def mock_fraud_tools_store_fraud_pattern(tool_name, params, context):
    return {"entry_id": "fp_test_1"}


def mock_fraud_tools_admin_override(tool_name, params, context):
    return {"overridden": True, "decision": params.get("decision")}
