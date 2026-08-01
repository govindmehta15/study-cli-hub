# animations.py - small, tasteful CLI animation primitives.
#
# Rule that must never be broken: every animated call site degrades to
# instant, plain output with the EXACT SAME final text when not attached to
# a real terminal (sys.stdin.isatty() is False) - only timing/spinner chrome
# differs. This project pipes commands via stdin and reads output for its
# own testing, so nothing here may change what gets printed or block on
# time.sleep() when non-interactive.
import random
import sys
import time

from rich import box
from rich.panel import Panel as _Panel

# A distinct, retro-terminal ASCII border (+, -, |) instead of Rich's default
# soft rounded Unicode box - reads as more "CLI-native", less GUI-like.
RETRO_BOX = box.ASCII


def cli_panel(*args, **kwargs):
    """Drop-in replacement for rich.panel.Panel with the retro CLI border
    applied by default (still overridable via an explicit box= kwarg)."""
    kwargs.setdefault("box", RETRO_BOX)
    return _Panel(*args, **kwargs)


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
    classic rotating -\\|/ spinner + message when interactive. When not
    interactive, prints the exact same message text (no spinner glyphs)
    and calls fn() directly."""
    if is_interactive():
        with console.status(f"[cyan]{message}[/cyan]", spinner="line"):
            return fn(*args, **kwargs)
    console.print(f"[yellow]{message}[/yellow]")
    return fn(*args, **kwargs)


def celebrate(console, message):
    """Short, generic milestone celebration. Degrades to a single plain line
    when non-interactive. Prefer one of the more specific animations below
    (rocket_launch, confetti_rain, streak_fire, pet_run, trophy_fireworks,
    science_animation) where one fits - this is the plain fallback."""
    if not is_interactive():
        console.print(f"🎉 {message}")
        return
    for frame in ["🎉", "✨", "🎊", "✨", "🎉"]:
        console.print(f"\r{frame} {message}", end="")
        console.file.flush()
        time.sleep(0.08)
    console.print()


def _term_width(console):
    try:
        width = console.size.width
    except Exception:
        width = 0
    return max(20, (width or 60) - 12)


def _sweep(console, message, sprite, color, step=2, delay=0.02):
    """Shared helper: slides `sprite` left-to-right across the terminal
    once, then prints the final message in `color`. Used by every
    full-width animation below so they all behave consistently."""
    if not is_interactive():
        console.print(f"{sprite} {message}")
        return
    width = _term_width(console)
    for i in range(0, width, step):
        console.print(f"\r{' ' * i}{sprite}", end="")
        console.file.flush()
        time.sleep(delay)
    console.print()
    console.print(f"[bold {color}]{sprite} {message}[/bold {color}]")


def rocket_launch(console, message):
    """Big-milestone animation: a rocket flies across the whole terminal
    width. Used for the first subject you ever create."""
    _sweep(console, message, "🚀", "cyan", step=2, delay=0.018)


def pet_run(console, message, pet=None):
    """A small animal runs across the terminal - a lighter, playful
    celebration for smaller wins."""
    pet = pet or random.choice(["🐱", "🐶", "🐢", "🐰", "🦊"])
    _sweep(console, message, pet, "green", step=3, delay=0.02)


def confetti_rain(console, message, rows=3):
    """Falling confetti across a few full-width lines - for social/community
    milestones (first feed post, first comment, etc.)."""
    if not is_interactive():
        console.print(f"🎉 {message}")
        return
    confetti = ["🎉", "🎊", "✨", "⭐", "💫", " ", " ", " "]
    width = _term_width(console)
    for _ in range(rows):
        console.print("".join(random.choice(confetti) for _ in range(width // 2)))
        time.sleep(0.06)
    console.print(f"[bold magenta]🎉 {message}[/bold magenta]")


def streak_fire(console, streak_days, message):
    """Building flame animation for daily-streak milestones - the flame
    grows with the streak length, capping out at 5 flames."""
    if not is_interactive():
        console.print(f"🔥 {message}")
        return
    intensity = min(5, max(1, streak_days // 10 + 1))
    for i in range(1, intensity + 1):
        console.print(f"\r{'🔥' * i}", end="")
        console.file.flush()
        time.sleep(0.12)
    console.print()
    console.print(f"[bold red]🔥 {message}[/bold red]")


def trophy_fireworks(console, message):
    """Fireworks building up to a trophy - for a perfect quiz score."""
    if not is_interactive():
        console.print(f"🏆 {message}")
        return
    frames = ["🎆", "✨ 🎆 ✨", "🎇 ✨ 🎆 ✨ 🎇", "🏆 ✨ 🎉 ✨ 🏆"]
    for frame in frames:
        console.print(f"\r{frame.center(_term_width(console))}", end="")
        console.file.flush()
        time.sleep(0.18)
    console.print()
    console.print(f"[bold yellow]🏆 {message}[/bold yellow]")


# Subject-name keyword -> (symbols to animate with, color). Longest/most
# specific keywords should stay early since detect_theme() returns the
# first match by insertion order.
SUBJECT_THEMES = {
    "physics": ("⚛∮∇λ⚡", "cyan"),
    "chemistry": ("⚗🧪⚛🔬", "green"),
    "biology": ("🧬🔬🌱🦠", "green"),
    "math": ("∑∫π√∞±≈", "magenta"),
    "computer": ("01{}<>⌘", "cyan"),
    "programming": ("01{}<>⌘", "cyan"),
    "astronomy": ("🚀🌌⭐🪐", "blue"),
    "space": ("🚀🌌⭐🪐", "blue"),
    "science": ("⚛🧪🔬∑", "cyan"),
}


def detect_theme(subject_name):
    """Matches a subject name against SUBJECT_THEMES by substring; returns
    (symbols, color) or None if nothing matches."""
    lower = subject_name.lower()
    for keyword, theme in SUBJECT_THEMES.items():
        if keyword in lower:
            return theme
    return None


def science_animation(console, subject_name, message):
    """Themed animation using the subject's own symbols (atoms for physics,
    math operators for math, etc.) if the subject name matches a known
    theme. Returns False (and prints nothing) if no theme matched, so
    callers can fall back to a generic celebration instead."""
    theme = detect_theme(subject_name)
    if not theme:
        return False
    symbols, color = theme
    if not is_interactive():
        console.print(f"[{color}]{message}[/{color}]")
        return True
    width = _term_width(console)
    for i in range(0, width, 4):
        frame = "".join(random.choice(symbols) for _ in range(3))
        console.print(f"\r{' ' * i}{frame}", end="")
        console.file.flush()
        time.sleep(0.025)
    console.print()
    console.print(f"[bold {color}]{message}[/bold {color}]")
    return True
