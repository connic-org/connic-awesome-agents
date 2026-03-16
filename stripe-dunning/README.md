# Stripe Dunning

Automated payment recovery for Stripe subscriptions. Analyzes failed payment webhooks, decides the appropriate dunning stage based on attempt count and customer history, and composes personalized recovery emails.

```bash
pip install connic-composer-sdk
connic init my-project --templates=stripe-dunning   # new project
connic init . --templates=stripe-dunning            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## How It Works

1. Stripe sends a webhook event (payment failed, subscription updated/deleted).
2. Middleware filters irrelevant events with `StopProcessing` and extracts customer metadata into context.
3. **payment-analyzer** (LLM) looks up customer payment history from the database, decides the dunning stage, records the event, and optionally triggers the recovery-composer.
4. **recovery-composer** (LLM) writes a personalized recovery email matching the dunning stage tone, outputting structured JSON (`to`, `subject`, `body`) for the Email outbound connector.
5. **dunning-pipeline** (Sequential) chains analysis then email composition.

## Connic Features Used

| Feature | Where |
|---------|-------|
| **Stripe inbound connector** | Receives Stripe webhook events |
| Sequential agent | `dunning-pipeline.yaml` |
| `trigger_agent` | `payment-analyzer.yaml` dynamically triggers `recovery-composer` |
| Database | Stores and queries customer payment history via `db_find` / `db_insert` |
| `StopProcessing` middleware | Filters irrelevant Stripe events |
| Middleware context enrichment | Extracts `stripe_customer_id`, `customer_email`, `customer_name` into context |
| Output schemas | `payment-analysis.json`, `recovery-email.json` |
| Custom tools | `payment_tools.py` for retry delay calculation and amount formatting |

## Connector Setup

Add a **Stripe inbound** connector to your agent from the agent detail page in the Connic dashboard:

| Setting | Value |
|---------|-------|
| Webhook secret | `whsec_...` (from Stripe dashboard) |
| Linked agent | `payment-analyzer` or `dunning-pipeline` |

Add an **Email outbound** connector to send the recovery emails. The recovery-composer outputs JSON with `to`, `subject`, `body` fields that the Email outbound connector parses for SMTP delivery.

## Structure

```
stripe-dunning/
  agents/
    payment-analyzer.yaml    # Analyzes Stripe events, decides dunning action
    recovery-composer.yaml   # Writes personalized recovery emails
    dunning-pipeline.yaml    # Sequential: analyze then compose
  tools/
    payment_tools.py         # Retry delay calculation, amount formatting
  middleware/
    payment-analyzer.py      # Filters irrelevant events, extracts customer ID
  schemas/
    payment-analysis.json    # Analysis output schema
    recovery-email.json      # Email output schema
  requirements.txt
```
