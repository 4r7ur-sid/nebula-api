from rake_spacy import Rake
from nltk.corpus import stopwords
import re
stopwords = stopwords.words('english')
REMOVE_PUNCTUATION = re.compile(r'[^\w\s\d]')
ALL_NUMBERS = re.compile(r'^[0-9]+$')
POS_PATTERNS = [" ".join(["(\w+)_!"+pos for pos in p.split()]) for p in [
    "VERB NOUN", "NOUN VERB NOUN", "ADJ NOUN", "VERB NOUN NOUN"
]]


def find_sub_list(sl, l):
    sll = len(sl)
    for ind in (i for i, e in enumerate(l) if e == sl[0]):
        if l[ind:ind+sll] == sl:
            return ind, ind+sll-1


def extract_word_matching_pos_pattern(doc):
    tokens = []
    matches = list()
    text_pos = " ".join([token.text+"_!"+token.pos_ for token in doc])
    vocab = [token.text for token in doc]
    for i, pattern in enumerate(POS_PATTERNS):
        for result in re.findall(pattern, text_pos):
            data = find_sub_list(list(result), vocab)
            if data:
                start, end = data
                matches.append(doc[start:end])
    return matches


def custom_extractor(doc):
    tokens = []
    # Extract spans of tokens that are noun, adjective, verb, adverb, or named entity
    custom_patterns = (extract_word_matching_pos_pattern(doc))
    for pattern in custom_patterns:
        # Create a Span for each match and add it to the matches
        tokens.append(pattern)
    for span in doc.noun_chunks:
        tokens.append(span)
    for span in doc.ents:
        tokens.append(span)
    all_tokens = []
    for token in tokens:
        try:
            _data = token.text.split()
            if len(_data) < 2:
                continue
            if _data[0].lower() in stopwords:
                token = token.char_span(
                    token.start_char + len(_data[0]) + 1, token.end_char)
            if _data[-1].lower() in stopwords:
                token = token.char_span(
                    token.start_char, token.end_char - len(_data[-1]) - 1)
            if not token:
                continue
            _data = token.text.split()
            if (ALL_NUMBERS.match(_data[0])):
                continue
            _t = token
            if _t and len(_t) > 1:
                all_tokens.append(_t)
        except Exception as e:
            print(e)
    return all_tokens


class GetKeywords:
    def __init__(self, nlp):
        self.extractor = Rake(nlp=nlp, phraser_class=custom_extractor)

    def get_keywords_stats(self, keywords, text):
        seen = set()
        _top = []
        for keyword in keywords:
            if str(keyword[1]).lower() not in seen and len(str(keyword[1]).split(" ")) > 1 and keyword[0] > 1:
                _keyword = str(keyword[1])
                _keyword = REMOVE_PUNCTUATION.sub('', _keyword).strip()
                _top.append({
                    "keyword": _keyword,
                    "score": keyword[0],
                    "count": text.count(_keyword)
                })
                seen.add(_keyword.lower())
        return _top

    def get_keywords(self, text):
        keywords = self.extractor.apply(text)
        keywords = self.get_keywords_stats(keywords, text)
        return keywords
