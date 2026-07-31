from prompt_toolkit.completion import Completer, Completion


class SlashCompleter(Completer):
    """Live '/' command menu, filtered by prefix as the user types (Claude-Code style)."""

    def __init__(self, commands):
        # commands: list of (name, args_hint, description)
        self.commands = commands

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.startswith("/"):
            return
        typed = text[1:]
        if " " in typed:
            return
        for name, args_hint, description in self.commands:
            bare_name = name[1:]  # command without the leading "/"
            if bare_name.lower().startswith(typed.lower()):
                display = name + (" " + args_hint if args_hint else "")
                yield Completion(
                    bare_name,
                    start_position=-len(typed),
                    display=display,
                    display_meta=description,
                )
