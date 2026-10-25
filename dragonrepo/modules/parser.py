"""Command parsing and security workflow categorization."""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path


SECURITY_TOOLS: dict[str, tuple[str, str]] = {
    "nmap": ("Enumeration", "Port scan"),
    "rustscan": ("Enumeration", "Fast port scan"),
    "masscan": ("Enumeration", "Mass port scan"),
    "ffuf": ("Content Discovery", "Directory discovery"),
    "gobuster": ("Content Discovery", "Directory discovery"),
    "feroxbuster": ("Content Discovery", "Directory discovery"),
    "dirsearch": ("Content Discovery", "Directory discovery"),
    "nuclei": ("Vulnerability Assessment", "Template vulnerability scan"),
    "httpx": ("Web Testing", "HTTP probing"),
    "katana": ("Reconnaissance", "Web crawling"),
    "amass": ("Reconnaissance", "Subdomain enumeration"),
    "subfinder": ("Reconnaissance", "Subdomain enumeration"),
    "nikto": ("Web Testing", "Web server assessment"),
    "sqlmap": ("Exploitation", "SQL injection testing"),
    "hydra": ("Authentication Testing", "Credential attack"),
    "smbclient": ("Enumeration", "SMB enumeration"),
    "enum4linux": ("Enumeration", "Windows/Samba enumeration"),
    "ldapsearch": ("Enumeration", "LDAP enumeration"),
    "whoami": ("Post-Exploitation", "Identity validation"),
    "id": ("Post-Exploitation", "Identity validation"),
    "hostname": ("Post-Exploitation", "Host context"),
    "ip": ("Reconnaissance", "Network context"),
    "ifconfig": ("Reconnaissance", "Network context"),
    "curl": ("Web Testing", "HTTP request"),
    "wget": ("Web Testing", "HTTP download"),
    "nc": ("Exploitation", "Network interaction"),
    "netcat": ("Exploitation", "Network interaction"),
    "python": ("Exploitation", "Script execution"),
    "python3": ("Exploitation", "Script execution"),
    "bash": ("Exploitation", "Shell execution"),
    "sh": ("Exploitation", "Shell execution"),
    "scp": ("Evidence Collection", "File transfer"),
    "cp": ("Evidence Collection", "File collection"),
}

NOISE_COMMANDS: frozenset[str] = frozenset(
    {
        "clear",
        "reset",
        "cls",
        "fastfetch",
        "neofetch",
        "screenfetch",
        "paleofetch",
        "pfetch",
        "ufetch",
        "macchina",
        "archey",
        "archey3",
        "nitch",
        "cd",
        "pwd",
        "ls",
        "ll",
        "la",
        "exit",
        "logout",
        "history",
        "alias",
        "unalias",
        "jobs",
        "fg",
        "bg",
        "wait",
        "help",
        "source",
        "which",
        "type",
        "whereis",
        "man",
        "less",
        "more",
        "most",
        "vi",
        "vim",
        "nvim",
        "nano",
        "emacs",
        "micro",
        "hx",
    }
)

SHELL_OPERATORS: tuple[str, ...] = ("&&", "||", ";", "|")

KEYWORD_CATEGORIES: tuple[tuple[tuple[str, ...], str, str], ...] = (
    (("screenshot", "scrot", "gnome-screenshot", "import "), "Evidence Collection", "Screenshot capture"),
    (("subdomain", "dns", "zone-transfer"), "Reconnaissance", "DNS reconnaissance"),
    (("login", "password", "passwd", "credential"), "Authentication Testing", "Credential testing"),
    (("exploit", "payload", "reverse shell", "meterpreter"), "Exploitation", "Exploit validation"),
    (("linpeas", "winpeas", "privesc"), "Post-Exploitation", "Privilege escalation checks"),
)


@dataclass(frozen=True)
class ParsedCommand:
    command: str
    executable: str
    arguments: list[str]
    category: str
    activity: str


def parse_command(raw_command: str) -> ParsedCommand:
    """Parse a shell command into normalized report metadata."""
    command = raw_command.strip()
    if not command:
        return ParsedCommand(command="", executable="", arguments=[], category="Uncategorized", activity="Empty command")

    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()

    executable = Path(parts[0]).name if parts else ""
    category, activity = SECURITY_TOOLS.get(executable, ("Uncategorized", "Command execution"))

    lowered = command.lower()
    if category == "Uncategorized":
        for keywords, found_category, found_activity in KEYWORD_CATEGORIES:
            if any(keyword in lowered for keyword in keywords):
                category, activity = found_category, found_activity
                break

    return ParsedCommand(
        command=command,
        executable=executable,
        arguments=parts[1:],
        category=category,
        activity=activity,
    )


def is_noise_command(raw_command: str) -> bool:
    """Return True for shell noise that should never appear in a report.

    A command is noise when its executable is in NOISE_COMMANDS. Compound
    commands such as ``cd /tmp && nmap ...`` still count as real activity, so
    they are kept.
    """
    command = raw_command.strip()
    if not command:
        return True
    if any(operator in command for operator in SHELL_OPERATORS):
        return False
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()
    executable = Path(parts[0]).name if parts else ""
    return executable in NOISE_COMMANDS


def known_tool_names() -> list[str]:
    """Return supported security tools for UI display."""
    return sorted(SECURITY_TOOLS)
