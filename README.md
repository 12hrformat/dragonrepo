# DRAGON Report Generator

DRAGON Report Generator turns security-assessment workflow activity into ready-to-use reports.

Tired of making reports manually?

DRAGON tracks commands during an active engagement, categorizes common security tools, imports evidence such as screenshots and scan output, redacts sensitive data, and generates professional reports in:

* HTML
* Markdown
* JSON

<img width="936" height="317" alt="DRAGON Report Generator" src="https://github.com/user-attachments/assets/86ffcb5f-131b-421c-a994-99e0f6547dd0" />

## Features

* Command tracking for active projects
* Security-tool categorization
* Evidence collection
* Sensitive-data redaction
* HTML, Markdown, and JSON report generation
* Project-based engagement storage
* Terminal dashboard and statistics
* Zsh, Bash, and Fish shell hooks
* Optional PDF export when a supported PDF engine is installed

## Requirements

* Python 3.9 or newer
* Linux, macOS, or another Unix-like environment for shell-hook functionality
* Git for cloning the repository

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/12hrformat/dragonrepo.git
cd dragonrepo
```

Install DRAGON as a Python package:

```bash
python3 -m pip install .
```

After installation, verify the CLI:

```bash
dragonrepo --help
```

You can also verify the installation:

```bash
dragonrepo doctor
```

### Installing from a built wheel

To build the distributable package:

```bash
python3 -m pip install --upgrade build
python3 -m build
```

The build produces a wheel and source archive in `dist/`.

Install the wheel with:

```bash
python3 -m pip install dist/dragonrepo-1.0.0-py3-none-any.whl
```

## Quick Start

Create or activate a project:

```bash
dragonrepo start test-lab
```

Enable command tracking in your current terminal.

For Zsh:

```bash
eval "$(dragonrepo hook zsh)"
```

For Bash:

```bash
eval "$(dragonrepo hook bash)"
```

For Fish:

```bash
dragonrepo hook fish
```

Run your normal security-assessment tools during an authorized engagement.

For example:

```bash
nmap -sV 10.10.10.5
ffuf -u http://10.10.10.5/FUZZ -w /usr/share/wordlists/dirb/common.txt
```

Check the active project:

```bash
dragonrepo status
```

Generate the reports:

```bash
dragonrepo generate
```

The generated files are:

```text
report.html
report.md
report.json
```

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

If you forget the basic workflow:

```bash
dragonrepo
```

## Commands

### `dragonrepo start <project>`

Creates or resumes a project and makes it the active tracking session.

```bash
dragonrepo start acme-corp
```

### `dragonrepo stop`

Stops the active tracking session.

```bash
dragonrepo stop
```

### `dragonrepo status`

Shows the active project, start time, command count, and project directory.

```bash
dragonrepo status
```

### `dragonrepo list`

Lists known projects.

```bash
dragonrepo list
```

### `dragonrepo generate [project]`

Generates HTML, Markdown, and JSON reports.

For the active project:

```bash
dragonrepo generate
```

For a specific project:

```bash
dragonrepo generate acme-corp
```

### `dragonrepo open-report [project]`

Opens the project's HTML report using an available desktop opener.

```bash
dragonrepo open-report
```

For a specific project:

```bash
dragonrepo open-report acme-corp
```

### `dragonrepo pdf [project]`

Exports the generated HTML report to PDF when a supported PDF engine is available.

```bash
dragonrepo pdf
```

Supported PDF engines currently include `wkhtmltopdf` and WeasyPrint.

### `dragonrepo where [project]`

Shows project files, evidence, screenshots, scans, and report locations.

```bash
dragonrepo where
```

### `dragonrepo dashboard [project]`

Shows activity categories and command frequency.

```bash
dragonrepo dashboard
```

### `dragonrepo tools`

Shows recognized security tools.

```bash
dragonrepo tools
```

### `dragonrepo delete <project>`

Deletes a project and its local report data.

```bash
dragonrepo delete old-project
```

### `dragonrepo doctor`

Checks local DRAGON directories and launcher state.

```bash
dragonrepo doctor
```

### `dragonrepo guide`

Displays the basic DRAGON workflow.

```bash
dragonrepo guide
```

### `dragonrepo hook <shell>`

Prints shell integration code for command tracking.

```bash
dragonrepo hook zsh
dragonrepo hook bash
dragonrepo hook fish
```

## Shell Hooks

Enable the shell hook in every terminal you want tracked.

### Zsh

```bash
eval "$(dragonrepo hook zsh)"
```

To enable it automatically:

```bash
echo 'eval "$(dragonrepo hook zsh)"' >> ~/.zshrc
```

### Bash

```bash
eval "$(dragonrepo hook bash)"
```

### Fish

```bash
dragonrepo hook fish
```

Only use command tracking for systems and engagements you are authorized to assess.

## Project Storage

DRAGON stores project data in the user's home directory:

```text
~/.dragonrepo/projects/<project>/
```

Example:

```text
~/.dragonrepo/projects/test-lab/
```

A project may contain:

```text
commands.log
notes/
screenshots/
scans/
evidence/
reports/
config.json
dragonrepo.sqlite3
```

Reports are stored in:

```text
~/.dragonrepo/projects/<project>/reports/
```

For example:

```text
~/.dragonrepo/projects/test-lab/reports/report.html
~/.dragonrepo/projects/test-lab/reports/report.md
~/.dragonrepo/projects/test-lab/reports/report.json
```

## Evidence

Place evidence files in the appropriate project directory:

```text
~/.dragonrepo/projects/<project>/notes/
~/.dragonrepo/projects/<project>/screenshots/
~/.dragonrepo/projects/<project>/scans/
~/.dragonrepo/projects/<project>/evidence/
```

Supported evidence file types include:

```text
.xml
.json
.txt
.csv
.png
.jpg
.jpeg
```

After adding or changing evidence, regenerate the reports:

```bash
dragonrepo generate
```

## Recognized Tools

DRAGON automatically categorizes common security tools such as:

* `nmap`
* `rustscan`
* `masscan`
* `ffuf`
* `gobuster`
* `feroxbuster`
* `dirsearch`
* `nuclei`
* `httpx`
* `katana`
* `amass`
* `subfinder`
* `nikto`
* `sqlmap`
* `hydra`
* `smbclient`
* `enum4linux`
* `ldapsearch`

## Sensitive Data Protection

Before reports are generated, DRAGON attempts to redact sensitive information such as:

* API keys
* Tokens
* Passwords
* Authorization headers
* Bearer tokens
* Secrets
* Session cookies

Always review generated reports before sharing them externally.

Redaction is a safety aid and should not replace manual review.

## Project Structure

The source repository uses a standard Python package layout:

```text
dragonrepo/
├── pyproject.toml
├── README.md
├── LICENSE
├── requirements.txt
└── dragonrepo/
    ├── __init__.py
    ├── cli.py
    ├── modules/
    │   ├── __init__.py
    │   ├── evidence.py
    │   ├── parser.py
    │   ├── redactor.py
    │   ├── reporter.py
    │   ├── timeline.py
    │   └── tracker.py
    └── templates/
        ├── report.html.j2
        └── report.md.j2
