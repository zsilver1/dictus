from typing import List
import os
import tomlkit
from .model import LinkRegistry, Language, Lemma


class DictusParser:
    def __init__(self):
        self.lr = LinkRegistry()

    def run(self, *files) -> List[Language]:
        langs = []
        for fname in files:
            name = os.path.splitext(fname)[0]
            with open(fname) as f:
                contents = f.read()
            lang = self._parse_lang_from_file(name, contents)
            langs.append(lang)

        return langs

    def _parse_lang_from_file(self, lang_name: str, contents: str) -> Language:
        toml = tomlkit.parse(contents)
        lang_metadata = toml.pop("metadata", {})
        lang = Language(lang_name, **lang_metadata)
        for lemma, contents in toml.items():
            lem = Lemma(lang_name, lemma, self.lr, **contents)
            lang.lemmas.append(lem)
        return lang
