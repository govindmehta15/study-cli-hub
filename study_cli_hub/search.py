# search.py - full-text search across your own, global, and other users' notes.
import os

from study_cli_hub.file_viewer import TEXT_EXTENSIONS
from study_cli_hub.paths import (
    list_global_subjects,
    list_known_users,
    list_notes,
    list_subjects,
    subject_path,
)

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

MAX_FILES_SCANNED = 400
MAX_RESULTS = 50
SNIPPET_RADIUS = 60


def _extract_text(path, ext):
    """Best-effort text extraction, mirroring how file_viewer.py already
    reads each format for its interactive viewers."""
    try:
        if ext in TEXT_EXTENSIONS:
            with open(path, encoding="utf-8", errors="ignore") as f:
                return f.read()
        if ext == "pdf" and PyPDF2:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(page.extract_text() or "" for page in reader.pages)
        if ext in ("doc", "docx") and docx:
            document = docx.Document(path)
            return "\n".join(p.text for p in document.paragraphs)
    except Exception:
        return None
    return None


def _iter_targets(current_user_folder):
    """Yields (owner, subject, filename, path). owner is None for global
    subjects and the caller's own folder (both are "mine"); a real username
    string means it's someone else's read-only content."""

    def _walk(owner, folder):
        for subject in list_subjects(folder):
            for filename in list_notes(folder, subject):
                yield owner, subject, filename, os.path.join(subject_path(folder, subject), filename)

    if current_user_folder:
        yield from _walk(None, current_user_folder)
    for g in list_global_subjects():
        for filename in list_notes(None, g):
            yield None, g, filename, os.path.join(subject_path(None, g), filename)
    for u in list_known_users(exclude=current_user_folder):
        yield from _walk(u, u)


def search_notes(term, current_user_folder):
    """Case-insensitive substring search. Returns (results, truncated) where
    each result is {owner, subject, filename, snippet, match_count}."""
    term_lower = term.lower()
    results, scanned = [], 0
    truncated = False
    for owner, subject, filename, path in _iter_targets(current_user_folder):
        if scanned >= MAX_FILES_SCANNED or len(results) >= MAX_RESULTS:
            truncated = True
            break
        scanned += 1
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"
        text = _extract_text(path, ext)
        if not text:
            continue
        idx = text.lower().find(term_lower)
        if idx == -1:
            continue
        start = max(0, idx - SNIPPET_RADIUS)
        end = min(len(text), idx + len(term) + SNIPPET_RADIUS)
        snippet = text[start:end].replace("\n", " ")
        results.append({
            "owner": owner,
            "subject": subject,
            "filename": filename,
            "snippet": snippet,
            "match_count": text.lower().count(term_lower),
        })
    return results, truncated
