# DRAGON Report Generator

DRAGON Report Generator turns security-assessment workflow activity into ready-to-use reports.

Tired of making reports manually?

DRAGON tracks commands during an active engagement, categorizes common security tools, imports evidence such as screenshots and scan output, redacts sensitive data, and generates professional reports in HTML, Markdown, and JSON.

<img width="936" height="317" alt="DRAGON Report Generator" src="https://github.com/user-attachments/assets/86ffcb5f-131b-421c-a994-99e0f6547dd0" />

## Features

* Command tracking for active projects, scoped to the terminal you enable it in
* Automatic filtering of shell noise (`clear`, `fastfetch`, `cd`, `ls`, pagers, editors, and more)
* Security-tool categorization
* Evidence collection and sensitive-data redaction
* HTML, Markdown, and JSON reports, plus optional PDF export
* Project-based storage with a terminal dashboard
* Zsh, Bash, and Fish shell hooks

## Requirements

* Python 3.9 or newer
* Linux, macOS, or another Unix-like environment for shell-hook functionality

## Installation

All methods end with the same `dragonrepo` CLI on your `PATH`.

**From PyPI (recommended):**

```bash
python3 -m pip install dragonrepo
```

**From source (system-wide install script):**

```bash
git clone https://github.com/12hrformat/dragonrepo.git
cd dragonrepo
chmod +x install.sh
sudo ./install.sh
```

The script installs the package into an isolated virtual environment at `/opt/dragonrepo/.venv` and links the `dragonrepo` launcher into `/usr/local/bin`. It requires `sudo`, Python 3.9 or newer, and leaves your system Python untouched. Re-run it any time to update.

If you prefer not to install system-wide, install the package directly instead (it still exposes the same `dragonrepo` command):

```bash
cd dragonrepo
python3 -m pip install .
```

**From a built wheel:**

```bash
git clone https://github.com/12hrformat/dragonrepo.git
cd dragonrepo
python3 -m pip install --upgrade build
python3 -m build
python3 -m pip install dist/dragonrepo-*.whl
```

Verify:

```bash
dragonrepo --help
dragonrepo doctor
```

## Quick Start

```bash
dragonrepo start test-lab          # create or resume a project
eval "$(dragonrepo hook zsh)"      # enable tracking in THIS terminal (bash/fish below)
nmap -sV 10.10.10.5                # work normally
dragonrepo status                  # active project and command count
dragonrepo generate                # build HTML, Markdown, and JSON reports
dragonrepo open-report             # open the HTML report
```

Run `dragonrepo` with no arguments for the same workflow as an on-screen guide.

## Shell Hooks

DRAGON tracks commands **per terminal**. The hook only enables recording for the terminal where you run it — every other terminal keeps working normally and is *not* logged. When tracking is enabled, the shell prints a short reminder so it is always clear which terminal is being recorded.

**Zsh:**

```bash
eval "$(dragonrepo hook zsh)"
```

**Bash:**

```bash
eval "$(dragonrepo hook bash)"
```

**Fish:**

```bash
dragonrepo hook fish
```

To enable it automatically, add the matching line to your shell rc file, for example:

```bash
echo 'eval "$(dragonrepo hook zsh)"' >> ~/.zshrc
```

Only use command tracking for systems and engagements you are authorized to assess.

## Noise Filtering

Not every command belongs in a report. DRAGON automatically skips shell noise so your timeline stays focused on real assessment activity:

* Terminal control: `clear`, `reset`, `cls`
* System-info splashes: `fastfetch`, `neofetch`, `screenfetch`, `pfetch`, `archey`, and similar
* Navigation and builtins: `cd`, `pwd`, `ls`, `ll`, `la`, `exit`, `history`, `alias`, `jobs`, `fg`, `bg`, `source`, `which`, `type`
* Pagers: `man`, `less`, `more`, `most`
* Editors: `vi`, `vim`, `nvim`, `nano`, `emacs`, `micro`, `hx`
* DRAGON's own commands (for example `dragonrepo status`)

