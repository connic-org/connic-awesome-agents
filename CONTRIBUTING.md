# Contributing

Thank you for contributing agent templates. This guide explains how to add or improve templates.

## Template Structure

Each template is a complete Connic project:

```
template-id/
  agents/           # Required: at least one .yaml agent config
    *.yaml
  tools/            # Optional: Python tool modules
    *.py
  middleware/       # Optional: before/after hooks per agent
    *.py            # Filename must match agent name
  schemas/          # Optional: JSON Schema for structured output
    *.json
  requirements.txt  # Required (can be empty with comments)
  README.md         # Required
```

## Quality Standards

Templates in this repo should be genuinely useful, not just minimal examples:

- **Agents**: Write detailed, actionable system prompts. Include clear decision criteria, not just "analyze the input and respond."
- **Tools**: Implement real logic with proper type hints, docstrings, and error handling. No placeholder "replace with real implementation" stubs.
- **Middleware**: Every middleware should do something meaningful (validation, enrichment, filtering, metrics). Empty pass-through middleware should not be included.
- **Schemas**: Define complete schemas with descriptions, enums for constrained values, and `required` fields.
- **READMEs**: Explain how the template works, which Connic features it uses (with a table), and how to set up the relevant connectors.

## Feature Showcase

Each template should demonstrate at least 3-4 Connic platform features. Check the feature coverage matrix in the main README.md and try to fill gaps. Available features to showcase:

- Agent types: LLM, sequential, tool
- Connectors: HTTP, Cron, Kafka, WebSocket, MCP, SQS, S3, PostgreSQL, Email, Stripe
- Built-in tools: `trigger_agent`, `query_knowledge`, `store_knowledge`, `delete_knowledge`, `web_search`
- Conditional tools, concurrency control, MCP server integration
- Middleware: `StopProcessing`, context enrichment, request validation
- Output schemas, reasoning config, retry options, timeouts, max_concurrent_runs

## Naming Conventions

- Folder names: lowercase, hyphen-separated (e.g. `kafka-fraud-detector`)
- Agent YAML `name` field: must match filename without `.yaml`
- Middleware files: must match agent name (e.g. `middleware/my-agent.py` for agent `my-agent`)
- Tool modules: snake_case Python files (e.g. `tools/fraud_tools.py`)

## Testing

```bash
cd connic-awesome-agents/your-template
connic lint    # Validate structure and config
connic test    # Test against Connic cloud (requires connic login)
```

## Pull Request Process

1. Fork the repository
2. Create a branch: `git checkout -b add-template-your-name`
3. Add your template following the standards above
4. Run `connic lint` in your template folder to confirm it validates
5. Open a PR with the checklist from the PR template
