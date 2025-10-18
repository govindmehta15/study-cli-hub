# file_viewer.py
import os, csv
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
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

def view_file_rich(user_folder, subject, filename):
    path = os.path.join("subjects", user_folder, subject, filename) if user_folder else os.path.join("subjects", subject, filename)
    if not os.path.exists(path):
        console.print(f"[red]File '{filename}' not found[/red]")
        return
    try:
        ext = filename.split(".")[-1].lower()
        console.print(Panel(f"[bold cyan]Opening {filename}[/bold cyan]"))
        if ext in ["txt","md","py","json"]:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                for i, line in enumerate(lines,1):
                    console.print(f"[green]{i:>3}[/green] {line.strip()}")
                console.print("[bold yellow]End of file. Press Enter to continue...[/bold yellow]")
                input()
        elif ext == "pdf":
            if not PyPDF2:
                console.print("[red]PyPDF2 not installed[/red]")
                return
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages[:2]:
                    console.print(page.extract_text())
                console.print("[bold yellow]PDF preview complete[/bold yellow]")
        elif ext in ["doc", "docx"]:
            if not docx:
                console.print("[red]python-docx not installed[/red]")
                return
            doc = docx.Document(path)
            for para in doc.paragraphs[:20]:
                console.print(para.text)
            console.print("[bold yellow]DOCX preview complete[/bold yellow]")
        elif ext == "csv":
            with open(path, "r", newline="", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                for i,row in enumerate(reader):
                    console.print(", ".join(row))
                    if i >= 9: break
                console.print("[bold yellow]CSV preview complete[/bold yellow]")
        else:
            console.print(f"[red]Unsupported file format '{ext}'[/red]")
    except Exception as e:
        handle_error(e)
