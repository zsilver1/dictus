from typing import Optional, Set, List, Dict
from dataclasses import dataclass
import re
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
from fuzzywuzzy import process

LINK_REGEX_STR = r"(?:(?P<lang>[^\d\W]*):)?(?P<lemma>\D*)(?::(?P<index>\d*))?"
LINK_REGEX = re.compile(LINK_REGEX_STR)

MARKDOWN_LINK_REGEX = r"\[\[(?:(?P<lang>[^\d\W]*):)?(?P<lemma>\D*)(?::(?P<index>\d*))?\]\]"


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

    def find_best_lang_match(self, input_lang: str) -> str:
        return process.extractOne(input_lang, self.lang_set)[0]

    def add_link(self, link: Link, from_lang: str, from_lemma: str, from_def_id: int):
        if link.lang not in self.lang_set:
            link.lang = self.find_best_lang_match(link.lang)
        self.links[DefId(from_lang, from_lemma, from_def_id)] = link
        self.backlinks[DefId(link.lang, link.lemma, link.def_index)] = link

    def get_links(self, lang: str, lemma: str, def_id: int) -> List[Link]:
        return self.links[DefId(lang, lemma, def_id)]

    def get_backlinks(self, lang: str, lemma: str, def_id: int) -> List[Link]:
        return self.backlinks[DefId(lang, lemma, def_id)]


class DictusLinkProcessor(InlineProcessor):
    def __init__(self, pattern, md=None, lr: LinkRegistry = None):
        super().__init__(pattern, md)
        self.lr = lr

    def handleMatch(self, m, data):
        el = etree.Element("a")
        lemma = m.group("lemma")
        lang = m.group("lang")
        index = m.group("index")
        if lang and index:
            lang = self.lr.find_best_lang_match(lang)
            el.attrib["href"] = f"{lang}.html#{lemma}:{index}"
            el.text = f"{lang}:{lemma}"
        elif lang:
            lang = self.lr.find_best_lang_match(lang)
            el.attrib["href"] = f"{lang}.html#{lemma}"
            el.text = f"{lang}:{lemma}"
        elif index:
            el.attrib["href"] = f"#{lemma}:{index}"
            el.text = f"{lemma}"
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
