"""
Define the main abstractions of ASS : a corpus of item to be analyse using machin learning techniques 
- ASSCorpus : encapsulated set of ASSItem with statistics, a vocabulary and so on
- ASSItem : an item of a corpus made up of few meta data and text content
"""

import logging
import json

# Bib manager import
from bibtexparser.bwriter import BibTexWriter
from bibtexparser import load as loadbibtex
from bibtexparser import loads as loadstrtex

# Typing import ... because I love Java
from abc import abstractmethod
from typing import TYPE_CHECKING, Union, TextIO

if TYPE_CHECKING:
    from PyASS.ass_abstractions import ASSCorpus
    from PyASS.ass_abstractions import ASSItem

from PyASS import ass_constant

logger = logging.getLogger(__name__)


class ASSCorpus:
    """
    A set of item to be NLPed
    """
    _corpus: set

    def __init__(self, **kwargs):
        """
        :Keyword Arguments:
        * *bibtex* (``bibfile``) --
          a bib file with several entries
        * *bibjson* (``jsonfile``) --
          a json file that describe the corpus
        """
        if ass_constant.BIB_ENTRY in kwargs:
            with kwargs[ass_constant.BIB_ENTRY] as bib_file:
                self._corpus = set([ASSArticle(bib_dict=bib) for bib
                                    in list(loadbibtex(bib_file).entries_dict.values())])
        elif ass_constant.BIB_JSON in kwargs:
            with kwargs[ass_constant.BIB_JSON] as bib_json:
                self._corpus = set([ASSArticle(**{ass_constant.BIB_JSON: bib}) for bib in bib_json])
        else:
            self._corpus = set()

    def __repr__(self):
        """
        The representation of a corpus
        :return: a string representation of the corpus
        """
        return ''.joint("A corpus made of ", len(self._corpus),
                        " with types: ", [type(item) for item in self._corpus])

    def corpus(self) -> frozenset:
        """
        The encapsulated set of item that made up a given corpus
        """
        return frozenset(self._corpus)

    def append(self, another_corpus) -> None:
        """
        :param ASSCorpus another_corpus:
        """
        try:
            self._corpus.update(another_corpus.corpus())
        except ValueError:
            raise

    def add_item(self, item: 'ASSItem') -> 'ASSCorpus':
        self._corpus.add(item)
        return self

    def add_article(self, bibentry: Union[str, TextIO]):
        """
        :param Union[str, dict] bibentry:
        """
        print(self._corpus)
        if isinstance(bibentry, TextIO):
            a = ASSArticle(**{ass_constant.BIB_ENTRY: bibentry})
            self._corpus.add(a)
        elif isinstance(bibentry, str):
            self._corpus.add(ASSArticle(**{ass_constant.BIB_STR: bibentry}))
        else:
            raise TypeError
        return self


class ASSItem:
    """
    An elemental textual item to be grouped in a corpus
    """
    _labels: list

    @abstractmethod
    def title(self) -> str:
        pass

    @abstractmethod
    def keywords(self) -> list:
        pass

    @abstractmethod
    def author(self) -> list:
        pass

    @abstractmethod
    def content(self) -> str:
        pass

    @abstractmethod
    def raw(self) -> dict:
        pass

    @abstractmethod
    def export_bibtex(self, file):
        pass

    def labels(self) -> list:
        """
        The list of user labels associated with the entry
        :return: list -- a list of string labels
        """
        return self._labels

    def export_json(self, file):
        file = open(file, "w")
        file.write(''.join([ass_constant.TITLE_TAG, ": ", self.title()]))
        file.write(''.join([ass_constant.KEYWORD_TAG, ": ", self.keywords()]))
        file.write(''.join([ass_constant.CONTENT_TAG, ": ", self.content()]))
        file.close()


class ASSArticle(ASSItem):
    """
    The basic item element for a corpus made of scientific articles
    """
    _title: str
    _keywords: list
    _abstract: str
    _author: list
    _doi: str
    _issn: str

    _content: str

    def __init__(self, **kwargs):
        """
        :Keyword Arguments:
        * *bibtex* (``bib entry``) --
          a bibtex file entry
        * *bibstr* (``bib str``) --
          a bibtex string entry
        * *bibjson* (``str``) --
          a raw json serialization of an ASSArticle
        * *bib_dict* (``dict``) --
          a dict of entries (take the first one)
        """
        bibentry: dict
        if ass_constant.BIB_ENTRY in kwargs:
            bibentry = list(loadbibtex(open(kwargs[ass_constant.BIB_ENTRY])).entries_dict.values())[0]
        elif ass_constant.BIB_STR in kwargs:
            bibentry = list(loadstrtex(kwargs[ass_constant.BIB_STR]).entries_dict.values())[0]
        elif ass_constant.BIB_JSON in kwargs:
            bibentry = json.load(kwargs[ass_constant.BIB_STR])
        elif ass_constant.BIB_DICT in kwargs:
            bibentry = kwargs[ass_constant.BIB_DICT]
        self._title = bibentry.get(ass_constant.TITLE_TAG, None)
        self._author = bibentry.get(ass_constant.AUTHOR_TAG, None)
        self._keywords = bibentry.get(ass_constant.KEYWORD_TAG, None)
        self._abstract = bibentry.get(ass_constant.ABSTRACT_TAG, None)
        self._content = bibentry.get(ass_constant.CONTENT_TAG, None)
        self._doi = bibentry.get(ass_constant.DOI_TAG, None)
        self._issn = bibentry.get(ass_constant.ISSN_TAG, None)

    def __repr__(self):
        return self._content

    def title(self):
        return self._title

    def author(self):
        return self._author

    def abstract(self):
        return self._abstract

    def keywords(self):
        return self._keywords

    def content(self):
        return self._content

    def raw(self) -> dict:
        return {
            ass_constant.DOI_TAG: (self._doi if self._doi else ass_constant.NA),
            ass_constant.ISSN_TAG: (self._issn if self._issn else ass_constant.NA),
            ass_constant.TITLE_TAG: (self._title if self._title else ass_constant.NA),
            ass_constant.AUTHOR_TAG: ('; '.join(self._author) if self._author else ass_constant.NA),
            ass_constant.ABSTRACT_TAG: (self._abstract if self._abstract else ass_constant.NA),
            ass_constant.KEYWORD_TAG: ('; '.join(self._keywords) if self._keywords else ass_constant.NA),
            ass_constant.CONTENT_TAG: (self._content if self._content else ass_constant.NA)
        }

    def export_bibtex(self, file):
        with open(file, 'w') as bib_file:
            bib_file.write(BibTexWriter().write(
                {
                    ass_constant.TITLE_TAG: self._title,
                    ass_constant.AUTHOR_TAG: self._author,
                    ass_constant.KEYWORD_TAG: self._keywords,
                    ass_constant.ABSTRACT_TAG: self._abstract
                }
            ))

    def export_json(self, file):
        file = open(file, "w")
        file.write(json.dumps(
            self.raw(),
            ensure_ascii=False,
            indent=0
        ))
        file.close()
