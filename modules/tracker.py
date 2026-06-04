"""Project/session persistence for DRAGON Report Generator."""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .parser import parse_command
from .redactor import redact_text


APP_DIR = Path(os.environ.get("DRAGONREPO_HOME", Path.home() / ".dragonrepo"))
PROJECTS_DIR = APP_DIR / "projects"
ACTIVE_SESSION = APP_DIR / "active_session.json"
LOG_FILE = APP_DIR / "dragonrepo.log"

PROJECT_SUBDIRS = ("notes", "screenshots", "scans", "evidence", "reports")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def setup_logging() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def ensure_app_dirs() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def normalize_project_name(name: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in name.strip().lower())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    if not cleaned:
        raise ValueError("Project name cannot be empty.")
    return cleaned


def project_path(project: str) -> Path:
    return PROJECTS_DIR / normalize_project_name(project)


def db_path(project: str) -> Path:
    return project_path(project) / "dragonrepo.sqlite3"


@contextmanager
def connect(project: str) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path(project))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(project: str) -> None:
    with connect(project) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                command TEXT NOT NULL,
                executable TEXT NOT NULL,
                arguments TEXT NOT NULL,
                category TEXT NOT NULL,
                activity TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                title TEXT NOT NULL,
                details TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                path TEXT NOT NULL,
                kind TEXT NOT NULL,
                title TEXT NOT NULL,
                excerpt TEXT NOT NULL
            );
            """
        )


def create_project(project: str) -> Path:
    ensure_app_dirs()
    name = normalize_project_name(project)
    root = project_path(name)
    root.mkdir(parents=True, exist_ok=True)
    for subdir in PROJECT_SUBDIRS:
        (root / subdir).mkdir(exist_ok=True)
    (root / "commands.log").touch(exist_ok=True)
    config = root / "config.json"
    if not config.exists():
        config.write_text(
            json.dumps(
                {
                    "project": name,
                    "created_at": utc_now(),
                    "report_title": f"{name} Security Assessment",
                    "consultant": os.environ.get("USER", "DRAGON Operator"),
                    "scope": [],
                    "severity_model": "Informational/Low/Medium/High/Critical",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    init_db(name)
    add_event(name, "session", "Project initialized", f"Project directory created at {root}")
    return root


def start_session(project: str) -> Path:
    root = create_project(project)
    name = normalize_project_name(project)
    ACTIVE_SESSION.write_text(json.dumps({"project": name, "started_at": utc_now()}, indent=2) + "\n", encoding="utf-8")
    add_event(name, "session", "Started engagement", "Command tracking session activated.")
    return root


def stop_session() -> str | None:
    active = get_active_session()
    if not active:
        return None
    project = active["project"]
    add_event(project, "session", "Stopped engagement", "Command tracking session deactivated.")
    ACTIVE_SESSION.unlink(missing_ok=True)
    return project


def get_active_session() -> dict | None:
    if not ACTIVE_SESSION.exists():
        return None
    try:
        return json.loads(ACTIVE_SESSION.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logging.exception("Failed to parse active session")
        return None


def list_projects() -> list[Path]:
    ensure_app_dirs()
    return sorted(path for path in PROJECTS_DIR.iterdir() if path.is_dir())


def delete_project(project: str) -> Path:
    root = project_path(project)
    if not root.exists():
        raise FileNotFoundError(f"Project not found: {project}")
    active = get_active_session()
    if active and active.get("project") == normalize_project_name(project):
        ACTIVE_SESSION.unlink(missing_ok=True)
    return root


def add_event(project: str, event_type: str, title: str, details: str = "") -> None:
    init_db(project)
    with connect(project) as conn:
        conn.execute(
            "INSERT INTO events(timestamp, event_type, title, details) VALUES (?, ?, ?, ?)",
            (utc_now(), event_type, title, redact_text(details)),
        )


def record_command(raw_command: str, project: str | None = None) -> bool:
    active_project = project or (get_active_session() or {}).get("project")
    if not active_project:
        return False
    parsed = parse_command(raw_command)
    if not parsed.command:
        return False
    ignored_prefixes = ("dragonrepo record", "dragonrepo hook", "history", "fc -")
    if parsed.command.startswith(ignored_prefixes):
        return False

    init_db(active_project)
    command = redact_text(parsed.command)
    with connect(active_project) as conn:
        conn.execute(
            "INSERT INTO commands(timestamp, command, executable, arguments, category, activity) VALUES (?, ?, ?, ?, ?, ?)",
            (
                utc_now(),
                command,
                parsed.executable,
                json.dumps(parsed.arguments),
                parsed.category,
                parsed.activity,
            ),
        )
    with (project_path(active_project) / "commands.log").open("a", encoding="utf-8") as handle:
        handle.write(f"{utc_now()}\t{parsed.category}\t{command}\n")
    return True


def load_config(project: str) -> dict:
    config_path = project_path(project) / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Project configuration not found: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def fetch_commands(project: str) -> list[dict]:
    init_db(project)
    with connect(project) as conn:
        rows = conn.execute("SELECT * FROM commands ORDER BY timestamp ASC").fetchall()
    return [dict(row) for row in rows]


def fetch_events(project: str) -> list[dict]:
    init_db(project)
    with connect(project) as conn:
        rows = conn.execute("SELECT * FROM events ORDER BY timestamp ASC").fetchall()
    return [dict(row) for row in rows]


def fetch_evidence(project: str) -> list[dict]:
    init_db(project)
    with connect(project) as conn:
        rows = conn.execute("SELECT * FROM evidence ORDER BY timestamp ASC").fetchall()
    return [dict(row) for row in rows]


def store_evidence(project: str, items: list[dict]) -> None:
    init_db(project)
    with connect(project) as conn:
        conn.execute("DELETE FROM evidence")
        conn.executemany(
            "INSERT INTO evidence(timestamp, path, kind, title, excerpt) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    item["timestamp"],
                    item["path"],
                    item["kind"],
                    item["title"],
                    item["excerpt"],
                )
                for item in items
            ],
        )
