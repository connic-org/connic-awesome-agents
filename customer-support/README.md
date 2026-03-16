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

## Connector Setup

Add a **WebSocket** connector from the agent detail page in the [Connic dashboard](https://connic.co) for real-time chat support:

| Setting | Value |
|---------|-------|
| Streaming responses | `true` |
| Require authentication | `true` |
| Session timeout (seconds) | `3600` (1 hour) |
| Max messages per session | `100` |
| Linked agent | `support-pipeline` |

After creating the connector, open its detail page to copy the auto-generated **WebSocket URL** and **Secret Key**. Connect via WebSocket and send the secret as the first message: `{"secret": "..."}`. Each session maintains conversation history across messages.

Optionally add an **HTTP Webhook (outbound)** connector to forward escalations to Slack or PagerDuty:

| Setting | Value |
|---------|-------|
| Mode | Outbound (Callback) |
| Callback URL | `https://your-server.com/escalations` |
| Linked agent | `support-responder` |

**Other connector options:**

- **HTTP Webhook (sync)** for ticketing system integrations (Zendesk, Intercom)
- **Email inbound** to process support emails (see the [email-helpdesk](../email-helpdesk) template)

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
