# Invoice Processor

Extract structured data from invoices and validate totals automatically. A sequential pipeline pairs an LLM extractor with a deterministic validator for reliable, auditable results.

```bash
pip install connic-composer-sdk
connic init my-project --templates=invoice   # new project
connic init . --templates=invoice            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## How It Works

1. **invoice-extractor** (LLM) reads the raw invoice text, extracts every field, and uses calculator tools to cross-check the math independently.
2. **invoice-validator** (Tool agent) runs a second, purely deterministic validation pass on the extracted numbers with zero token cost.
3. **invoice-pipeline** (Sequential) chains both agents so every invoice goes through extraction then validation.

## Connic Features Used

| Feature | Where |
|---------|-------|
| Sequential agent | `invoice-pipeline.yaml` |
| LLM agent with tools | `invoice-extractor.yaml` |
| Tool agent (no LLM) | `invoice-validator.yaml` |
| Output schema | `schemas/invoice.json` |
| Middleware (audit trail) | `middleware/invoice-extractor.py` |
| `retry_options` | Extractor retries up to 5 times |
| `timeout` | 45-second hard limit per extraction |

## Connector Setup

Add an **HTTP Webhook (sync)** connector from the agent detail page in the [Connic dashboard](https://connic.co) for real-time invoice processing:

| Setting | Value |
|---------|-------|
| Mode | Sync (Request-Response) |
| Linked agent | `invoice-pipeline` |

After creating the connector, open its detail page to copy the auto-generated **Webhook URL** and **Secret Key**. POST invoice data to that URL and receive the structured extraction result in the response. Authenticate with the `X-Connic-Secret` header or a `?secret=` query parameter. Sync mode has a 5-minute timeout.

**Other connector options:**

- **S3 inbound** to process invoices dropped into a bucket (see the [s3-document-pipeline](../s3-document-pipeline) template for S3 setup)
- **Email inbound** to extract invoices from email attachments (see the [email-helpdesk](../email-helpdesk) template for Email setup)
- **Kafka inbound** to consume invoice events from a message bus (see the [kafka-fraud-detector](../kafka-fraud-detector) template for Kafka setup)

## Structure

```
invoice/
  agents/
    invoice-extractor.yaml    # LLM extraction with calculator tools
    invoice-validator.yaml    # Deterministic math validation
    invoice-pipeline.yaml     # Sequential: extract then validate
  tools/
    invoice_tools.py          # add, multiply, calculate_tax, validate_totals
  middleware/
    invoice-extractor.py      # Audit trail with request_id and cost tracking
  schemas/
    invoice.json              # Structured output schema
  requirements.txt
```
