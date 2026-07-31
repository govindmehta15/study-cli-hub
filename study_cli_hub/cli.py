# cli.py - Study CLI Hub v5.0 entry point
import atexit
import os
import signal
import subprocess
import sys
from datetime import datetime

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from study_cli_hub import github_auth
from study_cli_hub.completer import SlashCompleter
from study_cli_hub.doc_repair import repair_document
from study_cli_hub.error_handler import handle_error
from study_cli_hub.file_uploader import upload_file
from study_cli_hub.file_viewer import view_file_rich
from study_cli_hub.paths import note_path, subject_path

console = Console()

MAIN_COMMANDS = [
    ("/study", "<name|number>", "Open a subject"),
    ("/create-subject", "", "Create a new subject"),
    ("/list", "", "Refresh the subjects list"),
    ("/switch-user", "", "Switch user folder or global mode"),
    ("/login", "", "Connect your GitHub account"),
    ("/logout", "", "Disconnect your GitHub account"),
    ("/whoami", "", "Show the connected GitHub account"),
    ("/sync", "", "Pull + push notes with GitHub now"),
    ("/help", "", "Show available commands"),
    ("/exit", "", "Exit (auto-syncs with GitHub)"),
]

SUBJECT_COMMANDS = [
    ("/read", "<note|number>", "Open a note in the interactive reader"),
    ("/edit", "<note|number>", "Edit a note with reason tracking"),
    ("/new-note", "", "Create a new note file"),
    ("/upload", "", "Upload a file via the file browser"),
    ("/repair", "<path>", "Diagnose a Word document's issues"),
    ("/help", "", "Show available commands"),
    ("/back", "", "Return to the subjects menu"),
]

# Global flag to track if auto-push has been done
auto_push_done = False


class SlashPrompt:
    """A '/' command prompt with a live, prefix-filtered menu (falls back to
    plain input when not attached to a real terminal, e.g. in scripts/CI)."""

    def __init__(self, commands):
        self.completer = SlashCompleter(commands)
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


def print_help(commands, title):
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

        console.print(Panel("[bold cyan]Auto GitHub Sync[/bold cyan]", expand=False))
        console.print("[yellow]Pulling latest changes...[/yellow]")
        pull_result = github_auth.git_pull()
        if pull_result.returncode == 0:
            console.print("[green]Successfully pulled latest changes[/green]")
        else:
            console.print("[yellow]Pull failed (normal if no remote exists, or run /login)[/yellow]")
    except FileNotFoundError:
        console.print("[yellow]Git not found - GitHub sync features disabled[/yellow]")
    except Exception as e:
        console.print(f"[yellow]GitHub sync error: {e}[/yellow]")


def auto_git_push():
    """Commit and push changes to GitHub, using a stored login token if present."""
    try:
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=os.getcwd())
        if status.returncode != 0:
            return
        if not status.stdout.strip():
            console.print("[green]No changes to push[/green]")
            return

        console.print(Panel("[bold cyan]Auto Push to GitHub[/bold cyan]", expand=False))
        subprocess.run(["git", "add", "."], capture_output=True, text=True, cwd=os.getcwd())

        commit_message = f"Auto-sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        commit_result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True, cwd=os.getcwd())
        if commit_result.returncode != 0:
            console.print("[yellow]Nothing to commit[/yellow]")
            return

        console.print("[yellow]Pushing to GitHub...[/yellow]")
        push_result = github_auth.git_push()
        if push_result.returncode == 0:
            console.print("[green]Successfully pushed to GitHub[/green]")
        else:
            reason = push_result.stderr.strip() or "check your GitHub login (/login) or remote permissions"
            console.print(f"[yellow]Push failed: {reason}[/yellow]")
    except FileNotFoundError:
        console.print("[yellow]Git not found - auto push skipped[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Auto push error: {e}[/yellow]")


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


def list_subjects(user_folder=None):
    """Get list of subjects for current user"""
    path = subject_path(user_folder)
    os.makedirs(path, exist_ok=True)
    subjects = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return sorted(subjects)


def list_notes(user_folder, subject):
    """Get list of notes in a subject"""
    path = subject_path(user_folder, subject)
    os.makedirs(path, exist_ok=True)
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files = [f for f in files if not f.startswith(".") and f != "edit_log.txt"]
    return sorted(files)


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
    """Create a new subject with description"""
    try:
        name = Prompt.ask("[yellow]Enter new subject name[/yellow]").strip()
        if not name:
            console.print("[red]Subject name cannot be empty![/red]")
            return

        path = subject_path(user_folder, name)
        if os.path.exists(path):
            console.print(f"[red]Subject '{name}' already exists![/red]")
            return

        os.makedirs(path, exist_ok=True)
        description = Prompt.ask("[yellow]Enter short description[/yellow]").strip()
        with open(os.path.join(path, f"description_{name}.txt"), "w", encoding="utf-8") as f:
            f.write(description)
        console.print(f"[green]Subject '{name}' created successfully![/green]")
    except Exception as e:
        handle_error(e)


def create_new_note(user_folder, subject):
    """Create a new note file"""
    try:
        filename = Prompt.ask("[yellow]Enter new note filename[/yellow]").strip()
        if not filename:
            console.print("[red]Filename cannot be empty![/red]")
            return
        if "." not in filename:
            filename += ".txt"

        path = note_path(user_folder, subject, filename)
        if os.path.exists(path):
            console.print(f"[red]File '{filename}' already exists![/red]")
            return

        content = Prompt.ask("[yellow]Enter initial content (optional)[/yellow]").strip()
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[green]Created new note: {filename}[/green]")
    except Exception as e:
        handle_error(e)


def display_subjects(subjects, user_folder=None):
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
    console.print(Align.center(Panel(Text("Welcome to CLI Study Hub v5.0", style="bold green"), expand=False)))
    console.print()

    auto_git_sync()
    check_git_status()

    user = Prompt.ask("[yellow]Enter your username (press Enter for Global mode)[/yellow]").strip()
    user_folder = user if user else None
    console.print(f"[green]Using {'user folder: ' + user_folder if user_folder else 'global mode'}[/green]")
    console.print()
    input("Press Enter to continue...")

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
                console.print(Panel("[bold green]Thanks for using CLI Study Hub![/bold green]", expand=False))
                global auto_push_done
                auto_push_done = True
                auto_git_push()
                break

            elif name == "/switch-user":
                user = Prompt.ask("[yellow]Enter new username (or press Enter for Global)[/yellow]").strip()
                user_folder = user if user else None
                console.print(f"[green]Switched to {'user: ' + user_folder if user_folder else 'global mode'}[/green]")
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
                    console.print("[red]Usage: /study <name|number>[/red]")
                    input("Press Enter to continue...")
                    continue
                subject = resolve_choice(subjects, arg, kind="subject")
                if subject:
                    subject_menu(user_folder, subject)

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
                    console.print("[red]Usage: /read <note|number>[/red]")
                    input("Press Enter to continue...")
                    continue
                filename = resolve_choice(notes, arg, kind="note")
                if filename:
                    view_file_rich(user_folder, subject, filename)

            elif name == "/edit":
                if not arg:
                    console.print("[red]Usage: /edit <note|number>[/red]")
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
                    console.print("[red]Usage: /repair <path-to-document>[/red]")
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


if __name__ == "__main__":
    main()
