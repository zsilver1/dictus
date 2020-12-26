#!/usr/bin/env python3
from typing import List
import os
import click
import pkg_resources
import shutil

from .parser import DictusParser, Dialect
from .generator import DictusGenerator


def dictus(
    input: List[str],
    dialect: Dialect,
    output_dir: str,
    templates: str,
    data: str,
    sort: bool,
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

    parser = DictusParser(dialect, sort)
    langs = parser.run(*files)
    if not langs:
        print("No languages were found...")
        return
    gen = DictusGenerator(
        langs,
        site_name="Language",
        output_dir=output_dir,
        template_dir=templates,
        data_dir=data,
    )
    gen.run()


def setup(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    if not os.path.isdir("data"):
        os.mkdir("data")
    css_file = pkg_resources.resource_filename(__name__, "data/dictus.css")
    js_file = pkg_resources.resource_filename(__name__, "data/dictus.js")
    shutil.copy(css_file, "data")
    shutil.copy(js_file, "data")

    if not os.path.isdir("templates"):
        os.mkdir("templates")
    base_temp_file = pkg_resources.resource_filename(__name__, "templates/base.jinja2")
    lang_temp_file = pkg_resources.resource_filename(__name__, "templates/lang.jinja2")
    shutil.copy(base_temp_file, "templates")
    shutil.copy(lang_temp_file, "templates")
    ctx.exit()


@click.command()
@click.option(
    "--setup",
    is_flag=True,
    callback=setup,
    expose_value=False,
    is_eager=True,
    help="Copies default templates, .js, and .css files to the current directory",
)
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
@click.option(
    "--sort",
    is_flag=True,
    default=True,
    help="If true, will alphabetize the lexicon",
)
def main(input, input_dialect, output_dir, templates, data, sort):
    dictus(input, Dialect(input_dialect), output_dir, templates, data, sort)


if __name__ == "__main__":
    main()
