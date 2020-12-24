from typing import Dict, List, Optional, Tuple
import os
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown

from .word_link import WordLinkExtension
from .model import Language


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
            autoescape=select_autoescape(["jinja2"]),
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
