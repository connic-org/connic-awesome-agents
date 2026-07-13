# Kafka Fraud Detector

Real-time transaction fraud detection on a Kafka event stream. Scores every transaction using velocity analysis, geo-anomaly detection, and knowledge base pattern matching. High-risk transactions are blocked and escalated.

```bash
pip install connic-composer-sdk
connic init my-project --templates=kafka-fraud-detector   # new project
connic init . --templates=kafka-fraud-detector            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## How It Works

1. Transactions flow in via a **Kafka inbound** connector.
2. Middleware extracts customer metadata and sets the `is_admin` flag.
3. **fraud-scorer** (LLM) runs velocity checks, geo-anomaly detection, and knowledge base lookups to produce a risk score.
4. Conditional tool access: `admin_override` is only available when `context.is_admin == True`.
5. Concurrency control ensures transactions from the same customer are processed sequentially (queued by `customer_id`).
6. For high/critical risk, `create_alert` forwards the alert (via `trigger_agent`) to **fraud-escalator** (Tool agent) for Kafka outbound delivery.

## Connic Features Used

| Feature | Where |
|---------|-------|
| **Kafka inbound connector** | Consumes transaction events from a topic |
| **Kafka outbound connector** | Publishes fraud alerts to alert topics |
| Conditional tools | `admin_override` only available when `context.is_admin == True` |
| Concurrency control | `concurrency.key: "data.customer_id"` with `on_conflict: queue` |
| Knowledge base | Stores and retrieves fraud patterns |
| Tool agent | `fraud-escalator.yaml` for deterministic alert formatting |
| `trigger_agent` from a custom tool | `create_alert` forwards high/critical alerts to `fraud-escalator` |
| Tool hooks | `hooks/fraud-scorer.py` guards `admin_override`, normalises transaction ids |
| Output schema | `schemas/fraud-assessment.json` |
| Middleware context enrichment | Sets `is_admin` and `customer_id` in context |
| `fallback_model` | Cross-provider fallback (`gemini/gemini-3.5-flash`) so a provider outage does not drop transaction scoring |
| `reasoning_effort` | `high` for the risk breakdown, overriding the project-default `low` |

## Testing

Run `connic test` from the project root. The suite (`tests/`) covers `fraud-scorer` (normal scoring, admin override, novel-pattern storage) and `fraud-escalator`. The scorer's custom tools are mocked via `tests/mocks/fraud_mocks.py`; the pure `format_escalation` tool runs for real in the escalator test.

## Connector Setup

Add both connectors from the agent detail page in the [Connic dashboard](https://connic.co).

**Kafka inbound** (transactions):

| Setting | Value |
|---------|-------|
| Mode | Inbound (Consumer) |
| Bootstrap servers | `kafka:9092` |
| Topic | `transactions` |
| Consumer Group ID | `fraud-detector` (leave empty to auto-generate) |
| Auto offset reset | `latest` |
| Security protocol | `PLAINTEXT` (or `SASL_SSL` for secured clusters) |
| SASL mechanism | `SCRAM-SHA-256` (only when using SASL) |
| SASL username | Your Kafka username (only when using SASL) |
| SASL password | Your Kafka password (only when using SASL) |
| Linked agent | `fraud-scorer` |

**Kafka outbound** (alerts):

| Setting | Value |
|---------|-------|
| Mode | Outbound (Producer) |
| Bootstrap servers | `kafka:9092` |
| Topic | `fraud-alerts` |
| Security protocol | `PLAINTEXT` (or `SASL_SSL` for secured clusters) |
| Linked agent | `fraud-escalator` |

If your Kafka brokers are in a private network, enable **Connect via Bridge** on both connectors and run the [Connic Bridge](https://connic.co/docs/v1/platform/bridge) in your network.

## Structure

```
kafka-fraud-detector/
  agents/
    _defaults.yaml           # Shared agent defaults (reasoning effort, timeout)
    fraud-scorer.yaml        # LLM fraud scoring with conditional tools
    fraud-escalator.yaml     # Tool agent for alert formatting
  tools/
    fraud_tools.py           # Velocity, geo-anomaly, alerting, admin override
  hooks/
    fraud-scorer.py          # Tool hooks: admin gate, id normalisation, logging
  middleware/
    fraud-scorer.py          # Extracts Kafka metadata, sets is_admin flag
  schemas/
    fraud-assessment.json    # Risk assessment output schema
  tests/
    fraud-scorer.yaml        # Scorer suite (custom tools mocked)
    fraud-escalator.yaml     # Escalator suite (real format_escalation)
    mocks/
      fraud_mocks.py         # Mock returns for the scorer's tools
  requirements.txt
```
