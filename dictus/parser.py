from typing import Dict, List, Optional, Tuple
import os
import markdown
import re
from .word_link import WordLinkExtension


class Word:
    def __init__(self, name: str):
        self.name = name
        self.text = ""
        self.props: Dict[str, str] = {}
        self.defs: List[Definition] = []

    def __repr__(self):
        return f"Word({self.name}, {self.props}, {self.defs})"


class Definition:
    def __init__(self):
        self.text = ""
        self.props: Dict[str, str] = {}

    def __repr__(self):
        return f"Def({self.props})"


class DictusParser:

    property_regex = re.compile(r"^\$\{(.*):\s*(.*)\}")

    def __init__(self, *files, **markdown_kwargs):
        self.words: List[Word] = []
        self.languages: Dict[str, List[Word]] = {}
        self.files = files
        for f in files:
            lang = self._extract_lang_name(f)
            self.languages[lang] = []
        self.cur_word: Optional[Word] = None
        self.cur_def: Optional[Definition] = None

        if not markdown_kwargs.get("extensions"):
            markdown_kwargs["extensions"] = []

        markdown_kwargs["extensions"].append(WordLinkExtension(self.languages.keys()))
        self.markdown = markdown.Markdown(**markdown_kwargs)

    def run(self) -> Dict[str, List[Word]]:
        for f in self.files:
            self._populate_from_file(f)
        return self.languages

    @staticmethod
    def _extract_lang_name(filename: str) -> str:
        filename = os.path.basename(filename)
        return os.path.splitext(filename)[0]

    @staticmethod
    def _get_header_from_line(line: str) -> Optional[str]:
        if line.strip().startswith("# "):
            header = line[2:].strip()
            return header
        return None

    @staticmethod
    def _get_prop_from_line(line: str) -> Optional[Tuple[str, str]]:
        line = line.strip()
        if m := DictusParser.property_regex.match(line):
            return (m.group(1), m.group(2))
        return None

    def _parse_markdown(self, text_lines: List[str]) -> str:
        text = "".join(text_lines)
        text = text.strip()
        return self.markdown.convert(text)

    def _populate_from_file(self, filename):
        lang = self._extract_lang_name(filename)
        words: List[Word] = []
        cur_text = []

        with open(filename) as f:
            lines = f.readlines()

        for line in lines:
            # create a new word
            if word := self._get_header_from_line(line):
                if self.cur_def and self.cur_word:
                    self.cur_def.text = self._parse_markdown(cur_text)
                    self.cur_word.defs.append(self.cur_def)
                    words.append(self.cur_word)
                    # clear the current def
                    self.cur_def = None
                elif self.cur_word:
                    self.cur_word.text = self._parse_markdown(cur_text)
                    words.append(self.cur_word)
                cur_text = []
                self.cur_word = Word(word)

            # create a new definition
            elif line.startswith("---"):
                if self.cur_def and self.cur_word:
                    self.cur_def.text = self._parse_markdown(cur_text)
                    cur_text = []
                    self.cur_word.defs.append(self.cur_def)
                self.cur_def = Definition()

            # parse properties and add to relevant word or def
            elif prop := self._get_prop_from_line(line):
                if self.cur_def:
                    self.cur_def.props[prop[0]] = prop[1]
                elif self.cur_word:
                    self.cur_word.props[prop[0]] = prop[1]

            else:
                cur_text.append(line)

        if self.cur_def and self.cur_word:
            self.cur_def.text = self._parse_markdown(cur_text)
            self.cur_word.defs.append(self.cur_def)

        elif self.cur_word:
            self.cur_word.text = self._parse_markdown(cur_text)
            words.append(self.cur_word)

        self.languages[lang] = words