# 🧠 CLI Study Hub v5.0 — Slash-Command Study Companion

**CLI Study Hub** is a terminal-first, community-driven study notebook. Every
command is a `/slash-command` with a live, Claude-Code-style autocomplete menu
— start typing and matching commands pop up as you go. Notes live in this
GitHub repo, so anyone with push access gets automatic, hassle-free syncing.

---

## 🚀 Install (no manual dependency wrangling)

The recommended way to run CLI Study Hub is with [`pipx`](https://pipx.pypa.io)
or [`uvx`](https://docs.astral.sh/uv/guides/tools/), which install the app
into its own isolated environment and pull in every dependency for you —
there's nothing else to install by hand.

```bash
# one-time install, then just run `study-hub` any time
pipx install study-cli-hub

# or run it without installing anything permanently
uvx study-cli-hub
```

> 📦 **Not on PyPI yet?** Until the maintainer publishes the first release
> (see [Publishing a release](#-publishing-a-release-maintainers) below),
> install straight from this repo:
> ```bash
> pipx install "git+https://github.com/govindmehta15/study-cli-hub.git"
> ```

### Run it

Your notes are stored as files in this repo's `subjects/` folder, so clone
the repo first, `cd` into it, then launch the app from there:

```bash
git clone https://github.com/govindmehta15/study-cli-hub.git
cd study-cli-hub
study-hub
```

---

## ⌨️ Slash Commands & Autocomplete

Every command starts with `/`. As soon as you type `/`, a live menu of
matching commands (with a one-line description of each) appears and narrows
down as you keep typing — just like Claude Code's slash menu. Press `Tab` /
`Enter` to accept a suggestion.

### 🏠 Main menu

| Command                     | Action                                   |
| ---------------------------- | ---------------------------------------- |
| `/study <name\|number>`      | Open a subject                           |
| `/create-subject`            | Add a new subject with a description     |
| `/list`                      | Refresh the subjects list                |
| `/switch-user`               | Switch user folder or global mode        |
| `/login`                     | Connect your GitHub account              |
| `/logout`                    | Disconnect your GitHub account           |
| `/whoami`                    | Show the connected GitHub account        |
| `/sync`                      | Pull + push notes with GitHub right now  |
| `/help`                      | Show this command list                   |
| `/exit`                      | Exit (auto-syncs with GitHub)            |

### 📘 Inside a subject

| Command                  | Action                                          |
| ------------------------- | ------------------------------------------------ |
| `/read <note\|number>`    | Open a note in the interactive reader             |
| `/edit <note\|number>`    | Edit a note with reason tracking + backup         |
| `/new-note`               | Create a new note file                            |
| `/upload`                 | Upload a file via the interactive file browser    |
| `/repair <path>`          | Diagnose a Word document's issues                 |
| `/help`                   | Show this command list                            |
| `/back`                   | Return to the subjects menu                       |

### 📖 Inside the interactive reader / document viewers

* `↑/↓` or `k/j` — scroll line by line
* `PgUp/PgDn` or `u/d` — jump multiple lines
* `SPACE`/`h` — highlight/unhighlight the current line
* `/` — search within the file
* `n`/`p` — next/previous search result
* `t` — toggle paragraphs/tables (DOCX only)
* `q` — quit back to the subject menu

---

## 🔐 Connect your GitHub account

Run `/login` once. It starts GitHub's **Device Flow**:

1. The CLI shows a one-time code and a URL (`github.com/login/device`).
2. Open the URL in any browser (phone or laptop) and enter the code.
3. Approve access — the CLI picks up the token automatically and stores it
   locally at `~/.config/study-cli-hub/credentials.json` (readable only by
   you).

From then on, `/sync` and the automatic pull-on-start/push-on-exit use your
GitHub login instead of relying on locally configured SSH keys or cached
credentials — so any collaborator can clone the repo and start syncing
immediately after `/login`, with no extra git configuration.

> You still need push access to this repository (as a collaborator) for
> pushes to succeed — `/login` handles *authentication*, not repo
> permissions. Ask a maintainer to add you as a collaborator, or fork the
> repo and open a pull request the usual GitHub way.

Use `/whoami` to check who's connected and `/logout` to disconnect.

---

## 🧑‍💻 Maintainer setup: enabling `/login`

`/login` needs a GitHub OAuth App with **Device Flow** enabled. This is a
one-time setup only the repo owner needs to do:

1. Go to **github.com/settings/developers → OAuth Apps → New OAuth App**.
2. Any homepage URL works (device flow doesn't use a callback URL). Save it.
3. Open the app's settings and check **"Enable Device Flow"**.
4. Copy the **Client ID** (no client secret is needed for device flow).
5. Set it wherever `study-hub` runs:
   ```bash
   export STUDY_HUB_GITHUB_CLIENT_ID=Iv1.xxxxxxxxxxxxxxxx
   ```
   Since a device-flow Client ID is a public identifier (not a secret), it's
   also safe to bake into `study_cli_hub/github_auth.py` directly if you'd
   rather ship it as a default so users don't need the env var at all.

Until this is configured, `/login` prints setup instructions instead of
failing silently.

---

## 📦 Publishing a release (maintainers)

This repo ships a `.github/workflows/publish.yml` that builds and uploads
the package to PyPI whenever you publish a GitHub Release, using
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (no
API tokens to store as secrets):

1. Create the project once on PyPI (`pip install build twine`, then
   `python -m build && twine upload dist/*` for the very first upload — or
   reserve the name via PyPI's UI).
2. On the PyPI project's **Settings → Publishing**, add a trusted publisher
   pointing at this GitHub repo, workflow file `publish.yml`, and
   environment `pypi`.
3. From then on, cutting a GitHub Release automatically publishes the new
   version — `pipx install study-cli-hub` picks it up immediately.

---

## 🧩 Project Layout

```
study-cli-hub/
├── pyproject.toml            # Package metadata + `study-hub` console script
├── study_cli_hub/
│   ├── cli.py                 # Slash-command REPL (main entry point)
│   ├── completer.py           # Live '/' autocomplete menu
│   ├── github_auth.py         # Device Flow login + token-authenticated git sync
│   ├── file_viewer.py         # Scrollable viewers (text/PDF/DOCX/CSV) with highlighting
│   ├── file_uploader.py       # Interactive file browser + upload
│   ├── doc_repair.py          # Word document diagnostics
│   ├── error_handler.py       # Centralized error logging
│   └── paths.py               # Subject/user folder path helpers
├── subjects/                  # All study notes (synced to GitHub)
│   ├── GlobalSubject/
│   │   ├── description_GlobalSubject.txt
│   │   └── note1.txt
│   └── <username>/
│       └── <Subject>/
└── .github/workflows/publish.yml
```

---

## 👥 Contribution Guide

1. **Fork** the repository (or ask to be added as a collaborator).
2. **Clone** it and run `pipx install -e .` from the clone for a live-editable install.
3. Run `study-hub`, `/login` once, then add subjects/notes as usual.
4. **Commit** with meaningful messages (or just let `/sync`/`/exit` auto-commit).
5. **Push** and open a **Pull Request**.

---

## 🌐 For Non-CLI Users

Browse all study notes directly on GitHub under [`/subjects`](subjects) —
each subject has a description file and notes in readable formats, viewable
on desktop or mobile without installing anything.

---

## 🧰 Requirements

* Python ≥ 3.9
* Git (for cloning & syncing)
* A terminal — `pipx`/`uvx` handle every Python dependency automatically

---

## ❤️ About the Project

CLI Study Hub is an open-source educational project for technical learners:
structured, subject-wise notes, studied efficiently from the terminal, kept
in sync on GitHub, and easy to contribute to.

> 🌍 Built for learners, by learners — one note at a time.

---

## 📧 Author & Community

**Created by:** [Govind Mehta](https://github.com/govindmehta15)
📍 India 🇮🇳

⭐ Star on GitHub and share with your study community!
