# cli.py - Study CLI Hub v5.0 entry point
import atexit
import difflib
import os
import random
import signal
import subprocess
import sys
from datetime import datetime, timezone

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.align import Align
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from study_cli_hub import __version__, animations, community, contribute, exporter, github_auth, local_state, pomodoro, quiz, search, srs, stats
from study_cli_hub.animations import cli_panel as Panel
from study_cli_hub.completer import SlashCompleter
from study_cli_hub.doc_repair import repair_document
from study_cli_hub.error_handler import handle_error
from study_cli_hub.file_uploader import upload_file
from study_cli_hub.file_viewer import open_in_editor, view_file_rich
from study_cli_hub.paths import (
    get_subject_description,
    get_visibility,
    list_global_subjects,
    list_known_users,
    list_notes,
    list_subjects,
    list_visible_subjects,
    note_path,
    set_visibility,
    subject_path,
)
from study_cli_hub.tui import CaptureConsole, TuiShell

console = Console()

MAIN_COMMANDS = [
    ("/study", "a subject name or number", "Open a subject"),
    ("/create-subject", "", "Create a new subject"),
    ("/list", "", "Refresh the subjects list"),
    ("/switch-user", "", "Switch user folder or global mode"),
    ("/explore", "", "Explore other users' study content"),
    ("/search", "what to search for", "Full-text search your and others' notes"),
    ("/quiz", "a subject name or number", "Quiz yourself (flashcards or AI-generated)"),
    ("/stats", "", "Show your subjects/notes/streak dashboard"),
    ("/leaderboard", "", "Rank all known users by streak/activity"),
    ("/digest", "", "See what's new since your last visit"),
    ("/pomodoro", "minutes, optional (default 25)", "Run a focus-session countdown timer"),
    ("/export", "json or csv, optional (default json)", "Back up your subjects/notes/stats to a file"),
    ("/feed", "", "Browse the global knowledge feed"),
    ("/chat", "a GitHub username", "Open an async chat with another user"),
    ("/login", "", "Connect your GitHub account"),
    ("/logout", "", "Disconnect your GitHub account"),
    ("/whoami", "", "Show the connected GitHub account"),
    ("/sync", "", "Pull + push notes with GitHub now"),
    ("/help", "", "Show available commands"),
    ("/exit", "", "Exit (auto-syncs with GitHub)"),
]

SUBJECT_COMMANDS = [
    ("/read", "a note name or number", "Open a note in the interactive reader"),
    ("/edit", "a note name or number", "Edit a note with reason tracking"),
    ("/new-note", "", "Create a new note file"),
    ("/upload", "", "Upload a file via the file browser"),
    ("/repair", "a file path", "Diagnose a Word document's issues"),
    ("/help", "", "Show available commands"),
    ("/back", "", "Return to the subjects menu"),
]

EXPLORE_COMMANDS = [
    ("/open", "a subject name or number", "Browse a user or global subject (read-only)"),
    ("/help", "", "Show available commands"),
    ("/back", "", "Return to the main menu"),
]

EXPLORE_USER_COMMANDS = [
    ("/study", "a subject name or number", "Open one of their subjects"),
    ("/help", "", "Show available commands"),
    ("/back", "", "Return to the users list"),
]

EXPLORE_SUBJECT_COMMANDS = [
    ("/read", "a note name or number", "Open a note in the interactive reader"),
    ("/help", "", "Show available commands"),
    ("/back", "", "Return to their subjects"),
]

FEED_COMMANDS = [
    ("/post", "", "Write a new post to the global feed"),
    ("/comment", "a number, then your text", "Comment on a feed post"),
    ("/react", "a number, then an emoji name", "React to a post (e.g. /react 2 heart)"),
    ("/refresh", "", "Reload the feed from GitHub"),
    ("/help", "", "Show available commands"),
    ("/back", "", "Return to the main menu"),
]

SEARCH_COMMANDS = [
    ("/open", "a result number", "Open a result in the reader"),
    ("/help", "", "Show available commands"),
    ("/back", "", "Return to the main menu"),
]

CHAT_COMMANDS = [
    ("/say", "your message", "Send a message"),
    ("/react", "a number, then an emoji name", "React to a message (e.g. /react 1 laugh)"),
    ("/refresh", "", "Check for new replies"),
    ("/help", "", "Show available commands"),
    ("/back", "", "Return to the main menu"),
]

# Global flag to track if auto-push has been done
auto_push_done = False


class SlashPrompt:
    """A '/' command prompt with a live, prefix-filtered menu (falls back to
    plain input when not attached to a real terminal, e.g. in scripts/CI)."""

    def __init__(self, commands, argument_candidates=None):
        self.completer = SlashCompleter(commands, argument_candidates=argument_candidates)
        self._session = None
        if sys.stdin.isatty():
            try:
                self._session = PromptSession(history=InMemoryHistory())
            except Exception:
                self._session = None

    def ask(self, message="Command"):
        if self._session is not None:
            return self._session.prompt(
                f"{message} > ",
                completer=self.completer,
                complete_while_typing=True,
            ).strip()
        return Prompt.ask(f"[yellow]{message} (type / to see commands)[/yellow]").strip()


def cleanup_and_push():
    """Cleanup function to auto-push on exit"""
    global auto_push_done
    if not auto_push_done:
        try:
            console.print("\n[yellow]Auto-saving changes...[/yellow]")
            auto_git_push()
            auto_push_done = True
        except Exception:
            pass


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    console.print("\n[yellow]Auto-saving changes before exit...[/yellow]")
    cleanup_and_push()
    sys.exit(0)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def parse_command(raw):
    """Accepts '/study 2' or the legacy bare 'study 2' form."""
    raw = raw.strip()
    if not raw:
        return None, ""
    if raw.startswith("/"):
        raw = raw[1:]
    parts = raw.split(" ", 1)
    name = "/" + parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""
    return name, arg


def print_help(commands, title, console=console):
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan", width=20)
    table.add_column("Args", style="dim", width=16)
    table.add_column("Description", width=45)
    for name, args_hint, description in commands:
        table.add_row(name, args_hint, description)
    console.print(table)


def auto_git_sync():
    """Pull latest notes from GitHub, using a stored login token if present."""
    try:
        result = subprocess.run(["git", "status"], capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            console.print("[yellow]Not in a git repository - GitHub sync skipped[/yellow]")
            return

        console.print(Panel("[bold cyan]🔄 Auto GitHub Sync[/bold cyan]", expand=False))
        pull_result = animations.with_spinner(console, "📥 Pulling latest changes...", github_auth.git_pull)
        if pull_result.returncode == 0:
            console.print("[green]✅ Successfully pulled latest changes[/green]")
        else:
            console.print("[yellow]⚠️ Pull failed (normal if no remote exists, or run /login)[/yellow]")
    except FileNotFoundError:
        console.print("[yellow]⚠️ Git not found - GitHub sync features disabled[/yellow]")
    except Exception as e:
        console.print(f"[yellow]⚠️ GitHub sync error: {e}[/yellow]")


def _has_unmerged_paths(cwd=None):
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, text=True, cwd=cwd or os.getcwd()
    )
    return bool(result.stdout.strip())


