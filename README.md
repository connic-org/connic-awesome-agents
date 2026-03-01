# Connic Awesome Agents

Production-ready agent templates for the [Connic](https://connic.co) platform. Each template is a complete project showcasing real-world use cases with detailed agent configurations, working tools, functional middleware, and structured output schemas.

## Templates

| Template | Use Case | Highlights |
|----------|----------|------------|
| [lead-enricher](./lead-enricher) | Automatic signup enrichment and ICP scoring | web_search, knowledge base, database |
| [invoice](./invoice) | Invoice data extraction and validation | Sequential pipeline, tool agent, retry, middleware audit trail |
| [customer-support](./customer-support) | Ticket triage and RAG-powered response | WebSocket streaming, knowledge base, StopProcessing spam filter |
| [s3-document-pipeline](./s3-document-pipeline) | Automated document processing from S3 | S3 trigger, multimodal input, file type validation |
| [stripe-dunning](./stripe-dunning) | Payment recovery for failed subscriptions | Stripe webhooks, trigger_agent, knowledge base history |
| [kafka-fraud-detector](./kafka-fraud-detector) | Real-time transaction fraud scoring | Kafka streams, conditional tools, concurrency control |
| [compliance-auditor](./compliance-auditor) | Scheduled compliance auditing | Cron trigger, web_search, MCP integration, reasoning |
| [postgres-change-notifier](./postgres-change-notifier) | Database change monitoring and alerting | PostgreSQL LISTEN/NOTIFY, trigger_agent, audit trail |
| [email-helpdesk](./email-helpdesk) | End-to-end email support automation | Email IMAP/SMTP, StopProcessing, full knowledge CRUD |
| [research-assistant](./research-assistant) | Multi-agent research orchestration | trigger_agent, web_search, reasoning budget, parallel dispatch |
| [sqs-order-processor](./sqs-order-processor) | Order validation and fulfillment | SQS queues, concurrency keys, tool agent, timeout |

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
| `query_knowledge` / `store_knowledge` (RAG) | lead-enricher, customer-support, kafka-fraud-detector, compliance-auditor, research-assistant |
| `delete_knowledge` | email-helpdesk |
| `db_find` / `db_insert` (database) | lead-enricher, stripe-dunning, postgres-change-notifier, compliance-auditor |
| `web_search` | lead-enricher, compliance-auditor, research-assistant |
| Output schemas | All templates |
| Conditional tools | kafka-fraud-detector |
| Concurrency control (key + on_conflict) | kafka-fraud-detector, sqs-order-processor |
| `StopProcessing` middleware | customer-support, s3-document-pipeline, stripe-dunning, email-helpdesk, sqs-order-processor |
| Middleware context injection | customer-support, stripe-dunning, kafka-fraud-detector, email-helpdesk, sqs-order-processor |
| Context in tools | customer-support, kafka-fraud-detector |
| MCP server integration | compliance-auditor |
| `max_iterations` | lead-enricher, customer-support, research-assistant |
| `reasoning` + `reasoning_budget` | compliance-auditor, research-assistant |
| `retry_options` | invoice, s3-document-pipeline |
| `timeout` | lead-enricher, invoice, compliance-auditor, research-assistant, sqs-order-processor |

## Quick Start

```bash
pip install connic-composer-sdk

connic init my-project --templates=invoice,customer-support

cd my-project
connic lint     # Validate locally
connic test     # Test with hot-reload
connic deploy   # Deploy to production
```

## Deploy

1. **Git integration**: Push to GitHub/GitLab, connect in the [Connic dashboard](https://connic.co)
2. **CLI deploy**: `connic login && connic deploy`
3. **Test first**: `connic test` creates an ephemeral environment with hot-reload

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add new templates or improve existing ones.
