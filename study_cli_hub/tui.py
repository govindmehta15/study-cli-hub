# tui.py - a fixed-layout terminal shell: scrollable output pane on top, a
# permanently pinned input line at the bottom with live '/' completion, and
# a bottom hint toolbar - the same layout Claude Code's and GitHub Copilot
# CLI's own UIs use, instead of a plain scrolling REPL.
#
# Built on prompt_toolkit's Application/Layout primitives (already a
# dependency here) rather than pulling in a whole separate TUI library.
#
# Design note: most of this app's existing menus/flows (create_subject,
# subject_menu, feed_menu, etc.) are built around classic blocking calls
# (Prompt.ask(), input()) that print straight to the real terminal. Those
# can't run *inside* a full-screen Application directly - so this shell
# exposes run_in_terminal(), prompt_toolkit's own documented mechanism for
# temporarily suspending the fixed layout, running a normal blocking
# function untouched, and then restoring the fixed layout afterward. That's
# what lets the main menu gain the real pinned-input experience without
# requiring every single screen in the app to be rewritten at once.
import io
import shutil

from prompt_toolkit.application import Application
from prompt_toolkit.application import run_in_terminal as _run_in_terminal
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.containers import Float, FloatContainer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.menus import CompletionsMenu
from rich.console import Console as RichConsole


class CaptureConsole:
    """A Rich Console that renders into an in-memory ANSI buffer instead of
    the real terminal, so its output can be fed into the TUI's scrollable
    pane via prompt_toolkit's ANSI() bridge. Width tracks the real terminal
    (recomputed on every pop_text(), so it stays correct even if the
    terminal is resized mid-session), falling back to 100 columns if the
    size can't be determined (e.g. not attached to a real terminal)."""

    def __init__(self, width=None):
        self._io = io.StringIO()
        self._fixed_width = width
        self.rich = RichConsole(file=self._io, force_terminal=True, width=self._current_width(), color_system="standard")

    def _current_width(self):
        if self._fixed_width:
            return self._fixed_width
        return shutil.get_terminal_size(fallback=(100, 24)).columns

    def refresh_width(self):
        """Call before rendering a new screen, so this frame's width
        matches the real terminal (which may have been resized since the
        last render)."""
        self.rich.width = self._current_width()

    def pop_text(self):
        text = self._io.getvalue()
        self._io.truncate(0)
        self._io.seek(0)
        return text


class TuiShell:
    """Fixed layout: a header line, a scrollable output pane, a permanently
    pinned input line (with live completion), and a bottom hint toolbar."""

    def __init__(self, completer, on_submit, header_text="", hint_text=""):
        self.header_text = header_text
        self.hint_text = hint_text
        self.on_submit = on_submit
        self._output_text = ""

        self.input_buffer = Buffer(completer=completer, complete_while_typing=True, multiline=False)

        kb = KeyBindings()

        @kb.add("enter")
        def _submit(event):
            text = self.input_buffer.text
            self.input_buffer.reset()
            self.on_submit(text)

        @kb.add("c-c")
        def _interrupt(event):
            event.app.exit(result="__interrupt__")

        self._output_window = Window(
            content=FormattedTextControl(text=self._render_output, focusable=False),
            wrap_lines=True,
            allow_scroll_beyond_bottom=True,
        )
        header_window = Window(
            content=FormattedTextControl(text=lambda: ANSI(self.header_text)), height=1
        )
        separator = Window(height=1, char="─")
        input_window = Window(content=BufferControl(buffer=self.input_buffer), height=1)
        toolbar_window = Window(
            content=FormattedTextControl(text=lambda: [("reverse", self.hint_text)]), height=1
        )

        body = HSplit([header_window, self._output_window, separator, input_window, toolbar_window])
        root = FloatContainer(
            content=body,
            floats=[Float(xcursor=True, ycursor=True, content=CompletionsMenu(max_height=10))],
        )

        self.app = Application(
            layout=Layout(root, focused_element=input_window),
            key_bindings=kb,
            full_screen=True,
            mouse_support=False,
        )

    def _render_output(self):
        return ANSI(self._output_text)

    def set_output(self, text):
        """Replaces the output pane's content and scrolls to the bottom -
        called each time the current screen needs a full redraw, mirroring
        how the old REPL cleared and reprinted the screen every loop."""
        self._output_text = text
        try:
            self._output_window.vertical_scroll = 10**9  # clamped to the real max during rendering
        except Exception:
            pass
        if self.app.is_running:
            self.app.invalidate()

    def run_in_terminal(self, func):
        """Suspends the fixed layout, runs `func` as a normal blocking call
        against the real terminal (so existing Prompt.ask()/input()-based
        code works completely unchanged), then restores the fixed layout.

        prompt_toolkit's run_in_terminal() schedules `func` on the event
        loop and returns a Future immediately - it does NOT block until
        `func` finishes. Callers that need to act on state `func` mutates
        (e.g. redrawing with post-`func` state) must do so via
        future.add_done_callback(...), not just code placed after this
        call returns."""
        return _run_in_terminal(lambda: func() or None)

    def exit(self):
        self.app.exit()

    def run(self):
        return self.app.run()
