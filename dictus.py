#!/usr/bin/env python
import cmd2
import sys
import argparse


class Dictus(cmd2.Cmd):
    def __init__(self):
        shortcuts = cmd2.DEFAULT_SHORTCUTS
        super().__init__(
            shortcuts=shortcuts, auto_load_commands=False, use_ipython=False
        )

        # don't need python scripting
        self.hidden_commands += ["py", "run_pyscript"]

        self._selected_word = ""
        self._selected_language = ""

        self.prompt = "> "

    def set_selected_word(self, new: str):
        if not new:
            return
        self._selected_word = new
        self.prompt = f"({self._selected_language}:{self._selected_word}) > "

    def set_selected_language(self, new: str):
        if not new:
            return
        self._selected_language = new
        if self._selected_word:
            self.prompt = f"({self._selected_language}:{self._selected_word}) > "
        else:
            self.prompt = f"({self._selected_language}) > "

    ############################
    # "exit" Command
    ############################
    def do_exit(self, _):
        return True

    ############################
    # "lang" Command
    ############################
    def lang_set(self, args):
        self.set_selected_language(args.lang)

    def lang_add(self, args):
        pass

    def lang_remove(self, args):
        pass

    lang_parser = argparse.ArgumentParser()
    sub = lang_parser.add_subparsers()
    parser_lang_set = sub.add_parser("set", help="Set the current active language")
    parser_lang_set.add_argument("lang", type=str, help="Language to set as active")
    parser_lang_set.set_defaults(func=lang_set)

    parser_lang_add = sub.add_parser("add", help="Create a new language")
    parser_lang_add.add_argument("lang", type=str, help="New language name")
    parser_lang_add.set_defaults(func=lang_add)

    @cmd2.with_argparser(lang_parser)
    def do_lang(self, args):
        func = getattr(args, "func", None)
        if func:
            func(self, args)
        else:
            self.do_help("lang")

    ############################
    # "word" Command
    ############################
    def word_add(self, args):
        pass

    def word_set(self, args):
        pass

    def word_remove(self, args):
        pass

    def word_edit(self, args):
        pass

    def desc_edit(self, args):
        pass

    word_parser = argparse.ArgumentParser()
    sub = word_parser.add_subparsers()
    parser_word_set = sub.add_parser("add", help="Add a new word, set as active")
    parser_word_set.add_argument("word", type=str, help="Word to add")
    parser_word_set.set_defaults(func=word_add)

    @cmd2.with_argparser(word_parser)
    def do_word(self, args):
        func = getattr(args, "func", None)
        if func:
            func(self, args)
        else:
            self.do_help("lang")

    ############################
    # "def" Command
    ############################
    def def_list(self, args):
        pass

    def def_add(self, args):
        pass

    def def_edit(self, args):
        pass

    def def_remove(self, args):
        pass

    def do_def(self, args):
        func = getattr(args, "func", None)
        if func:
            func(self, args)
        else:
            self.do_help("lang")

    ############################
    # "search" Command
    ############################
    def do_search(self, args):
        pass


if __name__ == "__main__":
    app = Dictus()
    sys.exit(app.cmdloop())
