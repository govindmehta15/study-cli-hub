# pomodoro.py - a focus-session countdown with a best-effort desktop
# notification when it ends. Runs as a normal blocking sub-screen (same
# pattern as quiz_menu/subject_menu), not a background thread: a thread
# printing into this app's fixed-layout TUI mid-render would corrupt the
# screen (prompt_toolkit's redraws assume nothing else writes to the
# terminal), so a live foreground countdown you can Ctrl+C out of early is
# the safe fit for the current architecture - not a true "runs in a corner
# while you take notes" widget.
import platform
import subprocess
import sys
import time

DEFAULT_MINUTES = 25


def _escape_for_osascript(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def send_desktop_notification(title, message):
    """Best-effort, cross-platform, and silent on failure - a missing
    notify-send/osascript/powershell must never crash the session."""
    system = platform.system()
    try:
        if system == "Darwin":
            script = f'display notification "{_escape_for_osascript(message)}" with title "{_escape_for_osascript(title)}"'
            subprocess.run(["osascript", "-e", script], check=False, timeout=5, capture_output=True)
        elif system == "Linux":
            subprocess.run(["notify-send", title, message], check=False, timeout=5, capture_output=True)
        elif system == "Windows":
            ps = (
                "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; "
                f"(New-Object System.Windows.Forms.NotifyIcon).ShowBalloonTip(5000, '{title}', '{message}', 'Info')"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False, timeout=5, capture_output=True)
    except Exception:
        pass


def run_countdown(console, minutes=DEFAULT_MINUTES, label="Focus session"):
    """Blocks for `minutes`, printing a live MM:SS countdown. Returns True
    if it ran to completion, False if cancelled early with Ctrl+C. Skips
    the countdown entirely (no sleeping) when not attached to a real
    terminal, per this project's non-interactive-must-not-block rule."""
    total_seconds = max(1, int(minutes * 60))

    if not sys.stdin.isatty():
        console.print(f"🍅 {label} ({minutes} min) - skipped countdown (non-interactive).")
        return True

    console.print(f"[bold cyan]🍅 {label}[/bold cyan]  ({minutes} min) - Ctrl+C to stop early")
    try:
        for remaining in range(total_seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            console.print(f"\r⏳ {mins:02d}:{secs:02d} remaining ", end="")
            console.file.flush()
            time.sleep(1)
        console.print()
        return True
    except KeyboardInterrupt:
        console.print("\n[yellow]Pomodoro cancelled early.[/yellow]")
        return False
