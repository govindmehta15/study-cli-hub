# 🧠 CLI Study Hub v5.0 — Slash-Command Study Companion

**CLI Study Hub** is a terminal-first, community-driven study notebook. Every
command is a `/slash-command` with a live, Claude-Code-style autocomplete menu
— start typing and matching commands pop up as you go. Notes live in this
GitHub repo, so anyone with push access gets automatic, hassle-free syncing.
A welcome banner, spinners during sync/network calls, and small emoji
celebrations for milestones (first subject, first post, streaks) make the
terminal experience feel alive — all of it degrades to plain, instant output
when the CLI isn't attached to a real terminal (e.g. scripted/piped use), so
nothing here ever blocks automation.

---

## 🚀 Install

**The only real requirement is Python 3.9+.** Everything else (`rich`,
`prompt_toolkit`, `requests`, `PyPDF2`, `python-docx`, `lxml`) is declared as
a normal dependency in [`pyproject.toml`](pyproject.toml) and gets pulled in
automatically by whichever installer you use below — there's nothing to
install by hand beyond Python itself and one small installer tool.

`study-cli-hub` is [published on PyPI](https://pypi.org/project/study-cli-hub/),
so any of these work on macOS, Linux, or Windows:

### Option A — [`uv`](https://docs.astral.sh/uv/) (recommended)

`uv` manages its own Python builds, so it isn't affected by a broken or
missing system/Homebrew Python — the most reliable option if you've ever
had installer trouble with Python before.

```bash
# 1. Install uv itself (one time):
curl -LsSf https://astral.sh/uv/install.sh | sh        # macOS / Linux
# or on Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Install the app:
uv tool install study-cli-hub

# ...or skip installing it permanently and just run it once:
uvx study-cli-hub
```

### Option B — [`pipx`](https://pipx.pypa.io)

```bash
# 1. Install pipx itself (one time):
brew install pipx && pipx ensurepath          # macOS (Homebrew)
sudo apt install pipx && pipx ensurepath      # Debian/Ubuntu
python3 -m pip install --user pipx && python3 -m pipx ensurepath   # any other Linux/Windows

# 2. Install the app:
pipx install study-cli-hub
```

> ⚠️ **Known issue on macOS:** if `pipx install` fails with
> `Broken Python installation, platform.mac_ver() returned an empty value`,
> that's a bug in a specific Homebrew Python bottle (seen with `python@3.14`),
> not with `study-cli-hub`. Point pipx at a different interpreter instead:
> ```bash
> pipx install --python /usr/bin/python3 study-cli-hub
> ```
> (or `--python $(brew --prefix python@3.12)/bin/python3.12` if you have that
> version installed). If you hit this, `uv` (Option A) avoids the whole class
> of problem since it never touches your system Python at all.

### Option C — plain `pip` (zero extra tools, if you'd rather not install `uv`/`pipx`)

```bash
python3 -m venv ~/.study-cli-hub-venv
~/.study-cli-hub-venv/bin/pip install study-cli-hub
# then use ~/.study-cli-hub-venv/bin/study-hub, or add it to your shell's PATH/alias
```

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
| `/explore`                   | Explore other users' study content (read-only) |
| `/search <term>`             | Full-text search your and others' notes  |
| `/stats`                     | Show your subjects/notes/streak dashboard |
| `/leaderboard`               | Rank all known users by streak/activity  |
| `/digest`                    | See what's new since your last visit     |
| `/feed`                      | Browse the global knowledge feed         |
| `/chat <username>`           | Open an async chat with another user     |
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

## 🌍 Community: explore, feed, comments, and chat

These features solve a different problem than the git-synced `subjects/`
notes: **no collaborator permissions, and no merge conflicts.** Instead of
writing shared files, they read/write [GitHub Discussions](https://docs.github.com/en/discussions)
on this repo. Any GitHub account can post or comment on a public repo's
Discussions without being added as a collaborator, and there's no file to
merge — GitHub's API is the single source of truth, so two people posting at
the same time can never conflict.

* **`/explore`** — browse other users' `subjects/` folders read-only (no
  GitHub login needed; it just reads the files already synced into this repo).
* **`/search <term>`** — full-text search across your own notes, every
  "global" subject, and (read-only) everyone else's notes — no login needed,
  it's pure local file search.
* **`/feed`** — a global text feed. `/post` to share something, `/comment
  <number> <text>` to reply to someone else's post, `/react <number> <emoji>`
  to react with 👍❤️😄🎉😕🚀👀 (e.g. `/react 2 heart`, or `/react 2.1 laugh` to
  react to comment 1 on post 2). Requires `/login`.
* **`/chat <username>`** — an async 1:1 thread with another GitHub user, one
  canonical thread per pair regardless of who starts it. It's not real-time —
  run `/chat <username>` or `/refresh` again later to pick up replies, same
  as checking a GitHub Discussion for new comments. `/react <number> <emoji>`
  works on messages too. Requires `/login`.
* **`/digest`** — "what's new since your last visit": new feed posts/comments
  and new chat messages. Compares against a timestamp stored locally on your
  own machine (`~/.config/study-cli-hub/state.json`) — deliberately not
  synced to the repo, since your read-receipts aren't anyone else's business
  and syncing them would just create pointless git noise. Requires `/login`.

> These need [GitHub Discussions enabled](https://docs.github.com/en/discussions/quickstart)
> on this repo (Settings → General → Features → Discussions). The CLI looks
> for categories named **"Feed"** and **"Chat"**; if they don't exist yet it
> falls back to whatever category is available (e.g. "General"), so there's
> nothing else to configure to get started — creating those two categories
> is optional polish for keeping the Discussions tab organized.

---

## 📊 Stats, streaks & the leaderboard

`/stats` shows your subject/note counts and your daily activity **streak** —
computed entirely from `git log` on your own `subjects/<username>/` folder,
not from a separate tracking file. That means it can't drift from reality,
gives you retroactive credit for history already in the repo, and needs
**zero GitHub API calls** for `/leaderboard` to rank every known user by the
same numbers.

Two honest limitations:
- `/stats` and `/leaderboard` need a **personal user folder** (`/switch-user`
  to one) — Global mode has no identity to attach a streak to.
- The streak reflects commit dates in your local clone's history, so it
  needs a normal (non-shallow) `git clone` — exactly what this README's
  clone instructions already do. It's also not tamper-proof (nothing stops
  backdating a commit), which is fine for a casual gamification feature, not
  a strict requirement.

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

**Using the app is auto-approved for anyone — changing the app's code is not.**
These are two different things and the CLI treats them differently:

- **Using the app** (creating subjects, notes, feed posts) only ever touches
  files under `subjects/<your-username>/`. If you're a collaborator, `/sync`
  pushes those changes straight to `main`. If you're *not* a collaborator,
  `/sync` automatically forks this repo under your own GitHub account,
  pushes your notes there, and opens a pull request back here — no need to
  ask anyone for access first. A GitHub Action
  (`.github/workflows/auto-merge-data-prs.yml`) checks that the PR only
  touches `subjects/**` and auto-approves + auto-merges it. You'll never see
  a pending-review screen just for adding your own notes.
- **Changing the app's code** (anything under `study_cli_hub/`,
  `pyproject.toml`, workflows, this README) always requires a real pull
  request reviewed by a maintainer — enforced by branch protection on `main`
  plus [`.github/CODEOWNERS`](.github/CODEOWNERS). The auto-merge Action
  above only fires for PRs that are 100% `subjects/**`; anything touching
  code is left for manual review, full stop.

