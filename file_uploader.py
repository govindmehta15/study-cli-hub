# file_uploader.py
import os, shutil
from rich.console import Console
from error_handler import handle_error

console = Console()
ALLOWED_FORMATS = ["txt","md","py","json","pdf","docx","csv"]

def upload_file(user_folder, subject):
    try:
        path = input("Enter full path of file to upload: ").strip()
        if not os.path.exists(path):
            console.print("[red]❌ File path invalid[/red]")
            return
        ext = path.split(".")[-1].lower()
        if ext not in ALLOWED_FORMATS:
            console.print(f"[red]⚠️ Unsupported format '{ext}'. Allowed: {ALLOWED_FORMATS}[/red]")
            return
        dest_folder = os.path.join("subjects", user_folder, subject) if user_folder else os.path.join("subjects", subject)
        os.makedirs(dest_folder, exist_ok=True)
        dest_path = os.path.join(dest_folder, os.path.basename(path))
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(os.path.basename(path))
            dest_path = os.path.join(dest_folder, f"{base}_copy{ext}")
        shutil.copy2(path, dest_path)
        console.print(f"[green]✅ File uploaded successfully to '{dest_path}'[/green]")
    except Exception as e:
        handle_error(e)
