# file_uploader.py
import os, platform, shutil, subprocess
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from study_cli_hub.animations import glitch_reveal
from study_cli_hub.error_handler import handle_error
from study_cli_hub.paths import subject_path

console = Console()
ALLOWED_FORMATS = [
    # Text files
    "txt", "md", "py", "json", "js", "html", "css", "xml", "yaml", "yml", 
    "ini", "cfg", "conf", "log", "sh", "bat", "ps1",
    # Documents
    "pdf", "doc", "docx", "csv",
    # Images
    "jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg", "webp",
    # Archives
    "zip", "rar", "7z", "tar", "gz", "bz2", "xz",
    # Executables
    "exe", "dll", "so", "dylib", "bin",
    # Media
    "mp3", "wav", "flac", "mp4", "avi", "mkv", "mov", "wmv"
]

def get_file_size(path):
    """Get human readable file size"""
    try:
        size = os.path.getsize(path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "Unknown"

def native_picker_label():
    """What to call the OS's native file picker in prompts."""
    system = platform.system()
    if system == "Darwin":
        return "Finder"
    if system == "Windows":
        return "File Explorer"
    return "file manager"


def open_native_file_picker():
    """Tries to open the OS's native file-picker dialog and returns the
    chosen path, or None if unavailable/cancelled/errored - callers should
    fall back to the in-terminal browser (browse_files) in that case, which
    is exactly what happens over SSH/headless sessions with no GUI."""
    system = platform.system()
    try:
        if system == "Darwin":
            result = subprocess.run(
                ["osascript", "-e", 'POSIX path of (choose file with prompt "Select a file to upload")'],
                capture_output=True, text=True, timeout=180,
            )
            return result.stdout.strip() or None if result.returncode == 0 else None

        if system == "Windows":
            ps_script = (
                "Add-Type -AssemblyName System.Windows.Forms; "
                "$f = New-Object System.Windows.Forms.OpenFileDialog; "
                "$f.Title = 'Select a file to upload'; "
                "if ($f.ShowDialog() -eq 'OK') { Write-Output $f.FileName }"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, text=True, timeout=180,
            )
            return result.stdout.strip() or None

        # Linux: try common native dialogs first
        if shutil.which("zenity"):
            result = subprocess.run(
                ["zenity", "--file-selection", "--title=Select a file to upload"],
                capture_output=True, text=True, timeout=180,
            )
            return result.stdout.strip() or None if result.returncode == 0 else None
        if shutil.which("kdialog"):
            result = subprocess.run(
                ["kdialog", "--getopenfilename"], capture_output=True, text=True, timeout=180,
            )
            return result.stdout.strip() or None if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None

    # Last-resort cross-platform attempt (works if a Tk/Tcl install is
    # present, which isn't guaranteed on minimal/headless systems).
    try:
        import tkinter
        from tkinter import filedialog
        root = tkinter.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(title="Select a file to upload")
        root.destroy()
        return path or None
    except Exception:
        return None


def browse_files(current_dir=None):
    """Interactive file browser"""
    if current_dir is None:
        current_dir = os.path.expanduser("~")  # Start from home directory
    
    while True:
        try:
            # Get directory contents
            items = []
            for item in sorted(os.listdir(current_dir)):
                item_path = os.path.join(current_dir, item)
                if os.path.isdir(item_path):
                    items.append(("📁", item, "Directory", ""))
                elif os.path.isfile(item_path):
                    ext = item.split(".")[-1].lower() if "." in item else ""
                    if ext in ALLOWED_FORMATS:
                        size = get_file_size(item_path)
                        items.append(("📄", item, ext.upper(), size))
                    else:
                        items.append(("📄", item, ext.upper() if ext else "File", get_file_size(item_path)))
            
            # Display current directory
            console.print(Panel(f"[bold cyan]📂 {current_dir}[/bold cyan]", title="Current Directory"))
            console.print(f"[dim]Total items: {len(items)} files/folders[/dim]")
            
            # Create table
            table = Table(title="Files and Folders", show_header=True, header_style="bold magenta")
            table.add_column("No.", width=4, justify="right")
            table.add_column("Type", width=4)
            table.add_column("Name", width=40)
            table.add_column("Type/Ext", width=10)
            table.add_column("Size", width=10)
            
            # Create display items list with proper numbering
            display_items = []
            
            # Add parent directory option first
            if current_dir != os.path.dirname(current_dir):
                display_items.append(("⬆️", ".. (Parent Directory)", "Directory", "", True))  # True = is_parent
            
            # Add regular items
            for icon, name, file_type, size in items:
                display_items.append((icon, name, file_type, size, False))  # False = not parent
            
            # Add items to table
            for i, (icon, name, file_type, size, is_parent) in enumerate(display_items):
                color = "green" if file_type == "Directory" else "white"
                if file_type.upper() in [f.upper() for f in ALLOWED_FORMATS]:
                    color = "cyan"
                table.add_row(str(i + 1), icon, f"[{color}]{name}[/{color}]", file_type, size)
            
            console.print(table)
            
            # Get user choice
            choice = Prompt.ask(
                "\n[yellow]Enter number to select, 'back', or type/paste a path to jump straight there "
                "(a folder path navigates into it, a file path selects it)[/yellow]"
            )

            if choice.lower() == "back":
                return None
            elif choice.lower() == "path":
                # Legacy explicit prompt, kept for anyone used to typing "path" first.
                manual_path = Prompt.ask("[yellow]Enter full path[/yellow]").strip()
                manual_path = os.path.expanduser(manual_path)
                if os.path.isfile(manual_path):
                    return manual_path
                elif os.path.isdir(manual_path):
                    current_dir = manual_path
                    continue
                else:
                    console.print("[red]❌ Invalid path[/red]")
                    continue
            elif os.path.sep in choice or choice.startswith("~"):
                # Looks like a path typed/pasted directly - jump straight there.
                jump_path = os.path.expanduser(choice.strip())
                if os.path.isfile(jump_path):
                    return jump_path
                elif os.path.isdir(jump_path):
                    current_dir = jump_path
                    continue
                else:
                    console.print(f"[red]❌ '{jump_path}' isn't a file or folder that exists[/red]")
                    continue
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(display_items):
                    selected_item = display_items[choice_num - 1]
                    icon, name, file_type, size, is_parent = selected_item
                    
                    if is_parent:
                        # Go to parent directory
                        current_dir = os.path.dirname(current_dir)
                    elif file_type == "Directory":
                        # Navigate into directory
                        item_path = os.path.join(current_dir, name)
                        current_dir = item_path
                    else:
                        # File selected
                        item_path = os.path.join(current_dir, name)
                        return item_path
                else:
                    console.print("[red]❌ Invalid choice[/red]")
            except ValueError:
                console.print("[red]❌ Please enter a valid number[/red]")
                
        except PermissionError:
            console.print("[red]❌ Permission denied to access this directory[/red]")
            return None
        except Exception as e:
            handle_error(e)
            return None

def upload_file(user_folder, subject):
    try:
        console.print(Panel("[bold green]📤 File Upload[/bold green]", expand=False))
        console.print(f"[yellow]Supported formats: {', '.join(ALLOWED_FORMATS)}[/yellow]")

        # Let user choose between the native OS file picker, the in-terminal
        # browser, or typing a path manually.
        picker_label = native_picker_label()
        choice = Prompt.ask(
            f"\n[yellow]Choose upload method:[/yellow] ([cyan]{picker_label}[/cyan] / terminal browse / type a path)",
            choices=["native", "browse", "path"],
            default="native",
        )

        if choice == "native":
            console.print(f"[dim]Opening {picker_label}...[/dim]")
            path = open_native_file_picker()
            if not path:
                console.print(
                    f"[yellow]{picker_label} isn't available here (e.g. no display/SSH session) "
                    "or nothing was selected - switching to in-terminal folder navigation.[/yellow]"
                )
                path = browse_files()
            if not path:
                console.print("[yellow]Upload cancelled[/yellow]")
                return
        elif choice == "browse":
            path = browse_files()
            if not path:
                console.print("[yellow]Upload cancelled[/yellow]")
                return
        else:
            path = Prompt.ask("[yellow]Enter full path of file to upload[/yellow]").strip()
            if not os.path.exists(path):
                console.print("[red]❌ File path invalid[/red]")
                return
        
        # Validate file
        if not os.path.isfile(path):
            console.print("[red]❌ Selected path is not a file[/red]")
            return
            
        ext = path.split(".")[-1].lower()
        if ext not in ALLOWED_FORMATS:
            console.print(f"[red]⚠️ Unsupported format '{ext}'. Allowed: {ALLOWED_FORMATS}[/red]")
            return
        
        # Show file info
        file_size = get_file_size(path)
        console.print(f"\n[cyan]Selected file:[/cyan] {os.path.basename(path)}")
        console.print(f"[cyan]Size:[/cyan] {file_size}")
        console.print(f"[cyan]Type:[/cyan] {ext.upper()}")
        
        # Confirm upload
        confirm = Prompt.ask("[yellow]Upload this file?[/yellow]", choices=["yes", "no"], default="yes")
        if confirm.lower() != "yes":
            console.print("[yellow]Upload cancelled[/yellow]")
            return
        
        # Upload file
        dest_folder = subject_path(user_folder, subject)
        os.makedirs(dest_folder, exist_ok=True)
        dest_path = os.path.join(dest_folder, os.path.basename(path))
        
        # Handle duplicate files
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(os.path.basename(path))
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(dest_folder, f"{base}_{counter}{ext}")
                counter += 1
            console.print(f"[yellow]⚠️ File exists, saving as: {os.path.basename(dest_path)}[/yellow]")
        
        shutil.copy2(path, dest_path)
        glitch_reveal(console, f"✅ Uploaded: {os.path.basename(dest_path)}", style="bold green")
        
    except Exception as e:
        handle_error(e)
