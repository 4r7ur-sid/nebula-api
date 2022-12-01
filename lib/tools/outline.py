# This class generates an outline from SERPS.
from bs4 import BeautifulSoup
import math
import numpy as np
from pprint import pprint
from pymongo import MongoClient
import re
from lib.clients.article import ArticleClient
from lib.clients.dfs import DFS
from lib.core._text import clean_text, remove_newline, remove_unicode, get_reading_score
from lib.core._html import between_elements, get_external_links

from lib.ml.get_facts import GetFacts
from lib.ml.get_keywords import GetKeywords
from lib.ml.clustering import Clustering
from lib.ml.prompts import generate_title, generate_description, generate_outline
import spacy
_nlp = spacy.load('en_core_web_lg')


class GenerateOutline:
    def __init__(self, serps, outline_id):
        self.serps = serps
        self.data = {

        }
        self.outline = {
            "facts": [],
            "meta": {
                "title": {
                    "competitors": [],
                    "ai": "",
                },
                "description": {
                    "competitors": [],
                    "ai": "",
                },
            },
            "outline": {
                "competitors": [],
            },
            "clusters": {},
            "articles_to_link": [],
        }
        self.heading_clusters = {}
        client = MongoClient("localhost", 27018)
        db = client["cadmus"]
        serp_data = db.serps.find_one(
            {"outline_id": outline_id}, {"location": 1, "faq": 1})
        self.location = serp_data["location"]
        if "faq" in serp_data and type(serp_data["faq"]) == list:
            self.outline["faq"] = [{
                "title": faq["title"],
                "description": faq["description"],
            } for faq in serp_data["faq"]]

    def generate(self):
        self.analyse_articles()
        self.cluster_headings()
        self.format_outline()
        return self.outline

    def format_outline(self):
        word_count = {
            "min": 0,
            "max": 0,
            "competitors": [],
        }
        readability = 0
        for data in self.data:
            word_count["competitors"].append(self.data[data]["word_count"])
            if word_count["min"] == 0 or self.data[data]["word_count"] < word_count["min"]:
                word_count["min"] = self.data[data]["word_count"]
            if self.data[data]["word_count"] > word_count["max"]:
                word_count["max"] = self.data[data]["word_count"]
            readability += self.data[data]["readability"]
            self.outline["meta"]["title"]["competitors"].append({
                "url": data,
                "text": self.data[data]["title"],
            })
            self.outline["meta"]["description"]["competitors"].append({
                "url": data,
                "text": self.data[data]["description"],
            })
            self.outline["outline"]["competitors"].append({
                "url": data,
                "outline": self.data[data]["structure"],
            })
            self.outline["articles_to_link"].extend(
                self.data[data]["external_links"])
            for heading in self.data[data]["headings"]:
                self.outline["facts"].extend(
                    self.data[data]["headings"][heading].get("facts", []))
                if heading in self.heading_clusters:
                    cluster_id = str(self.heading_clusters[heading])
                    if cluster_id not in self.outline["clusters"]:
                        self.outline["clusters"][cluster_id] = {
                            "headings": [],
                            "keywords": [],
                        }
                    self.outline["clusters"][cluster_id]["headings"].append(
                        self.data[data]["headings"][heading]["orignal"])
                    self.outline["clusters"][cluster_id]["keywords"].extend(
                        self.data[data]["headings"][heading].get("keywords", []))
        for cluster in self.outline["clusters"]:
            self.outline["clusters"][cluster]["keywords"] = self.get_top_keywords(
                self.outline["clusters"][cluster]["keywords"])
        word_count["80th"] = np.percentile(
            np.array(word_count["competitors"]), 80)
        self.outline["word_count"] = {
            "min": word_count["min"],
            "recommended": {
                "value": int(word_count["80th"]),
                "rounded": int(math.ceil(int(word_count["80th"]) / 100.0)) * 100
            },
            "max": word_count["max"],
            "competitors": word_count["competitors"],
        }
        self.outline["readability"] = int(readability/len(self.data))
        # GPT 3 Generation
        self.outline["meta"]["title"]["ai"] = [generate_title(
            [x["text"] for x in self.outline["meta"]["title"]["competitors"]]) for y in range(3)]
        self.outline["meta"]["title"]["ai"] = list(
            set(self.outline["meta"]["title"]["ai"]))
        self.outline["meta"]["description"]["ai"] = [generate_description(
            [x["text"] for x in self.outline["meta"]["description"]["competitors"]]) for y in range(3)]
        self.outline["meta"]["description"]["ai"] = list(
            set(self.outline["meta"]["description"]["ai"]))
        self.outline["outline"]["ai"] = generate_outline(
            self.outline["outline"]["competitors"], self.outline["meta"]["title"])
        # DFS Keywords
        _dfs = DFS()
        self.outline["competitor_rankings"] = _dfs.get_intersection(
            list(self.data.keys()), self.location)
        for i, keyword in enumerate(self.outline["competitor_rankings"]):
            for j, intersection in enumerate(keyword["intersection"]):
                self.outline["competitor_rankings"][i]["intersection"][j]["times_used"] = self.data[intersection["url"]]["text"].count(
                    keyword["keyword"])

    def get_data_between_headings(self, heading, next_heading):
        text = []
        for element in between_elements(heading, next_heading):
            if not element:
                continue
            if len(element.split()) < 10:
                continue
            text.append(remove_newline(remove_unicode(element)))
        text = text[1:]
        if len(text) > 0:
            return text

    def get_top_keywords(self, keywords, count=10):
        all_keywords = {}
        for keyword in keywords:
            text = keyword["keyword"]
            if text not in all_keywords:
                all_keywords[text] = keyword
            else:
                all_keywords[text]["count"] += keyword["count"]
                all_keywords[text]["score"] = (
                    all_keywords[text]["score"] + keyword["score"])/2
        all_keywords = all_keywords.values()
        keywords = sorted(all_keywords,
                          key=lambda x: (x["score"]) * x["count"],
                          reverse=True)
        return list(keywords)[:count]

    def analyse_articles(self):
        _gf = GetFacts(_nlp)
        _gk = GetKeywords(_nlp)
        for url in self.serps:
            try:
                article = ArticleClient(url).get()
            except Exception as e:
                print(e)
                continue
            self.data[url] = {}
            self.data[url]["title"] = article.title
            self.data[url]["text"] = clean_text(article.text)
            self.data[url]["description"] = article.meta_description or ""
            self.data[url]["word_count"] = len(self.data[url]["text"].split())
            self.data[url]["structure"] = []
            soup = BeautifulSoup(article.html, "html.parser")
            self.data[url]["readability"] = get_reading_score(" ".join(
                [p.text for p in soup.find_all(["p", re.compile('^h[1-6]$')])]))
            self.data[url]["external_links"] = get_external_links(
                soup, url, article.text)
            headings = soup.find_all(re.compile("^h[2-6]$"))
            self.data[url]["headings"] = {}
            for index, heading in enumerate(headings):
                text = clean_text(heading.text)
                self.data[url]["structure"].append(
                    {"tag": heading.name, "text": remove_newline(heading.text).strip()})
                if len(text.split()) == 1:
                    continue
                heading_obj = {}
                heading_obj["orignal"] = remove_newline(
                    remove_unicode(heading.text))
                if index != len(headings) - 1:
                    heading_obj["text"] = self.get_data_between_headings(
                        heading, headings[index + 1])
                else:
                    heading_obj["text"] = self.get_data_between_headings(
                        heading, None)
                if heading_obj["text"]:
                    heading_obj["facts"] = _gf.get(heading_obj["text"])
                    heading_obj["keywords"] = _gk.get_keywords(
                        " ".join(heading_obj["text"]))
                self.data[url]["headings"][text] = heading_obj
        del _gf
        del _gk
        return self.data

    def cluster_headings(self):
        headings = []
        for url in self.data:
            headings.extend(list(self.data[url]["headings"].keys()))
        _c = Clustering(headings)
        self.heading_clusters = _c.cluster()
        del _c