def _has_unpushed_commits(cwd=None):
    result = subprocess.run(
        ["git", "rev-list", "@{u}..HEAD", "--count"], capture_output=True, text=True, cwd=cwd or os.getcwd()
    )
    if result.returncode != 0:
        # No upstream tracking configured (e.g. this is the very first push) -
        # can't prove there's nothing to push, so assume there is.
        return True
    return result.stdout.strip() not in ("", "0")


def auto_git_push(max_attempts=3):
    """Commit and push changes to GitHub, using a stored login token if
    present. If the push is rejected because someone else pushed first
    (non-fast-forward), auto pull --rebase and retry - this is what makes
    concurrent pushes from many users hassle-free. The one case this can't
    resolve hands-off is two users editing the literal same lines of the
    same file; that surfaces as a real rebase conflict and needs a human.

    Also retries pushing commits that were already made in a *previous*
    run but never made it to the remote (e.g. all attempts were exhausted
    last time) - a plain "any uncommitted changes?" check would silently
    skip those forever.

    If the logged-in user isn't a collaborator (no direct push access),
    this falls back to forking the repo under their account and opening a
    PR instead - that's what makes using the app hassle-free for literally
    anyone, while code changes still require a maintainer-reviewed PR."""
    try:
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=os.getcwd())
        if status.returncode != 0:
            return

        if status.stdout.strip():
            subprocess.run(["git", "add", "."], capture_output=True, text=True, cwd=os.getcwd())
            commit_message = f"Auto-sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True, cwd=os.getcwd())

        if not _has_unpushed_commits():
            console.print("[green]✅ No changes to push[/green]")
            return

        access = contribute.has_push_access()
        if access is False:
            pr_url, err = animations.with_spinner(
                console, "🍴 No direct push access - syncing via your fork...", contribute.contribute_via_fork
            )
            if err:
                console.print(f"[red]❌ {err}[/red]")
            else:
                console.print(
                    f"[green]✅ Synced! Since this only touches your notes, it'll auto-merge shortly:[/green]\n{pr_url}"
                )
            return

        console.print(Panel("[bold cyan]🔄 Auto Push to GitHub[/bold cyan]", expand=False))

        for attempt in range(1, max_attempts + 1):
            push_result = animations.with_spinner(console, "📤 Pushing to GitHub...", github_auth.git_push)
            if push_result.returncode == 0:
                console.print("[green]✅ Successfully pushed to GitHub[/green]")
                return

            stderr = push_result.stderr or ""
            if not any(marker in stderr for marker in ("rejected", "fetch first", "non-fast-forward")):
                reason = stderr.strip() or "check your GitHub login (/login) or remote permissions"
                console.print(f"[red]❌ Push failed: {reason}[/red]")
                return

            console.print(
                f"[yellow]⚠️ Push rejected (attempt {attempt}/{max_attempts}) - someone else pushed first. "
                "Pulling + rebasing and retrying...[/yellow]"
            )
            pull_result = animations.with_spinner(console, "📥 Pulling + rebasing...", github_auth.git_pull)
            if pull_result.returncode != 0 or _has_unmerged_paths():
                console.print(Panel(
                    "[bold red]⚠️ Manual merge conflict during rebase[/bold red]\n\n"
                    "Someone else edited the exact same file/lines you did - this "
                    "needs a human. Resolve the conflict markers in the affected "
                    "file(s), then run:\n"
                    "  git add <file>\n  git rebase --continue\n"
                    "and /sync again. (Run 'git rebase --abort' to bail out instead.)",
                    expand=False,
                ))
                return
            # rebase succeeded cleanly - loop retries the push

        console.print(f"[yellow]⚠️ Still couldn't push after {max_attempts} attempts - try /sync again shortly.[/yellow]")
    except FileNotFoundError:
        console.print("[yellow]⚠️ Git not found - auto push skipped[/yellow]")
    except Exception as e:
        console.print(f"[yellow]⚠️ Auto push error: {e}[/yellow]")


def check_git_status():
    """Check if we're in a git repository and show status"""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            if result.stdout.strip():
                console.print("[yellow]You have uncommitted changes[/yellow]")
                console.print("[dim]These will be auto-committed and pushed on exit or /sync[/dim]")
            else:
                console.print("[green]Working directory is clean[/green]")
        else:
            console.print("[yellow]Not in a git repository[/yellow]")
    except FileNotFoundError:
        console.print("[yellow]Git not found - GitHub sync features disabled[/yellow]")


def resolve_choice(items, target, kind="item"):
    """Resolve a 1-based number or an exact name to an item from the list."""
    if target.isdigit():
        index = int(target)
        if 1 <= index <= len(items):
            return items[index - 1]
        console.print(f"[red]Invalid {kind} number! Choose 1-{len(items)}[/red]")
        return None
    if target not in items:
        console.print(f"[red]{kind.capitalize()} '{target}' not found![/red]")
        return None
    return target


def create_subject(user_folder):
    """Create a new subject with description, guided step by step."""
    try:
        console.print(Panel("[bold cyan]📚 Create a New Subject[/bold cyan]", expand=False))

        name = Prompt.ask("[yellow]Subject name[/yellow]").strip()
        if not name:
            console.print("[red]⚠️ Subject name cannot be empty![/red]")
            return
        if os.path.sep in name or (os.path.altsep and os.path.altsep in name) or ".." in name:
            console.print("[red]⚠️ Subject name can't contain path separators or '..'[/red]")
            return

        path = subject_path(user_folder, name)
        if os.path.exists(path):
            console.print(f"[red]⚠️ Subject '{name}' already exists! Use /study {name} to open it.[/red]")
            return

        existing = list_subjects(user_folder)
        close_matches = difflib.get_close_matches(name, existing, n=3, cutoff=0.75)
        if close_matches:
            console.print(f"[yellow]⚠️ This looks similar to existing subject(s): {', '.join(close_matches)}[/yellow]")
            if Prompt.ask("[yellow]Create it anyway?[/yellow]", choices=["yes", "no"], default="no") != "yes":
                console.print("[yellow]Cancelled.[/yellow]")
                return

        description = Prompt.ask("[yellow]Short description[/yellow] [dim](optional)[/dim]").strip()
        if not description:
            description = f"Notes for {name}"

        visibility = "public"
        if user_folder:
            visibility = Prompt.ask(
                "[yellow]Visible to other users via /explore and /search?[/yellow] "
                "[dim](private just hides it from other people in this app - it's still in the shared git repo)[/dim]",
                choices=["public", "private"],
                default="public",
            )

        console.print()
        review = f"[bold]Name:[/bold] {name}\n[bold]Description:[/bold] {description}"
        if user_folder:
            review += f"\n[bold]Visibility:[/bold] {'🔒 private' if visibility == 'private' else '🌐 public'}"
        console.print(Panel(review, title="Review", expand=False))
        if Prompt.ask("[yellow]Create this subject?[/yellow]", choices=["yes", "no"], default="yes") != "yes":
            console.print("[yellow]Cancelled.[/yellow]")
            return

        is_first_subject = user_folder and not existing

        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, f"description_{name}.txt"), "w", encoding="utf-8") as f:
            f.write(description)
        if user_folder:
            set_visibility(user_folder, name, visibility)

        if is_first_subject:
            animations.rocket_launch(console, f"Your first subject, '{name}', is live!")
        elif not animations.science_animation(console, name, f"'{name}' is ready to explore!"):
            console.print(f"[green]✅ Subject '{name}' created successfully![/green]")

        if Prompt.ask("[yellow]Add a note now?[/yellow]", choices=["yes", "no"], default="yes") == "yes":
            create_new_note(user_folder, name)
    except Exception as e:
        handle_error(e)


