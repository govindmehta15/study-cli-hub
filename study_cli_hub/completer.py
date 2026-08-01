from prompt_toolkit.completion import Completer, Completion


class SlashCompleter(Completer):
    """Live '/' command menu, filtered by prefix as the user types (Claude-Code
    style). Optionally also live-filters a command's argument (e.g. matching
    usernames/subjects as you type '/open <name>'), by substring match so a
    fragment of a name anywhere in it surfaces suggestions."""

    def __init__(self, commands, argument_candidates=None):
        # commands: list of (name, args_hint, description)
        # argument_candidates: optional {"/command": callable() -> list[str]}
        self.commands = commands
        self.argument_candidates = argument_candidates or {}

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.startswith("/"):
            return
        typed = text[1:]

        if " " not in typed:
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
            return

        command_part, _, arg_part = typed.partition(" ")
        provider = self.argument_candidates.get("/" + command_part.lower())
        if not provider:
            return
        for candidate, meta in provider():
            if arg_part.lower() in candidate.lower():
                yield Completion(
                    candidate,
                    start_position=-len(arg_part),
                    display=candidate,
                    display_meta=meta,
                )
