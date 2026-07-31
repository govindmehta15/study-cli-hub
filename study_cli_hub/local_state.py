# local_state.py - personal, per-device state (e.g. "have I seen this?" markers
# for /digest). Deliberately NOT git-synced: syncing one person's read-receipts
# into everyone else's clone would create pointless conflicts on the same file
# every user touches every run.
import json
import os

from study_cli_hub import github_auth


def _state_file():
    return os.path.join(github_auth.config_dir(), "state.json")


def load_state():
    path = _state_file()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(data):
    with open(_state_file(), "w", encoding="utf-8") as f:
        json.dump(data, f)


def get_last_seen(key):
    return load_state().get(f"last_seen_{key}")


def set_last_seen(key, when_iso):
    state = load_state()
    state[f"last_seen_{key}"] = when_iso
    save_state(state)
