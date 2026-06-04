"""Chronological engagement timeline reconstruction."""

from __future__ import annotations

from datetime import datetime


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def display_time(value: str) -> str:
    return _parse_time(value).astimezone().strftime("%H:%M")


def build_timeline(commands: list[dict], events: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for event in events:
        rows.append(
            {
                "timestamp": event["timestamp"],
                "time": display_time(event["timestamp"]),
                "title": event["title"],
                "category": event["event_type"].title(),
                "details": event.get("details", ""),
            }
        )
    for command in commands:
        rows.append(
            {
                "timestamp": command["timestamp"],
                "time": display_time(command["timestamp"]),
                "title": command["activity"],
                "category": command["category"],
                "details": command["command"],
            }
        )
    return sorted(rows, key=lambda row: row["timestamp"])
