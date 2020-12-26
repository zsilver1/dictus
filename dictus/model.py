from typing import List
from abc import ABC
import math
from collections import OrderedDict
from markdown import Markdown
from .link import DictusLinkExtension, LinkRegistry, LinkGroup, parse_link


MARKDOWN_KWARGS = {
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


def parse_markdown(text: str, lr: LinkRegistry) -> str:
    kwargs = MARKDOWN_KWARGS
    kwargs["extensions"].append(DictusLinkExtension(lr))
    markdown = Markdown(**kwargs)
    return markdown.convert(text)


class Language:
    def __init__(self, name, **kwargs):
        self.name = name
        self.lemmas = []
        self.pos_set = set()

        self.order: int = kwargs.pop("order", math.inf)
        self.display_name: str = kwargs.pop("display_name", name)

        for k, v in kwargs.items():
            setattr(self, k, v)


class Lemma(ABC):
    def __init__(self, lang: Language, name: str, lr: LinkRegistry, **kwargs):
        self._lr = lr
        self.lang = lang
        self.name = name
        self.text = parse_markdown(kwargs.pop("text", ""), lr)
        self.tags = [tag.strip() for tag in kwargs.pop("tags", [])]
        self.defs: List[Definition] = []

        def_list = kwargs.pop("defs", [])
        for i, d in enumerate(def_list):
            self.defs.append(Definition(lang, name, i + 1, lr, **d))

        for k, v in kwargs.items():
            setattr(self, k, v)


def _strip_list_or_str(list_or_str) -> List[str]:
    if isinstance(list_or_str, list):
        return [s.strip() for s in list_or_str]
    else:
        return [list_or_str.strip()]


class Definition:
    def __init__(
        self, lang: Language, lemma: str, index: int, lr: LinkRegistry, **kwargs
    ):
        self._lr = lr
        self.lang = lang
        self.lemma = lemma
        self.index = index

        self.text = parse_markdown(kwargs.pop("text", ""), lr)
        self.tags = _strip_list_or_str(kwargs.pop("tags", []))
        self.glosses = _strip_list_or_str(kwargs.pop("glosses", []))
        self.pos = _strip_list_or_str(kwargs.pop("pos", []))
        self.props = OrderedDict()
        if self.pos:
            lang.pos_set.update(self.pos)

        links = kwargs.pop("links", {})
        # populate links
        for type, link_strs in links.items():
            if not isinstance(link_strs, list):
                # in this case "link_strs" is actually a single link str
                link = parse_link(link_strs, self.lang.name, type)
                self._lr.add_link(link, self.lang.name, self.lemma, self.index)
            else:
                for link_str in link_strs:
                    link = parse_link(link_str, self.lang.name, type)
                    self._lr.add_link(link, self.lang.name, self.lemma, self.index)

        for k, v in kwargs.items():
            setattr(self, k, v)
            self.props[k] = v

    @property
    def link_groups(self) -> List[LinkGroup]:
        return self._lr.get_links(self.lang.name, self.lemma, self.index)

    @property
    def backlink_groups(self) -> List[LinkGroup]:
        return self._lr.get_backlinks(self.lang.name, self.lemma, self.index)
