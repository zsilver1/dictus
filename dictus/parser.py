from typing import List
import os
import tomlkit

from .model import Language, Lemma
from .link import LinkRegistry


class DictusParser:
    def run(self, *files) -> List[Language]:
        self.lang_list = []
        for fname in files:
            fname = os.path.basename(fname)
            lang_name = os.path.splitext(fname)[0]
            self.lang_list.append(lang_name)
        self.lr = LinkRegistry(set(self.lang_list))
        langs = []
        for lang_name, fname in zip(self.lang_list, files):
            with open(fname) as f:
                contents = f.read()
            lang = self._parse_lang_from_file(lang_name, contents)
            langs.append(lang)

        return langs

    def _parse_lang_from_file(self, lang_name: str, contents: str) -> Language:
        toml = tomlkit.parse(contents)
        lang_metadata = toml.pop("metadata", {})
        lang = Language(lang_name, **lang_metadata)
        for lemma, contents in toml.items():
            lem = Lemma(lang, lemma, self.lr, **contents)
            lang.lemmas.append(lem)
        return lang
