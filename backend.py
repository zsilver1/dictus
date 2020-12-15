from typing import Sequence, Tuple
from tinydb import TinyDB, Query


class Backend:
    def __init__(self, lexicon_file: str):
        self.db = TinyDB(lexicon_file)
        self.language = ""

    def set_language(self, language: str):
        self.language = language

    def all_entries(self, language: str = None) -> str:
        language = language or self.language
        entry = Query()
        return self.db.search(entry.language == language)

    def create_entry(
        self,
        name: str,
        pos: str,
        defs: Sequence[str],
        derivations: Sequence[Tuple[str, str]] = None,
        evolutions: Sequence[Tuple[str, str]] = None,
        derived_from: Sequence[Tuple[str, str]] = None,
        evolved_from: Sequence[Tuple[str, str]] = None,
        language: str = None,
    ):
        language = language or self.language
        table = self.db.table(language)
        item = {
            "name": name,
            "pos": pos,
            "defs": defs,
            "derivations": derivations or [],
            "evolutions": evolutions or [],
            "derived_from": derived_from or [],
            "evolved_from": evolved_from or [],
        }
        table.insert(item)

    def update_entry(
        self,
        name: str,
        pos: str,
        defs: Sequence[str],
        derivations: Sequence[Tuple[str, str]] = None,
        evolutions: Sequence[Tuple[str, str]] = None,
        derived_from: Sequence[Tuple[str, str]] = None,
        evolved_from: Sequence[Tuple[str, str]] = None,
        language: str = None,
    ):
        language = language or self.language
        table = self.db.table(language)
        item = {
            "name": name,
            "pos": pos,
            "defs": defs,
            "derivations": derivations or [],
            "evolutions": evolutions or [],
            "derived_from": derived_from or [],
            "evolved_from": evolved_from or [],
        }
        entry = Query()
        table.upsert(item, entry.name == name)

    def delete_entry(self, name: str, language: str = None):
        language = language or self.language
        table = self.db.table(language)
        entry = Query()
        table.remove(entry.name == name)

    def get_entry_by_name(self, name: str, language: str = None):
        language = language or self.language
        table = self.db.table(language)
        entry = Query()
        return table.search(entry.name == name)

    def get_entry_by_def(self, definition: str, language: str = None):
        def _def_matches(vals, definition: str):
            definition = definition.lower()
            for val in vals:
                val = val.lower()
                if val == definition:
                    return True
                if len(val) > len(definition):
                    if definition in val:
                        return True

        language = language or self.language
        table = self.db.table(language)
        entry = Query()
        return table.search(entry.defs.test(_def_matches, definition))
