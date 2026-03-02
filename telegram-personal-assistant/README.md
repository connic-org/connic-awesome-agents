# Telegram Personal Assistant

A persistent Telegram chatbot that remembers conversations, searches the web,
saves personal notes, and stores longer-form knowledge for later retrieval.
Showcases how a single agent can combine sessions, database, knowledge base,
and web search into a fully featured personal assistant.

```bash
pip install connic-composer-sdk
connic init my-project --templates=telegram-personal-assistant   # new project
connic init . --templates=telegram-personal-assistant            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## What it does

- Maintains multi-turn conversations via persistent sessions (7 day TTL)
- Searches the web on demand for current events, facts, documentation, etc.
- Saves and retrieves quick notes (reminders, facts, passwords) in the database
- Stores and queries longer-form knowledge (articles, summaries, how-tos) via RAG
- Formats all replies for Telegram using HTML tags

## Connic Features Used

| Feature | Where |
|---------|-------|
| Persistent sessions | `telegram-assistant.yaml` - `session.key: context.telegram_chat_id` with 7 day TTL |
| `web_search` | Built-in tool for real-time internet lookups |
| `db_insert` / `db_find` / `db_delete` (database) | `assistant_tools.py` - note CRUD in `notes` collection |
| `query_knowledge` / `store_knowledge` (RAG) | `assistant_tools.py` - personal knowledge base in `personal` namespace |
| Middleware context injection | `middleware/telegram-assistant.py` sets `telegram_chat_id` for session keying |

## Suggested Connectors

- **Telegram (inbound)** to receive messages from users
- **Telegram (outbound)** to send replies back to the chat

## Structure

```
telegram-personal-assistant/
  agents/
    telegram-assistant.yaml       # Chat agent with session + all tools
  tools/
    assistant_tools.py            # Note CRUD + knowledge store/query wrappers
  middleware/
    telegram-assistant.py         # Telegram payload extraction + reply formatting
  requirements.txt
```

## Example Conversation

```
User: Hey, remember that my flight to Berlin is on March 15th at 8am
Bot:  Got it, saved your flight details.

User: What's the weather in Berlin next week?
Bot:  Berlin next week: mostly cloudy, highs around 8-10 C, ...

User: What did I save about my flight?
Bot:  You have a flight to Berlin on March 15th at 8am.

User: Store this article summary for me: "The 2026 EU AI Act requires..."
Bot:  Stored in your knowledge base as "eu-ai-act-summary".

User: What do I have saved about EU regulations?
Bot:  From your knowledge base: The 2026 EU AI Act requires...
```

## Extending

- Add an output schema to return structured data alongside the chat reply
- Chain with a `calendar-sync` tool agent to create calendar events from saved notes
- Add conditional tools for admin-only operations like bulk note deletion
- Connect a second outbound connector (e.g. email) to forward summaries on demand
