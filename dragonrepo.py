#!/usr/bin/env python3
"""DRAGON Report Generator CLI."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from modules.parser import known_tool_names
from modules.reporter import render_reports
from modules.tracker import (
    ACTIVE_SESSION,
    PROJECTS_DIR,
    create_project,
    delete_project as resolve_delete_project,
    fetch_commands,
    get_active_session,
    list_projects,
    normalize_project_name,
    project_path,
    record_command,
    setup_logging,
    start_session,
    stop_session,
)


app = typer.Typer(
    name="dragonrepo",
    help="DRAGON Report Generator: turn pentest workflow activity into professional reports.",
    no_args_is_help=False,
    rich_markup_mode="rich",
)
console = Console()


BANNER = r"""
 ____  ____      _    ____  ___  _   _
|  _ \|  _ \    / \  / ___|/ _ \| \ | |
| | | | |_) |  / _ \| |  _| | | |  \| |
| |_| |  _ <  / ___ \ |_| | |_| | |\  |
|____/|_| \_\/_/   \_\____|\___/|_| \_|
       REPORT GENERATOR | dragonrepo
"""


def print_banner() -> None:
    console.print(
        Panel.fit(
            f"[bold red]{BANNER}[/bold red]\n"
            "[white]Track commands. Collect evidence. Generate clean security reports.[/white]",
            border_style="red",
        )
    )


def active_project_name() -> str | None:
    active = get_active_session()
    return active.get("project") if active else None


def choose_project(project: str | None) -> str:
    selected = normalize_project_name(project) if project else active_project_name()
    if not selected:
        console.print("[yellow]No project selected and no active session.[/yellow]")
        console.print("Start one with: [bold]dragonrepo start my-project[/bold]")
        raise typer.Exit(code=1)
    if not project_path(selected).exists():
        console.print(f"[red]Project not found:[/red] {selected}")
        raise typer.Exit(code=1)
    return selected


def print_quickstart() -> None:
    print_banner()
    table = Table(title="Simple Workflow")
    table.add_column("Step", style="bold red", justify="right")
    table.add_column("Command", style="bold")
    table.add_column("What it does")
    table.add_row("1", "dragonrepo start test-lab", "Creates a project and makes it active.")
    table.add_row("2", 'eval "$(dragonrepo hook zsh)"', "Turns on live command tracking for this terminal.")
    table.add_row("3", "nmap -sV 10.10.10.5", "Work normally. DRAGON records useful commands.")
    table.add_row("4", "dragonrepo status", "Shows the active project and command count.")
    table.add_row("5", "dragonrepo generate", "Builds HTML, Markdown, and JSON for the active project.")
    table.add_row("6", "dragonrepo open-report", "Opens the HTML report.")
    console.print(table)
    console.print(
        Panel(
            "[bold]Important:[/bold] run the hook command once in each new terminal you want tracked.\n"
            "Reports live in [bold]~/.dragonrepo/projects/<project>/reports/[/bold].",
            title="Tip",
            border_style="cyan",
        )
    )


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    setup_logging()
    if ctx.invoked_subcommand is None:
        print_quickstart()


@app.command()
def start(project: str = typer.Argument(..., help="Project name, e.g. acme-corp")) -> None:
    """Create or resume a project and activate command tracking."""
    previous = active_project_name()
    root = start_session(project)
    name = normalize_project_name(project)
    switch_note = f"\nPrevious active project: {previous}" if previous and previous != name else ""
    console.print(
        Panel(
            f"[bold green]Tracking active[/bold green]\n"
            f"Project: [bold]{name}[/bold]{switch_note}\n"
            f"Path: {root}",
            title="DRAGON Session",
            border_style="green",
        )
    )
    console.print("Next: [bold]eval \"$(dragonrepo hook zsh)\"[/bold], then run your normal tools.")


@app.command()
def stop() -> None:
    """Stop the active tracking session."""
    project = stop_session()
    if not project:
        console.print("[yellow]No active DRAGON session.[/yellow]")
        raise typer.Exit(code=1)
    console.print(f"[green]Stopped tracking project:[/green] {project}")


@app.command()
def status() -> None:
    """Show active project and engagement statistics."""
    active = get_active_session()
    if not active:
        console.print(Panel("[yellow]No active session.[/yellow]", title="DRAGON Status", border_style="yellow"))
        return
    project = active["project"]
    commands = fetch_commands(project)
    table = Table(title="Active DRAGON Session")
    table.add_column("Field", style="bold red")
    table.add_column("Value")
    table.add_row("Project", project)
    table.add_row("Started", active.get("started_at", "unknown"))
    table.add_row("Commands", str(len(commands)))
    table.add_row("Directory", str(project_path(project)))
    console.print(table)


@app.command("list")
def list_cmd() -> None:
    """List known projects."""
    projects = list_projects()
    if not projects:
        console.print("[yellow]No projects found.[/yellow]")
        return
    table = Table(title="DRAGON Projects")
    table.add_column("Project", style="bold")
    table.add_column("Commands")
    table.add_column("Path")
    for root in projects:
        try:
            commands = fetch_commands(root.name)
        except Exception:
            commands = []
        table.add_row(root.name, str(len(commands)), str(root))
    console.print(table)


@app.command()
def delete(project: str, yes: bool = typer.Option(False, "--yes", "-y", help="Delete without confirmation.")) -> None:
    """Delete a project directory and its local report data."""
    root = resolve_delete_project(project)
    if not yes and not typer.confirm(f"Delete {root}? This cannot be undone."):
        console.print("[yellow]Delete cancelled.[/yellow]")
        return
    shutil.rmtree(root)
    console.print(f"[green]Deleted project:[/green] {root.name}")


@app.command()
def generate(project: Optional[str] = typer.Argument(None, help="Project name; defaults to active project.")) -> None:
    """Generate HTML, Markdown, and JSON reports. Defaults to the active project."""
    name = choose_project(project)
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Collecting evidence, redacting secrets, and rendering reports...", total=None)
        outputs = render_reports(name)
    table = Table(title="Generated Reports")
    table.add_column("Format", style="bold red")
    table.add_column("Path")
    for fmt, path in outputs.items():
        table.add_row(fmt.upper(), str(path))
    console.print(table)
    console.print("Open it with: [bold]dragonrepo open-report[/bold]")


@app.command()
def pdf(project: Optional[str] = typer.Argument(None, help="Project name; defaults to active project.")) -> None:
    """Export a generated HTML report to PDF when a PDF engine is available."""
    name = choose_project(project)
    outputs = render_reports(name)
    html_path = outputs["html"]
    pdf_path = html_path.with_suffix(".pdf")

    wkhtmltopdf = shutil.which("wkhtmltopdf")
    if wkhtmltopdf:
        subprocess.run([wkhtmltopdf, str(html_path), str(pdf_path)], check=True)
        console.print(f"[green]PDF generated:[/green] {pdf_path}")
        return

    try:
        from weasyprint import HTML  # type: ignore
    except Exception:
        console.print("[yellow]PDF engine not found.[/yellow] Install wkhtmltopdf or add weasyprint to the environment, then rerun this command.")
        raise typer.Exit(code=1)

    HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    console.print(f"[green]PDF generated:[/green] {pdf_path}")


@app.command("open-report")
def open_report(project: Optional[str] = typer.Argument(None, help="Project name; defaults to active project.")) -> None:
    """Open the HTML report for a project, generating it first if needed."""
    name = choose_project(project)
    html_path = project_path(name) / "reports" / "report.html"
    if not html_path.exists():
        console.print("[yellow]No HTML report found yet. Generating one now...[/yellow]")
        render_reports(name)

    console.print(f"[green]HTML report:[/green] {html_path}")
    if shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", str(html_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif shutil.which("gio"):
        subprocess.Popen(["gio", "open", str(html_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        console.print("[yellow]No desktop opener found. Copy the path above into your browser.[/yellow]")


@app.command()
def guide() -> None:
    """Show the shortest way to use DRAGON."""
    print_quickstart()


@app.command("where")
def where_cmd(project: Optional[str] = typer.Argument(None, help="Project name; defaults to active project.")) -> None:
    """Show where project files and reports are stored."""
    name = choose_project(project)
    root = project_path(name)
    table = Table(title=f"Project Paths: {name}")
    table.add_column("Item", style="bold red")
    table.add_column("Path")
    table.add_row("Project", str(root))
    table.add_row("Commands", str(root / "commands.log"))
    table.add_row("Evidence", str(root / "evidence"))
    table.add_row("Screenshots", str(root / "screenshots"))
    table.add_row("Reports", str(root / "reports"))
    table.add_row("HTML", str(root / "reports" / "report.html"))
    console.print(table)


@app.command()
def dashboard(project: Optional[str] = typer.Argument(None, help="Project name; defaults to active project.")) -> None:
    """Show a terminal dashboard with project statistics."""
    selected = choose_project(project)
    commands = fetch_commands(selected)
    by_category: dict[str, int] = {}
    by_tool: dict[str, int] = {}
    for command in commands:
        by_category[command["category"]] = by_category.get(command["category"], 0) + 1
        if command["executable"]:
            by_tool[command["executable"]] = by_tool.get(command["executable"], 0) + 1

    console.print(Panel(f"[bold]{selected}[/bold]\nCommands tracked: {len(commands)}\nPath: {project_path(selected)}", title="DRAGON Dashboard", border_style="red"))
    cat_table = Table(title="Activity Categories")
    cat_table.add_column("Category")
    cat_table.add_column("Count", justify="right")
    for category, count in sorted(by_category.items(), key=lambda item: item[0]):
        cat_table.add_row(category, str(count))
    console.print(cat_table)

    tool_table = Table(title="Command Frequency")
    tool_table.add_column("Tool")
    tool_table.add_column("Count", justify="right")
    for tool, count in sorted(by_tool.items(), key=lambda item: item[1], reverse=True)[:15]:
        tool_table.add_row(tool, str(count))
    console.print(tool_table)


@app.command()
def tools() -> None:
    """Show recognized security tools."""
    table = Table(title="Recognized Security Tools")
    table.add_column("Tool")
    for tool in known_tool_names():
        table.add_row(tool)
    console.print(table)


@app.command(hidden=True)
def record(command: str = typer.Argument(..., help="Command line to record.")) -> None:
    """Record a command for shell integrations."""
    recorded = record_command(command)
    raise typer.Exit(code=0 if recorded else 0)


@app.command()
def hook(shell: str = typer.Argument("zsh", help="zsh, bash, or fish")) -> None:
    """Print shell integration code for live command tracking."""
    shell = shell.lower()
    if shell == "zsh":
        console.print(
            r'''
dragonrepo_preexec() {
  emulate -L zsh
  local cmd="$1"
  [[ "$cmd" == dragonrepo\ record* ]] && return
  command dragonrepo record "$cmd" >/dev/null 2>&1
}
autoload -Uz add-zsh-hook
add-zsh-hook preexec dragonrepo_preexec
'''.strip()
        )
    elif shell == "bash":
        console.print(
            r'''
dragonrepo_record_command() {
  local cmd="$(history 1 | sed 's/^ *[0-9]\+ *//')"
  [[ "$cmd" == dragonrepo\ record* ]] && return
  command dragonrepo record "$cmd" >/dev/null 2>&1
}
PROMPT_COMMAND="dragonrepo_record_command${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
'''.strip()
        )
    elif shell == "fish":
        console.print(
            r'''
function dragonrepo_record_command --on-event fish_preexec
    command dragonrepo record "$argv" >/dev/null 2>&1
end
'''.strip()
        )
    else:
        console.print("[red]Unsupported shell. Use zsh, bash, or fish.[/red]")
        raise typer.Exit(code=1)


@app.command()
def doctor() -> None:
    """Check local DRAGON directories and launcher state."""
    create_project("_doctor")
    doctor_project = PROJECTS_DIR / "_doctor"
    if doctor_project.exists():
        shutil.rmtree(doctor_project)
    table = Table(title="DRAGON Doctor")
    table.add_column("Check")
    table.add_column("Result")
    table.add_row("Home", str(PROJECTS_DIR.parent))
    table.add_row("Projects", "ok" if PROJECTS_DIR.exists() else "missing")
    table.add_row("Active session", str(ACTIVE_SESSION.exists()))
    table.add_row("Launcher", shutil.which("dragonrepo") or "not on PATH")
    console.print(table)


if __name__ == "__main__":
    app(prog_name="dragonrepo")
