# stats.py - study stats and activity streak, derived from git history so the
# numbers can never drift from reality and a leaderboard needs zero extra
# GitHub API calls (unlike the feed/chat, which do need the API).
import os
import subprocess
from datetime import date, timedelta

from study_cli_hub.paths import list_known_users, list_notes, list_subjects, subject_path

STREAK_LOOKBACK_DAYS = 400


def _user_commit_dates(user_folder, cwd=None, lookback_days=STREAK_LOOKBACK_DAYS):
    """Distinct calendar dates (YYYY-MM-DD) on which a commit touched
    subjects/<user_folder>/. Pure local `git log` - no GitHub API call, and
    requires a full (non-shallow) clone to see the whole history."""
    path = subject_path(user_folder)
    result = subprocess.run(
        ["git", "log", f"--since={lookback_days}.days", "--format=%ad", "--date=short", "--", path],
        capture_output=True, text=True, cwd=cwd or os.getcwd(),
    )
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def compute_streak(dates, today=None):
    """Walks backward from today counting consecutive days present in `dates`
    (a set of 'YYYY-MM-DD' strings)."""
    today = today or date.today()
    streak = 0
    cursor = today
    while cursor.isoformat() in dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def user_stats(user_folder, cwd=None):
    subjects = list_subjects(user_folder)
    notes = sum(len(list_notes(user_folder, s)) for s in subjects)
    dates = _user_commit_dates(user_folder, cwd=cwd)
    return {
        "user": user_folder,
        "subjects": len(subjects),
        "notes": notes,
        "streak": compute_streak(dates),
        "last_active": max(dates) if dates else None,
    }


def all_user_stats(cwd=None):
    """For /leaderboard: zero GitHub API calls, purely local git + filesystem."""
    return [user_stats(u, cwd=cwd) for u in list_known_users()]


def daily_activity(user_folder, days=7, cwd=None, today=None):
    """Active/inactive per day for the last `days` days (oldest first), for
    a terminal habit graph. A day with any commit reads as active - one big
    study session and three small ones both show as a single filled bar,
    which is the more honest daily signal than a raw commit tally."""
    today = today or date.today()
    dates = _user_commit_dates(user_folder, cwd=cwd)
    return [
        {"date": (today - timedelta(days=offset)).isoformat(), "active": (today - timedelta(days=offset)).isoformat() in dates}
        for offset in range(days - 1, -1, -1)
    ]
