# file_viewer.py
import os, csv, sys, getch
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from datetime import datetime
from error_handler import handle_error

console = Console()

try:
    import PyPDF2
except:
    PyPDF2 = None

try:
    import docx
except:
    docx = None

def get_key():
    """Cross-platform key input"""
    try:
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\xe0':  # Special key
                key = msvcrt.getch()
                if key == b'H': return 'up'
                elif key == b'P': return 'down'
                elif key == b'I': return 'page_up'
                elif key == b'Q': return 'page_down'
            elif key == b' ': return 'space'
            elif key == b'q': return 'quit'
            elif key == b'/': return 'search'
            elif key == b'h': return 'help'
            elif key == b'\r': return 'enter'
    except ImportError:
        # Unix/Linux/Mac
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # ESC sequence
                ch = sys.stdin.read(2)
                if ch == '[A': return 'up'
                elif ch == '[B': return 'down'
                elif ch == '[5~': return 'page_up'
                elif ch == '[6~': return 'page_down'
            elif ch == ' ': return 'space'
            elif ch == 'q': return 'quit'
            elif ch == '/': return 'search'
            elif ch == 'h': return 'help'
            elif ch == '\r': return 'enter'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None

def interactive_text_reader(path, filename):
    """Interactive text file reader with navigation and highlighting"""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        highlighted = set()
        search_results = []
        search_index = 0
        current_line = 0
        lines_per_page = 20
        
        while True:
            console.clear()
            
            # Header
            header = f"[bold cyan]{filename}[/bold cyan] | Line {current_line + 1}/{len(lines)}"
            if search_results:
                header += f" | Search: {len(search_results)} results"
            console.print(Panel(header, expand=False))
            
            # Help
            console.print("[dim]↑↓: Scroll | PgUp/PgDn: Page | Space: Highlight | /: Search | h: Help | q: Quit[/dim]")
            console.print()
            
            # Display lines
            start_line = max(0, current_line - lines_per_page // 2)
            end_line = min(len(lines), start_line + lines_per_page)
            
            for i in range(start_line, end_line):
                line_no = f"{i+1:>4}"
                line_text = lines[i].rstrip()
                
                # Highlighting
                if i in highlighted:
                    console.print(f"[bold black on yellow]{line_no} {line_text}[/bold black on yellow]")
                elif i == current_line:
                    console.print(f"[bold white on blue]{line_no} {line_text}[/bold white on blue]")
                else:
                    console.print(f"[green]{line_no}[/green] {line_text}")
            
            # Footer
            if current_line >= len(lines) - 1:
                console.print("\n[bold yellow]End of file[/bold yellow]")
            
            # Get user input
            key = get_key()
            if not key:
                continue
                
            if key == 'up':
                current_line = max(0, current_line - 1)
            elif key == 'down':
                current_line = min(len(lines) - 1, current_line + 1)
            elif key == 'page_up':
                current_line = max(0, current_line - lines_per_page)
            elif key == 'page_down':
                current_line = min(len(lines) - 1, current_line + lines_per_page)
            elif key == 'space':
                # Toggle highlight for current line
                if current_line in highlighted:
                    highlighted.remove(current_line)
                else:
                    highlighted.add(current_line)
            elif key == 'search':
                search_term = Prompt.ask("[yellow]Enter search term[/yellow]").strip()
                if search_term:
                    search_results = []
                    for i, line in enumerate(lines):
                        if search_term.lower() in line.lower():
                            search_results.append(i)
                    if search_results:
                        current_line = search_results[0]
                        console.print(f"[green]Found {len(search_results)} results[/green]")
                    else:
                        console.print("[red]No results found[/red]")
                        input("Press Enter to continue...")
            elif key == 'help':
                show_reader_help()
            elif key == 'quit':
                break
                
    except Exception as e:
        handle_error(e)

def show_reader_help():
    """Show help for the interactive reader"""
    console.clear()
    console.print(Panel("[bold cyan]Interactive Reader Help[/bold cyan]", expand=False))
    console.print()
    console.print("[green]Navigation:[/green]")
    console.print("  ↑ / ↓     - Scroll line by line")
    console.print("  PgUp/PgDn - Jump multiple lines")
    console.print()
    console.print("[yellow]Features:[/yellow]")
    console.print("  SPACE     - Highlight/unhighlight current line")
    console.print("  /         - Search for text in file")
    console.print("  h         - Show this help")
    console.print("  q         - Quit reader")
    console.print()
    input("Press Enter to continue...")

def edit_file_with_reason(user_folder, subject, filename):
    """Edit a file with reason tracking"""
    path = os.path.join("subjects", user_folder, subject, filename) if user_folder else os.path.join("subjects", subject, filename)
    
    if not os.path.exists(path):
        console.print(f"[red]File '{filename}' not found[/red]")
        return
    
    try:
        # Get edit reason
        reason = Prompt.ask("[yellow]Enter reason for editing this file[/yellow]").strip()
        if not reason:
            reason = "No reason provided"
        
        # Read current content
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Show current content
        console.print(Panel(f"[bold cyan]Editing: {filename}[/bold cyan]", expand=False))
        console.print(f"[dim]Reason: {reason}[/dim]")
        console.print()
        console.print("[yellow]Current content:[/yellow]")
        console.print(content)
        console.print()
        
        # Get new content
        console.print("[yellow]Enter new content (press Ctrl+D when done):[/yellow]")
        new_content = ""
        try:
            while True:
                line = input()
                new_content += line + "\n"
        except EOFError:
            pass
        
        # Save with reason tracking
        backup_path = path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        # Log the edit
        log_path = os.path.join("subjects", user_folder, subject, "edit_log.txt") if user_folder else os.path.join("subjects", subject, "edit_log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] Edited {filename} - Reason: {reason}\n")
            f.write(f"Backup saved as: {os.path.basename(backup_path)}\n\n")
        
        console.print(f"[green]✅ File edited successfully![/green]")
        console.print(f"[dim]Backup saved as: {os.path.basename(backup_path)}[/dim]")
        
    except Exception as e:
        handle_error(e)

def view_binary_file(path, filename, ext):
    """View binary files as hex dump"""
    try:
        console.print(f"[yellow]Binary file detected. Showing hex dump:[/yellow]")
        console.print()
        
        with open(path, "rb") as f:
            chunk_size = 16
            offset = 0
            
            for chunk in iter(lambda: f.read(chunk_size), b""):
                # Create hex representation
                hex_str = " ".join(f"{b:02x}" for b in chunk)
                hex_str = hex_str.ljust(47)  # Pad to align ASCII
                
                # Create ASCII representation
                ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                
                console.print(f"{offset:08x}: {hex_str} |{ascii_str}|")
                offset += len(chunk)
                
                # Limit output for very large files
                if offset > 1024:  # Show first 1KB
                    console.print(f"\n[yellow]... (showing first 1KB of {os.path.getsize(path)} bytes)[/yellow]")
                    break
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        console.print(f"[red]Error reading binary file: {e}[/red]")
        input("Press Enter to continue...")

def view_image_info(path, filename, ext):
    """Show image file information"""
    try:
        file_size = os.path.getsize(path)
        console.print(f"[cyan]Image file: {filename}[/cyan]")
        console.print(f"[cyan]Format: {ext.upper()}[/cyan]")
        console.print(f"[cyan]Size: {file_size:,} bytes[/cyan]")
        console.print()
        console.print("[yellow]Image files cannot be displayed in CLI.[/yellow]")
        console.print("[yellow]Use an image viewer or convert to text format.[/yellow]")
        input("\nPress Enter to continue...")
        
    except Exception as e:
        console.print(f"[red]Error reading image file: {e}[/red]")
        input("Press Enter to continue...")

def view_archive_info(path, filename, ext):
    """Show archive file information"""
    try:
        file_size = os.path.getsize(path)
        console.print(f"[cyan]Archive file: {filename}[/cyan]")
        console.print(f"[cyan]Format: {ext.upper()}[/cyan]")
        console.print(f"[cyan]Size: {file_size:,} bytes[/cyan]")
        console.print()
        console.print("[yellow]Archive files cannot be extracted in CLI.[/yellow]")
        console.print("[yellow]Use an archive manager to extract contents.[/yellow]")
        input("\nPress Enter to continue...")
        
    except Exception as e:
        console.print(f"[red]Error reading archive file: {e}[/red]")
        input("Press Enter to continue...")

def view_file_rich(user_folder, subject, filename, editable=False):
    """Main file viewer function - handles ALL file types in CLI"""
    path = os.path.join("subjects", user_folder, subject, filename) if user_folder else os.path.join("subjects", subject, filename)
    
    if not os.path.exists(path):
        console.print(f"[red]File '{filename}' not found[/red]")
        return
    
    try:
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"
        console.print(Panel(f"[bold cyan]Opening {filename} in CLI[/bold cyan]", expand=False))
        
        if editable:
            edit_file_with_reason(user_folder, subject, filename)
            return

        # Text-based files (interactive reader)
        if ext in ["txt", "md", "py", "json", "js", "html", "css", "xml", "yaml", "yml", "ini", "cfg", "conf", "log", "sh", "bat", "ps1"]:
            interactive_text_reader(path, filename)
            
        # PDF files
        elif ext == "pdf":
            if not PyPDF2:
                console.print("[red]PyPDF2 not installed - showing file info instead[/red]")
                file_size = os.path.getsize(path)
                console.print(f"[cyan]PDF file: {filename}[/cyan]")
                console.print(f"[cyan]Size: {file_size:,} bytes[/cyan]")
                console.print()
                console.print("[yellow]To view PDF content:[/yellow]")
                console.print("[cyan]pip install PyPDF2[/cyan]")
                input("\nPress Enter to continue...")
                return
                
            try:
                with open(path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    console.print(f"[cyan]PDF has {len(reader.pages)} pages[/cyan]")
                    for i, page in enumerate(reader.pages[:3]):  # Show first 3 pages
                        console.print(f"\n[bold]Page {i+1}:[/bold]")
                        text = page.extract_text()
                        if text.strip():
                            console.print(text)
                        else:
                            console.print("[dim]No text content found on this page[/dim]")
                    if len(reader.pages) > 3:
                        console.print(f"\n[yellow]... and {len(reader.pages) - 3} more pages[/yellow]")
                input("\nPress Enter to continue...")
            except Exception as e:
                console.print(f"[red]Error reading PDF: {e}[/red]")
                console.print()
                console.print("[yellow]This might be due to:[/yellow]")
                console.print("• Corrupted or encrypted PDF")
                console.print("• Unsupported PDF version")
                console.print("• PDF contains only images")
                console.print()
                console.print("[cyan]Try updating PyPDF2: pip install --upgrade PyPDF2[/cyan]")
                input("Press Enter to continue...")

        # Word documents
        elif ext in ["doc", "docx"]:
            if not docx:
                console.print("[red]python-docx not installed - showing file info instead[/red]")
                file_size = os.path.getsize(path)
                console.print(f"[cyan]Word document: {filename}[/cyan]")
                console.print(f"[cyan]Size: {file_size:,} bytes[/cyan]")
                console.print()
                console.print("[yellow]To view Word document content:[/yellow]")
                console.print("[cyan]pip install python-docx lxml[/cyan]")
                console.print()
                console.print("[dim]Note: lxml is required for python-docx to work properly[/dim]")
                input("\nPress Enter to continue...")
                return
                
            try:
                doc = docx.Document(path)
                console.print(f"[cyan]Document has {len(doc.paragraphs)} paragraphs[/cyan]")
                for i, para in enumerate(doc.paragraphs[:20]):
                    if para.text.strip():
                        console.print(para.text)
                if len(doc.paragraphs) > 20:
                    console.print(f"\n[yellow]... and {len(doc.paragraphs) - 20} more paragraphs[/yellow]")
                input("\nPress Enter to continue...")
            except Exception as e:
                console.print(f"[red]Error reading Word document: {e}[/red]")
                console.print()
                console.print("[yellow]This might be due to:[/yellow]")
                console.print("• Missing lxml dependency")
                console.print("• Corrupted or encrypted document")
                console.print("• Unsupported Word format")
                console.print()
                console.print("[cyan]Try: pip install lxml[/cyan]")
                input("Press Enter to continue...")

        # CSV files
        elif ext == "csv":
            try:
                with open(path, "r", newline="", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    console.print(f"[cyan]CSV has {len(rows)} rows[/cyan]")
                    for i, row in enumerate(rows[:10]):
                        console.print(f"Row {i+1}: {', '.join(row)}")
                    if len(rows) > 10:
                        console.print(f"\n[yellow]... and {len(rows) - 10} more rows[/yellow]")
                input("\nPress Enter to continue...")
            except Exception as e:
                console.print(f"[red]Error reading CSV: {e}[/red]")
                input("Press Enter to continue...")

        # Image files
        elif ext in ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg", "webp"]:
            view_image_info(path, filename, ext)

        # Archive files
        elif ext in ["zip", "rar", "7z", "tar", "gz", "bz2", "xz"]:
            view_archive_info(path, filename, ext)

        # Executable files
        elif ext in ["exe", "dll", "so", "dylib", "bin"]:
            console.print(f"[yellow]Executable file: {filename}[/yellow]")
            console.print("[yellow]Cannot execute or view binary executables in CLI.[/yellow]")
            input("Press Enter to continue...")

        # Audio/Video files
        elif ext in ["mp3", "wav", "flac", "mp4", "avi", "mkv", "mov", "wmv"]:
            file_size = os.path.getsize(path)
            console.print(f"[cyan]Media file: {filename}[/cyan]")
            console.print(f"[cyan]Format: {ext.upper()}[/cyan]")
            console.print(f"[cyan]Size: {file_size:,} bytes[/cyan]")
            console.print("[yellow]Media files cannot be played in CLI.[/yellow]")
            input("\nPress Enter to continue...")

        # Default: try to read as text, fallback to binary
        else:
            try:
                # First try to read as text
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(1000)  # Read first 1000 chars
                    if content.strip():
                        console.print(f"[yellow]Unknown text format '{ext}' - showing as text:[/yellow]")
                        console.print(content)
                        if len(content) == 1000:
                            console.print("\n[yellow]... (showing first 1000 characters)[/yellow]")
                        input("\nPress Enter to continue...")
                    else:
                        raise UnicodeDecodeError("", b"", 0, 1, "empty content")
            except (UnicodeDecodeError, UnicodeError):
                # If text reading fails, show as binary
                console.print(f"[yellow]Unknown binary format '{ext}' - showing hex dump:[/yellow]")
                view_binary_file(path, filename, ext)

    except Exception as e:
        console.print(f"[red]Unexpected error opening file: {e}[/red]")
        console.print("[yellow]File may be corrupted or in an unsupported format[/yellow]")
        input("Press Enter to continue...")
