import os

SUBJECTS_DIR = "subjects"


def subject_path(user_folder, subject=None):
    parts = [SUBJECTS_DIR] + ([user_folder] if user_folder else []) + ([subject] if subject else [])
    return os.path.join(*parts)


def note_path(user_folder, subject, filename):
    return os.path.join(subject_path(user_folder, subject), filename)
