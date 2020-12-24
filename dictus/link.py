from typing import Optional, Set, List, Dict
from collections import OrderedDict
from dataclasses import dataclass
import re
from functools import cached_property
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
from fuzzywuzzy import process

LINK_REGEX_STR = r"(?:(?P<lang>[^\d\W]*):)?(?P<lemma>[^:]*)(?::(?P<index>\d*))?"
LINK_REGEX = re.compile(LINK_REGEX_STR)

MARKDOWN_LINK_REGEX = (
    r"\[\[(?:(?P<lang>[^\d\W]*):)?(?P<lemma>[^:]*)(?::(?P<index>\d*))?\]\]"
)


@dataclass(frozen=True, eq=True)
class DefId:
    lang: str
    lemma: str
    def_index: int


@dataclass
class Link:
    type: str
    lang: str
    lemma: str
    def_index: int = 1

    @cached_property
    def url(self) -> str:
        el = etree.Element("a")
        if self.def_index:
            el.attrib["href"] = f"{self.lang}.html#{self.lemma}:{self.def_index}"
        else:
            el.attrib["href"] = f"{self.lang}.html#{self.lemma}"
        el.text = f"{self.lang}: {self.lemma}({self.def_index})"
        return etree.tostring(el, encoding="unicode")


@dataclass
class LinkGroup:
    type: str
    links: List[Link]


def parse_link(link_str: str, cur_lang: str, type: str) -> Link:
    m = re.match(LINK_REGEX, link_str)
    if not m:
        raise RuntimeError(f"Invalid link: {link_str}")
    lang = m.group("lang") or cur_lang
    lemma = m.group("lemma")
    index = m.group("index")

    # this handles the case where we have a link like "word:4" in this case, the
    # word will be in the lang group, the index will be in the lemma group, and
    # the index group will be None
    if not index and lemma.isnumeric():
        index = lemma
        lemma = lang
        lang = cur_lang
    return Link(type, lang, lemma, index)


class LinkRegistry:
    def __init__(self, lang_set: Set[str]):
        self.links: Dict[DefId, OrderedDict[str, List[Link]]] = {}
        self.backlinks: Dict[DefId, OrderedDict[str, List[Link]]] = {}
        self.lang_set = lang_set

    def find_best_lang_match(self, input_lang: str) -> str:
        return process.extractOne(input_lang, self.lang_set)[0]

    def add_link(self, link: Link, from_lang: str, from_lemma: str, from_def_id: int):
        if link.def_index:
            link.def_index = int(link.def_index)
        else:
            link.def_index = 1
        if link.lang not in self.lang_set:
            link.lang = self.find_best_lang_match(link.lang)

        d_id = DefId(from_lang, from_lemma, from_def_id)
        if not self.links.get(d_id):
            self.links[d_id] = OrderedDict()
        if not self.links[d_id].get(link.type):
            self.links[d_id][link.type] = []
        self.links[d_id][link.type].append(link)

        backlink_def_id = DefId(link.lang, link.lemma, link.def_index)
        backlink = Link(link.type, from_lang, from_lemma, from_def_id)
        if not self.backlinks.get(backlink_def_id):
            self.backlinks[backlink_def_id] = OrderedDict()
        if not self.backlinks[backlink_def_id].get(link.type):
            self.backlinks[backlink_def_id][link.type] = []
        self.backlinks[backlink_def_id][link.type].append(backlink)

    def get_links(self, lang: str, lemma: str, def_id: int) -> List[LinkGroup]:
        link_map = self.links.get(DefId(lang, lemma, def_id), {})
        if not link_map:
            return []
        ret = []
        for type, links in link_map.items():
            ret.append(LinkGroup(type, links))
        return ret

    def get_backlinks(self, lang: str, lemma: str, def_id: int) -> List[LinkGroup]:
        link_map = self.backlinks.get(DefId(lang, lemma, def_id), {})
        if not link_map:
            return []
        ret = []
        for type, links in link_map.items():
            ret.append(LinkGroup(type, links))
        return ret


class DictusLinkProcessor(InlineProcessor):
    def __init__(self, pattern, md=None, lr: LinkRegistry = None):
        super().__init__(pattern, md)
        self.lr = lr

    def handleMatch(self, m, data):
        el = etree.Element("a")
        lemma = m.group("lemma")
        lang = m.group("lang")
        index = m.group("index")

        # this handles the case where we have a link like "word:4" in this case, the
        # word will be in the lang group, the index will be in the lemma group, and
        # the index group will be None
        if not index and lemma.isnumeric():
            index = lemma
            lemma = lang
            lang = None

        if lang and index:
            lang = self.lr.find_best_lang_match(lang)
            el.attrib["href"] = f"{lang}.html#{lemma}:{index}"
            el.text = f"{lang}:{lemma}({index})"
        elif lang:
            lang = self.lr.find_best_lang_match(lang)
            el.attrib["href"] = f"{lang}.html#{lemma}"
            el.text = f"{lang}:{lemma}"
        elif index:
            el.attrib["href"] = f"#{lemma}:{index}"
            el.text = f"{lemma}({index})"
        else:
            el.attrib["href"] = f"#{lemma}"
            el.text = f"{lemma}"
        return el, m.start(0), m.end(0)


class DictusLinkExtension(Extension):
    def __init__(self, lr: LinkRegistry, **kwargs):
        self.lr = lr
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            DictusLinkProcessor(MARKDOWN_LINK_REGEX, md, self.lr), "dictuslink", 175
        )
