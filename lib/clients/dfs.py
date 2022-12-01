from http.client import HTTPSConnection
from base64 import b64encode
from os import getenv
from json import loads
from json import dumps
from pprint import pprint
import requests

DFS_USERNAME = "sidie.verma@gmail.com"
DFS_PASSWORD = "d5e185f74e130ddc"
BLOCK_LIST = ["www.quora.com", "www.flipkart.com",
              "www.snapdeal.com", "www.amazon.in"]


class RestClient:
    domain = "api.dataforseo.com"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def request(self, path, method, data=None):
        connection = HTTPSConnection(self.domain)
        try:
            base64_bytes = b64encode(
                ("%s:%s" % (self.username, self.password)).encode("ascii")
            ).decode("ascii")
            headers = {'Authorization': 'Basic %s' % base64_bytes,
                       'Content-Encoding': 'gzip'}
            connection.request(method, path, headers=headers, body=data)
            response = connection.getresponse()
            return loads(response.read().decode())
        finally:
            connection.close()

    def get(self, path):
        return self.request(path, 'GET')

    def post(self, path, data):
        if isinstance(data, str):
            data_str = data
        else:
            data_str = dumps(data)
        return self.request(path, 'POST', data_str)


class DFS:
    def __init__(self):
        self.client = RestClient(DFS_USERNAME, DFS_PASSWORD)

    def get_serp(self, keyword, location, block=BLOCK_LIST):
        post_data = dict()
        # simple way to set a task
        post_data[len(post_data)] = dict(
            language_code="en",
            location_name=location,
            keyword=keyword
        )
        serps = {
            "results": [],
            "faq": [],
            "related_searches": [],
        }
        response = self.client.post(
            "/v3/serp/google/organic/live/advanced", post_data)
        if response["status_code"] == 20000:
            for url in response["tasks"][0]["result"][0]["items"]:
                if url["type"] in ["organic", "featured_snippet"] and url.get("domain", "") not in block and len(serps["results"]) < 20:
                    serps["results"].append({
                        "url": url["url"],
                        "title": url["title"],
                        "description": url["description"],
                        "type": url["type"],
                        "domain": url.get("domain", ""),
                        "rank": url["rank_absolute"],
                    })
                    if "faq" in url and url["faq"]:
                        serps["faq"].extend(url["faq"].get("items", []))
                elif url["type"] == "related_searches":
                    serps["related_searches"].extend(url["items"])
        else:
            print("error. Code: %d Message: %s" %
                  (response["status_code"], response["status_message"]))
        return serps

    def get_intersection(self, urls, location):
        post_data = dict()
        pages = {}
        for idx, url in enumerate(urls):
            pages[str(idx+1)] = url
        post_data[len(post_data)] = dict(
            language_code="en",
            location_name=location,
            pages=pages,
            include_serp_info=False,
            include_subdomains=False,
            intersection_mode="union",
            limit=100,
            order_by=["intersection_result.2.rank_absolute,asc"]
        )
        response = self.client.post(
            "/v3/dataforseo_labs/google/page_intersection/live", post_data)
        keywords = []
        if response["status_code"] == 20000:
            for keyword in response["tasks"][0]["result"][0]["items"]:
                try:
                    intersections = []
                    featured_snippet = False
                    for intersection in keyword["intersection_result"]:
                        if keyword["intersection_result"][intersection] and keyword["intersection_result"][intersection]["type"] != "paid":
                            intersections.append({
                                "url": keyword["intersection_result"][intersection]["url"],
                                "rank": keyword["intersection_result"][intersection]["rank_absolute"],
                            })
                            if not featured_snippet and "is_featured_snippet" in keyword["intersection_result"][intersection]:
                                featured_snippet = keyword["intersection_result"][intersection]["is_featured_snippet"]

                    keywords.append({
                        "keyword": keyword["keyword_data"]["keyword"],
                        "competition": keyword["keyword_data"]["keyword_info"]["competition_level"],
                        "search_volume": keyword["keyword_data"]["keyword_info"]["search_volume"],
                        "monthly_searches": keyword["keyword_data"]["keyword_info"]["monthly_searches"],
                        "intersection": intersections,
                        "featured_snippet": featured_snippet
                    })
                except Exception as e:
                    print(e)
                    pass
        return keywords
