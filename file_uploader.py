# file_uploader.py
import os, shutil
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from error_handler import handle_error

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
            choice = Prompt.ask("\n[yellow]Enter number to select, 'back' to go back, or 'path' to enter path manually[/yellow]")
            
            if choice.lower() == "back":
                return None
            elif choice.lower() == "path":
                manual_path = Prompt.ask("[yellow]Enter full file path[/yellow]").strip()
                if os.path.exists(manual_path) and os.path.isfile(manual_path):
                    return manual_path
                else:
                    console.print("[red]❌ Invalid file path[/red]")
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
        
        # Let user choose between file browser or manual path
        choice = Prompt.ask("\n[yellow]Choose upload method:[/yellow]", choices=["browse", "path"], default="browse")
        
        if choice == "browse":
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
        dest_folder = os.path.join("subjects", user_folder, subject) if user_folder else os.path.join("subjects", subject)
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
        console.print(f"[green]✅ File uploaded successfully to '{dest_path}'[/green]")
        
    except Exception as e:
        handle_error(e)
