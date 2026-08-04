# animations.py - small, tasteful CLI animation primitives.
#
# Rule that must never be broken: every animated call site degrades to
# instant, plain output with the EXACT SAME final text when not attached to
# a real terminal (sys.stdin.isatty() is False) - only timing/spinner chrome
# differs. This project pipes commands via stdin and reads output for its
# own testing, so nothing here may change what gets printed or block on
# time.sleep() when non-interactive.
import random
import string
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


def static_transition(console, frames=3, height=6):
    """Old-CRT-style noise/static that briefly plays before the branded
    startup banner appears - a quick 'tuning in' effect. No-op when
    non-interactive (there's no final state to preserve for a transition)."""
    if not is_interactive():
        return
    noise_chars = "#%&@*+~."
    width = _term_width(console)
    for _ in range(frames):
        console.clear()
        for _ in range(height):
            console.print("".join(random.choice(noise_chars) if random.random() > 0.4 else " " for _ in range(width)))
        time.sleep(0.05)
    console.clear()


def print_startup_banner(console, app_name="STUDY HUB", version="", tagline=""):
    """Branded ASCII-art startup banner (big block-letter app name behind a
    quick noise/static 'power-on' transition) - the same kind of moment
    gh copilot/Claude Code use to open their own sessions. Degrades to one
    plain line when non-interactive."""
    if not is_interactive():
        console.print(f"{app_name} {version}".strip())
        return

    static_transition(console)

    try:
        import pyfiglet
        big_text = pyfiglet.figlet_format(app_name, font="slant").rstrip("\n")
    except Exception:
        big_text = app_name

    body = "\n".join(f"[bold cyan]{line}[/bold cyan]" for line in big_text.splitlines())
    footer = " ".join(part for part in (version, f"· {tagline}" if tagline else "") if part)
    if footer:
        body += f"\n\n[dim]{footer}[/dim]"
    console.print(cli_panel(body, expand=False))


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
        console.print(f"{frame} {message}", end="\r")
        console.file.flush()
        time.sleep(0.08)
    console.print()


def _term_width(console):
    try:
        width = console.size.width
    except Exception:
        width = 0
    return max(20, (width or 60) - 12)


def _term_height(console):
    try:
        height = console.size.height
    except Exception:
        height = 0
    return max(6, (height or 24) - 10)


def section_reveal(console, title, color="cyan"):
    """Quick full-width wipe that reveals a section title - used when
    entering a frequently-visited screen (like /explore's), so it stays
    snappy (~0.15s total) rather than a slow one-off spectacle like the
    milestone animations below. Degrades to printing `title` instantly."""
    if not is_interactive():
        console.print(f"[bold {color}]{title}[/bold {color}]")
        return
    # NOTE: a leading "\r" embedded in the text itself gets silently
    # stripped by Rich's markup/Text parser (verified directly - even with
    # no markup at all), so the carriage return has to go through `end=`
    # instead, which Rich passes through raw. Every sweep/overwrite
    # animation in this module follows this same pattern for that reason.
    width = _term_width(console)
    frames = 6
    for i in range(1, frames + 1):
        filled = int(width * i / frames)
        console.print(f"[{color}]{'─' * filled}[/{color}]", end="\r")
        console.file.flush()
        time.sleep(0.012)
    console.print()
    console.print(f"[bold {color}]{title}[/bold {color}]")


def row_shimmer(console, color="dim cyan"):
    """Brief animated 'loading' placeholder shown just before a list/table
    renders - an ambient touch for screens with nothing else animated.
    Non-interactive: no-op, since there's no final state worth preserving
    for a transition that's about to be immediately overwritten anyway."""
    if not is_interactive():
        return
    for frame in ["▱▱▱▱", "▰▱▱▱", "▰▰▱▱", "▰▰▰▱", "▰▰▰▰"]:
        console.print(f"[{color}]loading {frame}[/{color}]", end="\r")
        console.file.flush()
        time.sleep(0.035)
    console.print(" " * 24, end="\r")


def _sweep(console, message, sprite, color, step=2, delay=0.02):
    """Shared helper: slides `sprite` left-to-right across the terminal
    once, then prints the final message in `color`. Used by every
    full-width animation below so they all behave consistently."""
    if not is_interactive():
        console.print(f"{sprite} {message}")
        return
    width = _term_width(console)
    for i in range(0, width, step):
        console.print(f"{' ' * i}{sprite}", end="\r")
        console.file.flush()
        time.sleep(delay)
    console.print()
    console.print(f"[bold {color}]{sprite} {message}[/bold {color}]")