**Hassle-free with many users pushing at once:** if two people run `/sync`
around the same time, the second push gets rejected (git's normal
non-fast-forward check). The CLI handles this automatically — it pulls with
`--rebase` and retries the push (up to 3 times) without you doing anything.
Because every user only ever writes inside their own `subjects/<username>/`
folder, this almost always resolves cleanly on its own. The one case it
can't: two people editing the exact same lines of the exact same file — that
surfaces a clear "needs a human" message with the exact `git` commands to
resolve it, instead of silently discarding anyone's work.

Use `/whoami` to check who's connected and `/logout` to disconnect.

---

## 🔑 `/login`'s OAuth App

`/login` works out of the box — no setup needed. It uses a GitHub OAuth App
(Device Flow enabled) whose Client ID is baked into
`study_cli_hub/github_auth.py` (`DEFAULT_GITHUB_CLIENT_ID`). This is a public
identifier, not a secret — no client secret is ever used or needed for
Device Flow — so it's safe to commit and ship in the published package.

Running your own fork against a different OAuth App? Override it without
touching the code:
```bash
export STUDY_HUB_GITHUB_CLIENT_ID=Iv1.xxxxxxxxxxxxxxxx
```
(register your own at **github.com/settings/developers → New OAuth App**,
with **"Enable Device Flow"** checked).

