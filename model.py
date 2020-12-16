from typing import Sequence, Optional, Dict
from tinydb import TinyDB, Query
from tinydb.database import Document


DocId = int
Word = str


class Model:

    LANGUAGE_TABLE = "languages"
    WORD_TABLE = "words"
    DEFS_TABLE = "defs"

    def __init__(self, db_file):
        self.db = TinyDB(db_file)
        self.lang = None
        self.lang_id = None
        # words table contains word_id -> {word, language_id, [definition_ids]}
        # languages table contains id -> {language}
        # definitions table contains def_id -> {pos, [glosses], desc, word_id, lang_id}
        self.lang_table = self.db.table(self.LANGUAGE_TABLE)
        self.word_table = self.db.table(self.WORD_TABLE)
        self.defs_table = self.db.table(self.DEFS_TABLE)

    def insert_word(self, word: Word) -> DocId:
        return self.word_table.insert({"word": word, "lang": self.lang_id})

    def insert_language(self, lang: str) -> DocId:
        return self.lang_table.insert({"language": lang})

    def insert_def(self, new_def: Dict):
        new_def["lang"] = self.lang_id
        self.defs_table.insert(new_def)

    def set_language(self, lang: str):
        language = Query()
        rec = self.lang_table.get(language.language == lang)
        if not rec:
            raise RuntimeError("Language not found")
        self.lang = lang
        self.lang_id = rec.doc_id

    def get_word_by_id(self, word_id: DocId) -> Optional[Document]:
        return self.word_table.get(doc_id=word_id)

    def search_words_by_name(self, word_name: str) -> Sequence[Document]:
        word = Query()
        return self.word_table.search(
            (word.word == word_name) & (word.lang == self.lang_id)
        )

    @staticmethod
    def _gloss_test(vals, gloss):
        gloss = gloss.lower()
        for v in vals:
            v = v.lower()
            if v == gloss:
                return True
            if gloss in v:
                return True
        return False

    def search_words_by_gloss(self, gloss: str) -> Sequence[Document]:

        definition = Query()
        return self.defs_table.search(
            (definition.glosses.test(self._gloss_test, gloss))
            & (definition.lang == self.lang_id)
        )

    def search_words_by_pos(self, pos: str) -> Sequence[Document]:
        definition = Query()
        return self.defs_table.search(
            (definition.pos == pos) & (definition.lang == self.lang_id)
        )

    def search_words_by_gloss_pos(self, gloss: str, pos: str) -> Sequence[Word]:
        definition = Query()
        return self.defs_table.search(
            (definition.glosses.test(self._gloss_test, gloss))
            & (definition.pos == pos)
            & (definition.lang == self.lang_id)
        )

    def get_all_words(self) -> Sequence[Document]:
        word = Query()
        return self.word_table.search(word.lang == self.lang_id)

    def update_word(self, word_id: DocId, new_word: Dict):
        pass

    def update_def(self, def_id: DocId, new_def: Dict):
        pass

    def update_lang(self, lang_id: DocId, new_lang: Dict):
        pass

    def get_all_languages(self) -> Sequence[str]:
        return [rec["language"] for rec in self.lang_table.all()]