Compound commands are always kept, because they may contain real activity:

```bash
cd /tmp && nmap -sV 10.10.10.5
```

The list lives in `dragonrepo/modules/parser.py` (`NOISE_COMMANDS`) if you want to extend it.

## Commands

| Command | Description |
| --- | --- |
| `dragonrepo start <project>` | Create or resume a project and make it active. |
| `dragonrepo stop` | Stop the active tracking session. |
| `dragonrepo status` | Show the active project, start time, and command count. |
| `dragonrepo list` | List known projects. |
| `dragonrepo generate [project]` | Generate HTML, Markdown, and JSON reports. |
| `dragonrepo open-report [project]` | Open the HTML report, generating it first if needed. |
| `dragonrepo pdf [project]` | Export the HTML report to PDF (`wkhtmltopdf` or WeasyPrint). |
| `dragonrepo where [project]` | Show project files, evidence, and report locations. |
| `dragonrepo dashboard [project]` | Show activity categories and command frequency. |
| `dragonrepo tools` | Show recognized security tools. |
| `dragonrepo delete <project>` | Delete a project and its local data. |
| `dragonrepo doctor` | Check local directories and launcher state. |
| `dragonrepo guide` | Display the basic workflow. |
| `dragonrepo hook <shell>` | Print shell integration code (`zsh`, `bash`, or `fish`). |

Commands that accept `[project]` default to the active project.

## Example Full Session

```bash
dragonrepo start htb-machine
eval "$(dragonrepo hook zsh)"

nmap -sV -oX scans/nmap.xml 10.10.10.5
subfinder -d example.com -o scans/subdomains.txt
ffuf -u http://10.10.10.5/FUZZ -w /usr/share/wordlists/dirb/common.txt

dragonrepo status
dragonrepo generate
dragonrepo open-report
```

## Project Storage

Project data lives in `~/.dragonrepo/projects/<project>/`:

```text
commands.log
notes/  screenshots/  scans/  evidence/  reports/
config.json
dragonrepo.sqlite3
```

Drop evidence files (`.xml`, `.json`, `.txt`, `.csv`, `.png`, `.jpg`, `.jpeg`) into the matching subdirectory, then run `dragonrepo generate` to include them. Reports are written to `reports/` as `report.html`, `report.md`, and `report.json`.

## Recognized Tools

DRAGON automatically categorizes common security tools, including `nmap`, `rustscan`, `masscan`, `ffuf`, `gobuster`, `feroxbuster`, `dirsearch`, `nuclei`, `httpx`, `katana`, `amass`, `subfinder`, `nikto`, `sqlmap`, `hydra`, `smbclient`, `enum4linux`, and `ldapsearch`.

## Sensitive Data Protection

Before reports are generated, DRAGON attempts to redact sensitive information such as API keys, tokens, passwords, authorization headers, bearer tokens, secrets, and session cookies.

Redaction is a safety aid, not a replacement for manual review. Always review generated reports before sharing them externally.

## Development

Run the CLI directly from a cloned source tree without installing:

```bash
git clone https://github.com/12hrformat/dragonrepo.git
cd dragonrepo
python3 -m dragonrepo.cli --help
```

The package layout is a standard Python package (`dragonrepo/cli.py`, `dragonrepo/modules/`, and bundled Jinja templates in `dragonrepo/templates/`), exposed through the `dragonrepo.cli:app` entry point.

## Troubleshooting

* **`dragonrepo` is not found** — reinstall with `python3 -m pip install .` and verify with `dragonrepo --help`. If it installed to a user-local bin directory, add that directory to `PATH`.
* **Commands are not tracked** — enable the hook again with `eval "$(dragonrepo hook zsh)"` (or bash/fish), run a command, then check `dragonrepo status`.
* **Report generation fails** — confirm the active project exists (`dragonrepo status`) and regenerate with `dragonrepo generate`.
* **`report.html` cannot be opened** — it is a file, not a directory. Use `dragonrepo open-report` or open the file in a browser.

## License

MIT License.
