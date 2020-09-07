from abc import ABC, abstractmethod
import spacy


class ASSTokenizer(ABC):
    """
    The higher order abstraction to encapsulate tokenizer. This class provides the
    general contract to be used in text analysis, e.g. split text into tokens, POS or
    tagging
    """

    @abstractmethod
    def tokenize(self, text):
        """
        Main function to NLP basic text processing, including tokenization, lemmatization,
        POS and tagging. Depending on the ``_tokengine_'' you'll have other feature available
        :param text: the text to be processed
        :return: the text spit into token with NLP attributes (e.g. tag, POS)
        """
        pass


class ASSSpacyTokenizer(ASSTokenizer):
    """
    A tokenizer based on spaCy: https://spacy.io
    """
    _tokenizer: spacy.Language

    def __init__(self, tokengine: str):
        if not tokengine == "en_core_web_sm":
            raise AttributeError("tokenizer "+tokengine+" is not yet supported")
        self._tokenizer = spacy.load(tokengine)

    def tokenize(self, text):
        return self._tokenizer.nlp(text)
