# Knowledge Copilot

A long-running internal knowledge copilot served over WebSocket. Employees chat with it through a panel in the company portal; it discovers how the knowledge base is organized, answers strictly from the docs, labels every reply with its sources, and logs unanswerable questions for the docs team. Each user keeps one persistent session that survives reconnects and weeks of conversation thanks to context compression and stored-history compaction.

```bash
pip install connic-composer-sdk
connic init my-project --templates=knowledge-copilot   # new project
connic init . --templates=knowledge-copilot            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## How It Works

1. Middleware resolves the portal `user_id` from the WebSocket payload into context so the session key resolves. Messages without one are rejected via `StopProcessing` before the LLM runs.
2. **knowledge-copilot** (LLM) explores the knowledge base hierarchy with `list_topics` (wrapping `kb_list_namespaces`), searches with `search_docs` (wrapping `query_knowledge`, optionally scoped to a topic), and answers only from retrieved content.
3. When the docs have no answer, the agent calls `report_gap`, which writes the question to a `knowledge_gaps` database collection for the docs team.
4. The `after` middleware appends a provenance footer naming the topics consulted (recorded in context by `search_docs`). Guardrail rejections skip the footer because `run_after_on_block: false` is set.
5. Because sessions run for weeks, `context_compression` recovers from context-window overflows in-run, and `session_history` compaction summarizes older stored runs every 5 runs so the session never grows unbounded.

## Connic Features Used

| Feature | Where |
|---------|-------|
| Persistent sessions | `knowledge-copilot.yaml` - `session.key: context.user_id` with 30 day TTL |
| `context_compression` | Keeps 12 recent messages verbatim, 60k prompt-token budget |
| `session_history` compaction | Compacts stored history every 5 runs, keeping 2 recent runs unsummarized |
| `fallback_model` | Anthropic primary, `gemini/gemini-2.5-pro` fallback (both accept a raw reasoning budget) |
| `reasoning_budget` | 2048 thinking tokens instead of an effort level |
| `kb_list_namespaces` | Wrapped by `copilot_tools.list_topics` for topic discovery |
| `query_knowledge` (RAG) | Wrapped by `copilot_tools.search_docs` with optional topic scoping |
| `db_insert` (database) | `copilot_tools.report_gap` writes to the `knowledge_gaps` collection |
| `data_exfiltration` guardrail | Output guardrail blocks credential leaks and bulk doc dumps |
| `run_after_on_block: false` | Guardrail rejections skip the provenance footer |
| `StopProcessing` middleware | Blocks messages without a `user_id` before the LLM runs |
| Context in tools | `search_docs` records consulted topics in context for the footer |

## Connector Setup

Add a **WebSocket** connector from the agent detail page in the [Connic dashboard](https://connic.co):

| Setting | Value |
|---------|-------|
| Streaming responses | `true` |
| Require authentication | `true` |
| Session timeout (seconds) | `3600` (1 hour) |
| Max messages per session | `100` |
| Linked agent | `knowledge-copilot` |

After creating the connector, open its detail page to copy the auto-generated **WebSocket URL** and **Secret Key**. Connect via WebSocket, send the secret as the first message (`{"secret": "..."}`), then send messages carrying the portal user ID:

```json
{"type": "message", "id": "1", "payload": {"message": "How do I roll back a deploy?", "context": {"user_id": "u_401"}}}
```

The connector-level session covers one socket connection; the agent-level `session` keyed on `user_id` is what carries the conversation across reconnects, deploys, and days away. Note that with output guardrails enabled, the full response is inspected before any text is streamed to the client.

The copilot answers from whatever lives in your project knowledge base. Seed it under hierarchical namespaces (e.g. `engineering.deploys`, `policies.hr`) via the dashboard or `store_knowledge`; `list_topics` picks up the hierarchy automatically.

## Testing

Run `connic test` to execute `tests/knowledge-copilot.yaml`. All three `copilot_tools` are mocked (`tests/mocks/copilot_mocks.py`) with `strict_mocks`, so no knowledge base or database is touched. The search mock returns an empty result for the office-pets question, which deterministically drives the gap-reporting path.

## Structure

```
knowledge-copilot/
  agents/
    knowledge-copilot.yaml    # Session + compression + guardrails + fallback model
  tools/
    copilot_tools.py          # Topic discovery, scoped doc search, gap reporting
  middleware/
    knowledge-copilot.py      # user_id resolution (StopProcessing) + provenance footer
  requirements.txt
```

## Example Conversation

```
User: Where are the deploy runbooks?
Bot:  Deploy docs live under engineering.deploys (6 entries), covering
      releases, rollbacks, and the on-call checklist.

      [Sources: engineering.deploys]

User: (three days later) And how do I roll one back?
Bot:  From the release channel, run the rollback command with the release ID
      you want to revert to, confirm the previous release is healthy in the
      dashboard, then post a summary in the incident thread.

      [Sources: engineering.deploys]

User: Do we have a policy on bringing dogs to the office?
Bot:  I could not find anything about pets in the office in the docs. I have
      logged this as a documentation gap for the docs team.

      [No knowledge base sources consulted]
```
