# file_viewer.py
import os
import csv
from error_handler import handle_error

try:
    import PyPDF2
except:
    PyPDF2 = None

try:
    import docx
except:
    docx = None

def view_file(user_folder, subject, filename):
    path = os.path.join("subjects", user_folder, subject, filename) if user_folder else os.path.join("subjects", subject, filename)
    if not os.path.exists(path):
        print(f"❌ File '{filename}' not found!")
        return
    try:
        ext = filename.split('.')[-1].lower()
        if ext in ['txt', 'md', 'py', 'json']:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                print("\n" + f.read())
        elif ext == 'pdf':
            if not PyPDF2:
                print("⚠️ PyPDF2 not installed. Cannot open PDF.")
                return
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages[:2]:  # preview first 2 pages
                    print(page.extract_text())
        elif ext in ['doc', 'docx']:
            if not docx:
                print("⚠️ python-docx not installed. Cannot open DOCX.")
                return
            doc = docx.Document(path)
            for para in doc.paragraphs[:20]:  # preview first 20 lines
                print(para.text)
        elif ext == 'csv':
            with open(path, 'r', newline='', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    print(', '.join(row))
                    if i >= 9:
                        break
        else:
            print(f"⚠️ Unsupported file format '{ext}'.")
    except Exception as e:
        handle_error(e)
