"""Evidence discovery and import."""

from __future__ import annotations

import base64
import mimetypes
from datetime import datetime, timezone
from pathlib import Path

from .redactor import redact_text
from .tracker import project_path, store_evidence


SUPPORTED_EXTENSIONS = {".xml", ".json", ".txt", ".csv", ".png", ".jpg", ".jpeg"}
TEXT_EXTENSIONS = {".xml", ".json", ".txt", ".csv"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def _timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def _text_excerpt(path: Path, max_chars: int = 2400) -> str:
    try:
        return redact_text(path.read_text(encoding="utf-8", errors="replace")[:max_chars])
    except OSError:
        return "[Unable to read evidence file]"


def _image_excerpt(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path)
    mime = mime or "application/octet-stream"
    try:
        data = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return ""
    return f"data:{mime};base64,{data}"


def collect_evidence(project: str) -> list[dict]:
    root = project_path(project)
    items: list[dict] = []
    for folder_name in ("notes", "screenshots", "scans", "evidence"):
        folder = root / folder_name
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            kind = "screenshot" if path.suffix.lower() in IMAGE_EXTENSIONS else "output"
            excerpt = _image_excerpt(path) if kind == "screenshot" else _text_excerpt(path)
            items.append(
                {
                    "timestamp": _timestamp(path),
                    "path": str(path.relative_to(root)),
                    "kind": kind,
                    "title": path.stem.replace("_", " ").replace("-", " ").title(),
                    "excerpt": excerpt,
                }
            )
    store_evidence(project, items)
    return items
