import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor

from fuzzywuzzy import process


class WordLinkProcessor(InlineProcessor):
    def __init__(self, pattern, md=None, langs=None):
        super().__init__(pattern, md)
        self.langs = langs or []

    def handleMatch(self, m, data):
        el = etree.Element("a")
        word = m.group("word")
        if lang := m.group("lang"):
            lang = process.extractOne(lang, self.langs)[0]
            el.attrib["href"] = f"{lang}.html#{word}"
            el.text = f"{lang}:{word}"
        else:
            el.attrib["href"] = f"#{word}"
            el.text = f"{word}"
        return el, m.start(0), m.end(0)


class WordLinkExtension(Extension):
    regex = r"\[\[(?:(?P<lang>\w*):)?(?P<word>\w*)\]\]"

    def __init__(self, langs, **kwargs):
        self.langs = langs
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            WordLinkProcessor(self.regex, md, self.langs), "wordlink", 175
        )
