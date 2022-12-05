from lib.clients.article import ArticleClient
from lib.clients.open_ai import OpenAi
from lib.ml.summarize import Summarize
from lib.ml.get_keywords import GetKeywords
import random
import spacy


class StatusGenerator:
    def __init__(self, url, social_media="linkedin", variations=1):
        self.url = url
        self.social_media = social_media
        self.text = ""
        self.variations = variations

    def get_article(self):
        article_client = ArticleClient(self.url)
        article = article_client.get_article()
        self.text = article

    def summarize(self):
        summarize = Summarize(self.text, 50)
        return summarize.summarize()

    def generate(self):
        self.get_article()
        summary = self.summarize()
        gk = GetKeywords(nlp=spacy.load('en_core_web_lg'))
        keywords = gk.get_keywords(" ".join(summary))
        hashtags = []
        for keyword in keywords:
            hashtags.append(
                f"#{keyword['keyword'].strip().title().replace(' ', '')}")
        PROMPT = f"Generate an elaborate and engaging {self.social_media} post explaining learnings from the Text:\n\"\"\"\nText:"
        statuses = []
        cutoff = int(len(summary) * 0.5)
        if cutoff > 20:
            cutoff = 20
        for x in range(0, self.variations):
            _s = random.sample(summary, cutoff)
            _s = " ".join(_s)
            status = OpenAi().generate((PROMPT + (_s) + "\n\"\"\"\nPost:"))
            checker = 0
            while len(status) <= 20:
                status = OpenAi().generate((PROMPT + (_s) + "\n\"\"\"\nPost:"))
                checker += 1
                if checker > 3:
                    break
            statuses.append(status)
        return {
            "statuses": statuses,
            "hashtags": hashtags,
        }
