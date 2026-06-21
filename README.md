# DRAGON Report Generator
🤖 DRAGON REPO turns a bug bounty commands into a ready-to-use reports.

tired of making reports? 
dragonrepo tracks commands during an active engagement, categorizes common security tools, imports evidence (such as screenshots), redacts sensitive data (like apikeys, passwords etc), and generates professional reports in:

- HTML
- Markdown
- JSON

<img width="936" height="317" alt="ChatGPT Image Jun 4, 2026, 02_51_56 PM" src="https://github.com/user-attachments/assets/86ffcb5f-131b-421c-a994-99e0f6547dd0" />
CONTACT-->INTAGRAM @12HRFORMAT

## Install

From the project folder:
```bash
git clone https://github.com/12hrformat/dragonrepo.git
cd dragonrepo
mkdir assets reports
sudo bash install.sh
```

After installation, run it from anywhere:

```bash
dragonrepo
```

## Quick Start

Create or activate a project:

```bash
dragonrepo start (your project name)
```

Enable command tracking in your current terminal
Run this command to hook your current terminal- if you want multiple terminals run this command on all of them

```bash
eval "$(dragonrepo hook zsh)"
```

Run your normal tools:

```bash
nmap -sV 10.10.10.5
ffuf -u http://10.10.10.5/FUZZ -w /usr/share/wordlists/dirb/common.txt
```

Check what is being tracked:

```bash
dragonrepo status
```

Generate the report:

```bash
dragonrepo generate
```

Open the HTML report:

```bash
dragonrepo open-report
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
If you forget what to do, run:

```bash
dragonrepo
```

## Commands

### `dragonrepo start <project>`

Creates or resumes a project and makes it the active tracking session.

Example:

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

### `dragonrepo generate`

Generates HTML, Markdown, and JSON reports for the active project.

```bash
dragonrepo generate
```

You can also generate for a specific project:

```bash
dragonrepo generate acme-corp
```

### `dragonrepo open-report`

Opens the active project's HTML report.

```bash
dragonrepo open-report
```

For a specific project:

```bash
dragonrepo open-report acme-corp
```

### `dragonrepo where`

Shows where project files, evidence, screenshots, and reports are stored.

```bash
dragonrepo where
```

### `dragonrepo list`

Lists all projects.

```bash
dragonrepo list
```

### `dragonrepo dashboard`

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

Deletes a project.

```bash
dragonrepo delete old-project
```

## Shell Hooks

You must enable the shell hook in each terminal you want tracked.

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

To make tracking easier, add the hook command to your shell config.

For Zsh:

```bash
echo 'eval "$(dragonrepo hook zsh)"' >> ~/.zshrc
```

## Project Folders

Projects are stored in:

```text
~/.dragonrepo/projects/<project>/
```

Each project contains:

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

Reports are saved in:

```text
~/.dragonrepo/projects/<project>/reports/
```

Example:

```text
~/.dragonrepo/projects/test-lab/reports/report.html
```

## Evidence

Drop evidence files into:

```text
~/.dragonrepo/projects/<project>/notes/
~/.dragonrepo/projects/<project>/screenshots/
~/.dragonrepo/projects/<project>/scans/
~/.dragonrepo/projects/<project>/evidence/
```

Supported file types:

```text
.xml .json .txt .csv .png .jpg .jpeg
```

Then regenerate:

```bash
dragonrepo generate
```

## Recognized Tools

DRAGON automatically categorizes common tools such as:

- `nmap`
- `rustscan`
- `masscan`
- `ffuf`
- `gobuster`
- `feroxbuster`
- `dirsearch`
- `nuclei`
- `httpx`
- `katana`
- `amass`
- `subfinder`
- `nikto`
- `sqlmap`
- `hydra`
- `smbclient`
- `enum4linux`
- `ldapsearch`

## Sensitive Data Protection

Before reports are generated, DRAGON attempts to redact:

- API keys
- Tokens
- Passwords
- Authorization headers
- Bearer tokens
- Secrets
- Session cookies

Always review reports before sending them to a client.

## Troubleshooting

### Report says `0 commands tracked`

Check the active project:

```bash
dragonrepo status
```

If you tracked commands in `test-lab`, generate that project:

```bash
dragonrepo generate test-lab
```

### Commands are not being tracked

Run the hook again:

```bash
eval "$(dragonrepo hook zsh)"
```

Then run a command and check:

```bash
dragonrepo status
```

### You cannot `cd` into `report.html`

`report.html` is a file, not a directory.

Use:

```bash
dragonrepo open-report
```

Or:

```bash
xdg-open ~/.dragonrepo/projects/<project>/reports/report.html
```

## License
Open source friendly. Review and adapt for your own security workflow.
