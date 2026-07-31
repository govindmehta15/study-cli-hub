# animations.py - small, tasteful CLI animation primitives.
#
# Rule that must never be broken: every animated call site degrades to
# instant, plain output with the EXACT SAME final text when not attached to
# a real terminal (sys.stdin.isatty() is False) - only timing/spinner chrome
# differs. This project pipes commands via stdin and reads output for its
# own testing, so nothing here may change what gets printed or block on
# time.sleep() when non-interactive.
import sys
import time


def is_interactive():
    return sys.stdin.isatty()


def typewriter(console, text, style=None, delay=0.012):
    """Reveals text character-by-character on a real terminal; prints the
    exact same final string instantly and unchanged otherwise."""
    if not is_interactive():
        console.print(text, style=style)
        return
    for ch in text:
        console.print(ch, style=style, end="")
        console.file.flush()
        time.sleep(delay)
    console.print()


def with_spinner(console, message, fn, *args, **kwargs):
    """Wraps a blocking call (git pull/push, a GraphQL request) with a
    spinner + message when interactive. When not interactive, prints the
    exact same message text (no spinner glyphs) and calls fn() directly."""
    if is_interactive():
        with console.status(f"[cyan]{message}[/cyan]", spinner="dots"):
            return fn(*args, **kwargs)
    console.print(f"[yellow]{message}[/yellow]")
    return fn(*args, **kwargs)


def celebrate(console, message):
    """Short milestone celebration (first subject, first post, streak
    milestones). Degrades to a single plain line when non-interactive."""
    if not is_interactive():
        console.print(f"🎉 {message}")
        return
    for frame in ["🎉", "✨", "🎊", "✨", "🎉"]:
        console.print(f"\r{frame} {message}", end="")
        console.file.flush()
        time.sleep(0.08)
    console.print()
