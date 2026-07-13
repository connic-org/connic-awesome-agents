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
| `fallback_model` | `order-validator` falls back to `anthropic/claude-sonnet-5` so queued orders keep processing during a provider outage |

## Connector Setup

Add both connectors from the agent detail page in the [Connic dashboard](https://connic.co).

**SQS inbound** (orders):

| Setting | Value |
|---------|-------|
| Mode | Inbound (Consumer) |
| Queue URL | `https://sqs.eu-central-1.amazonaws.com/123/orders` |
| Region | `eu-central-1` |
| AWS Access Key ID | Your IAM access key with SQS permissions |
| AWS Secret Access Key | Your IAM secret key |
| Max messages per poll | `10` |
| Wait time (seconds) | `20` (long polling) |
| Visibility timeout (seconds) | `60` |
| Linked agent | `order-pipeline` |

**SQS outbound** (results):

| Setting | Value |
|---------|-------|
| Mode | Outbound (Producer) |
| Queue URL | `https://sqs.eu-central-1.amazonaws.com/123/fulfillment` |
| Region | `eu-central-1` |
| AWS Access Key ID | Your IAM access key with SQS permissions |
| AWS Secret Access Key | Your IAM secret key |
| Message Group ID (FIFO only) | Set to route by customer for FIFO queues |
| Linked agent | `order-fulfiller` |

If your SQS queues are in a private network, enable **Connect via Bridge** on both connectors and run the [Connic Bridge](https://connic.co/docs/v1/platform/bridge) in your network.

## Testing

`connic test` runs the suites in `tests/`. `order_tools` is stubbed via
`tests/mocks/order_mocks.py`, so cases are deterministic and write nothing — the
validator's tool calls are still recorded and asserted. `tests/order-pipeline.yaml`
runs the full validate-then-fulfill chain end to end.

## Optional: human-in-the-loop approvals

To require a human decision before the warehouse is notified, add an
[approval](https://connic.co/docs/v1/platform/approvals) block to
`agents/order-fulfiller.yaml`:

```yaml
approval:
  tools:
    - order_tools.create_fulfillment
  timeout: 3600
  message: "Approve fulfillment before the warehouse is notified."
  on_rejection: continue   # rejection feeds back to the agent instead of failing
```

This pauses each run until someone approves it on the Approvals page, so it is
left out of the active config — the deploy-gate test suite runs non-interactively.

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
