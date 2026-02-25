# Kafka Fraud Detector

Real-time transaction fraud detection on a Kafka event stream. Scores every transaction using velocity analysis, geo-anomaly detection, and knowledge base pattern matching. High-risk transactions are blocked and escalated.

## How It Works

1. Transactions flow in via a **Kafka inbound** connector.
2. Middleware extracts customer metadata and sets the `is_admin` flag.
3. **fraud-scorer** (LLM) runs velocity checks, geo-anomaly detection, and knowledge base lookups to produce a risk score.
4. Conditional tool access: `admin_override` is only available when `context.is_admin == True`.
5. Concurrency control ensures transactions from the same customer are processed sequentially (queued by `customer_id`).
6. High-risk alerts are sent to **fraud-escalator** (Tool agent) for Kafka outbound delivery.

## Connic Features Used

| Feature | Where |
|---------|-------|
| **Kafka inbound connector** | Consumes transaction events from a topic |
| **Kafka outbound connector** | Publishes fraud alerts to alert topics |
| Conditional tools | `admin_override` only available when `context.is_admin == True` |
| Concurrency control | `concurrency.key: "data.customer_id"` with `on_conflict: queue` |
| `max_concurrent_runs: 10` | Handles high-throughput transaction streams |
| Knowledge base | Stores and retrieves fraud patterns |
| Tool agent | `fraud-escalator.yaml` for deterministic alert formatting |
| Output schema | `schemas/fraud-assessment.json` |
| Middleware context enrichment | Sets `is_admin` and `customer_id` in context |

## Connector Setup

**Kafka inbound** (transactions):

| Setting | Value |
|---------|-------|
| Bootstrap servers | `kafka:9092` |
| Topic | `transactions` |
| Group ID | `fraud-detector` |
| Auto offset reset | `latest` |
| Linked agent | `fraud-scorer` |

**Kafka outbound** (alerts):

| Setting | Value |
|---------|-------|
| Bootstrap servers | `kafka:9092` |
| Topic | `fraud-alerts` |
| Linked agent | `fraud-escalator` |

## Structure

```
kafka-fraud-detector/
  agents/
    fraud-scorer.yaml        # LLM fraud scoring with conditional tools
    fraud-escalator.yaml     # Tool agent for alert formatting
  tools/
    fraud_tools.py           # Velocity, geo-anomaly, alerting, admin override
  middleware/
    fraud-scorer.py          # Extracts Kafka metadata, sets is_admin flag
  schemas/
    fraud-assessment.json    # Risk assessment output schema
  requirements.txt
```
