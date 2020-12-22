#!/usr/bin/env python3
from typing import Dict, List, Optional, Tuple
import os
import re
import click
from collections import OrderedDict
from jinja2 import Environment, PackageLoader, select_autoescape
import xml.etree.ElementTree as etree

import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor

from fuzzywuzzy import process


class WordLinkProcessor(InlineProcessor):
    def __init__(self, pattern, md=None, langs=None):
        super().__init__(pattern, md)
        self.langs = langs or []

    def handleMatch(self, m, data):
        el = etree.Element("a")
        word = m.group("word")
        if lang := m.group("lang"):
            lang = process.extractOne(lang, self.langs)[0]
            el.attrib["href"] = f"{lang}.html#{word}"
            el.text = f"{lang}:{word}"
        else:
            el.attrib["href"] = f"#{word}"
            el.text = f"{word}"
        return el, m.start(0), m.end(0)


class WordLinkExtension(Extension):
    regex = r"\[\[(?:(?P<lang>\w*):)?(?P<word>\w*)\]\]"

    def __init__(self, langs, **kwargs):
        self.langs = langs
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            WordLinkProcessor(self.regex, md, self.langs), "wordlink", 175
        )


class Word:
    def __init__(self, name: str):
        self.name = name
        self.text = ""
        self.props: OrderedDict[str, str] = OrderedDict()
        self.defs: List[Definition] = []

    def __repr__(self):
        return f"Word({self.name}, {self.props}, {self.defs})"


class Definition:
    def __init__(self):
        self.text = ""
        self.props: Dict[str, str] = {}

    def __repr__(self):
        return f"Def({self.props})"


class Language:
    def __init__(self, name):
        self.name = name
        self.display_name = self._format_lang_for_display(name)
        self.words: List[Word] = []
        self.pos_set = set()

    @staticmethod
    def _format_lang_for_display(lang_name: str):
        return "-".join(map(str.capitalize, lang_name.split("_")))


class DictusParser:

    property_regex = re.compile(r"^\$\{(.*):\s*(.*)\}")

    def __init__(self, *files, **markdown_kwargs):
        self.languages: List[Language] = []
        self.files = files

        lang_names = []
        for f in files:
            lang_names.append(self._extract_lang_name(f))
        self.cur_word: Optional[Word] = None
        self.cur_def: Optional[Definition] = None
        self.cur_lang: Optional[Language] = None

        if not markdown_kwargs.get("extensions"):
            markdown_kwargs["extensions"] = []

        markdown_kwargs["extensions"].append(WordLinkExtension(lang_names))
        self.markdown = markdown.Markdown(**markdown_kwargs)

    def run(self) -> List[Language]:
        for f in self.files:
            self.cur_word = None
            self.cur_def = None
            self.cur_lang = None
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

    def _get_prop_from_line(self, line: str) -> Optional[Tuple[str, str]]:
        line = line.strip()
        if m := DictusParser.property_regex.match(line):
            # special case for parts of speech
            if m.group(1) == "pos":
                self.cur_lang.pos_set.add(m.group(2).lower().strip())
            return (m.group(1), m.group(2))
        return None

    def _parse_markdown(self, text_lines: List[str]) -> str:
        text = "".join(text_lines)
        text = text.strip()
        return self.markdown.convert(text)

    def _populate_from_file(self, filename):
        lang = self._extract_lang_name(filename)
        self.cur_lang = Language(lang)
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
                elif self.cur_word:
                    self.cur_word.text = self._parse_markdown(cur_text)
                    cur_text = []
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
            words.append(self.cur_word)

        elif self.cur_word:
            self.cur_word.text = self._parse_markdown(cur_text)
            words.append(self.cur_word)

        self.cur_lang.words = words
        self.languages.append(self.cur_lang)


class DictusGenerator:
    def __init__(
        self,
        langs: List[Language],
        site_name: str = "Dictionary",
        template_dir: str = "templates",
        output_dir: str = "build",
        data_dir: str = "data",
    ):
        self.site_name = site_name
        self.output_dir = output_dir
        self.env = Environment(
            loader=PackageLoader("dictus", template_dir),
            autoescape=select_autoescape(["html"]),
        )
        self.langs = langs

    def run(self):
        for lang in self.langs:
            path = os.path.join(self.output_dir, f"{lang.name}.html")
            with open(path, "w") as f:
                f.write(self._render_lang_file(lang))

    def _render_lang_file(self, lang: Language) -> str:
        template = self.env.get_template("lang.jinja2")
        return template.render(
            site_name=self.site_name,
            lang=lang,
            langs=[(l.name, l.display_name) for l in self.langs],
        )


def _markdown_kwargs():
    return {
        "extensions": [
            "footnotes",
            "tables",
            "smarty",
            "sane_lists",
            "pymdownx.betterem",
            "pymdownx.caret",
            "pymdownx.tilde",
        ]
    }


def dictus(input: List[str], output_dir: str, templates: str, data: str):
    files = []
    for i in input:
        if os.path.isdir(i):
            files += os.listdir(i)
        else:
            files.append(i)

    parser = DictusParser(*files, **_markdown_kwargs())
    langs = parser.run()

    gen = DictusGenerator(
        langs,
        site_name="Language",
        output_dir=output_dir,
        # template_dir=templates,
        # data_dir=data,
    )
    gen.run()


@click.command()
@click.option(
    "--input",
    "--in",
    help="Input markdown file or directory with markdown files",
    multiple=True,
    required=True,
    type=click.Path(exists=True),
)
@click.option(
    "--output-dir",
    "--out",
    help="Output directory to write html files",
    type=click.Path(exists=True, file_okay=False),
)
@click.option(
    "--templates",
    help="Directory with templates 'base.jinja2' and 'lang.jinja2'",
    type=click.Path(exists=True, file_okay=False),
)
@click.option(
    "--data",
    help="Path containing 'dictus.css' and 'dictus.js' files to be included in the output",
    type=click.Path(exists=True, file_okay=False),
)
def main(input, output_dir, templates, data):
    dictus(input, output_dir, templates, data)


if __name__ == "__main__":
    main()
