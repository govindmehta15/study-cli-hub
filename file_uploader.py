# file_uploader.py
import os
import shutil
from error_handler import handle_error

ALLOWED_FORMATS = ['txt', 'md', 'py', 'json', 'pdf', 'docx', 'csv']

def upload_file(user_folder, subject):
    try:
        path = input("Enter full path of file to upload: ").strip()
        if not os.path.exists(path):
            print("❌ File path invalid.")
            return
        ext = path.split('.')[-1].lower()
        if ext not in ALLOWED_FORMATS:
            print(f"⚠️ Unsupported format '{ext}'. Allowed: {ALLOWED_FORMATS}")
            return
        dest_folder = os.path.join("subjects", user_folder, subject) if user_folder else os.path.join("subjects", subject)
        os.makedirs(dest_folder, exist_ok=True)
        dest_path = os.path.join(dest_folder, os.path.basename(path))
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(os.path.basename(path))
            dest_path = os.path.join(dest_folder, f"{base}_copy{ext}")
        shutil.copy2(path, dest_path)
        print(f"✅ File uploaded successfully to '{dest_path}'")
    except Exception as e:
        handle_error(e)
