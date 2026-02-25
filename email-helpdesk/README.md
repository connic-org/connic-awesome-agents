# Email Helpdesk

End-to-end email support automation. Classifies incoming emails, filters auto-replies and spam before the LLM runs, drafts contextual replies using the knowledge base, and sends them via SMTP.

## How It Works

1. The **Email inbound connector** polls an IMAP mailbox for new messages.
2. Middleware catches auto-replies and spam headers with `StopProcessing` (zero tokens used).
3. **email-classifier** (LLM) determines intent, urgency, department, and language.
4. **email-responder** (LLM) searches the knowledge base, drafts a reply in the sender's language, and outputs structured JSON (`to`, `subject`, `body`) matching the Email outbound connector format.
5. The **Email outbound connector** parses the agent's JSON output and sends the reply via SMTP.

## Connic Features Used

| Feature | Where |
|---------|-------|
| **Email inbound connector** | Polls IMAP mailbox for new emails |
| **Email outbound connector** | Sends replies via SMTP |
| Sequential agent | `helpdesk-pipeline.yaml` |
| `StopProcessing` middleware | Filters auto-replies and spam headers |
| Middleware context enrichment | Extracts `from_address`, `sender_name`, `original_subject` into context |
| Knowledge base (full CRUD) | `query_knowledge`, `store_knowledge`, `delete_knowledge` |
| Output schemas | `email-classification.json` (classifier), `email-reply.json` (responder with `to`/`subject`/`body` for SMTP) |

## Connector Setup

**Email inbound** (IMAP):

| Setting | Value |
|---------|-------|
| IMAP host | `imap.example.com` |
| IMAP port | `993` |
| Use SSL | `true` |
| Username | `support@example.com` |
| Mailbox | `INBOX` |
| Filter unread only | `true` |
| Mark as read | `true` |
| Linked agent | `helpdesk-pipeline` |

**Email outbound** (SMTP):

| Setting | Value |
|---------|-------|
| SMTP host | `smtp.example.com` |
| SMTP port | `587` |
| Use TLS | `true` |
| From address | `support@example.com` |
| From name | `Company Support` |
| Linked agent | `email-responder` |

## Structure

```
email-helpdesk/
  agents/
    email-classifier.yaml    # Intent, urgency, department classification
    email-responder.yaml     # RAG-powered reply drafting
    helpdesk-pipeline.yaml   # Sequential: classify then respond
  middleware/
    email-classifier.py      # Auto-reply/spam filter with StopProcessing
  schemas/
    email-classification.json  # Classifier output: intent, urgency, dept, from_address
    email-reply.json           # Responder output: to, subject, body (Email outbound format)
  requirements.txt
```
