import sys
from dataclasses import dataclass
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML

from backend import Backend, Entry


bindings = KeyBindings()


@bindings.add("c-d")
@bindings.add("c-c")
def _exit(event):
    sys.exit(0)


@dataclass
class Action:
    name: str
    func: object


class App:
    def __init__(self, lexicon: str):
        self.backend = Backend(lexicon)
        self.actions = {"a": Action("edit", self.edit)}
        self.cur_actions = self.actions

    def handle_input(self, input_str):
        try:
            self.cur_actions[input_str].func()
            return True
        except KeyError:
            return False

    def toolbar(self):
        html = ""
        for key, action in self.cur_actions.items():
            html += f"{key} - {action.name} | "
        html = " " + html[:-3]
        return HTML(html)

    def edit(self):
        print("edited")


@click.command()
@click.option("--lexicon", default="lexicon.json", required=True)
def main(lexicon):
    a = App()
    session = PromptSession()
    while 1:
        user_input = session.prompt(
            "> ", bottom_toolbar=a.toolbar, key_bindings=bindings
        )
        handled = a.handle_input(user_input)
        if not handled:
            print(f'"{user_input}" is not a valid command...\n')


if __name__ == "__main__":
    main()
