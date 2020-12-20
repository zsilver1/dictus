from typing import List
import os

from jinja2 import Environment, PackageLoader, select_autoescape

from parser import Language, Word, Definition


class DictusGenerator:
    def __init__(
        self,
        langs: List[Language],
        site_name: str = "Dictionary",
        template_dir: str = "templates",
        output_dir: str = "build"
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
        return template.render(site_name=self.site_name, lang=lang)

    @staticmethod
    def _format_lang_for_display(lang_name: str):
        return "-".join(map(str.capitalize, lang_name.split("_")))
