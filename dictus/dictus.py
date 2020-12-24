#!/usr/bin/env python3
from typing import List
import os
import click

from .parser import DictusParser, Dialect
from .generator import DictusGenerator


def dictus(
    input: List[str], dialect: Dialect, output_dir: str, templates: str, data: str
):
    files = []
    ext = dialect.value
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

    parser = DictusParser(dialect)
    langs = parser.run(*files)

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
    "--input-dialect",
    "--dialect",
    help="Input file dialect",
    required=True,
    default="yaml",
    type=click.Choice([e.value for e in Dialect], case_sensitive=False),
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
def main(input, input_dialect, output_dir, templates, data):
    dictus(input, Dialect(input_dialect), output_dir, templates, data)


if __name__ == "__main__":
    main()
