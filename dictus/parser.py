from typing import List
import os
from enum import Enum

from .model import Language, Lemma
from .link import LinkRegistry


class Dialect(Enum):
    YAML = "yaml"
    TOML = "toml"
    JSON = "json"

    @staticmethod
    def parse_contents(dialect, text: str) -> str:
        if dialect == Dialect.YAML:
            import yaml

            return yaml.safe_load(text)
        elif dialect == Dialect.TOML:
            import tomlkit

            return tomlkit.parse(text)
        elif dialect == Dialect.JSON:
            import json

            return json.loads(text)


class DictusParser:
    def __init__(self, dialect: Dialect):
        self.dialect = dialect

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
            if lang:
                lang.pos_set = list(lang.pos_set)
                lang.pos_set.sort()
                langs.append(lang)

        return langs

    def _parse_lang_from_file(self, lang_name: str, contents: str) -> Language:
        lang_dict = Dialect.parse_contents(self.dialect, contents)
        if not lang_dict:
            return None
        lang_metadata = lang_dict.pop("metadata", {})
        lang = Language(lang_name, **lang_metadata)
        for lemma, contents in lang_dict.items():
            if not contents:
                continue
            lem = Lemma(lang, lemma, self.lr, **contents)
            lang.lemmas.append(lem)
        return lang
