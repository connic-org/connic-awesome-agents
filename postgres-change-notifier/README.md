# PostgreSQL Change Notifier

Intelligent database change monitoring via PostgreSQL LISTEN/NOTIFY. Analyzes change events, classifies significance, and routes notifications to the right team. Perfect for audit trailing and real-time alerting on critical data changes.

## How It Works

1. A PostgreSQL trigger fires `NOTIFY` on table changes.
2. The **PostgreSQL inbound connector** delivers the payload to `change-analyzer`.
3. **change-analyzer** (LLM) classifies the significance, decides who to alert, and uses `trigger_agent` to call the notification dispatcher for important changes.
4. **notification-dispatcher** (Tool agent) formats the alert for outbound webhook delivery.
5. High-significance events are stored in the knowledge base for audit trailing.

## Connic Features Used

| Feature | Where |
|---------|-------|
| **PostgreSQL inbound connector** | LISTEN/NOTIFY triggers on table changes |
| `trigger_agent` | `change-analyzer.yaml` dynamically triggers `notification-dispatcher` |
| Tool agent | `notification-dispatcher.yaml` for deterministic formatting |
| Knowledge base | Stores high-significance events for audit trail |
| Output schema | `schemas/change-analysis.json` |
| Custom tools | Rule-based pre-classification and notification formatting |

## Connector Setup

Configure a **PostgreSQL inbound** connector:

| Setting | Value |
|---------|-------|
| Host | `your-db-host` |
| Port | `5432` |
| Database | `production` |
| Channel | `data_changes` |
| Parse JSON payload | `true` |
| SSL mode | `require` |
| Linked agent | `change-analyzer` |

Add an **HTTP Webhook (outbound)** connector to forward notifications to Slack, Teams, or PagerDuty.

### Database Setup

Create a trigger function that sends NOTIFY events:

```sql
CREATE OR REPLACE FUNCTION notify_data_change()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM pg_notify('data_changes', json_build_object(
    'table', TG_TABLE_NAME,
    'operation', TG_OP,
    'old', CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
    'new', CASE WHEN TG_OP != 'DELETE' THEN row_to_json(NEW) ELSE NULL END,
    'timestamp', NOW()
  )::text);
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION notify_data_change();
```

## Structure

```
postgres-change-notifier/
  agents/
    change-analyzer.yaml         # Classifies changes and decides notifications
    notification-dispatcher.yaml # Tool agent for formatting alerts
  tools/
    notification_tools.py        # Change classification and dispatch formatting
  schemas/
    change-analysis.json         # Analysis output schema
  requirements.txt
```
