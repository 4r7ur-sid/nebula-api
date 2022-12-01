from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


class Summarize:
    def __init__(self, data, sentences=30):
        self.data = data
        self.sentences = sentences

    def summarize(self):
        sentences = []
        parser = PlaintextParser.from_string(self.data, Tokenizer("english"))
        stemmer = Stemmer("english")
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words("english")
        for sentence in summarizer(parser.document, self.sentences):
            sentences.append(str(sentence))
        return sentences
