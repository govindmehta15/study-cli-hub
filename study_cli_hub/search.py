# search.py - full-text search across your own, global, and other users' notes.
import csv
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


def _extract_chunks(path, ext):
    """Best-effort text extraction, split into (location, kind, text) chunks
    so a match can be jumped straight to instead of always opening at the
    top: one chunk per line (text files), per data row (CSV), per page
    (PDF), or per paragraph (DOCX). location is 1-based."""
    try:
        if ext in TEXT_EXTENSIONS:
            with open(path, encoding="utf-8", errors="ignore") as f:
                return [(i + 1, "line", line) for i, line in enumerate(f.readlines())]
        if ext == "csv":
            with open(path, newline="", encoding="utf-8", errors="ignore") as f:
                rows = list(csv.reader(f))
            data_rows = rows[1:] if len(rows) > 1 else rows
            return [(i + 1, "row", " ".join(str(c) for c in row)) for i, row in enumerate(data_rows)]
        if ext == "pdf" and PyPDF2:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return [(i + 1, "page", page.extract_text() or "") for i, page in enumerate(reader.pages)]
        if ext in ("doc", "docx") and docx:
            document = docx.Document(path)
            # Match interactive_docx_viewer()'s filtering so a jump target
            # (paragraph N) points at the same paragraph in both places.
            non_empty = [p for p in document.paragraphs if p.text.strip()]
            return [(i + 1, "paragraph", p.text) for i, p in enumerate(non_empty)]
    except Exception:
        return []
    return []


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
    each result is {owner, subject, filename, snippet, match_count,
    location, location_kind} - location/location_kind let the caller jump
    straight to the match (a line, CSV row, PDF page, or DOCX paragraph)."""
    term_lower = term.lower()
    results, scanned = [], 0
    truncated = False
    for owner, subject, filename, path in _iter_targets(current_user_folder):
        if scanned >= MAX_FILES_SCANNED or len(results) >= MAX_RESULTS:
            truncated = True
            break
        scanned += 1
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"
        chunks = _extract_chunks(path, ext)
        if not chunks:
            continue

        match_count = sum(chunk_text.lower().count(term_lower) for _, _, chunk_text in chunks)
        if match_count == 0:
            continue

        location, location_kind, snippet = None, None, ""
        for loc, kind, chunk_text in chunks:
            idx = chunk_text.lower().find(term_lower)
            if idx != -1:
                location, location_kind = loc, kind
                start = max(0, idx - SNIPPET_RADIUS)
                end = min(len(chunk_text), idx + len(term) + SNIPPET_RADIUS)
                snippet = chunk_text[start:end].replace("\n", " ")
                break

        results.append({
            "owner": owner,
            "subject": subject,
            "filename": filename,
            "snippet": snippet,
            "match_count": match_count,
            "location": location,
            "location_kind": location_kind,
        })
    return results, truncated
