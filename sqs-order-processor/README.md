# SQS Order Processor

E-commerce order validation and fulfillment pipeline powered by AWS SQS. Validates orders for completeness, business rules, fraud signals, and inventory availability, then creates fulfillment records for approved orders.

```bash
pip install connic-composer-sdk
connic init my-project --templates=sqs-order-processor   # new project
connic init . --templates=sqs-order-processor            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## How It Works

1. Orders arrive via an **SQS inbound** connector.
2. Middleware rejects malformed payloads with `StopProcessing` (zero tokens).
3. **order-validator** (LLM) checks completeness, calculates totals independently, verifies inventory, and flags fraud signals.
4. **order-fulfiller** (Tool agent) creates fulfillment records for approved orders.
5. Results are sent to an **SQS outbound** connector for downstream processing.

## Connic Features Used

| Feature | Where |
|---------|-------|
| **SQS inbound connector** | Consumes orders from an SQS queue |
| **SQS outbound connector** | Publishes validation results and fulfillment records |
| Sequential agent | `order-pipeline.yaml` |
| Concurrency control | `concurrency.key: "customer_id"` ensures one order per customer at a time |
| `timeout: 30` | Strict timeout for order processing latency |
| Tool agent | `order-fulfiller.yaml` for deterministic fulfillment creation |
| `StopProcessing` middleware | Rejects malformed orders before LLM |
| Output schema | `schemas/order-validation.json` |
| Custom tools | Total calculation, inventory check, fulfillment creation |

## Connector Setup

**SQS inbound** (orders):

| Setting | Value |
|---------|-------|
| Queue URL | `https://sqs.eu-central-1.amazonaws.com/123/orders` |
| Region | `eu-central-1` |
| Max messages | `10` |
| Wait time seconds | `20` (long polling) |
| Visibility timeout | `60` |
| Linked agent | `order-pipeline` |

**SQS outbound** (results):

| Setting | Value |
|---------|-------|
| Queue URL | `https://sqs.eu-central-1.amazonaws.com/123/fulfillment` |
| Region | `eu-central-1` |
| Linked agent | `order-fulfiller` |

For FIFO queues, set `message_group_id` to route by customer.

## Structure

```
sqs-order-processor/
  agents/
    order-validator.yaml     # LLM validation with business rules and fraud detection
    order-fulfiller.yaml     # Tool agent for fulfillment creation
    order-pipeline.yaml      # Sequential: validate then fulfill
  tools/
    order_tools.py           # Total calculation, inventory check, fulfillment
  middleware/
    order-validator.py       # Malformed payload rejection with StopProcessing
  schemas/
    order-validation.json    # Validation output schema
  requirements.txt
```