---

## 🛡️ Maintainer setup: branch protection on `main`

This repo's `main` branch requires a pull request for every change, including
the maintainer's own — enforced via GitHub branch protection with
`.github/CODEOWNERS` requiring review on code paths. Data-only PRs
(`subjects/**`) skip human review entirely via the auto-merge Action above;
everything else needs a real review.

One unavoidable GitHub limitation to know about: with a single collaborator
on the repo, there's nobody else who *can* approve your own code PRs.
GitHub's answer to this is the same for every solo-maintainer OSS project —
repo admins get a "merge without waiting for requirements" button on their
own PRs (a deliberate bypass, not a silent one: you have to click it, and
GitHub logs that it happened). The rule still does its job of blocking
*direct pushes* and blocking *everyone else's* code changes from merging
without review; add a second collaborator as a code owner if you want actual
second-person review on your own changes too.

---

## 📦 Publishing a new release (maintainers)

[study-cli-hub](https://pypi.org/project/study-cli-hub/) is already live on
PyPI via a one-time [Trusted Publisher](https://docs.pypi.org/trusted-publishers/)
link (no API tokens stored anywhere). Shipping a new version is just:

1. Bump `version` in `pyproject.toml`, land it through the normal
   code-review PR flow (see [Contribution Guide](#-contribution-guide)).
2. `gh release create vX.Y.Z --generate-notes` (or via the GitHub UI).
3. That's it — `.github/workflows/publish.yml` builds and uploads
   automatically. `uv tool install study-cli-hub` / `pipx upgrade
   study-cli-hub` pick up the new version immediately.

---

## 🧩 Project Layout

```
study-cli-hub/
├── pyproject.toml            # Package metadata + `study-hub` console script
├── study_cli_hub/
│   ├── cli.py                 # Slash-command REPL (main entry point)
│   ├── completer.py           # Live '/' autocomplete menu
│   ├── github_auth.py         # Device Flow login + token-authenticated git sync
│   ├── community.py           # Feed/comments/chat/reactions via GitHub Discussions (permission-less, conflict-free)
│   ├── search.py              # Full-text search across your and others' notes
│   ├── stats.py                # git-log-derived streak/leaderboard stats (zero API calls)
│   ├── local_state.py         # Personal, per-device "last seen" markers for /digest (not git-synced)
│   ├── animations.py          # Typewriter/spinner/celebration primitives (degrade to plain output non-interactively)
│   ├── contribute.py           # Fork + auto-PR fallback for non-collaborators (hassle-free app usage)
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

**Adding study notes** — no setup beyond `/login`:

1. `git clone https://github.com/govindmehta15/study-cli-hub.git && cd study-cli-hub`
2. `pipx install study-cli-hub` (or `pipx install -e .` for a live-editable install), then `study-hub`
3. `/login` once, then add subjects/notes as usual.
4. `/sync` or `/exit` — auto-commits, and auto-forks + opens a PR for you if you're not a
   collaborator. Either way, notes-only changes auto-merge with no wait.

**Changing the app's code** — needs an actual review, so use the normal GitHub flow:

1. **Fork** the repository.
2. **Clone** your fork and run `pipx install -e .` for a live-editable install.
3. Make your change, commit, push to your fork.
4. Open a **Pull Request** — a maintainer (per `.github/CODEOWNERS`) will review it.

---

## 🌐 For Non-CLI Users

Browse all study notes directly on GitHub under [`/subjects`](subjects) —
each subject has a description file and notes in readable formats, viewable
on desktop or mobile without installing anything.

---

## 🧰 Requirements

* **Python ≥ 3.9** — the only hard requirement. Every other Python package
  (`rich`, `prompt_toolkit`, `requests`, `PyPDF2`, `python-docx`, `lxml`) is
  installed automatically by `uv`/`pipx`/`pip` — you never install these by hand.
* **Git** — for cloning the repo and for `/sync` to work.
* **`uv` or `pipx`** (recommended, not strictly required) — see
  [Install](#-install) above for exact commands per OS. Option C shows how to
  install with plain `pip` and no extra tool at all, if you'd rather not.

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
