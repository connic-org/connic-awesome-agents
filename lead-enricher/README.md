# Lead Enricher

Automatically enriches and qualifies new signups. When someone fills in your
signup form, this agent researches their company, scores fit against your ideal
customer profile, and stores the result so your team can prioritize outreach.

## What it does

- Triggered by a webhook when a new signup arrives
- Web-searches the company to find size, industry, funding stage, and tech signals
- Loads your ICP scoring rubric from the knowledge base (or uses a sensible default)
- Scores fit 0-100 and assigns a status: qualified, nurture, or low
- Saves the enriched lead to the database with a research summary

## Setup

1. Deploy the agent to a project at [connic.co](https://connic.co)
2. Configure a webhook connector to receive signups
3. Optionally seed your ICP criteria so scoring reflects your actual target customer:

```python
from connic.tools import store_knowledge

await store_knowledge(
    "Target customer: B2B SaaS companies with 20-500 employees, Series A or later. "
    "High-fit industries: fintech, HR tech, devtools, e-commerce infra. "
    "Strong signals: recent funding, hiring engineers, using modern cloud stack.",
    namespace="icp",
    entry_id="icp-criteria",
)
```

Without seeded criteria the agent falls back to a generic B2B rubric.

## Input format

The webhook payload should include at minimum:

```json
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "company": "Acme Corp"
}
```

## Score thresholds

| Score | Status    | Suggested action           |
|-------|-----------|----------------------------|
| 70+   | qualified | Personal outreach          |
| 40-69 | nurture   | Add to drip sequence       |
| <40   | low       | No immediate action needed |

## Extending

- Chain with an `outreach-drafter` agent that writes a personalized first email
  for qualified leads
- Add a Slack notification tool to alert your team when a high-scoring lead arrives
- Expand `save_lead` to also push to your CRM via an outbound webhook
