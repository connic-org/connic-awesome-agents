"""Middleware for document-intake.

Validates file size and type before running the LLM. Rejects unsupported
formats with StopProcessing to avoid wasted tokens.

The S3 inbound connector delivers a JSON payload with:
bucket, key, size, etag, event_name, event_time, _s3,
and optionally content: {text, content_type, size_bytes, encoding}
"""

import json
from typing import Any

try:
    from connic.exceptions import StopProcessing
except ImportError:
    class StopProcessing(Exception):
        pass

SUPPORTED_TYPES = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "text/markdown",
    "text/html",
    "image/png",
    "image/jpeg",
    "image/webp",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

MAX_SIZE_BYTES = 50 * 1024 * 1024


async def before(content: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Reject unsupported file types and oversized files before LLM runs."""
    parts = content.get("parts", [])
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            try:
                payload = json.loads(part["text"])
            except (json.JSONDecodeError, TypeError):
                continue

            if not isinstance(payload, dict):
                continue

            context["s3_bucket"] = payload.get("bucket", "")
            context["s3_key"] = payload.get("key", "")
            context["pipeline_stage"] = "intake"

            file_size = payload.get("size", 0)
            if file_size > MAX_SIZE_BYTES:
                raise StopProcessing(
                    f"File too large: {file_size} bytes "
                    f"(max {MAX_SIZE_BYTES // (1024*1024)} MB). "
                    f"Key: {payload.get('key', 'unknown')}"
                )

            file_content = payload.get("content", {})
            if isinstance(file_content, dict):
                ct = file_content.get("content_type", "")
                if ct and ct not in SUPPORTED_TYPES:
                    raise StopProcessing(
                        f"Unsupported file type: {ct}. "
                        f"Supported: {', '.join(sorted(SUPPORTED_TYPES))}"
                    )

    return content


async def after(response: str, context: dict[str, Any]) -> str:
    """Track processing metrics."""
    context["pipeline_stage"] = "intake_complete"
    return response
