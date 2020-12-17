from typing import Sequence, Optional, Dict
from tinydb import TinyDB, Query
from tinydb.database import Document


DocId = int


class Model:

    LANGUAGE_TABLE = "languages"
    WORD_TABLE = "words"
    DEFS_TABLE = "defs"
    LINKS_TABLE = "links"
    METADATA_TABLE = "metadata"

    def __init__(self, db_file):
        self.db = TinyDB(db_file)
        self._lang = None
        self._lang_id = None

        # languages table contains id -> {language}
        self.lang_table = self.db.table(self.LANGUAGE_TABLE)

        # words table contains word_id -> {word, language_id, [definition_ids]}
        self.word_table = self.db.table(self.WORD_TABLE)

        # definitions table contains def_id -> {pos, [glosses], desc, word_id, lang_id}
        self.defs_table = self.db.table(self.DEFS_TABLE)

        # links table contains link_id -> {from_word (id), to_word (id), link_type (str)}
        self.links_table = self.db.table(self.LINKS_TABLE)

        # metadata table contains a single document that we will continue to update
        self.metadata_table = self.db.table(self.METADATA_TABLE)

    @property
    def lang(self):
        if not self._lang:
            raise RuntimeError("Must select language")
        return self._lang

    @property
    def lang_id(self):
        if not self._lang_id:
            raise RuntimeError("Must select language")
        return self._lang_id

    def insert_word(self, word: str) -> DocId:
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
        self._lang = lang
        self._lang_id = rec.doc_id

    def lang_context(self, lang: str):
        old_lang = self.lang
        self.set_language(lang)
        yield
        self.set_language(old_lang)

    def get_word_by_id(self, word_id: DocId) -> Optional[Document]:
        return self.word_table.get(doc_id=word_id)

    def search_words_by_name(self, word_name: str) -> Sequence[Document]:
        word = Query()
        return self.word_table.search(
            (word.word == word_name) & (word.lang == self.lang_id)
        )

    def search_defs_by_word(self, word_id: DocId) -> Sequence[Document]:
        definition = Query()
        return self.defs_table.search(
            (definition.word_id == word_id) & (definition.lang_id) == self.lang_id
        )

    @staticmethod
    def _gloss_test(vals, gloss):
        gloss = gloss.lower()
        for v in vals:
            v = v.lower()
            if v == gloss:
                return True
        return False

    @staticmethod
    def _gloss_test_less_strict(vals, gloss):
        gloss = gloss.lower()
        for v in vals:
            v = v.lower().split()
            if len(v) > 1:
                if gloss in v:
                    return True
        return False

    def search_words_by_gloss(self, gloss: str) -> Sequence[Document]:

        definition = Query()
        res = self.defs_table.search(
            (definition.glosses.test(self._gloss_test, gloss))
            & (definition.lang == self.lang_id)
        )
        if not res:
            res = self.defs_table.search(
                (definition.glosses.test(self._gloss_test_less_strict, gloss))
                & (definition.lang == self.lang_id)
            )
        return res

    def search_words_by_pos(self, pos: str) -> Sequence[Document]:
        definition = Query()
        return self.defs_table.search(
            (definition.pos == pos) & (definition.lang == self.lang_id)
        )

    def search_words_by_gloss_pos(self, gloss: str, pos: str) -> Sequence[str]:
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
        self.word_table.update(new_word, doc_ids=word_id)

    def update_def(self, def_id: DocId, new_def: Dict):
        self.defs_table.update(new_def, doc_ids=def_id)

    def update_lang_name(self, lang_id: DocId, new_lang: str):
        self.lang_table.update({"language": new_lang}, doc_ids=lang_id)

    def insert_link(self, from_word: DocId, to_word: DocId, link_type: str) -> DocId:
        if not self.word_table.get(from_word):
            raise RuntimeError(f"Invalid word id {from_word}")
        if not self.word_table.get(to_word):
            raise RuntimeError(f"Invalid word id {to_word}")
        return self.links_table.insert(
            {"from_word": from_word, "to_word": to_word, "link_type": link_type}
        )

    def get_all_languages(self) -> Sequence[str]:
        return [rec["language"] for rec in self.lang_table.all()]

    def delete_word(self, word_id: DocId):
        self.word_table.remove(doc_ids=word_id)
        definition = Query()
        self.defs_table.remove(definition.word_id == word_id)
        link = Query()
        self.links_table.remove((link.from_word == word_id) | (link.to_word == word_id))

    def delete_def(self, def_id: DocId):
        self.defs_table.remove(doc_ids=def_id)

    def delete_link(self, link_id: DocId):
        self.links_table.remove(doc_ids=link_id)