```

The CLI is exposed through the package entry point:

```text
dragonrepo.cli:app
```

The Jinja templates are bundled inside the Python package so report generation works after installation.

## Development

Build the package locally:

```bash
python3 -m pip install --upgrade build
python3 -m build
```

Run the CLI directly from the source tree:

```bash
python3 -m dragonrepo.cli --help
```

For a clean package test:

```bash
python3 -m pip install dist/dragonrepo-1.0.0-py3-none-any.whl
dragonrepo --help
```

Then test the main workflow:

```bash
dragonrepo start packaging-test
dragonrepo status
dragonrepo generate
```

## Troubleshooting

### `dragonrepo` is not found

Make sure the package was installed successfully:

```bash
python3 -m pip install .
```

Then verify:

```bash
dragonrepo --help
```

If the executable was installed into a user-local directory that is not on `PATH`, add that directory to your shell's `PATH`.

### Report generation fails

Check that the active project exists:

```bash
dragonrepo status
```

Then regenerate:

```bash
dragonrepo generate
```

### Commands are not being tracked

Enable the appropriate shell hook again.

For Zsh:

```bash
eval "$(dragonrepo hook zsh)"
```

For Bash:

```bash
eval "$(dragonrepo hook bash)"
```

For Fish:

```bash
dragonrepo hook fish
```

Then run a command and check:

```bash
dragonrepo status
```

### `report.html` cannot be opened

`report.html` is a file, not a directory.

Use:

```bash
dragonrepo open-report
```

or open the generated HTML file manually in a browser.

## License

MIT License.