def create_new_note(user_folder, subject):
    """Create a new note file"""
    try:
        filename = Prompt.ask("[yellow]Enter new note filename[/yellow]").strip()
        if not filename:
            console.print("[red]⚠️ Filename cannot be empty![/red]")
            return
        if os.path.sep in filename or (os.path.altsep and os.path.altsep in filename) or ".." in filename:
            console.print("[red]⚠️ Filename can't contain path separators or '..'[/red]")
            return
        if "." not in filename:
            filename += ".txt"

        path = note_path(user_folder, subject, filename)
        if os.path.exists(path):
            console.print(f"[red]⚠️ File '{filename}' already exists! Use /edit instead.[/red]")
            return

        console.print(f"[dim]Creating '{filename}' - opens your editor if $EDITOR is set.[/dim]")
        content = open_in_editor("")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[green]✅ Created new note: {filename}[/green]")
    except Exception as e:
        handle_error(e)


def display_subjects(subjects, user_folder=None, console=console):
    """Display subjects in a rich table"""
    if not subjects:
        console.print("[yellow]No subjects found. Create one with /create-subject[/yellow]")
        return

    table = Table(
        title=f"Subjects Available {'(User: ' + user_folder + ')' if user_folder else '(Global)'}",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("No.", justify="right", width=4)
    table.add_column("Subject Name", width=30)
    table.add_column("Notes", justify="right", width=8)

    for i, sub in enumerate(subjects, 1):
        table.add_row(str(i), sub, str(len(list_notes(user_folder, sub))))

    console.print(table)


def display_notes(notes, subject):
    """Display notes in a rich table"""
    if not notes:
        console.print("[yellow]No notes found. Create one with /new-note or /upload[/yellow]")
        return

    ext_colors = {
        "txt": "green", "md": "cyan", "py": "magenta", "json": "yellow",
        "js": "yellow", "html": "red", "css": "blue", "xml": "green",
        "yaml": "cyan", "yml": "cyan", "pdf": "red", "doc": "blue",
        "docx": "blue", "csv": "yellow",
    }

    table = Table(title=f"Notes in {subject}", show_header=True, header_style="bold cyan")
    table.add_column("No.", justify="right", width=4)
    table.add_column("Filename", width=40)
    table.add_column("Type", width=8)

    for i, note in enumerate(notes, 1):
        ext = note.split(".")[-1].lower() if "." in note else "txt"
        color = ext_colors.get(ext, "white")
        table.add_row(str(i), f"[{color}]{note}[/{color}]", ext.upper())

    console.print(table)


def main():
    """Main CLI application"""
    atexit.register(cleanup_and_push)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    clear_screen()
    animations.print_startup_banner(
        console, app_name="STUDY HUB", version=f"v{__version__}", tagline="slash-command study notebook"
    )
    console.print()

    auto_git_sync()
    check_git_status()

    user = Prompt.ask("[yellow]Enter your username (press Enter for Global mode)[/yellow]").strip()
    user_folder = user if user else None
    console.print(f"[green]✅ Using {'user folder: ' + user_folder if user_folder else 'global mode'}[/green]")
    console.print()
    input("Press Enter to continue...")

    # The fixed-layout TUI (pinned input + live completion + scrollable
    # output, like Claude Code's/Copilot CLI's own UIs) needs a real
    # terminal - prompt_toolkit's full-screen Application can't run against
    # a plain pipe. Piped/scripted/non-tty use (including this project's
    # own automated testing) falls back to the classic scrolling REPL,
    # unchanged.
    if sys.stdin.isatty():
        _main_menu_tui(user_folder)
    else:
        _main_menu_classic(user_folder)


def _main_menu_tui(user_folder):
    """Main menu using the fixed-layout shell: a permanently pinned input
    line at the bottom (with live '/' completion) and a scrollable output
    pane above it. Diving into an actual feature (a subject, /explore,
    /feed, ...) temporarily suspends this fixed layout to run that screen
    exactly as it always has, then restores it on /back or /exit."""
    state = {"user_folder": user_folder, "subjects": []}

    def header_text():
        who = "user: " + state["user_folder"] if state["user_folder"] else "global mode"
        return f"🧠 STUDY HUB  ·  {who}"

    capture = CaptureConsole()

    def render_main_screen(shell):
        capture.refresh_width()
        state["subjects"] = list_subjects(state["user_folder"])
        display_subjects(state["subjects"], state["user_folder"], console=capture.rich)
        capture.rich.print()
        print_help(MAIN_COMMANDS, "Commands (type / for live suggestions)", console=capture.rich)
        shell.header_text = header_text()
        shell.set_output(capture.pop_text())

    def run_classic(shell, func):
        """Suspends the fixed layout, runs `func` as a normal blocking
        action against the real terminal, then redraws the main screen.

        run_in_terminal() schedules `func` on the event loop and returns
        immediately (it does not block) - so the redraw must happen in a
        completion callback, not right after this call returns. Otherwise
        it would run before `func` has actually executed and capture
        stale state (e.g. missing a /switch-user update)."""
        def wrapped():
            try:
                func()
            except Exception as e:
                handle_error(e)
                input("Press Enter to continue...")
        future = shell.run_in_terminal(wrapped)
        future.add_done_callback(lambda f: render_main_screen(shell))

    def handle_submit(shell, raw):
        name, arg = parse_command(raw)
        if name is None:
            return

        if name in ("/exit", "/quit"):
            shell.exit()
            return

        elif name == "/switch-user":
            def _switch_user():
                new_user = Prompt.ask("[yellow]Enter new username (or press Enter for Global)[/yellow]").strip()
                state["user_folder"] = new_user if new_user else None
                console.print(f"[green]✅ Switched to {'user: ' + state['user_folder'] if state['user_folder'] else 'global mode'}[/green]")
                input("Press Enter to continue...")
            run_classic(shell, _switch_user)

        elif name == "/create-subject":
            run_classic(shell, lambda: (create_subject(state["user_folder"]), input("Press Enter to continue...")))

        elif name == "/list":
            render_main_screen(shell)

        elif name == "/login":
            run_classic(shell, lambda: (github_auth.login(console), input("Press Enter to continue...")))

        elif name == "/logout":
            run_classic(shell, lambda: (github_auth.logout(console), input("Press Enter to continue...")))

        elif name == "/whoami":
            run_classic(shell, lambda: (github_auth.whoami(console), input("Press Enter to continue...")))

        elif name == "/sync":
            run_classic(shell, lambda: (auto_git_sync(), auto_git_push(), input("Press Enter to continue...")))

        elif name == "/help":
            run_classic(shell, lambda: (print_help(MAIN_COMMANDS, "Main Menu Commands"), input("Press Enter to continue...")))

        elif name in ("/study", "/learn"):
            if not arg:
                run_classic(shell, lambda: (
                    console.print("[red]Type /study followed by a subject name or number[/red]"),
                    input("Press Enter to continue..."),
                ))
                return
            subject = resolve_choice(state["subjects"], arg, kind="subject")
            if subject:
                run_classic(shell, lambda: subject_menu(state["user_folder"], subject))
            else:
                render_main_screen(shell)

        elif name == "/explore":
            run_classic(shell, lambda: explore_menu(state["user_folder"]))

        elif name == "/search":
            if not arg:
                run_classic(shell, lambda: (
                    console.print("[red]Type /search followed by what you want to find[/red]"),
                    input("Press Enter to continue..."),
                ))
                return
            run_classic(shell, lambda: search_menu(state["user_folder"], arg))

        elif name == "/quiz":
            if not arg:
                run_classic(shell, lambda: (
                    console.print("[red]Type /quiz followed by a subject name or number[/red]"),
                    input("Press Enter to continue..."),
                ))
                return
            subject = resolve_choice(state["subjects"], arg, kind="subject")
            if subject:
                run_classic(shell, lambda: quiz_menu(state["user_folder"], subject))
            else:
                render_main_screen(shell)

        elif name == "/stats":
            if not state["user_folder"]:
                run_classic(shell, lambda: (
                    console.print("[yellow]Stats/streaks need a personal user folder - /switch-user to one first.[/yellow]"),
                    input("Press Enter to continue..."),
                ))
                return
            run_classic(shell, lambda: (show_stats(state["user_folder"]), input("Press Enter to continue...")))

        elif name == "/leaderboard":
            run_classic(shell, lambda: (show_leaderboard(), input("Press Enter to continue...")))

        elif name == "/digest":
            if not community.is_logged_in():
                run_classic(shell, lambda: (
                    console.print("[yellow]Run /login first to see your digest.[/yellow]"),
                    input("Press Enter to continue..."),
                ))
                return
            run_classic(shell, lambda: (show_digest(), input("Press Enter to continue...")))

        elif name == "/pomodoro":
            run_classic(shell, lambda: pomodoro_flow(_parse_pomodoro_minutes(arg)))

        elif name == "/export":
            fmt = arg.strip().lower() if arg and arg.strip().lower() == "csv" else "json"
            run_classic(shell, lambda: export_flow(state["user_folder"], fmt))

        elif name == "/feed":
            run_classic(shell, feed_menu)

        elif name == "/chat":
            if not arg:
                run_classic(shell, lambda: (
                    console.print("[red]Type /chat followed by a GitHub username[/red]"),
                    input("Press Enter to continue..."),
                ))
                return
            run_classic(shell, lambda: chat_menu(arg))

        else:
            run_classic(shell, lambda: (
                console.print("[red]Unknown command. Type / to see the available commands.[/red]"),
                input("Press Enter to continue..."),
            ))

    shell = TuiShell(
        completer=SlashCompleter(MAIN_COMMANDS),
        on_submit=lambda raw: handle_submit(shell, raw),
        header_text=header_text(),
        hint_text=" Ctrl+C Exit  ·  / Commands  ·  /help Help ",
    )
    render_main_screen(shell)
    shell.run()

    clear_screen()
    animations.typewriter(console, "👋 Thanks for using CLI Study Hub!", style="bold green")
    global auto_push_done
    auto_push_done = True
    auto_git_push()


def _main_menu_classic(user_folder):
    """Classic clear-and-reprint REPL main menu - the non-tty fallback for
    piped/scripted use (this project's own automated testing included),
    since the fixed-layout TUI requires a real terminal."""
    prompt = SlashPrompt(MAIN_COMMANDS)

    while True:
        try:
            clear_screen()
            subjects = list_subjects(user_folder)
            display_subjects(subjects, user_folder)
            console.print()
            print_help(MAIN_COMMANDS, "Commands (type / for live suggestions)")

            name, arg = parse_command(prompt.ask())
            if name is None:
                continue

            if name in ("/exit", "/quit"):
                clear_screen()
                animations.typewriter(console, "👋 Thanks for using CLI Study Hub!", style="bold green")
                global auto_push_done
                auto_push_done = True
                auto_git_push()
                break

            elif name == "/switch-user":
                user = Prompt.ask("[yellow]Enter new username (or press Enter for Global)[/yellow]").strip()
                user_folder = user if user else None
                console.print(f"[green]✅ Switched to {'user: ' + user_folder if user_folder else 'global mode'}[/green]")
                input("Press Enter to continue...")

            elif name == "/create-subject":
                create_subject(user_folder)
                input("Press Enter to continue...")

            elif name == "/list":
                continue

            elif name == "/login":
                github_auth.login(console)
                input("Press Enter to continue...")

            elif name == "/logout":
                github_auth.logout(console)
                input("Press Enter to continue...")

            elif name == "/whoami":
                github_auth.whoami(console)
                input("Press Enter to continue...")

            elif name == "/sync":
                auto_git_sync()
                auto_git_push()
                input("Press Enter to continue...")

            elif name == "/help":
                print_help(MAIN_COMMANDS, "Main Menu Commands")
                input("Press Enter to continue...")

            elif name == "/study" or name == "/learn":
                if not arg:
                    console.print("[red]Type /study followed by a subject name or number[/red]")
                    input("Press Enter to continue...")
                    continue
                subject = resolve_choice(subjects, arg, kind="subject")
                if subject:
                    subject_menu(user_folder, subject)

            elif name == "/explore":
                explore_menu(user_folder)

            elif name == "/search":
                if not arg:
                    console.print("[red]Type /search followed by what you want to find[/red]")
                    input("Press Enter to continue...")
                    continue
                search_menu(user_folder, arg)

            elif name == "/quiz":
                if not arg:
                    console.print("[red]Type /quiz followed by a subject name or number[/red]")
                    input("Press Enter to continue...")
                    continue
                subject = resolve_choice(subjects, arg, kind="subject")
                if subject:
                    quiz_menu(user_folder, subject)

            elif name == "/stats":
                if not user_folder:
                    console.print("[yellow]Stats/streaks need a personal user folder - /switch-user to one first.[/yellow]")
                    input("Press Enter to continue...")
                    continue
                show_stats(user_folder)
                input("Press Enter to continue...")

            elif name == "/leaderboard":
                show_leaderboard()
                input("Press Enter to continue...")

            elif name == "/digest":
                if not community.is_logged_in():
                    console.print("[yellow]Run /login first to see your digest.[/yellow]")
                    input("Press Enter to continue...")
                    continue
                show_digest()
                input("Press Enter to continue...")

            elif name == "/pomodoro":
                minutes = _parse_pomodoro_minutes(arg)
                pomodoro_flow(minutes)

            elif name == "/export":
                fmt = arg.strip().lower() if arg and arg.strip().lower() == "csv" else "json"
                export_flow(user_folder, fmt)

            elif name == "/feed":
                feed_menu()

            elif name == "/chat":
                if not arg:
                    console.print("[red]Type /chat followed by a GitHub username[/red]")
                    input("Press Enter to continue...")
                    continue
                chat_menu(arg)

            else:
                console.print("[red]Unknown command. Type / to see the available commands.[/red]")
                input("Press Enter to continue...")

        except Exception as e:
            handle_error(e)
            input("Press Enter to continue...")


def subject_menu(user_folder, subject):
    """Handle commands inside a subject"""
    prompt = SlashPrompt(SUBJECT_COMMANDS)

    while True:
        try:
            clear_screen()
            notes = list_notes(user_folder, subject)
            display_notes(notes, subject)
            console.print()
            print_help(SUBJECT_COMMANDS, "Commands (type / for live suggestions)")

            name, arg = parse_command(prompt.ask())
            if name is None:
                continue

            if name == "/back":
                break

            elif name == "/help":
                print_help(SUBJECT_COMMANDS, f"Commands in {subject}")
                input("Press Enter to continue...")

            elif name == "/read":
                if not arg:
                    console.print("[red]Type /read followed by a note name or number[/red]")
                    input("Press Enter to continue...")
                    continue
                filename = resolve_choice(notes, arg, kind="note")
                if filename:
                    view_file_rich(user_folder, subject, filename)

            elif name == "/edit":
                if not arg:
                    console.print("[red]Type /edit followed by a note name or number[/red]")
                    input("Press Enter to continue...")
                    continue
                filename = resolve_choice(notes, arg, kind="note")
                if filename:
                    view_file_rich(user_folder, subject, filename, editable=True)
                    input("Press Enter to continue...")

            elif name == "/new-note":
                create_new_note(user_folder, subject)
                input("Press Enter to continue...")

            elif name == "/upload":
                upload_file(user_folder, subject)
                input("Press Enter to continue...")

            elif name == "/repair":
                if not arg:
                    console.print("[red]Type /repair followed by the path to a document[/red]")
                    input("Press Enter to continue...")
                    continue
                repair_document(arg)
                input("Press Enter to continue...")

            else:
                console.print("[red]Unknown command. Type / to see the available commands.[/red]")
                input("Press Enter to continue...")

        except Exception as e:
            handle_error(e)
            input("Press Enter to continue...")


def explore_menu(current_user_folder):
    """Read-only browsing of everyone's content: other users' subjects AND
    every global subject, in one list. Type '/open <part-of-a-name>' and
    matching entries appear live as you type, the same way slash commands
    do."""

    def combined_entries():
        users = list_known_users(exclude=current_user_folder)
        # An empty personal folder (no subjects created yet) is
        # indistinguishable from an empty global subject by the on-disk
        # heuristic alone - explicitly exclude the current user's own
        # folder so it never shows up as something to "explore".
        globals_ = [g for g in list_global_subjects() if g != current_user_folder]
        return [("user", u) for u in users] + [("global", g) for g in globals_]

    def argument_provider():
        candidates = []
        for kind, name_ in combined_entries():
            if kind == "user":
                candidates.append((name_, f"👤 user - {len(list_visible_subjects(name_))} subject(s)"))
            else:
                candidates.append((name_, f"🌍 global subject - {len(list_notes(None, name_))} note(s)"))
        return candidates

    prompt = SlashPrompt(EXPLORE_COMMANDS, argument_candidates={"/open": argument_provider})

    while True:
        try:
            clear_screen()
            entries = combined_entries()
            console.print(Panel("[bold cyan]🌍 Explore Everyone's Content[/bold cyan]", expand=False))
            if not entries:
                console.print("[yellow]Nothing to explore yet.[/yellow]")
            else:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("No.", justify="right", width=4)
                table.add_column("Name", width=20)
                table.add_column("Type", width=16)
                table.add_column("Contains", justify="right", width=12)
                table.add_column("About", width=28)
                for i, (kind, name_) in enumerate(entries, 1):
                    if kind == "user":
                        visible = list_visible_subjects(name_)
                        about = ", ".join(visible[:3]) + ("…" if len(visible) > 3 else "") if visible else "[dim]nothing public yet[/dim]"
                        table.add_row(str(i), name_, "👤 User", f"{len(visible)} subjects", about)
                    else:
                        desc = get_subject_description(None, name_) or "[dim]no description[/dim]"
                        table.add_row(str(i), name_, "🌍 Global subject", f"{len(list_notes(None, name_))} notes", desc[:60])
                console.print(table)
            console.print()
            print_help(EXPLORE_COMMANDS, "Commands (type / for live suggestions)")

            name, arg = parse_command(prompt.ask())
            if name is None:
                continue

            if name == "/back":
                break
            elif name == "/help":
                print_help(EXPLORE_COMMANDS, "Explore Commands")
                input("Press Enter to continue...")
            elif name == "/open":
                if not arg:
                    console.print("[red]Type /open followed by a name or number[/red]")
                    input("Press Enter to continue...")
                    continue
                names_only = [n for _, n in entries]
                target = resolve_choice(names_only, arg, kind="entry")
                if target:
                    kind_by_name = dict((n, k) for k, n in entries)
                    if kind_by_name[target] == "user":
                        explore_user_menu(target)
                    else:
                        explore_subject_menu(None, target)
            else:
                console.print("[red]Unknown command. Type / to see the available commands.[/red]")
                input("Press Enter to continue...")

        except Exception as e:
            handle_error(e)
            input("Press Enter to continue...")


def explore_user_menu(target_user):
    prompt = SlashPrompt(EXPLORE_USER_COMMANDS)

    while True:
        try:
            clear_screen()
            subjects = list_visible_subjects(target_user)
            console.print(Panel(f"[bold cyan]👤 @{target_user}'s public subjects[/bold cyan]", expand=False))
            if not subjects:
                console.print("[yellow]Nothing public here yet.[/yellow]")
            else:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("No.", justify="right", width=4)
                table.add_column("Subject", width=24)
                table.add_column("Notes", justify="right", width=8)
                table.add_column("About", width=40)
                for i, s in enumerate(subjects, 1):
                    desc = get_subject_description(target_user, s) or "[dim]no description[/dim]"
                    table.add_row(str(i), s, str(len(list_notes(target_user, s))), desc[:60])
                console.print(table)
            console.print()
            print_help(EXPLORE_USER_COMMANDS, "Commands (type / for live suggestions)")

            name, arg = parse_command(prompt.ask())
            if name is None:
                continue

            if name == "/back":
                break
            elif name == "/help":
                print_help(EXPLORE_USER_COMMANDS, f"Browsing @{target_user}")
                input("Press Enter to continue...")
            elif name == "/study":
                if not arg:
                    console.print("[red]Type /study followed by a subject name or number[/red]")
                    input("Press Enter to continue...")
                    continue
                subject = resolve_choice(subjects, arg, kind="subject")
                if subject:
                    explore_subject_menu(target_user, subject)
            else:
                console.print("[red]Unknown command. Type / to see the available commands.[/red]")
                input("Press Enter to continue...")

        except Exception as e:
            handle_error(e)
            input("Press Enter to continue...")


def explore_subject_menu(target_user, subject):
    prompt = SlashPrompt(EXPLORE_SUBJECT_COMMANDS)

    while True:
        try:
            clear_screen()
            notes = list_notes(target_user, subject)
            display_notes(notes, subject)
            console.print()
            print_help(EXPLORE_SUBJECT_COMMANDS, "Commands (type / for live suggestions)")

            name, arg = parse_command(prompt.ask())
            if name is None:
                continue

            if name == "/back":
                break
            elif name == "/help":
                print_help(EXPLORE_SUBJECT_COMMANDS, f"{subject} (read-only)")
                input("Press Enter to continue...")
            elif name == "/read":
                if not arg:
                    console.print("[red]Type /read followed by a note name or number[/red]")
                    input("Press Enter to continue...")
                    continue
                filename = resolve_choice(notes, arg, kind="note")
                if filename:
                    view_file_rich(target_user, subject, filename)
            else:
                console.print("[red]Unknown command. Type / to see the available commands.[/red]")
                input("Press Enter to continue...")

        except Exception as e:
            handle_error(e)
            input("Press Enter to continue...")


def render_bar(value, max_value, width=24):
    filled = int(width * value / max_value) if max_value else 0
    return "█" * filled + "░" * (width - filled)


STREAK_MILESTONES = {7, 30, 100}


def show_stats(user_folder):
    data = stats.user_stats(user_folder)
    scale = max(data["subjects"], data["notes"], 10)
    console.print(Panel(f"[bold cyan]📊 Study Stats — {user_folder}[/bold cyan]", expand=False))
    console.print(f"Subjects  {render_bar(data['subjects'], scale)}  {data['subjects']}")
    console.print(f"Notes     {render_bar(data['notes'], scale)}  {data['notes']}")
    streak_line = f"🔥 Streak  {data['streak']} day(s)"
    if data["last_active"]:
        streak_line += f" (last active {data['last_active']})"
    console.print(streak_line)

    days = stats.daily_activity(user_folder, days=7)
    day_labels = " ".join(datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a")[0] for d in days)
    day_bars = " ".join("█" if d["active"] else "░" for d in days)
    console.print()
    console.print(f"Last 7 days   {day_labels}")
    console.print(f"              {day_bars}")

    if data["streak"] in STREAK_MILESTONES:
        animations.streak_fire(console, data["streak"], f"{data['streak']}-day streak! Keep it going!")


def show_leaderboard():
    rows = stats.all_user_stats()
    if not rows:
        console.print("[yellow]No known users yet - create a subject under a personal user folder first.[/yellow]")
        return
    rows.sort(key=lambda s: (s["streak"], s["notes"]), reverse=True)
    table = Table(title="🏆 Leaderboard", show_header=True, header_style="bold magenta")
    table.add_column("Rank", justify="right", width=4)
    table.add_column("User", width=20)
    table.add_column("🔥 Streak", justify="right", width=10)
    table.add_column("Notes", justify="right", width=8)
    table.add_column("Subjects", justify="right", width=8)
    for i, s in enumerate(rows, 1):
        table.add_row(str(i), s["user"], str(s["streak"]), str(s["notes"]), str(s["subjects"]))
    console.print(table)


def _parse_ts(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def show_digest():
    me = community.current_username()
    now = datetime.now(timezone.utc)
    since_feed = local_state.get_last_seen("feed")
    since_chat = local_state.get_last_seen("chat")
    since_feed_dt = _parse_ts(since_feed) if since_feed else None
    since_chat_dt = _parse_ts(since_chat) if since_chat else None

    console.print(Panel("[bold cyan]📰 What's new since your last visit[/bold cyan]", expand=False))

    feed_items, err = community.list_feed()
    if err:
        console.print(f"[red]{err}[/red]")
    else:
        new_posts = [i for i in feed_items if not since_feed_dt or _parse_ts(i["createdAt"]) > since_feed_dt]
        new_comments = sum(
            1 for i in feed_items for c in i["comments"]["nodes"]
            if not since_feed_dt or _parse_ts(c["createdAt"]) > since_feed_dt
        )
        console.print(f"[green]{len(new_posts)} new post(s), {new_comments} new comment(s) on the feed[/green]")

    threads, err = community.list_my_chat_threads(me)
    if err:
        console.print(f"[red]{err}[/red]")
    else:
        any_chat_news = False
        for t in threads:
            new_msgs = [
                c for c in t["comments"]["nodes"]
                if (not since_chat_dt or _parse_ts(c["createdAt"]) > since_chat_dt)
                and (c["author"]["login"] if c["author"] else "ghost") != me
            ]
            if new_msgs:
                any_chat_news = True
                other = t["title"][len(community.CHAT_PREFIX):]
                console.print(f"[cyan]💬 {len(new_msgs)} new message(s) in chat: {other}[/cyan]")
        if not any_chat_news:
            console.print("[dim]No new chat messages.[/dim]")

    local_state.set_last_seen("feed", now.isoformat())
    local_state.set_last_seen("chat", now.isoformat())


def _parse_pomodoro_minutes(arg):
    if not arg:
        return pomodoro.DEFAULT_MINUTES
    try:
        minutes = float(arg.strip())
        return minutes if minutes > 0 else pomodoro.DEFAULT_MINUTES
    except ValueError:
        return pomodoro.DEFAULT_MINUTES


def pomodoro_flow(minutes):
    label = "Focus session"
    completed = pomodoro.run_countdown(console, minutes=minutes, label=label)
    if completed:
        pomodoro.send_desktop_notification("CLI Study Hub", f"{label} complete - take a break!")
        animations.celebrate(console, "Pomodoro complete - nice focus!")
    input("Press Enter to continue...")


def export_flow(user_folder, fmt):
    data = exporter.build_export(user_folder)
    who = user_folder or "global"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"study-hub-export-{who}-{timestamp}.{fmt}"
    content = exporter.to_csv(data) if fmt == "csv" else exporter.to_json(data)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[green]✅ Exported {len(data['subjects'])} subject(s) to {filename}[/green]")
    except OSError as e:
        console.print(f"[red]❌ Couldn't write {filename}: {e}[/red]")
    input("Press Enter to continue...")


def search_menu(user_folder, term):
    prompt = SlashPrompt(SEARCH_COMMANDS)
    results, truncated = search.search_notes(term, user_folder)

    while True:
        try:
            clear_screen()
            console.print(Panel(f"[bold cyan]🔍 Search results for '{term}'[/bold cyan]", expand=False))
            if not results:
                console.print("[yellow]No matches found.[/yellow]")
            else:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("No.", justify="right", width=4)
                table.add_column("Owner", width=14)
                table.add_column("Subject / File", width=32)
                table.add_column("At", width=10)
                table.add_column("Snippet", width=44)
                for i, r in enumerate(results, 1):
                    owner_label = r["owner"] or ("you" if user_folder else "global")
                    at = f"{r['location_kind']} {r['location']}" if r["location"] else "-"
                    table.add_row(str(i), owner_label, f"{r['subject']}/{r['filename']}", at, r["snippet"])
                console.print(table)
                if truncated:
                    console.print("[dim]Results truncated - refine your search term for more precise matches.[/dim]")
            console.print()
            print_help(SEARCH_COMMANDS, "Commands (type / for live suggestions)")

            name, arg = parse_command(prompt.ask())
            if name is None:
                continue

            if name == "/back":
                break
            elif name == "/help":
                print_help(SEARCH_COMMANDS, "Search Commands")
                input("Press Enter to continue...")
            elif name == "/open":
                if not arg.isdigit() or not (1 <= int(arg) <= len(results)):
                    console.print(f"[red]Invalid result number! Choose 1-{len(results)}[/red]")
                    input("Press Enter to continue...")
                    continue
                r = results[int(arg) - 1]
                view_file_rich(r["owner"] or user_folder, r["subject"], r["filename"], jump_to=r["location"])
            else:
                console.print("[red]Unknown command. Type / to see the available commands.[/red]")
                input("Press Enter to continue...")

        except Exception as e:
            handle_error(e)
            input("Press Enter to continue...")


def quiz_menu(user_folder, subject):
    """Quiz yourself on a subject: flashcards (Q:/A: pairs in your notes,
    always free) and/or AI-generated multiple choice (BYOK ANTHROPIC_API_KEY)."""
    flashcards = quiz.collect_flashcards(user_folder, subject)
    ai_available = quiz.is_ai_configured()

    if not flashcards and not ai_available:
        console.print(Panel(
            "[bold yellow]No quiz material yet[/bold yellow]\n\n"
            "Add flashcards to any note in this subject with lines like:\n"
            "  Q: Your question here\n"
            "  A: Your answer here\n\n"
            "Or set ANTHROPIC_API_KEY to generate multiple-choice questions "
            "from your free-form notes automatically (bring your own key - "
            "see the README's '/quiz' section).",
            expand=False,
        ))
        input("Press Enter to continue...")
        return

    mode = "flashcards"
    if flashcards and ai_available:
        mode = Prompt.ask("[yellow]Quiz mode[/yellow]", choices=["flashcards", "ai"], default="flashcards")
    elif ai_available and not flashcards:
        mode = "ai"

    questions = flashcards
    if mode == "ai":
        notes_text = quiz.collect_notes_text(user_folder, subject)
        generated, err = animations.with_spinner(
            console, "🤖 Generating quiz questions...", quiz.generate_ai_questions, subject, notes_text
        )
        if err:
            console.print(f"[red]❌ {err}[/red]")
            if not flashcards:
                input("Press Enter to continue...")
                return
            console.print("[yellow]Falling back to your flashcards instead.[/yellow]")
            input("Press Enter to continue...")
            mode = "flashcards"
        else:
            questions = generated

    if not questions:
        console.print("[yellow]Nothing to quiz on.[/yellow]")
        input("Press Enter to continue...")
        return

    srs_state = None
    if mode == "flashcards":
        srs_state = srs.load_state(user_folder, subject)
        all_ids = [srs.card_id(q["question"]) for q in questions]
        due_ids = set(srs.due_card_ids(srs_state, all_ids))
        due_questions = [q for q, cid in zip(questions, all_ids) if cid in due_ids]
        if due_questions and len(due_questions) < len(questions):
            console.print(f"[cyan]📅 {len(due_questions)}/{len(questions)} card(s) due for review today.[/cyan]")
            if Prompt.ask("[yellow]Study just the due cards?[/yellow]", choices=["yes", "no"], default="yes") == "yes":
                questions = due_questions
        elif due_questions:
            questions = due_questions

    questions = list(questions)
    random.shuffle(questions)
    total = len(questions)
    score = 0

    console.print(Panel(f"[bold cyan]🎮 Quiz: {subject}[/bold cyan] ({mode}, {total} question(s))", expand=False))
    input("Press Enter to start...")

    for i, q in enumerate(questions, 1):
        clear_screen()
        console.print(Panel(f"[bold cyan]Question {i}/{total}[/bold cyan]", expand=False))
        console.print(q["question"])
        console.print()

        if mode == "ai":
            for idx, choice_text in enumerate(q["choices"], 1):
                console.print(f"  {idx}. {choice_text}")
            console.print()
            answer = Prompt.ask("[yellow]Your answer[/yellow]", choices=[str(n) for n in range(1, len(q["choices"]) + 1)])
            if int(answer) - 1 == q["answer_index"]:
                score += 1
                animations.celebrate(console, "Correct!")
            else:
                console.print(f"[red]❌ Not quite - the answer was: {q['choices'][q['answer_index']]}[/red]")
                input("Press Enter to continue...")
        else:
            input("[dim]Press Enter to reveal the answer...[/dim]")
            console.print(f"[cyan]A:[/cyan] {q['answer']}")
            quality = int(Prompt.ask(
                "[yellow]How well did you recall it?[/yellow] (1=blackout, 3=hesitated, 5=perfect)",
                choices=["1", "2", "3", "4", "5"], default="4",
            ))
            if srs_state is not None:
                cid = srs.card_id(q["question"])
                record = srs.review_card(srs_state, cid, quality)
                console.print(f"[dim]Next review: {record['next_review_date']}[/dim]")
            if quality >= 3:
                score += 1
                console.print("[green]✅ Nice![/green]")
            else:
                console.print("[yellow]No worries - it'll come up again sooner next time.[/yellow]")
            input("Press Enter to continue...")

    if srs_state is not None:
        srs.save_state(user_folder, subject, srs_state)

    clear_screen()
    pct = round(100 * score / total) if total else 0
    console.print(Panel(f"[bold cyan]🏁 Quiz complete: {subject}[/bold cyan]", expand=False))
    console.print(f"Score: {score}/{total} ({pct}%)")
    if pct == 100:
        animations.trophy_fireworks(console, "Perfect score!")
    elif pct >= 80:
        animations.pet_run(console, "Great job!")
    input("Press Enter to continue...")


def format_reactions(groups):
    parts = []
    for g in groups or []:
        count = g["reactors"]["totalCount"]
        if count == 0:
            continue
        emoji = community.REACTION_EMOJI.get(g["content"], g["content"])
        marker = "*" if g["viewerHasReacted"] else ""
        parts.append(f"{emoji}{count}{marker}")
    return "  ".join(parts)


def resolve_feed_target(items, index_str):
    """'2' -> the post itself; '2.1' -> comment 1 of post 2. Returns
    (item_dict, kind) where kind is 'post' or 'comment', or (None, None)."""
    post_part, _, comment_part = index_str.partition(".")
    if not post_part.isdigit() or not (1 <= int(post_part) <= len(items)):
        return None, None
    post = items[int(post_part) - 1]
    if not comment_part:
        return post, "post"
    comments = post["comments"]["nodes"]
    if not comment_part.isdigit() or not (1 <= int(comment_part) <= len(comments)):
        return None, None
    return comments[int(comment_part) - 1], "comment"


def display_feed(items):
    if not items:
        console.print("[yellow]No posts yet. Be the first with /post![/yellow]")
        return
    for i, item in enumerate(items, 1):
        author = item["author"]["login"] if item["author"] else "ghost"
        text = item.get("body") or item["title"]
        reactions = format_reactions(item.get("reactionGroups"))
        header = f"#{i} · @{author} · {item['createdAt']}" + (f" · {reactions}" if reactions else "")

        body = text
        comments = item["comments"]["nodes"]
        if comments:
            body += "\n\n[dim]Comments:[/dim]"
            for j, c in enumerate(comments, 1):
                c_author = c["author"]["login"] if c["author"] else "ghost"
                c_reactions = format_reactions(c.get("reactionGroups"))
                body += f"\n  [bold]{i}.{j}[/bold] [cyan]@{c_author}[/cyan]: {c['body']}"
                if c_reactions:
                    body += f"  {c_reactions}"

        console.print(Panel(body, title=header, expand=False))


def feed_menu():
    """Global knowledge feed - read/write via GitHub Discussions, so any
    logged-in GitHub account can post/comment with no repo permissions
    and no merge conflicts (there's no file being shared)."""
    if not community.is_logged_in():
        console.print("[yellow]Run /login first to use the global feed.[/yellow]")
        input("Press Enter to continue...")
        return

    prompt = SlashPrompt(FEED_COMMANDS)
    items = []

    def refresh():
        nonlocal items
        result, err = animations.with_spinner(console, "📰 Loading feed...", community.list_feed)
        if err:
            console.print(f"[red]❌ {err}[/red]")
            items = []
        else:
            items = result

    refresh()

    while True:
        try:
            clear_screen()
            console.print(Panel("[bold cyan]📰 Global Knowledge Feed[/bold cyan]", expand=False))
            display_feed(items)
            console.print()
            print_help(FEED_COMMANDS, "Commands (type / for live suggestions)")

            name, arg = parse_command(prompt.ask())
            if name is None:
                continue

            if name == "/back":
                break
            elif name == "/help":
                print_help(FEED_COMMANDS, "Feed Commands")
                input("Press Enter to continue...")
            elif name == "/refresh":
                refresh()
            elif name == "/post":
                text = Prompt.ask("[yellow]What do you want to share?[/yellow]").strip()
                if not text:
                    console.print("[red]⚠️ Post cannot be empty![/red]")
                else:
                    is_first_post = not items
                    _, err = community.post_to_feed(text)
                    if err:
                        console.print(f"[red]❌ {err}[/red]")
                    else:
                        if is_first_post:
                            animations.confetti_rain(console, "Your first post is live on the feed!")
                        else:
                            console.print("[green]✅ Posted![/green]")
                        refresh()
                input("Press Enter to continue...")
            elif name == "/comment":
                if not arg or " " not in arg:
                    console.print("[red]Type /comment followed by a number, then your text[/red]")
                    input("Press Enter to continue...")
                    continue
                index_str, text = arg.split(" ", 1)
                if not index_str.isdigit() or not (1 <= int(index_str) <= len(items)):
                    console.print(f"[red]⚠️ Invalid post number! Choose 1-{len(items)}[/red]")
                    input("Press Enter to continue...")
                    continue
                target = items[int(index_str) - 1]
                _, err = community.comment_on_feed_post(target["id"], text.strip())
                if err:
                    console.print(f"[red]❌ {err}[/red]")
                else:
                    console.print("[green]✅ Comment added![/green]")
                    refresh()
                input("Press Enter to continue...")
            elif name == "/react":
                parts = arg.split(" ", 1)
                if len(parts) != 2:
                    console.print("[red]Type /react followed by a number, then an emoji name (thumbsup, heart, laugh, hooray, confused, rocket, or eyes)[/red]")
                    input("Press Enter to continue...")
                    continue
                index_str, emoji_name = parts
                content = community.normalize_reaction(emoji_name)
                target, kind = resolve_feed_target(items, index_str)
                if not target or not content:
                    console.print("[red]Type /react followed by a post number (or post.comment, e.g. 2.1), then an emoji name[/red]")
                    input("Press Enter to continue...")
                    continue
                currently = community.has_reacted(target, content)
                _, err = community.toggle_reaction(target["id"], content, currently)
                if err:
                    console.print(f"[red]{err}[/red]")
                else:
                    refresh()
            else:
                console.print("[red]Unknown command. Type / to see the available commands.[/red]")
                input("Press Enter to continue...")

        except Exception as e:
            handle_error(e)
            input("Press Enter to continue...")


def display_chat(thread, me):
    comments = thread["comments"]["nodes"]
    if not comments:
        console.print("[yellow]No messages yet. Say hello with /say![/yellow]")
        return
    for i, c in enumerate(comments, 1):
        author = c["author"]["login"] if c["author"] else "ghost"
        who = "[green]You[/green]" if author == me else f"[cyan]@{author}[/cyan]"
        reactions = format_reactions(c.get("reactionGroups"))
        console.print(f"[bold]{i}[/bold] {who} · [dim]{c['createdAt']}[/dim]\n  {c['body']}" + (f"  {reactions}" if reactions else "") + "\n")


def chat_menu(other_username):
    """Async chat over a GitHub Discussion thread - not real-time, but
    permission-less and conflict-free like the rest of the community layer.
    Run /refresh (or just re-open /chat later) to pick up new replies."""
    if not community.is_logged_in():
        console.print("[yellow]Run /login first to chat.[/yellow]")
        input("Press Enter to continue...")
        return

    me = community.current_username()
    if me and me.lower() == other_username.lower():
        console.print("[yellow]You can't chat with yourself.[/yellow]")
        input("Press Enter to continue...")
        return

    prompt = SlashPrompt(CHAT_COMMANDS)
    thread = {"id": None, "comments": {"nodes": []}}

    def refresh():
        nonlocal thread
        result, err = animations.with_spinner(
            console, "💬 Checking for messages...", community.get_or_create_chat_thread, me, other_username
        )
        if err:
            console.print(f"[red]❌ {err}[/red]")
        else:
            thread = result

    refresh()

    while True:
        try:
            clear_screen()
            console.print(Panel(
                f"[bold cyan]💬 Chat with @{other_username}[/bold cyan]\n"
                "[dim]Async - messages sync whenever either of you runs /chat or /refresh[/dim]",
                expand=False,
            ))
            display_chat(thread, me)
            console.print()
            print_help(CHAT_COMMANDS, "Commands (type / for live suggestions)")

            name, arg = parse_command(prompt.ask())
            if name is None:
                continue

            if name == "/back":
                break
            elif name == "/help":
                print_help(CHAT_COMMANDS, f"Chat with @{other_username}")
                input("Press Enter to continue...")
            elif name == "/refresh":
                refresh()
            elif name == "/say":
                if not arg:
                    console.print("[red]Type /say followed by your message[/red]")
                    input("Press Enter to continue...")
                    continue
                if not thread.get("id"):
                    console.print("[red]Chat thread isn't ready yet - try /refresh.[/red]")
                    input("Press Enter to continue...")
                    continue
                _, err = community.send_chat_message(thread["id"], arg)
                if err:
                    console.print(f"[red]{err}[/red]")
                else:
                    refresh()
            elif name == "/react":
                parts = arg.split(" ", 1)
                messages = thread["comments"]["nodes"]
                if len(parts) != 2 or not parts[0].isdigit() or not (1 <= int(parts[0]) <= len(messages)):
                    console.print("[red]Type /react followed by a message number, then an emoji name (thumbsup, heart, laugh, hooray, confused, rocket, or eyes)[/red]")
                    input("Press Enter to continue...")
                    continue
                index_str, emoji_name = parts
                content = community.normalize_reaction(emoji_name)
                if not content:
                    console.print("[red]Unknown emoji. Try: thumbsup, heart, laugh, hooray, confused, rocket, eyes[/red]")
                    input("Press Enter to continue...")
                    continue
                target = messages[int(index_str) - 1]
                currently = community.has_reacted(target, content)
                _, err = community.toggle_reaction(target["id"], content, currently)
                if err:
                    console.print(f"[red]{err}[/red]")
                else:
                    refresh()
            else:
                console.print("[red]Unknown command. Type / to see the available commands.[/red]")
                input("Press Enter to continue...")

        except Exception as e:
            handle_error(e)
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
