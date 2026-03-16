# Compliance Auditor

Scheduled compliance auditing with real-time regulatory intelligence. Combines web search for regulatory updates, MCP tools for framework documentation, a knowledge base for policy retrieval, and the database for audit history tracking.

```bash
pip install connic-composer-sdk
connic init my-project --templates=compliance-auditor   # new project
connic init . --templates=compliance-auditor            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## How It Works

1. A **Cron connector** triggers `compliance-scanner` on a schedule (e.g. weekly).
2. The scanner searches the web for recent regulatory changes, queries internal policies from the knowledge base, and looks up framework best practices via MCP.
3. It identifies compliance gaps, scores overall risk, and stores findings.
4. **audit-reporter** transforms raw findings into an executive summary and detailed report.

## Connic Features Used

| Feature | Where |
|---------|-------|
| **Cron inbound connector** | Scheduled weekly/monthly audits |
| `web_search` tool | Checks for new regulatory developments |
| MCP server integration | Context7 for framework documentation lookup |
| Knowledge base (RAG) | Retrieves internal compliance policies semantically |
| Database | Stores and queries audit history via `db_find` / `db_insert` |
| `reasoning: true` | Deep analysis with transparent reasoning chain |
| `reasoning_budget: 16384` | Extended thinking for complex compliance analysis |
| Output schema | `schemas/audit-report.json` |
| `timeout: 120` | Extended timeout for thorough multi-source research |

## Connector Setup

Add a **Cron inbound** connector to your agent from the agent detail page in the Connic dashboard:

| Setting | Value |
|---------|-------|
| Schedule | `0 9 * * 1` (every Monday at 9 AM) |
| Prompt | `Run a GDPR and SOC 2 compliance audit for our SaaS platform` |
| Linked agent | `compliance-scanner` |

Optionally add an **HTTP Webhook (outbound)** or **Email outbound** connector to distribute the report.

## Structure

```
compliance-auditor/
  agents/
    compliance-scanner.yaml   # Deep research with web_search, MCP, RAG, reasoning
    audit-reporter.yaml       # Formats findings into executive report
  tools/
    compliance_tools.py       # Risk scoring and finding formatting
  schemas/
    audit-report.json         # Structured audit output
  requirements.txt
```
