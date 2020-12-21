#!/usr/bin/env python3
from typing import List
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


def dictus(input: List[str], output_dir: str, templates: str):
    files = []
    for i in input:
        if os.path.isdir(i):
            files += os.listdir(i)
        else:
            files.append(i)

    parser = DictusParser(*files, **_markdown_kwargs())
    langs = parser.run()

    gen = DictusGenerator(
        langs, site_name="Language", output_dir=output_dir, # template_dir=templates 
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
def main(input, output_dir, templates):
    dictus(input, output_dir, templates)


if __name__ == "__main__":
    main()
