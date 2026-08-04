# exporter.py - portable JSON/CSV backup of a user's own subjects, notes,
# stats, and flashcard SRS progress. Keeps the "hassle-free, no lock-in"
# promise honest: everything here is plain data you can read/reuse without
# this app, matching the git+plaintext storage model (no database export
# format to keep in sync).
import csv
import io
import json
from datetime import datetime, timezone

from study_cli_hub import srs, stats
from study_cli_hub.paths import get_subject_description, get_visibility, list_notes, list_subjects


def build_export(user_folder):
    subject_rows = []
    for subject in list_subjects(user_folder):
        notes = list_notes(user_folder, subject)
        srs_state = srs.load_state(user_folder, subject)
        subject_rows.append({
            "subject": subject,
            "description": get_subject_description(user_folder, subject),
            "visibility": get_visibility(user_folder, subject) if user_folder else "public",
            "notes": notes,
            "note_count": len(notes),
            "srs_cards_tracked": len(srs_state),
        })

    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "user": user_folder or "(global)",
        "stats": stats.user_stats(user_folder) if user_folder else None,
        "subjects": subject_rows,
    }


def to_json(data):
    return json.dumps(data, indent=2)


def to_csv(data):
    """One row per note (subject/description/visibility repeated per row) -
    the flat shape that fits a spreadsheet. Stats and SRS counts are
    per-subject summaries that don't fit this shape; use to_json for those."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["subject", "note", "description", "visibility", "srs_cards_tracked"])
    for row in data["subjects"]:
        notes = row["notes"] or [""]
        for note in notes:
            writer.writerow([row["subject"], note, row["description"], row["visibility"], row["srs_cards_tracked"]])
    return buf.getvalue()
