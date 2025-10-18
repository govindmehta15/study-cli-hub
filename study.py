# study.py - CLI Study Hub v4.0
import os, sys, subprocess, signal, atexit
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.align import Align

# Force install ALL dependencies on startup
try:
    from dependency_checker import force_install_all_dependencies
    console = Console()
    console.print(Panel("[bold cyan]🚀 CLI Study Hub - Ensuring All Dependencies[/bold cyan]", expand=False))
    
    if not force_install_all_dependencies():
        console.print(Panel("[bold red]❌ Failed to install dependencies. Please check your internet connection.[/bold red]", expand=False))
        sys.exit(1)
    
    console.print(Panel("[bold green]✅ All dependencies ready! Starting application...[/bold green]", expand=False))
    
except ImportError:
    print("Warning: dependency_checker.py not found")
    # Fallback: try to install requirements.txt
    try:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    except:
        print("Failed to install dependencies automatically")

from file_viewer import view_file_rich
from file_uploader import upload_file
from error_handler import handle_error

console = Console()
SUBJECTS_DIR = "subjects"

# Global flag to track if auto-push has been done
auto_push_done = False

def cleanup_and_push():
    """Cleanup function to auto-push on exit"""
    global auto_push_done
    if not auto_push_done:
        try:
            console.print("\n[yellow]🔄 Auto-saving changes...[/yellow]")
            auto_git_push()
            auto_push_done = True
        except:
            pass

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    console.print("\n[yellow]🔄 Auto-saving changes before exit...[/yellow]")
    cleanup_and_push()
    sys.exit(0)

# Register cleanup functions
atexit.register(cleanup_and_push)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def git_sync_prompt(action="start"):
    """Show GitHub sync recommendations"""
    console.print(Panel(f"[bold magenta]🔄 GitHub Sync — {action.upper()}[/bold magenta]", expand=False))
    if action == "start":
        console.print("💡 [yellow]Recommended before starting:[/yellow]")
        console.print("   [cyan]git pull --rebase[/cyan]  (fetch latest updates)")
        console.print()
        console.print("💡 [yellow]Recommended after finishing:[/yellow]")
        console.print("   [cyan]git add . && git commit -m 'Update notes' && git push[/cyan]")
    else:
        console.print("💡 [yellow]Don't forget to sync your changes:[/yellow]")
        console.print("   [cyan]git add . && git commit -m 'Update notes' && git push[/cyan]")
    console.print()

def auto_git_sync():
    """Automatically sync with GitHub - pull updates and push changes"""
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            console.print("[yellow]⚠️ Not in a git repository - GitHub sync skipped[/yellow]")
            return True
        
        console.print(Panel("[bold cyan]🔄 Auto GitHub Sync[/bold cyan]", expand=False))
        
        # Pull latest changes
        console.print("[yellow]📥 Pulling latest changes...[/yellow]")
        pull_result = subprocess.run(['git', 'pull', '--rebase'], 
                                   capture_output=True, text=True, cwd=os.getcwd())
        if pull_result.returncode == 0:
            console.print("[green]✅ Successfully pulled latest changes[/green]")
        else:
            console.print("[yellow]⚠️ Pull failed (this is normal if no remote exists)[/yellow]")
        
        return True
        
    except FileNotFoundError:
        console.print("[yellow]⚠️ Git not found - GitHub sync features disabled[/yellow]")
        return True
    except Exception as e:
        console.print(f"[yellow]⚠️ GitHub sync error: {e}[/yellow]")
        return True

