import os

SUBJECTS_DIR = "subjects"


def subject_path(user_folder, subject=None):
    parts = [SUBJECTS_DIR] + ([user_folder] if user_folder else []) + ([subject] if subject else [])
    return os.path.join(*parts)


def note_path(user_folder, subject, filename):
    return os.path.join(subject_path(user_folder, subject), filename)


def list_known_users(exclude=None):
    """Top-level folders under subjects/ whose children are subject folders
    (rather than note files) are treated as per-user folders."""
    if not os.path.isdir(SUBJECTS_DIR):
        return []
    users = []
    for entry in sorted(os.listdir(SUBJECTS_DIR)):
        if entry == exclude:
            continue
        full = os.path.join(SUBJECTS_DIR, entry)
        if os.path.isdir(full) and any(os.path.isdir(os.path.join(full, child)) for child in os.listdir(full)):
            users.append(entry)
    return users


def list_global_subjects():
    """Top-level folders under subjects/ that are NOT user folders - i.e.
    their children are note files directly, mirroring list_known_users()'s
    heuristic but inverted."""
    if not os.path.isdir(SUBJECTS_DIR):
        return []
    subs = []
    for entry in sorted(os.listdir(SUBJECTS_DIR)):
        full = os.path.join(SUBJECTS_DIR, entry)
        if os.path.isdir(full) and not any(
            os.path.isdir(os.path.join(full, child)) for child in os.listdir(full)
        ):
            subs.append(entry)
    return subs


def list_subjects(user_folder=None):
    """Get list of subjects for current user"""
    path = subject_path(user_folder)
    os.makedirs(path, exist_ok=True)
    subjects = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return sorted(subjects)


def list_notes(user_folder, subject):
    """Get list of notes in a subject"""
    path = subject_path(user_folder, subject)
    os.makedirs(path, exist_ok=True)
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files = [f for f in files if not f.startswith(".") and f != "edit_log.txt"]
    return sorted(files)
