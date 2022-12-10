from bs4 import BeautifulSoup
import numpy as np
from nltk.tokenize import sent_tokenize
from collections import Counter
from pprint import pprint
import re
import spacy
from urllib.parse import urlparse

# Custom Imports
from lib.core._text import clean_text, remove_newline, remove_unicode, get_reading_score
from lib.ml.clustering import Clustering
from lib.clients.article import ArticleClient
from lib.ml.get_facts import GetFacts
from lib.ml.get_keywords import GetKeywords
from lib.ml.get_entities import GetEntities
from lib.core._html import between_elements, get_external_links


class ContentGapAnalysis:
    def __init__(self, idx, location, keyword, serps, url):
        self.idx = idx
        self.location = location
        self.keyword = keyword

        self.url = url
        self.article_data = {}

        self.serps = serps
        self.serp_data = []
        self.output = []

        self.output = {
            "analysis_id": self.idx,
            "location": self.location,
            "keyword": self.keyword,
            "facts": [],
        }
        self._nlp = spacy.load('en_core_web_lg')

    def analyse(self):
        _gf = GetFacts(self._nlp)
        _gk = GetKeywords(self._nlp)
        _ge = GetEntities(self._nlp)
        self.article_data = self.analyse_article(
            self.url, _gf, _gk, _ge)
        if self.article_data is None:
            return None
        for serp in self.serps:
            analysis = self.analyse_article(serp, _gf, _gk, _ge)
            if analysis is not None:
                self.serp_data.append(analysis)
        if len(self.serp_data) == 0:
            return None
        # Formatting Output
        all_headings = []
        for data in self.serp_data:
            for heading in data["headings"]:
                all_headings.append(heading["orignal"])
                self.output["facts"].extend(heading.get("facts", []))
        for heading in self.article_data["headings"]:
            all_headings.append(heading["orignal"])
        # Forming output
        self.output["facts"] = list(set(self.output["facts"]))
        clustered_headings = self.cluster_headings(all_headings)
        self.format_cluster(clustered_headings)
        self.reduce_clusters()
        self.output["article"] = self.article_data
        del _gf
        del _gk
        return self.output

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

    def analyse_article(self, url, _gf, _gk, _ge):
        data = {}
        try:
            article = ArticleClient(url).get()
        except Exception as e:
            return None
        soup = BeautifulSoup(article.html, "html.parser")
        data["url"] = url
        data["title"] = article.title
        data["description"] = article.meta_description or ""
        data["text"] = clean_text(article.text)
        data["entities"] = _ge.get(sent_tokenize(data["text"]))
        data["word_count"] = len(data["text"].split())
        data["external_links"] = get_external_links(
            soup, url, article.text)
        data["readability"] = get_reading_score(" ".join(
            [p.text for p in soup.find_all(["p", re.compile('^h[1-6]$')])]))
        headings = soup.find_all(re.compile("^h[1-6]$"))
        data["headings"] = []
        for heading in headings:
            text = clean_text(heading.text)
            if len(text.split()) == 1:
                continue
            heading_obj = {}
            heading_obj["orignal"] = remove_newline(
                remove_unicode(heading.text))
            heading_obj["text"] = self.get_data_between_headings(
                heading, None)
            heading_obj["tag"] = heading.name
            if heading_obj["text"]:
                heading_obj["facts"] = _gf.get(heading_obj["text"])
                heading_obj["keywords"] = _gk.get_keywords(
                    " ".join(heading_obj["text"]))
            data["headings"].append(heading_obj)
        return data

    def cluster_headings(self, headings):
        _c = Clustering(headings)
        heading_clusters = _c.cluster()
        output = {}
        for cluster in heading_clusters:
            if heading_clusters[cluster] not in output:
                output[heading_clusters[cluster]] = set()
            output[heading_clusters[cluster]].add(cluster)
        del _c
        return output

    def format_cluster(self, heading_clusters):
        article_headings = [heading["orignal"]
                            for heading in self.article_data["headings"]]
        article_headings = set(article_headings)
        seen = []
        self.article_data["word_counts"] = []
        self.article_data["readabilties"] = []
        heading_mapping = {}
        for serp in self.serp_data:
            self.article_data["word_counts"].append(serp["word_count"])
            self.article_data["readabilties"].append(serp["readability"])
            for heading in serp["headings"]:
                heading_mapping[heading["orignal"]
                                ] = heading.get("keywords", [])
        for idx, heading in enumerate(self.article_data["headings"]):
            for cluster in heading_clusters:
                if heading["orignal"] in heading_clusters[cluster]:
                    seen.append(cluster)
                    self.article_data["headings"][idx]["cluster"] = cluster
                    self.article_data["headings"][idx]["competitors"] = {}
                    for competitor in heading_clusters[cluster] - article_headings:
                        self.article_data["headings"][idx]["competitors"][competitor] = {
                            "keywords": heading_mapping[competitor]
                        }
        self.article_data["not_covered"] = []
        for cluster in heading_clusters:
            if cluster not in seen:
                data = {
                    "headings": list(heading_clusters[cluster] - article_headings),
                    "keywords": []
                }
                for keywords in (heading_clusters[cluster] - article_headings):
                    data["keywords"].extend(heading_mapping[keywords])
                self.article_data["not_covered"].append(data)

    def reduce_external_links(self):
        serp_urls = []
        all_external_links = []
        for serp in self.serp_data:
            domain = urlparse(serp["url"]).netloc
            serp_urls.append(domain)

        for serp in self.serp_data:
            for link in serp["external_links"]:
                if link["domain"] not in serp_urls:
                    all_external_links.append(link["domain"])
        _c = Counter(all_external_links)
        important_domains = []
        for c in _c:
            if _c[c] > 1:
                important_domains.append(c)
        self.article_data["external_links"] = []

        for serp in self.serp_data:
            for link in serp["external_links"]:
                if link["domain"] in important_domains:
                    if link not in self.article_data["external_links"]:
                        article_data["external_links"][link["domain"]] = []
                    self.article_data["external_links"][link["domain"]].append(
                        link)

    def reduce_word_count(self):
        word_count = {
            "your": self.article_data["word_count"],
            "min": min(self.article_data["word_counts"]),
            "max": max(self.article_data["word_counts"]),
            "competitors": self.article_data["word_counts"],
            "recommended": np.percentile(
                np.array(self.article_data["word_counts"]), 80)
        }
        self.article_data["word_count"] = word_count
        del self.article_data["word_counts"]

    def reduce_readability(self):
        readability = {
            "your": self.article_data["readability"],
            "min": min(self.article_data["readabilties"]),
            "max": max(self.article_data["readabilties"]),
            "competitors": self.article_data["readabilties"],
            "recommended": np.percentile(
                np.array(self.article_data["readabilties"]), 20)
        }
        self.article_data["readability"] = readability
        del self.article_data["readabilties"]

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

    def is_keyword_covered(self, keyword):
        if keyword in self.article_data["text"]:
            return True
        return False

    def reduce_keywords(self):
        for (idx, heading) in enumerate(self.article_data["headings"]):
            if "keywords" in heading:
                self.article_data["headings"][idx]["keywords"] = self.get_top_keywords(
                    heading["keywords"])
                for (idy, competitor) in enumerate(heading["competitors"]):
                    self.article_data["headings"][idx]["competitors"][competitor]["keywords"] = self.get_top_keywords(
                        heading["competitors"][competitor]["keywords"])
                    for keyword_index, keyword in enumerate(self.article_data["headings"][idx]["competitors"][competitor]["keywords"]):
                        self.article_data["headings"][idx]["competitors"][competitor]["keywords"][keyword_index]["covered"] = self.is_keyword_covered(
                            keyword["keyword"])
        for (idx, not_covered) in enumerate(self.article_data["not_covered"]):
            self.article_data["not_covered"][idx]["keywords"] = self.get_top_keywords(
                not_covered["keywords"], 20)
            for keyword_index, keyword in enumerate(self.article_data["not_covered"][idx]["keywords"]):
                self.article_data["not_covered"][idx]["keywords"][keyword_index]["covered"] = self.is_keyword_covered(
                    keyword["keyword"])

    def reduce_entities(self):
        article_entities = [x["text"] for x in self.article_data["entities"]]
        self.article_data["entities"] = []
        all_entities = {}
        for serp in self.serp_data:
            for entity in serp["entities"]:
                if entity["text"] not in all_entities:
                    all_entities[entity["text"]] = {
                        "text": entity["text"],
                        "count": 1,
                        "label": entity["label"],
                        "usage": [entity["sentence"]],
                        "covered": entity["text"] in article_entities
                    }
                else:
                    all_entities[entity["text"]]["count"] += 1
                    all_entities[entity["text"]]["usage"].append(
                        entity["sentence"])
        for entity in all_entities.values():
            self.article_data["entities"].append(entity)

    def reduce_clusters(self):
        self.reduce_word_count()
        self.reduce_readability()
        self.reduce_keywords()
        self.reduce_external_links()
        self.reduce_entities()
        del self.article_data["text"]
        for idx, heading in enumerate(self.article_data["headings"]):
            if "facts" in heading:
                del self.article_data["headings"][idx]["facts"]
            if "text" in heading:
                del self.article_data["headings"][idx]["text"]
        self.output["competitors"] = []
        for competitor in self.serp_data:
            self.output["competitors"].append({
                "title": competitor["title"],
                "description": competitor["description"],
                "url": competitor["url"]
            })
        for (idx, heading) in enumerate(self.article_data["headings"]):
            if "competitors" in heading:
                output = {
                    "headings": list(self.article_data["headings"][idx]["competitors"].keys())
                }
                keywords = []
                for head in self.article_data["headings"][idx]["competitors"].values():
                    keywords.extend(head["keywords"])
                if len(keywords) > 0:
                    output["keywords"] = self.get_top_keywords(keywords, 20)
                else:
                    output["keywords"] = []
                self.article_data["headings"][idx]["competitors"] = output
