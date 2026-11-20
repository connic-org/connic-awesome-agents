# Chat Page Builder

A chat app where the agent builds pages next to the conversation: dashboards, charts, reports, calculators and trackers. Ask for something to look at, and a page opens in a panel beside the chat. Ask for a change, and the same page updates in place. Pages keep working after the chat ends, read live data under access rules, and can save what visitors enter.

Two agents share the work. **chat-assistant** runs on a fast model, talks to the visitor and keeps their data. When a page is needed, it hands a brief to **page-designer**, which runs on a stronger model with a written design brief and an example page, publishes the page as an instance of an app, previews it, looks at a screenshot and fixes what's off before it answers.

```bash
pip install connic-composer-sdk
connic init my-project --templates=chat-page-builder   # new project
connic init . --templates=chat-page-builder            # existing project
```

[connic CLI docs](https://connic.co/docs/v1/reference/cli)

## How It Works

1. The visitor signs in to the **chat app** (`apps/chat/`) and writes a message. It goes over the `assistant-chat` WebSocket connector, which only that app can open.
2. The `chat-assistant` middleware keys the session on the signed-in visitor plus the chat's ID, and adds a note with the visitor's name and today's date.
3. **chat-assistant** answers plain questions itself. For a page, it gathers the data (from the conversation, from `db_find`, or sample data it labels as such), stores data that should stay live in the `page_data` collection, and calls `trigger_agent("page-designer", ...)` with a brief and the data or a reference to it.
4. **page-designer** reads an example page from Files, writes `index.html`, `app.js` and `data.json` into a folder under `pages/`, and calls `app_publish`. connic adds that tool because the agent lists the `pages` app under `apps:`, and it returns the page's `url` and an `embed_url` signed in as the chat visitor.
5. page-designer calls `app_preview`, which connic adds next to `app_publish`. It opens the page as the visitor and returns a full-page screenshot, console errors and warnings (including files the content security policy blocked) and uncaught script errors. The designer fixes what looks wrong, publishes again to the same instance and previews again (two rounds at most). It returns a structured result (`schemas/page-result.json`).
6. chat-assistant replies with a short summary and a Markdown link to the page. The chat app turns links to `/i/<instance id>/` into page cards and opens the newest one in its panel.

Every page loads the same base from the **pages app** (`apps/pages/`): Tailwind CSS, Chart.js, Lucide icons, the Inter font and a theme, all served from the app's own host. Models write these libraries well, the default content security policy allows them, and a change to the theme restyles every published page on the next deploy.

## connic Features Used

| Feature | Where |
|---------|-------|
| Apps | `apps/chat.yaml` (the chat) and `apps/pages.yaml` (the page base), built on every deploy |
| App instances (`instances_only`) | The pages app serves only what agents publish, under `/i/<instance id>/` |
| `app_publish`, `app_preview` and embed links | `page-designer.yaml` `apps:` entry with `user: context.end_user` returns `embed_url`; `app_preview` checks each published page |
| Embedding (`embed.origins`) | The chat app shows pages in an iframe |
| `content_security_policy` | The chat app allows frames from the pages app's host |
| WebSocket connector (`apps_only`, progress events) | `connectors/assistant-chat.yaml`; the chat shows each step while the designer works |
| `trigger_agent` (agent-to-agent) | chat-assistant hands the brief and data to page-designer |
| Access rules (agents and apps) | Visitors only see their own `page_data`, `page_state` and page files; `set` stamps the owner |
| `db_find` / `db_insert` / `db_update` / `db_delete` | chat-assistant keeps live datasets in `page_data` |
| Files (`file_read`, `file_write`, `file_list`) | Page sources under `pages/`, example pages under `page-examples/` |
| Output schema | `schemas/page-result.json` |
| `reasoning_effort` | `high` for page-designer, `low` for chat-assistant |
| Persistent sessions | `session.key: context.conversation_key` (visitor plus chat), 30-day TTL |
| Concurrency control | One run at a time per chat (`concurrency.key: conversation_id`) |
| `context_compression` | Long chats that build many pages |
| `StopProcessing` middleware | Both agents stop runs that don't come from a signed-in chat visitor |

## Setup

1. **Install the apps' dependencies.** connic installs them on every deploy; `connic dev` builds locally and needs them installed:

   ```bash
   cd apps/chat && npm install && cd ../pages && npm install && cd ../..
   ```

2. **Run or deploy.** `connic dev` for an environment with hot reload, or `connic deploy`. Apps need the developer plan or higher; this template uses two apps per environment.

3. **Upload the example page.** page-designer copies its patterns from Files. Upload `page-examples/dashboard/index.html`, `app.js` and `data.json` to the environment's Files under `page-examples/dashboard/`, in the dashboard's Files page or with connic MCP's `write_file`. Add your own examples next to it (`page-examples/<name>/`) and the designer picks the one closest to each request, without a deploy.

4. **Pin the embed origin.** `apps/pages.yaml` lets any `*.connic.app` host frame the pages so the template works on the first deploy. Replace it with the chat app's address from the Apps page (for example `https://chat-1a2b3c4d.connic.app`), or with your custom domain.

5. **Open the chat app** from the Apps page and sign in. Both apps use connic accounts, so project members can try it right away. For customers or employees without a connic account, switch `auth` in `apps/chat.yaml` to `oidc` or `public` (see the [apps docs](https://connic.co/docs/v1/apps)). Pages open through embed links, which sign the panel in as the chat visitor in every mode.

`app_preview` runs in a cloud browser and counts as browser usage. It can't reach pages served on `localhost`, so page-designer skips the check there and says so in its notes.

## Data

| Where | What | Who sees it |
|-------|------|-------------|
| `page_data` collection | Datasets chat-assistant stores for live pages, one document per row with a `dataset` field | The visitor it was stored for (`owner`) |
| `page_state` collection | What visitors save on a page (check-ins, notes, settings), with a `kind` field | The visitor who saved it |
| Files `pages/<slug>/` | Each page's source, written by page-designer | page-designer, for the same visitor |
| Files `apps/pages/<instance id>/` | connic's copy of each published instance | Read-only |

Published pages are kept until you delete them on the app's Instances tab. To expire them, add `max_age_days` to the `apps:` entry in `page-designer.yaml`.

## Customizing

- **Look:** colors, font and chart defaults live in `apps/pages/src/lib/page.js`; the chat app uses the same tokens in `apps/chat/src/styles.css`. Keep one accent color.
- **Design rules:** the "Design" section of `page-designer.yaml`. Rules there plus a good example page do more than a longer prompt.
- **Data sources:** give chat-assistant the tools that reach your data (Python tools, MCP servers, Retrieval) and it passes the results on as `data` or stores them in `page_data`.
- **Models:** chat-assistant needs speed, page-designer needs a model that writes good front-end code and reads screenshots.

## Testing

The template has no `connic test` suite: every run needs a signed-in visitor from the chat app, and page-designer's work depends on the deployed pages app and `app_preview`. Check it by hand in the chat app after `connic dev` or a deploy.

## Structure

```
chat-page-builder/
  agents/
    chat-assistant.yaml       # Fast chat agent: conversation, data, calls page-designer
    page-designer.yaml        # Stronger model: design brief, app_publish, app_preview check
  apps/
    chat.yaml                 # Chat app: sign-in, connector, CSP for the page frame
    chat/                     # Chat UI (no framework): messages, page cards, page panel
    pages.yaml                # instances_only base: embed origins, data access rules
    pages/                    # Libraries and theme every page loads from /lib/
  connectors/
    assistant-chat.yaml       # apps_only WebSocket with streaming and progress events
  middleware/
    chat-assistant.py         # Session key per visitor and chat, date note, StopProcessing
    page-designer.py          # StopProcessing for runs without a chat visitor
  page-examples/
    dashboard/                # Example page to upload to Files
  schemas/
    page-result.json          # What page-designer returns
  requirements.txt
```

## Example Conversation

```
User: A sales dashboard for our six coffee shops: revenue by month, best products
      and a store ranking. Use sample data.

Bot:  Here's a sales dashboard with sample data: twelve months of revenue against
      last year, revenue by product and all six stores ranked by revenue. Want a
      filter by city next?
      [Coffee shop sales]  (opens in the panel)

User: Make the store table sortable and show the change against last year.

Bot:  Done: the table sorts by any column and shows each store's change against
      last year in green or red.
      [Coffee shop sales]  (version 2, same address)
```
