from bs4 import NavigableString
from urllib.parse import urlparse
SOCIAL_LINKS = ["facebook.com",
                "twitter.com",
                "linkedin.com",
                "plus.google.com",
                "pinterest.com",
                "youtube.com",
                "instagram.com",
                "tumblr.com",
                "flickr.com",
                "reddit.com",
                "stumbleupon.com",
                "digg.com",
                "delicious.com",
                "vimeo.com",
                "soundcloud.com",
                "slideshare.net",
                "foursquare.com",
                "yelp.com",
                "github.com",
                "behance.net",
                "dribbble.com",
                "quora.com",
                "twitch.tv",
                "slack.com",
                "snapchat.com",
                "vine.co",
                "vk.com",
                "ok.ru",
                "weibo.com",
                "xing.com",
                "trello.com",
                "bitbucket.org",
                "about.me",
                "disqus.com",
                "goodreads.com",
                "imgur.com",
                "meetup.com",
                "scribd.com",
                "tripadvisor.com",
                "tripit.com",
                "tumblr.com",
                "whatsapp.com",
                "wikipedia.org",
                "wordpress.com",
                "yelp.com",
                "youtube.com",
                "zillow.com",
                "houzz.com",
                "reddit.com",
                "foursquare.com",
                "yelp.com",
                "github.com",
                "behance.net",
                "dribbble.com",
                "quora.com",
                "twitch.tv",
                "slack.com",
                "snapchat.com",
                "vine.co",
                "vk.com",
                "ok.ru",
                "weibo.com",
                "xing.com",
                "trello.com",
                "bitbucket.org",
                "about.me",
                "disqus.com",
                "goodreads.com",
                "imgur.com",
                "meetup.com",
                "scribd.com",
                "tripadvisor.com",
                "tripit.com",
                "tumblr.com",
                "whatsapp.com",
                "wikipedia.org",
                "wordpress.com",
                "yelp.com",
                "youtube.com",
                "zillow.com",
                "houzz.com",
                "reddit.com",
                "foursquare.com",
                "yelp.com",
                "github.com",
                "behance.net",
                "dribbble.com",
                "quora.com",
                "twitch.tv"]


def between_elements(cur, end):
    while cur and cur != end:
        if isinstance(cur, NavigableString):
            text = cur.text.strip()
            if len(text):
                yield text
        cur = cur.next_element

# Check if social media links are present
# Return True or False


def get_social_links(link):
    for social in SOCIAL_LINKS:
        if social in link:
            return True
    return False


def get_external_links(soup, url, text):
    links = []
    text = text.lower()
    domain = urlparse(url).netloc
    for paragraph in soup.find_all('p'):
        for link in paragraph.find_all('a'):
            # Check if the link points to other domain
            if link.get('href') and link.get('href').startswith('http'):
                if domain not in link.get('href') and not get_social_links(link.get('href')) and link.text.lower() in text:
                    links.append({
                        "url": link.get('href'),
                        "text": link.text.strip(),
                        "postion": text.find(link.text.lower())
                    })
    return links
