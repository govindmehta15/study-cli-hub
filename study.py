# study.py
import os, sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.align import Align
from file_viewer import view_file_rich
from file_uploader import upload_file
from error_handler import handle_error

console = Console()
SUBJECTS_DIR = "subjects"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def list_subjects(user_folder=None):
    path = os.path.join(SUBJECTS_DIR, user_folder) if user_folder else SUBJECTS_DIR
    os.makedirs(path, exist_ok=True)
    subjects = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return subjects

def list_notes(user_folder, subject):
    path = os.path.join(SUBJECTS_DIR, user_folder, subject) if user_folder else os.path.join(SUBJECTS_DIR, subject)
    os.makedirs(path, exist_ok=True)
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def create_subject(user_folder):
    try:
        name = Prompt.ask("[yellow]Enter new subject name[/yellow]").strip()
        if not name:
            console.print("[red]Subject name cannot be empty![/red]")
            return
        path = os.path.join(SUBJECTS_DIR, user_folder, name) if user_folder else os.path.join(SUBJECTS_DIR, name)
        os.makedirs(path, exist_ok=True)
        desc_file = os.path.join(path, f"description_{name}.txt")
        with open(desc_file, "w") as f:
            f.write(Prompt.ask("Enter short description"))
        console.print(f"[green]Subject '{name}' created successfully![/green]")
    except Exception as e:
        handle_error(e)

def select_subject(subjects):
    table = Table(title="Subjects Available", show_header=True, header_style="bold magenta")
    table.add_column("No.", justify="right")
    table.add_column("Subject Name")
    for i, sub in enumerate(subjects, 1):
        table.add_row(str(i), sub)
    console.print(table)
    choice = Prompt.ask("[yellow]Enter subject number or command[/yellow]")
    return choice

def select_note(notes):
    table = Table(title="Notes Available", show_header=True, header_style="bold cyan")
    table.add_column("No.", justify="right")
    table.add_column("Filename")
    for i, n in enumerate(notes, 1):
        ext_color = {
            "txt":"green",
            "md":"cyan",
            "py":"magenta",
            "csv":"yellow",
            "pdf":"red",
            "docx":"blue"
        }.get(n.split(".")[-1].lower(), "white")
        table.add_row(str(i), f"[{ext_color}]{n}[/{ext_color}]")
    console.print(table)
    cmd = Prompt.ask("[yellow]Enter command[/yellow]")
    return cmd

def main():
    clear_screen()
    console.print(Panel("[bold green]👋 Welcome to CLI Study Hub v3.1[/bold green]", expand=False))
    user = Prompt.ask("Enter your username (press Enter for Global mode)").strip()
    user_folder = user if user else None

    while True:
        try:
            subjects = list_subjects(user_folder)
            cmd = select_subject(subjects)
            if cmd.lower() == "exit":
                console.print("[green]Exiting... Remember to git add/commit/push![/green]")
                break
            elif cmd.lower() == "switch user":
                user = Prompt.ask("Enter new username").strip()
                user_folder = user if user else None
            elif cmd.lower() == "create subject":
                create_subject(user_folder)
            elif cmd.isdigit() and 0 < int(cmd) <= len(subjects):
                subject = subjects[int(cmd)-1]
                while True:
                    notes = list_notes(user_folder, subject)
                    note_cmd = select_note(notes)
                    if note_cmd.lower() == "back":
                        break
                    elif note_cmd.startswith("read ") or note_cmd.startswith("view pdf ") or note_cmd.startswith("view doc ") or note_cmd.startswith("analyze csv "):
                        filename = note_cmd.split(" ", 1)[1].strip()
                        view_file_rich(user_folder, subject, filename)
                    elif note_cmd.lower() == "upload note":
                        upload_file(user_folder, subject)
                    else:
                        console.print("[red]Invalid command[/red]")
            else:
                console.print("[red]Invalid choice[/red]")
        except Exception as e:
            handle_error(e)

if __name__ == "__main__":
    main()
