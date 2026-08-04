# srs.py - lightweight spaced-repetition scheduling (a simplified SM-2) for
# the Q:/A: flashcards /quiz already collects. State is one small JSON file
# per subject, git-synced alongside the notes it schedules - no database,
# consistent with the rest of this app's plain-file storage model.
import hashlib
import json
import os
from datetime import date, timedelta

from study_cli_hub.paths import subject_path

SRS_STATE_FILE = ".srs_state.json"
DEFAULT_EASE_FACTOR = 2.5
MIN_EASE_FACTOR = 1.3


def card_id(question):
    """A stable id for a flashcard derived from its question text, since
    flashcards themselves have no persistent id - they're re-parsed from
    Q:/A: lines in plain notes every time."""
    return hashlib.sha1(question.strip().lower().encode("utf-8")).hexdigest()[:12]


def _state_path(user_folder, subject):
    return os.path.join(subject_path(user_folder, subject), SRS_STATE_FILE)


def load_state(user_folder, subject):
    try:
        with open(_state_path(user_folder, subject), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(user_folder, subject, state):
    with open(_state_path(user_folder, subject), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def due_card_ids(state, all_card_ids, today=None):
    """Cards never reviewed, or whose scheduled date has arrived/passed."""
    today_iso = (today or date.today()).isoformat()
    return [cid for cid in all_card_ids if state.get(cid, {}).get("next_review_date", today_iso) <= today_iso]


def review_card(state, cid, quality, today=None):
    """Records one review and reschedules the card. `quality` is a 1-5
    recall grade (1 = didn't know it, 5 = perfect recall) - a simplified
    SM-2 where scores below 3 restart the interval instead of failing
    outright, since this is casual self-study, not a strict drill.
    Mutates `state` in place and returns the updated record."""
    today = today or date.today()
    card = state.get(cid, {"repetitions": 0, "interval": 0, "ease_factor": DEFAULT_EASE_FACTOR})

    if quality < 3:
        card["repetitions"] = 0
        interval = 1
    else:
        reps = card["repetitions"]
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(card["interval"] * card["ease_factor"])
        card["repetitions"] = reps + 1

    card["interval"] = max(1, interval)
    card["ease_factor"] = max(
        MIN_EASE_FACTOR,
        card["ease_factor"] + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )
    card["next_review_date"] = (today + timedelta(days=card["interval"])).isoformat()
    card["last_quality"] = quality
    state[cid] = card
    return card
