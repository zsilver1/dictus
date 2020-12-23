from typing import List, Union, Dict, Optional, Set
from dataclasses import dataclass
import re
from abc import ABC
import math

from fuzzywuzzy import process


@dataclass(frozen=True, eq=True)
class DefId:
    lang: str
    lemma: str
    def_id: str


@dataclass
class Link:
    type: str
    lang: str
    lemma: str
    def_index: Optional[int] = None


LINK_REGEX = re.compile(r"(?:(?P<lang>[^:]*):)?(?P<lemma>\w*)(?::(?P<index>\d*))?")


def parse_link(link_str: str, cur_lang: str, type: str) -> Link:
    m = re.match(LINK_REGEX, link_str)
    if not m:
        raise RuntimeError(f"Invalid link: {link_str}")
    lang = m.group("lang") or cur_lang
    return Link(type, lang, m.group("lemma"), m.group("index"))


class LinkRegistry:
    def __init__(self, lang_set: Set[str]):
        self.links: Dict[DefId, List[Link]] = {}
        self.backlinks: Dict[DefId, List[Link]] = {}
        self.lang_set = lang_set

    def _find_best_lang_match(self, input_lang: str) -> str:
        return process.extractOne(input_lang, self.lang_list)[0]

    def add_link(self, link: Link, from_lang: str, from_lemma: str, from_def_id: int):
        if link.lang not in self.lang_set:
            link.lang = self._find_best_lang_match(link.lang)
        self.links[DefId(from_lang, from_lemma, from_def_id)] = link
        self.backlinks[DefId(link.lang, link.lemma, link.def_index)] = link

    def get_links(self, lang: str, lemma: str, def_id: int) -> List[Link]:
        return self.links[DefId(lang, lemma, def_id)]

    def get_backlinks(self, lang: str, lemma: str, def_id: int) -> List[Link]:
        return self.backlinks[DefId(lang, lemma, def_id)]


class Lemma(ABC):
    def __init__(self, lang: str, name: str, lr: LinkRegistry, **kwargs):
        self._lr = lr
        self.lang = lang
        self.name = name
        self.text = kwargs.pop("text", "")
        self.tags: List[str] = kwargs.pop("tags", [])
        self.defs: List[Definition] = []

        def_list = kwargs.pop("defs", [])
        for i, d in enumerate(def_list):
            self.defs.append(Definition(lang, name, i, lr, **d))

        for k, v in kwargs.items():
            setattr(self, k, v)


class Definition:
    def __init__(self, lang: str, lemma: str, index: int, lr: LinkRegistry, **kwargs):
        self._lr = lr
        self.lang = lang
        self.lemma = lemma
        self.index = index

        self.text = kwargs.pop("text", "")
        self.tags: List[str] = kwargs.pop("tags", [])
        self.glosses = kwargs.pop("glosses", [])
        self.pos: Union[str, List[str]] = kwargs.pop("pos", None)

        links = kwargs.pop("links", [])
        # populate links
        for type, link_strs in links.items():
            if not isinstance(link_strs, list):
                # in this case "link_strs" is actually a single link str
                link = Link.parse_link(link_strs, self.lang, type)
                self._lr.add_link(link, self.lang, self.lemma, self.index)
            else:
                for link_str in link_strs:
                    link = Link.parse_link(link_str, self.lang, type)
                    self._lr.add_link(link, self.lang, self.lemma, self.index)

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def links(self) -> List[Link]:
        return self._lr.get_links(self.lang, self.lemma, self.index)

    @property
    def backlinks(self) -> List[Link]:
        return self._lr.get_backlinks(self.lang, self.lemma, self.index)


class Language:
    def __init__(self, name, **kwargs):
        self.name = name
        self.lemmas: List[Lemma] = []
        self.pos_set = set()

        self.order: int = kwargs.pop("order", math.inf)
        self.display_name: str = kwargs.pop("display_name", name)

        for k, v in kwargs.items():
            setattr(self, k, v)
