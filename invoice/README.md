# Invoice Processor

Extract structured data from invoices and validate totals automatically. A sequential pipeline pairs an LLM extractor with a deterministic validator for reliable, auditable results.

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
| `max_concurrent_runs` | Extractor handles 3 invoices in parallel |
| `timeout` | 45-second hard limit per extraction |

## Suggested Connectors

- **HTTP Webhook (sync)** for real-time API calls from your ERP
- **S3 inbound** to process invoices dropped into a bucket
- **Email inbound** to extract invoices from email attachments
- **Kafka inbound** to consume invoice events from a message bus

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
