"""Middleware for page-designer.

Pages belong to the chat visitor chat-assistant acts for: the files rules,
the data the page reads and the embed link all need that visitor. A run
without one (from the dashboard, a test or another trigger) stops here with
a clear message instead of failing at the first file write.
"""

from typing import Any

from connic import StopProcessing


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    if not (context.get("end_user") or {}).get("id"):
        raise StopProcessing("page-designer builds pages for a chat visitor. Ask chat-assistant in the chat app.")
    return content
