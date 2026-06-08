# Connic Awesome Agents

Production-ready agent templates for the [Connic](https://connic.co) platform. Each template is a complete project showcasing real-world use cases with detailed agent configurations, working tools, functional middleware, and structured output schemas.

## Templates

| Template | Use Case | Highlights |
|----------|----------|------------|
| [lead-enricher](./lead-enricher) | Automatic signup enrichment and ICP scoring | web_search, knowledge base, `db_upsert` |
| [invoice](./invoice) | Invoice data extraction and validation | Sequential pipeline, tool agent, retry, middleware audit trail |
| [customer-support](./customer-support) | Ticket triage and RAG-powered response | WebSocket streaming, guardrails, A/B variant, StopProcessing spam filter |
| [s3-document-pipeline](./s3-document-pipeline) | Automated document processing from S3 | S3 trigger, multimodal input, file type validation |
| [stripe-dunning](./stripe-dunning) | Payment recovery for failed subscriptions | Stripe webhooks, trigger_agent, knowledge base history |
| [kafka-fraud-detector](./kafka-fraud-detector) | Real-time transaction fraud scoring | Kafka streams, conditional tools, tool hooks, concurrency control |
| [compliance-auditor](./compliance-auditor) | Scheduled compliance auditing | Cron trigger, web_search, MCP, discoverable tools, reasoning |
| [postgres-change-notifier](./postgres-change-notifier) | Database change monitoring and alerting | PostgreSQL LISTEN/NOTIFY, trigger_agent, audit trail |
| [email-helpdesk](./email-helpdesk) | End-to-end email support automation | Email IMAP/SMTP, guardrails, StopProcessing, full knowledge CRUD |
| [research-assistant](./research-assistant) | Multi-agent research orchestration | trigger_agent, web_search, discoverable tools, parallel dispatch |
| [sqs-order-processor](./sqs-order-processor) | Order validation and fulfillment | SQS queues, concurrency keys, tool agent, timeout |
| [telegram-personal-assistant](./telegram-personal-assistant) | Persistent Telegram chatbot with memory | Telegram, persistent sessions, web_search, database, knowledge base |

## Feature Coverage

Every Connic feature is demonstrated in at least one template:

### Connectors

| Connector | Template |
|-----------|----------|
| HTTP Webhook | lead-enricher, customer-support, invoice |
| Cron | compliance-auditor |
| Kafka (in + out) | kafka-fraud-detector |
| WebSocket | customer-support |
| MCP Server | compliance-auditor |
| AWS SQS (in + out) | sqs-order-processor |
| AWS S3 | s3-document-pipeline |
| PostgreSQL | postgres-change-notifier |
| Email (IMAP + SMTP) | email-helpdesk |
| Stripe | stripe-dunning |
| Telegram (in + out) | telegram-personal-assistant |

### Agent Types

| Type | Templates |
|------|-----------|
| LLM agent | All templates |
| Sequential agent | invoice, customer-support, s3-document-pipeline, stripe-dunning, email-helpdesk, sqs-order-processor |
| Tool agent | invoice, kafka-fraud-detector, postgres-change-notifier, sqs-order-processor |

### Platform Features

| Feature | Template |
|---------|----------|
| `trigger_agent` (agent-to-agent) | stripe-dunning, postgres-change-notifier, research-assistant |
| `query_knowledge` / `store_knowledge` (RAG) | lead-enricher, customer-support, kafka-fraud-detector, compliance-auditor, research-assistant, telegram-personal-assistant |
| `delete_knowledge` | email-helpdesk |
| `db_find` / `db_upsert` (database) | lead-enricher, stripe-dunning, postgres-change-notifier, compliance-auditor, telegram-personal-assistant |
| `web_search` | lead-enricher, compliance-auditor, research-assistant, telegram-personal-assistant |
| Output schemas | All templates |
| Conditional tools | kafka-fraud-detector |
| Concurrency control (key + on_conflict) | kafka-fraud-detector, sqs-order-processor |
| `StopProcessing` middleware | customer-support, s3-document-pipeline, stripe-dunning, email-helpdesk, sqs-order-processor |
| Tool hooks (`before` / `after`) | kafka-fraud-detector |
| Guardrails (input / output) | customer-support, email-helpdesk |
| Discoverable tools | compliance-auditor, research-assistant |
| A/B testing variant | customer-support |
| Agent tests (`connic test`) | All templates |
| `_defaults.yaml` (cascading config) | All templates |
| Persistent sessions | telegram-personal-assistant |
| Middleware context injection | customer-support, stripe-dunning, kafka-fraud-detector, email-helpdesk, sqs-order-processor, telegram-personal-assistant |
| Context in tools | customer-support, kafka-fraud-detector |
| MCP server integration | compliance-auditor |
| `max_iterations` | lead-enricher, customer-support, research-assistant |
| `reasoning_effort` | compliance-auditor, research-assistant, _defaults (all) |
| `retry_options` | invoice, s3-document-pipeline |
| `timeout` | lead-enricher, invoice, compliance-auditor, research-assistant, sqs-order-processor |

### Models

Templates use a deliberate mix of providers and their latest models to show
Connic's model-agnostic runtime: `gemini/gemini-3.5-flash` for fast/cheap
classification and validation, `openai/gpt-5.5` for customer-facing drafting,
and `anthropic/claude-opus-4-8` / `claude-sonnet-4-6` for deep reasoning.

### Not enabled by default

Two features are documented in the relevant template READMEs as ready-to-enable
blocks rather than active config, because both are incompatible with the
non-interactive deploy-gate test suite: **human-in-the-loop approvals**
(pauses a run for a human decision — see [sqs-order-processor](./sqs-order-processor))
and **API spec tools** (`api:` operations need an uploaded OpenAPI spec — see
[stripe-dunning](./stripe-dunning)).

## Quick Start

```bash
pip install connic-composer-sdk

connic init my-project --templates=invoice,customer-support

cd my-project
connic lint     # Validate locally
connic dev      # Iterate with hot-reload
connic test     # Run the test suites in tests/
connic deploy   # Deploy to production (deploy gate runs tests first)
```

## Testing

Every template ships a `tests/` suite. `connic test` runs each case against a
throwaway deployment and exits non-zero on failure, and the deploy gate runs the
same suite before every release. External tools (Stripe, SQS, S3, email, Kafka,
Postgres) are stubbed with `tests/mocks/` so cases are deterministic and free of
side effects — see [the testing docs](https://connic.co/docs/v1/composer/testing).

## Deploy

1. **Git integration**: Push to GitHub/GitLab, connect in the [Connic dashboard](https://connic.co)
2. **CLI deploy**: `connic login && connic deploy`
3. **Iterate first**: `connic dev` creates an ephemeral environment with hot-reload

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add new templates or improve existing ones.
