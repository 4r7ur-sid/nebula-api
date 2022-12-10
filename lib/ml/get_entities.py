class GetEntities:
    def __init__(self, nlp):
        self.nlp = nlp

    def get(self, docs):
        entities = []
        for text in docs:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'PRODUCT', 'ORG', 'NORP', 'FAC', 'GPE', 'EVENT', 'WORK_OF_ART', 'LAW ']:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "sentence": "..."+ent.sent.text[ent.start_char - 50:ent.end_char + 50]+"...",
                        # Get 5 full words before and after the entity

                    })
        return entities
