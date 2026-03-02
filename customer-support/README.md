# Customer Support

Intelligent ticket triage and RAG-powered response drafting. The triager classifies priority, category, and sentiment; the responder searches the knowledge base before answering and stores new solutions for future use.

```bash
pip install connic-composer-sdk
connic init my-project --templates=customer-support   # new project
connic init . --templates=customer-support            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## How It Works

1. **support-triager** (LLM) classifies the ticket and extracts routing metadata. Middleware blocks spam senders using `StopProcessing` before the LLM is ever called.
2. **support-responder** (LLM) queries the knowledge base for existing answers, drafts a response matching the customer's tone, and stores new solutions it discovers.
3. **support-pipeline** (Sequential) chains triage then response.

## Connic Features Used

| Feature | Where |
|---------|-------|
| Sequential agent | `support-pipeline.yaml` |
| Knowledge base RAG | `support-responder.yaml` uses `query_knowledge` and `store_knowledge` |
| `StopProcessing` middleware | `middleware/support-triager.py` blocks spam without running the LLM |
| Context injection in tools | `support_tools.py` receives `context` with `run_id`, `connector_id` |
| Output schema | `schemas/ticket-classification.json` |
| Middleware context enrichment | Sets `channel` in context for downstream agents |

## Suggested Connectors

- **WebSocket (sync, streaming: true)** for real-time chat support with streaming responses
- **HTTP Webhook (sync)** for ticketing system integrations (Zendesk, Intercom)
- **Email inbound** to process support emails
- **HTTP Webhook (outbound)** to send escalations to Slack or PagerDuty

## Structure

```
customer-support/
  agents/
    support-triager.yaml      # Priority + category + sentiment classification
    support-responder.yaml    # RAG-powered response drafting
    support-pipeline.yaml     # Sequential: triage then respond
  tools/
    support_tools.py          # Escalation formatting with context injection
  middleware/
    support-triager.py        # Spam filter (StopProcessing) + context enrichment
  schemas/
    ticket-classification.json
  requirements.txt
```
