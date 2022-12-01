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
        PROMPT = f"Generate an engaging {self.social_media} post with hashtags from the Text:\n\"\"\"\nText:"
        statuses = []
        for x in range(0, self.variations):
            _s = random.sample(summary, int(len(summary) * 0.5))
            status = OpenAi().generate((PROMPT + " ".join(_s) + "\n\"\"\"\nPost:"))
            statuses.append(status)
        return {
            "statuses": statuses,
            "hashtags": hashtags,
        }