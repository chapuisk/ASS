import spacy


class ASSTokenizer:
    """
    Choose among several pre-trained tokenizer to tokenize a corpus
    """

    def __init__(self, tokengine: str):
        if tokengine == 'spacy':
            _tokenizer = spacy.load("en_core_web_sm")
        else:
            raise AttributeError("tokenizer "+tokengine+" is not yet supported")
