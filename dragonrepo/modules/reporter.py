"""Report data modeling and rendering."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .evidence import collect_evidence
from .redactor import redact_mapping, redact_text
from .timeline import build_timeline
from .tracker import fetch_commands, fetch_events, fetch_evidence, load_config, project_path


REPORT_SECTIONS = [
    "Executive Summary",
    "Methodology",
    "Reconnaissance",
    "Enumeration",
    "Content Discovery",
    "Vulnerability Assessment",
    "Findings",
    "Evidence",
    "Timeline",
    "Recommendations",
    "Conclusion",
]


def _template_env() -> Environment:
    root = Path(__file__).resolve().parent.parent / "templates"
    return Environment(
        loader=FileSystemLoader(root),
        autoescape=select_autoescape(("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _group_commands(commands: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for command in commands:
        grouped[command["category"]].append(command)
    return dict(sorted(grouped.items()))


def _finding_summaries(commands: list[dict], evidence: list[dict]) -> list[dict]:
    findings: list[dict] = []
    counts = Counter(command["category"] for command in commands)
    if counts.get("Vulnerability Assessment") or any("nuclei" in command["command"] for command in commands):
        findings.append(
            {
                "severity": "Informational",
                "title": "Automated vulnerability assessment performed",
                "summary": "Automated assessment activity was observed. Review attached scan output for validated issues before client delivery.",
                "recommendation": "Validate scanner results manually, remove false positives, and assign severities based on business impact.",
            }
        )
    if counts.get("Authentication Testing"):
        findings.append(
            {
                "severity": "Medium",
                "title": "Authentication attack surface tested",
                "summary": "Authentication-focused testing commands were executed, indicating login or credential attack paths were assessed.",
                "recommendation": "Enforce MFA, rate limiting, lockout controls, and centralized monitoring for authentication endpoints.",
            }
        )
    if evidence:
        findings.append(
            {
                "severity": "Informational",
                "title": "Evidence artifacts collected",
                "summary": f"{len(evidence)} evidence artifact(s) were imported into this report package.",
                "recommendation": "Retain evidence securely and redact client-sensitive material before external distribution.",
            }
        )
    return findings


def build_report_context(project: str) -> dict:
    collect_evidence(project)
    config = load_config(project)
    commands = redact_mapping(fetch_commands(project))
    events = redact_mapping(fetch_events(project))
    evidence = redact_mapping(fetch_evidence(project))
    timeline = build_timeline(commands, events)
    grouped = _group_commands(commands)
    frequencies = Counter(command["executable"] for command in commands if command["executable"])
    categories = Counter(command["category"] for command in commands)
    findings = _finding_summaries(commands, evidence)
    now = datetime.now().astimezone()

    return {
        "project": project,
        "config": config,
        "generated_at": now.strftime("%Y-%m-%d %H:%M %Z"),
        "sections": REPORT_SECTIONS,
        "commands": commands,
        "events": events,
        "evidence": evidence,
        "timeline": timeline,
        "grouped_commands": grouped,
        "findings": findings,
        "stats": {
            "total_commands": len(commands),
            "total_evidence": len(evidence),
            "category_counts": dict(categories),
            "tool_frequency": dict(frequencies.most_common()),
        },
        "executive_summary": redact_text(
            f"DRAGON Report Generator reconstructed the {project} engagement from tracked operator activity, "
            f"including {len(commands)} command(s), {len(evidence)} evidence artifact(s), and "
            f"{len(grouped)} activity category/categories."
        ),
    }


def render_reports(project: str) -> dict[str, Path]:
    root = project_path(project)
    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    context = build_report_context(project)
    env = _template_env()

    outputs = {
        "html": reports_dir / "report.html",
        "markdown": reports_dir / "report.md",
        "json": reports_dir / "report.json",
    }
    outputs["html"].write_text(env.get_template("report.html.j2").render(**context), encoding="utf-8")
    outputs["markdown"].write_text(env.get_template("report.md.j2").render(**context), encoding="utf-8")
    outputs["json"].write_text(json.dumps(context, indent=2, default=str) + "\n", encoding="utf-8")
    return outputs
