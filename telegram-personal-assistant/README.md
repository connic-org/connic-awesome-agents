# Telegram Personal Assistant

A multimodal Telegram personal assistant that handles text, images, voice memos,
files, and video. It remembers conversations, searches the web, saves personal
notes, and stores longer-form knowledge for later retrieval. Showcases how a
single agent can combine sessions, database, knowledge base, web search, and
multimodal input into a fully featured personal assistant.

```bash
pip install connic-composer-sdk
connic init my-project --templates=telegram-personal-assistant   # new project
connic init . --templates=telegram-personal-assistant            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## What it does

- Processes multimodal input: text, images, voice messages, audio, video, documents
- Maintains multi-turn conversations via persistent sessions (7 day TTL)
- Searches the web on demand for current events, facts, documentation, etc.
- Saves and retrieves quick notes (reminders, facts, passwords) in the database
- Stores and queries longer-form knowledge (articles, summaries, how-tos) via RAG
- Formats all replies for Telegram using HTML tags
- Matches the user's language automatically

## Multimodal Support

The middleware preserves all media parts from incoming Telegram messages so the
LLM receives the full multimodal content:

| Input Type | What the Agent Does |
|------------|---------------------|
| Text | Answers questions, conversations, task help |
| Photos / Images | Describes content, reads text (OCR), analyzes charts |
| Voice memos | Responds to spoken content |
| Audio files | Processes and responds to audio content |
| Documents (PDF, etc.) | Summarizes, answers questions, extracts info |
| Video / Video notes | Analyzes visual content |

When media arrives without text, the agent proactively describes the content and
asks how it can help. When media includes a caption, it uses that as the question.

## Connic Features Used

| Feature | Where |
|---------|-------|
| Persistent sessions | `telegram-assistant.yaml` - `session.key: context.telegram_chat_id` with 7 day TTL |
| `web_search` / `web_read_page` | Built-in tools for real-time internet lookups |
| `db_insert` / `db_find` / `db_delete` (database) | `assistant_tools.py` - note CRUD in `notes` collection |
| `query_knowledge` / `store_knowledge` (RAG) | `assistant_tools.py` - personal knowledge base in `personal` namespace |
| Middleware multimodal passthrough | `middleware/telegram-assistant.py` preserves all media parts for the LLM |

## Connector Setup

This template requires two Telegram connectors: one inbound to receive messages and one outbound to send replies. Both share the same bot token.

### 1. Create a Telegram bot

1. Open Telegram and start a chat with [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts to choose a name and username
3. Copy the bot token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2. Add Telegram inbound connector

From the agent detail page in the [Connic dashboard](https://connic.co), add a **Telegram** connector:

| Setting | Value |
|---------|-------|
| Mode | Inbound (Receive Messages) |
| Bot token | Your bot token from @BotFather |
| Allowed user IDs | Your Telegram user ID (optional, restricts who can use the bot) |
| Linked agent | `telegram-assistant` |

The webhook is registered with Telegram automatically when you create the connector. To find your Telegram user ID, send a message to [@userinfobot](https://t.me/userinfobot).

### 3. Add Telegram outbound connector

Add a second **Telegram** connector for sending replies:

| Setting | Value |
|---------|-------|
| Mode | Outbound (Send Messages) |
| Bot token | Same bot token from @BotFather |
| Default chat ID | Leave empty (the middleware includes `chat_id` in the agent output) |
| Linked agent | `telegram-assistant` |

The middleware in `telegram-assistant.py` extracts the `chat_id` from each incoming message and includes it in the agent's response as `{"chat_id": ..., "text": "..."}`, so the outbound connector knows which chat to reply to.

## Structure

```
telegram-personal-assistant/
  agents/
    telegram-assistant.yaml       # Multimodal chat agent with session + all tools
  tools/
    assistant_tools.py            # Note CRUD + knowledge store/query wrappers
  middleware/
    telegram-assistant.py         # Telegram payload extraction + multimodal passthrough
  requirements.txt
```

## Example Conversations

```
User: Hey, remember that my flight to Berlin is on March 15th at 8am
Bot:  Got it, saved your flight details.

User: What's the weather in Berlin next week?
Bot:  Berlin next week: mostly cloudy, highs around 8-10 C, ...

User: [sends a photo of a restaurant menu]
Bot:  I can see a menu from "Trattoria Roma". The pasta dishes range from
      12-18 EUR. Want me to save this or help you pick something?

User: [sends a voice memo: "What did I save about my flight?"]
Bot:  You have a flight to Berlin on March 15th at 8am.

User: [sends a PDF document]
Bot:  This is a 12-page contract for... Here are the key points: ...
      Want me to save a summary to your knowledge base?
```

## Extending

- Add an output schema to return structured data alongside the chat reply
- Chain with a `calendar-sync` tool agent to create calendar events from saved notes
- Add conditional tools for admin-only operations like bulk note deletion
- Connect a second outbound connector (e.g. email) to forward summaries on demand
