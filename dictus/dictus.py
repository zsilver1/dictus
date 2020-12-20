#!/usr/bin/env python3

import os
import click

from parser import DictusParser
from generator import DictusGenerator


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


def dictus(input: str, output_dir: str, templates: str):
    files = []
    if os.path.isdir(input):
        files = os.listdir(input)
    else:
        files = [input]

    parser = DictusParser(*files, **_markdown_kwargs())
    langs = parser.run()

    gen = DictusGenerator(
        langs, site_name="Language", template_dir=templates, output_dir=output_dir
    )


@click.command()
@click.option(
    "--input",
    "--in",
    help="Input markdown file or directory with markdown files",
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
def main(input, output_dir, templates):
    dictus(input, output_dir, templates)


if __name__ == "__main__":
    main()