def rocket_launch(console, message):
    """Big-milestone animation: a rocket flies across the whole terminal
    width, leaving a two-row exhaust trail for a fuller, bigger feel than a
    plain single-line sweep. Used for the first subject you ever create."""
    if not is_interactive():
        console.print(f"🚀 {message}")
        return
    width = _term_width(console)
    trail_chars = "·∘○"
    for i in range(0, width, 2):
        console.print(f"{' ' * i}🚀", end="\r")
        console.file.flush()
        time.sleep(0.018)
    console.print()
    trail_width = min(width, 60)
    for row in range(2):
        console.print(f"[dim cyan]{''.join(random.choice(trail_chars) for _ in range(trail_width))}[/dim cyan]")
        time.sleep(0.05)
    console.print(f"[bold cyan]🚀 {message}[/bold cyan]")


def pet_run(console, message, pet=None):
    """A small animal runs across the terminal - a lighter, playful
    celebration for smaller wins."""
    pet = pet or random.choice(["🐱", "🐶", "🐢", "🐰", "🦊"])
    _sweep(console, message, pet, "green", step=3, delay=0.02)


def confetti_rain(console, message, rows=None):
    """Falling confetti across a few full-width lines - for social/community
    milestones (first feed post, first comment, etc.). Row count scales
    with the terminal's own height (capped) instead of a fixed small
    number, for a bigger, fuller burst on taller terminals."""
    if not is_interactive():
        console.print(f"🎉 {message}")
        return
    confetti = ["🎉", "🎊", "✨", "⭐", "💫", " ", " ", " "]
    width = _term_width(console)
    row_count = rows if rows is not None else min(6, max(3, _term_height(console) // 4))
    for _ in range(row_count):
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
        console.print("🔥" * i, end="\r")
        console.file.flush()
        time.sleep(0.12)
    console.print()
    console.print(f"[bold red]🔥 {message}[/bold red]")


def trophy_fireworks(console, message):
    """Fireworks building up to a trophy - for a perfect quiz score. Bursts
    across a few full-width rows before the single-line build-up, for a
    bigger, fuller celebration than a plain center-line sweep."""
    if not is_interactive():
        console.print(f"🏆 {message}")
        return
    width = _term_width(console)
    burst_chars = "🎆✨🎇⭐"
    for _ in range(3):
        console.print("".join(random.choice(burst_chars) if random.random() > 0.55 else " " for _ in range(width)))
        time.sleep(0.12)
    frames = ["🎆", "✨ 🎆 ✨", "🎇 ✨ 🎆 ✨ 🎇", "🏆 ✨ 🎉 ✨ 🏆"]
    for frame in frames:
        console.print(frame.center(width), end="\r")
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


# Special-character + letter pool for glitch_reveal()'s scramble effect.
GLITCH_CHARS = "~₹!@#$%^&*()_-+=\\|:;\"'<,>.?/{[}]" + string.ascii_uppercase


def glitch_reveal(console, text, style="bold cyan", cycles=10, delay=0.02):
    """Big 'decoding' effect: every character cycles through random special
    symbols/letters before locking into place left-to-right, until the real
    text is fully revealed. Degrades to printing `text` instantly, unchanged,
    when non-interactive."""
    if not is_interactive():
        console.print(text, style=style)
        return
    length = len(text)
    for frame in range(1, cycles + 1):
        settled = int(length * frame / cycles)
        display = [
            ch if (ch == " " or i < settled) else random.choice(GLITCH_CHARS)
            for i, ch in enumerate(text)
        ]
        console.print("".join(display), style=style, end="\r")
        console.file.flush()
        time.sleep(delay)
    console.print()


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
        frame = "".join(random.choice(symbols) for _ in range(5))
        console.print(f"{' ' * i}{frame}", end="\r")
        console.file.flush()
        time.sleep(0.025)
    console.print()
    console.print("".join(random.choice(symbols) for _ in range(width)), style=f"dim {color}")
    console.print(f"[bold {color}]{message}[/bold {color}]")
    return True
