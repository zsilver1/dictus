from typing import Sequence, Optional, Tuple
from tinydb import TinyDB, Query
from tinydb.table import Table


DocId = int


class Word:
    def __init__(self, word_name: str, defs: Sequence[Definition] = None):
        self.word_name = word_name
        self.defs = defs or []

    def dump(self) -> dict:
        return {
            "word": self.word_name,
            "defs": [d.dump() for d in self.defs],
        }

    @staticmethod
    def load(word_dict: dict) -> Word:
        return Word(word_dict["word"], word_dict["defs"])


class Definition:
    def __init__(self, pos: str, glosses: Sequence[str], desc: str = None):
        self.pos = pos
        self.glosses = glosses
        self.desc = desc

    def dump(self) -> dict:
        return {"pos": self.pos, "glosses": self.glosses, "desc": self.desc}

    @staticmethod
    def load(def_dict) -> Definition:
        return Definition(def_dict["pos"], def_dict["glosses"], def_dict.get("desc"))


class Model:

    LANGUAGE_TABLE = "languages"

    def __init__(self, db_file):
        self.db = TinyDB(db_file)
        self.lang = None

    def _get_lang_table(self, lang: str) -> Table:
        lang = lang or self.lang
        if not lang:
            raise RuntimeError("No language selected")
        return self.db.table(lang)

    def insert_word(self, word: Word, lang: str = None) -> DocId:
        table = self._get_lang_table(lang)
        return table.insert(word.dump())

    def insert_language(self, lang: str) -> DocId:
        if lang == Model.LANGUAGE_TABLE:
            raise RuntimeError("Invalid language name: 'languages'")

        language = Query()
        if self.db.get(language.language == lang):
            raise RuntimeError("Language already exists")

        lang_table = self.db.table(Model.LANGUAGE_TABLE)
        lang_table.insert({"language": lang})

    def set_language(self, lang: str):
        lang_table = self.db.table(Model.LANGUAGE_TABLE)
        language = Query()
        if not self.db.get(language.language == lang):
            raise RuntimeError("Language not found")
        self.lang = lang

    def get_word_by_id(self, word_id: DocId, lang: str = None) -> Optional[Word]:
        table = self._get_lang_table(lang)
        word = Query()
        doc = table.get(doc_id=word_id)
        if doc:
            return Word.load(doc)
        return None

    def search_words_by_name(self, word_name: str, lang: str = None) -> Sequence[Word]:
        table = self._get_lang_table(lang)
        word = Query()
        docs = table.search((word.word == word_name))
        return [Word.load(w) for w in docs]

    def search_words_by_gloss(
        self, gloss: str, lang: str = None
    ) -> Sequence[Tuple[Word, int]]:
        def _gloss_test(vals, gloss):
            gloss = gloss.lower()
            for v in vals:
                v = v.lower()
                if v == gloss:
                    return True
                if gloss in v:
                    return True
            return False

        table = self._get_lang_table(lang)
        word = Query()
        def_q = Query()
        docs = table.search((word.defs.any(def_q.glosses.test(_gloss_test, gloss))))
        return [Word.load(w) for w in docs]

    def search_words_by_pos(
        self, pos: str, lang: str = None
    ) -> Sequence[Tuple[Word, int]]:
        table = self._get_lang_table(lang)
        word = Query()
        def_q = Query()
        docs = table.search((word.defs.any(def_q.glosses.test(_gloss_test, gloss))))
        return [Word.load(w) for w in docs]
        

    def search_words_by_gloss_pos(
        self,
        gloss: str,
        pos: str,
        lang: str = None,
    ) -> Sequence[Word]:
        table = self._get_lang_table(lang)
        word = Query()

    def get_all_words(self, lang: str = None) -> Sequence[Word]:
        table = self._get_lang_table(lang)
        return [Word.load(w) for w in table.all()]

    def get_all_languages(self) -> Sequence[str]:
        lang_table = self.db.table(Model.LANGUAGE_TABLE)
        return lang_table.all()