def auto_git_push():
    """Automatically push changes to GitHub"""
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            return True
        
        # Check if there are changes to commit
        if not result.stdout.strip():
            console.print("[green]✅ No changes to push[/green]")
            return True
        
        console.print(Panel("[bold cyan]📤 Auto Push to GitHub[/bold cyan]", expand=False))
        
        # Add all changes
        console.print("[yellow]📝 Adding changes...[/yellow]")
        add_result = subprocess.run(['git', 'add', '.'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
        if add_result.returncode != 0:
            console.print("[red]❌ Failed to add changes[/red]")
            return False
        
        # Commit changes
        console.print("[yellow]💾 Committing changes...[/yellow]")
        commit_message = f"Auto-sync: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}"
        commit_result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                     capture_output=True, text=True, cwd=os.getcwd())
        if commit_result.returncode != 0:
            console.print("[yellow]⚠️ Nothing to commit (no changes)[/yellow]")
            return True
        
        # Push changes
        console.print("[yellow]🚀 Pushing to GitHub...[/yellow]")
        push_result = subprocess.run(['git', 'push'], 
                                   capture_output=True, text=True, cwd=os.getcwd())
        if push_result.returncode == 0:
            console.print("[green]✅ Successfully pushed to GitHub[/green]")
        else:
            console.print("[yellow]⚠️ Push failed (this is normal if no remote exists)[/yellow]")
        
        return True
        
    except FileNotFoundError:
        console.print("[yellow]⚠️ Git not found - auto push skipped[/yellow]")
        return True
    except Exception as e:
        console.print(f"[yellow]⚠️ Auto push error: {e}[/yellow]")
        return True

def check_git_status():
    """Check if we're in a git repository and show status"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            if result.stdout.strip():
                console.print("[yellow]⚠️ You have uncommitted changes[/yellow]")
                console.print("[dim]These will be auto-committed and pushed on exit[/dim]")
            else:
                console.print("[green]✅ Working directory is clean[/green]")
        else:
            console.print("[yellow]⚠️ Not in a git repository[/yellow]")
    except FileNotFoundError:
        console.print("[yellow]⚠️ Git not found - GitHub sync features disabled[/yellow]")

def list_subjects(user_folder=None):
    """Get list of subjects for current user"""
    path = os.path.join(SUBJECTS_DIR, user_folder) if user_folder else SUBJECTS_DIR
    os.makedirs(path, exist_ok=True)
    subjects = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return sorted(subjects)

def list_notes(user_folder, subject):
    """Get list of notes in a subject"""
    path = os.path.join(SUBJECTS_DIR, user_folder, subject) if user_folder else os.path.join(SUBJECTS_DIR, subject)
    os.makedirs(path, exist_ok=True)
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    # Filter out backup and log files
    files = [f for f in files if not f.startswith('.') and not f.endswith('.backup_') and f != 'edit_log.txt']
    return sorted(files)

def create_subject(user_folder):
    """Create a new subject with description"""
    try:
        name = Prompt.ask("[yellow]Enter new subject name[/yellow]").strip()
        if not name:
            console.print("[red]Subject name cannot be empty![/red]")
            return
        
        # Check if subject already exists
        path = os.path.join(SUBJECTS_DIR, user_folder, name) if user_folder else os.path.join(SUBJECTS_DIR, name)
        if os.path.exists(path):
            console.print(f"[red]Subject '{name}' already exists![/red]")
            return
            
        os.makedirs(path, exist_ok=True)
        desc_file = os.path.join(path, f"description_{name}.txt")
        description = Prompt.ask("[yellow]Enter short description[/yellow]").strip()
        with open(desc_file, "w", encoding="utf-8") as f:
            f.write(description)
        console.print(f"[green]✅ Subject '{name}' created successfully![/green]")
    except Exception as e:
        handle_error(e)

def create_new_note(user_folder, subject):
    """Create a new note file"""
    try:
        filename = Prompt.ask("[yellow]Enter new note filename[/yellow]").strip()
        if not filename:
            console.print("[red]Filename cannot be empty![/red]")
            return
        
        # Add .txt extension if no extension provided
        if '.' not in filename:
            filename += '.txt'
            
        path = os.path.join(SUBJECTS_DIR, user_folder, subject, filename) if user_folder else os.path.join(SUBJECTS_DIR, subject, filename)
        
        if os.path.exists(path):
            console.print(f"[red]File '{filename}' already exists![/red]")
            return
            
        # Get initial content
        content = Prompt.ask("[yellow]Enter initial content (optional)[/yellow]").strip()
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[green]✅ Created new note: {filename}[/green]")
    except Exception as e:
        handle_error(e)

def display_subjects(subjects, user_folder=None):
    """Display subjects in a rich table"""
    if not subjects:
        console.print("[yellow]No subjects found. Create one with 'create subject'[/yellow]")
        return
        
    table = Table(title=f"📚 Subjects Available {'(User: ' + user_folder + ')' if user_folder else '(Global)'}", 
                  show_header=True, header_style="bold magenta")
    table.add_column("No.", justify="right", width=4)
    table.add_column("Subject Name", width=30)
    table.add_column("Notes", justify="right", width=8)
    
    for i, sub in enumerate(subjects, 1):
        notes_count = len(list_notes(user_folder, sub))
        table.add_row(str(i), sub, str(notes_count))
    
    console.print(table)
    console.print()
    console.print("[blue]Commands:[/blue]")
    console.print("  [cyan]study <subject>[/cyan]     - Open subject (use number or name)")
    console.print("  [cyan]learn <subject>[/cyan]     - Open subject (use number or name)")
    console.print("  [cyan]create subject[/cyan]      - Add new subject")
    console.print("  [cyan]list[/cyan]                - Refresh subjects list")
    console.print("  [cyan]switch user[/cyan]         - Switch user folder")
    console.print("  [cyan]exit[/cyan]                - Exit CLI")

def display_notes(notes, subject):
    """Display notes in a rich table"""
    if not notes:
        console.print("[yellow]No notes found. Create one with 'new note' or upload files[/yellow]")
        return
        
    table = Table(title=f"📝 Notes in {subject}", show_header=True, header_style="bold cyan")
    table.add_column("No.", justify="right", width=4)
    table.add_column("Filename", width=40)
    table.add_column("Type", width=8)
    
    for i, note in enumerate(notes, 1):
        ext = note.split(".")[-1].lower() if "." in note else "txt"
        ext_color = {
            # Text files
            "txt": "green", "md": "cyan", "py": "magenta", "json": "yellow",
            "js": "yellow", "html": "red", "css": "blue", "xml": "green",
            "yaml": "cyan", "yml": "cyan", "ini": "white", "cfg": "white",
            "conf": "white", "log": "red", "sh": "green", "bat": "white", "ps1": "blue",
            # Documents
            "pdf": "red", "doc": "blue", "docx": "blue", "csv": "yellow",
            # Images
            "jpg": "magenta", "jpeg": "magenta", "png": "magenta", "gif": "magenta",
            "bmp": "magenta", "tiff": "magenta", "svg": "magenta", "webp": "magenta",
            # Archives
            "zip": "yellow", "rar": "yellow", "7z": "yellow", "tar": "yellow",
            "gz": "yellow", "bz2": "yellow", "xz": "yellow",
            # Executables
            "exe": "red", "dll": "red", "so": "red", "dylib": "red", "bin": "red",
            # Media
            "mp3": "cyan", "wav": "cyan", "flac": "cyan", "mp4": "cyan",
            "avi": "cyan", "mkv": "cyan", "mov": "cyan", "wmv": "cyan"
        }.get(ext, "white")
        table.add_row(str(i), f"[{ext_color}]{note}[/{ext_color}]", ext.upper())
    
    console.print(table)
    console.print()
    console.print("[blue]Commands:[/blue]")
    console.print("  [cyan]read <note>[/cyan]         - Open note (use number or filename)")
    console.print("  [cyan]edit <note>[/cyan]         - Edit note (use number or filename)")
    console.print("  [cyan]new note[/cyan]            - Create new note")
    console.print("  [cyan]upload[/cyan]              - Upload file via file picker")
    console.print("  [cyan]back[/cyan]                - Return to subjects")

def main():
    """Main CLI application"""
    clear_screen()
    
    # Welcome screen
    welcome_text = Text("👋 Welcome to CLI Study Hub v4.0", style="bold green")
    console.print(Align.center(Panel(welcome_text, expand=False)))
    console.print()
    
    # Automatic GitHub sync
    auto_git_sync()
    check_git_status()
    
    # Get user
    user = Prompt.ask("[yellow]Enter your username (press Enter for Global mode)[/yellow]").strip()
    user_folder = user if user else None
    
    if user_folder:
        console.print(f"[green]✅ Using user folder: {user_folder}[/green]")
    else:
        console.print("[green]✅ Using global mode[/green]")
    
    console.print()
    input("Press Enter to continue...")
    
    # Main loop
    while True:
        try:
            clear_screen()
            subjects = list_subjects(user_folder)
            display_subjects(subjects, user_folder)
            
            cmd = Prompt.ask("\n[yellow]Enter command[/yellow]").strip().lower()
            
            # Exit CLI
            if cmd in ["exit", "quit"]:
                clear_screen()
                console.print(Panel("[bold green]👋 Thanks for using CLI Study Hub![/bold green]", expand=False))
                
                # Auto push changes to GitHub
                global auto_push_done
                auto_push_done = True
                auto_git_push()
                
                break
            
            # Switch user
            elif cmd == "switch user":
                user = Prompt.ask("[yellow]Enter new username (or press Enter for Global)[/yellow]").strip()
                user_folder = user if user else None
                console.print(f"[green]Switched to {'user: ' + user_folder if user_folder else 'global mode'}[/green]")
                input("Press Enter to continue...")
            
            # Create subject
            elif cmd == "create subject":
                create_subject(user_folder)
                input("Press Enter to continue...")
            
            # List subjects (refresh)
            elif cmd == "list":
                continue  # Will redisplay subjects
            
            # Study subject by name or number
            elif cmd.startswith("study "):
                target = cmd.split(" ", 1)[1].strip()
                
                # Check if it's a number (for selecting by index)
                if target.isdigit():
                    subject_index = int(target)
                    if 1 <= subject_index <= len(subjects):
                        subject = subjects[subject_index - 1]
                    else:
                        console.print(f"[red]Invalid subject number! Choose 1-{len(subjects)}[/red]")
                        input("Press Enter to continue...")
                        continue
                else:
                    # It's a subject name
                    if target not in subjects:
                        console.print(f"[red]Subject '{target}' not found![/red]")
                        input("Press Enter to continue...")
                        continue
                    subject = target
                
                subject_menu(user_folder, subject)
            
            # Learn by number (kept for backward compatibility)
            elif cmd.startswith("learn "):
                target = cmd.split(" ", 1)[1].strip()
                
                # Check if it's a number (for selecting by index)
                if target.isdigit():
                    subject_index = int(target)
                    if 1 <= subject_index <= len(subjects):
                        subject = subjects[subject_index - 1]
                    else:
                        console.print(f"[red]Invalid subject number! Choose 1-{len(subjects)}[/red]")
                        input("Press Enter to continue...")
                        continue
                else:
                    # It's a subject name
                    if target not in subjects:
                        console.print(f"[red]Subject '{target}' not found![/red]")
                        input("Press Enter to continue...")
                        continue
                    subject = target
                
                subject_menu(user_folder, subject)
            
            else:
                console.print("[red]Invalid command![/red]")
                input("Press Enter to continue...")
                
        except Exception as e:
            handle_error(e)
            input("Press Enter to continue...")

def subject_menu(user_folder, subject):
    """Handle commands inside a subject"""
    while True:
        try:
            clear_screen()
            notes = list_notes(user_folder, subject)
            display_notes(notes, subject)
            
            note_cmd = Prompt.ask("\n[yellow]Enter command[/yellow]").strip().lower()
            
            if note_cmd == "back":
                break
            
            elif note_cmd.startswith("read "):
                target = note_cmd.split(" ", 1)[1].strip()
                
                # Check if it's a number (for selecting by index)
                if target.isdigit():
                    note_index = int(target)
                    if 1 <= note_index <= len(notes):
                        filename = notes[note_index - 1]
                    else:
                        console.print(f"[red]Invalid note number! Choose 1-{len(notes)}[/red]")
                        input("Press Enter to continue...")
                        continue
                else:
                    # It's a filename
                    filename = target
                    if filename not in notes:
                        console.print(f"[red]Note '{filename}' not found![/red]")
                        input("Press Enter to continue...")
                        continue
                
                view_file_rich(user_folder, subject, filename)
            
            elif note_cmd.startswith("edit "):
                target = note_cmd.split(" ", 1)[1].strip()
                
                # Check if it's a number (for selecting by index)
                if target.isdigit():
                    note_index = int(target)
                    if 1 <= note_index <= len(notes):
                        filename = notes[note_index - 1]
                    else:
                        console.print(f"[red]Invalid note number! Choose 1-{len(notes)}[/red]")
                        input("Press Enter to continue...")
                        continue
                else:
                    # It's a filename
                    filename = target
                    if filename not in notes:
                        console.print(f"[red]Note '{filename}' not found![/red]")
                        input("Press Enter to continue...")
                        continue
                
                view_file_rich(user_folder, subject, filename, editable=True)
                input("Press Enter to continue...")
            
            elif note_cmd == "new note":
                create_new_note(user_folder, subject)
                input("Press Enter to continue...")
            
            elif note_cmd == "upload":
                upload_file(user_folder, subject)
                input("Press Enter to continue...")
            
            else:
                console.print("[red]Invalid command![/red]")
                input("Press Enter to continue...")
                
        except Exception as e:
            handle_error(e)
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
