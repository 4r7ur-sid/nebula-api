class GetFacts:
    def __init__(self, nlp):
        self.nlp = nlp

    def get(self, docs):
        facts = []
        for text in docs:
            doc = self.nlp(text)
            for sent in doc.sents:
                seen = set()
                for token in sent:
                    if token.ent_type_ in ['PERCENT', 'MONEY', 'TIME', 'DATE', 'QUANTITY', 'PERSON', 'PRODUCT', 'ORG']:
                        if token.ent_type_ not in seen:
                            seen.add(token.ent_type_)
                    if len(seen) >= 2 and len(seen.intersection(set(['PERCENT', 'MONEY', 'QUANTITY']))) > 0:
                        facts.append(sent.text)
                        break
        return facts
