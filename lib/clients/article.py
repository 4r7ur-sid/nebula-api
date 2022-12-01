from newspaper import Article


class ArticleClient:
    def __init__(self, url):
        self.url = url

    def get(self):
        article = Article(self.url)
        article.download()
        article.parse()
        return article

    def get_article(self):
        article = Article(self.url)
        article.download()
        article.parse()
        return article.text

    def get_html(self):
        article = Article(self.url)
        article.download()
        article.parse()
        return article.html
