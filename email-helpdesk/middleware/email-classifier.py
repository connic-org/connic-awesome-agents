"""Middleware for email-classifier.

Filters auto-replies and obvious spam before the LLM runs.
Extracts sender metadata into context for the entire pipeline.

The Email inbound connector delivers a JSON payload with fields:
from, from_address, to, subject, body_text, body_html, attachments, _email
"""

import json
import re
from typing import Any

from connic.core import StopProcessing

AUTO_REPLY_PATTERNS = [
    r"out of office",
    r"automatic reply",
    r"auto-reply",
    r"i am currently out",
    r"on vacation until",
    r"delivery status notification",
    r"undeliverable",
    r"mailer-daemon",
]


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Filter auto-replies and enrich context with sender info."""
    parts = content.get("parts", [])
    full_text = ""
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            full_text += part["text"]

    email_data = None
    try:
        email_data = json.loads(full_text)
    except (json.JSONDecodeError, TypeError):
        pass

    if isinstance(email_data, dict):
        context["from_address"] = email_data.get("from_address", "")
        context["sender_name"] = _extract_name(email_data.get("from", ""))
        context["original_subject"] = email_data.get("subject", "")
        context["message_id"] = email_data.get("message_id", "")

        body = email_data.get("body_text", "") or email_data.get("body_html", "")
        subject = email_data.get("subject", "")
        check_text = f"{subject} {body}".lower()
    else:
        check_text = full_text.lower()

    for pattern in AUTO_REPLY_PATTERNS:
        if re.search(pattern, check_text):
            raise StopProcessing("Auto-reply detected. No response needed.")

    from_addr = (email_data or {}).get("from_address", "").lower()
    if "mailer-daemon" in from_addr or "noreply" in from_addr:
        raise StopProcessing("System email detected. No response needed.")

    return content


async def after(response: str, context: dict[str, Any]) -> str:
    """Pass classification through to the responder."""
    return response


def _extract_name(from_field: str) -> str:
    """Extract display name from 'Name <email>' format."""
    match = re.match(r"^([^<]+)<", from_field)
    if match:
        return match.group(1).strip()
    return from_field.split("@")[0] if "@" in from_field else from_field
