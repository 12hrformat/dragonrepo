"""Sensitive data detection and redaction."""

from __future__ import annotations

import re
from typing import Iterable


REDACTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("authorization_header", re.compile(r"(?i)(authorization\s*:\s*)(bearer|basic)?\s+[A-Za-z0-9._~+/=-]{12,}")),
    ("bearer_token", re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}")),
    ("password_assignment", re.compile(r"(?i)\b(password|passwd|pwd)\s*([=:]\s*|\s+)[^\s'\";,]{3,}")),
    ("token_assignment", re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|token|secret)\s*([=:]\s*|\s+)[^\s'\";,]{8,}")),
    ("cookie_secret", re.compile(r"(?i)\b(session|sessionid|connect\.sid|jwt|auth)[_-]?(cookie)?=([A-Za-z0-9%._~+/=-]{12,})")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL)),
    ("generic_long_secret", re.compile(r"\b[A-Za-z0-9_\-]{32,}\.[A-Za-z0-9_\-]{16,}\.[A-Za-z0-9_\-]{16,}\b")),
)


def redact_text(value: str) -> str:
    """Replace likely secrets with stable placeholders."""
    redacted = value
    for name, pattern in REDACTION_PATTERNS:
        if name == "authorization_header":
            redacted = pattern.sub(r"\1[REDACTED_AUTHORIZATION]", redacted)
        elif name in {"password_assignment", "token_assignment"}:
            redacted = pattern.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", redacted)
        elif name == "cookie_secret":
            redacted = pattern.sub(lambda match: f"{match.group(1)}{match.group(2) or ''}=[REDACTED_COOKIE]", redacted)
        else:
            redacted = pattern.sub(f"[REDACTED_{name.upper()}]", redacted)
    return redacted


def redact_mapping(items: Iterable[dict]) -> list[dict]:
    """Redact every string value inside shallow dictionaries."""
    cleaned: list[dict] = []
    for item in items:
        cleaned.append({key: redact_text(value) if isinstance(value, str) else value for key, value in item.items()})
    return cleaned
