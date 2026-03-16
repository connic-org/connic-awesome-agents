# Research Assistant

Multi-agent research system that decomposes complex questions, dispatches specialist agents for web and knowledge base research in parallel, and synthesizes findings into a structured report with confidence scoring.

```bash
pip install connic-composer-sdk
connic init my-project --templates=research-assistant   # new project
connic init . --templates=research-assistant            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## How It Works

1. **research-orchestrator** (LLM) receives a research question and breaks it into sub-questions.
2. Uses `trigger_agent` to dispatch sub-questions to specialists:
   - **web-researcher** searches the internet using `web_search`
   - **knowledge-analyst** searches the internal knowledge base
3. The orchestrator synthesizes all results, identifies conflicts, assesses confidence, and produces a structured report.
4. The final report is stored in the knowledge base for future reference.

## Connic Features Used

| Feature | Where |
|---------|-------|
| `trigger_agent` orchestration | `research-orchestrator.yaml` dispatches to specialists |
| `web_search` tool | `web-researcher.yaml` for internet research |
| Knowledge base (RAG) | `knowledge-analyst.yaml` for internal data |
| `reasoning: true` | Orchestrator uses extended reasoning for synthesis |
| `reasoning_budget: 32768` | Large reasoning budget for complex analysis |
| `max_iterations: 50` | Allows many tool calls for thorough research |
| `timeout: 180` | Extended timeout for multi-agent coordination |
| Output schema | `schemas/research-report.json` |
| Custom tools | Confidence assessment and citation formatting |

## Connector Setup

Add an **HTTP Webhook (sync)** connector from the agent detail page in the [Connic dashboard](https://connic.co) for on-demand research requests:

| Setting | Value |
|---------|-------|
| Mode | Sync (Request-Response) |
| Linked agent | `research-orchestrator` |

After creating the connector, open its detail page to copy the auto-generated **Webhook URL** and **Secret Key**. POST your research question to that URL and receive the structured report in the response. Authenticate with the `X-Connic-Secret` header or a `?secret=` query parameter. Sync mode has a 5-minute timeout, which is sufficient given the agent's 180-second timeout.

**Other connector options:**

- **WebSocket (sync, streaming)** for real-time research with progressive updates
- **Cron inbound** for scheduled market research or competitive analysis (see the [compliance-auditor](../compliance-auditor) template for Cron setup)
- **MCP server** to expose research capabilities to IDE-based AI assistants

## Structure

```
research-assistant/
  agents/
    research-orchestrator.yaml  # Decomposes questions, dispatches, synthesizes
    web-researcher.yaml         # Internet research specialist
    knowledge-analyst.yaml      # Internal knowledge base specialist
  tools/
    research_tools.py           # Confidence assessment, citation formatting
  schemas/
    research-report.json        # Structured research output
  requirements.txt
```
