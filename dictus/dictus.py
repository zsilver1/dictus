#!/usr/bin/env python3
from typing import Dict, List, Optional, Tuple
import os
import re
import math
import click
from collections import OrderedDict
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown

from .word_link import WordLinkExtension


class DictusParser:
    pass


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
        self.data_dir = data_dir

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
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


def dictus(input: List[str], ext: str, output_dir: str, templates: str, data: str):
    files = []
    if not ext.startswith("."):
        ext = f".{ext}"
    for i in input:
        if os.path.isdir(i):
            files += [
                os.path.join(i, f)
                for f in os.listdir(i)
                if os.path.splitext(f)[1] == ext
            ]
        else:
            if os.path.splitext(i)[1] == ext:
                files.append(i)

    parser = DictusParser(*files, **_markdown_kwargs())
    langs = parser.run()

    gen = DictusGenerator(
        langs,
        site_name="Language",
        output_dir=output_dir,
        template_dir=templates,
        data_dir=data,
    )
    gen.run()


@click.command()
@click.option(
    "--input",
    "--in",
    help="Input file or directory",
    multiple=True,
    required=True,
    type=click.Path(exists=True),
)
@click.option(
    "--input-ext",
    "--ext",
    help="Input file extension (e.g. 'md')",
    required=True,
    default="md",
    type=str,
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
    default="templates/",
    type=click.Path(exists=True, file_okay=False),
)
@click.option(
    "--data",
    help="Path containing 'dictus.css' and 'dictus.js' files to be included in the output",
    default="data/",
    type=click.Path(exists=True, file_okay=False),
)
def main(input, input_ext, output_dir, templates, data):
    dictus(input, input_ext, output_dir, templates, data)


if __name__ == "__main__":
    main()
