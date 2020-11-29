import scrapy
from crawler.items import ArticleItem
from scrapy.loader import ItemLoader
from htmldate import find_date
from newspaper import Article, Config
import re
import nltk
nltk.download("punkt")


class ORFSpider(scrapy.Spider):
    name = "orf"
    allowed_domains = ["orf.at"]
    # https://rss.orf.at/
    start_urls = ['https://rss.orf.at/news.xml', "https://rss.orf.at/oesterreich.xml", "https://rss.orf.at/science.xml",
                  "https://rss.orf.at/wien.xml", "https://rss.orf.at/noe.xml", "https://rss.orf.at/burgenland.xml",
                  "https://rss.orf.at/ooe.xml", "https://rss.orf.at/salzburg.xml", "https://rss.orf.at/steiermark.xml",
                  "https://rss.orf.at/kaernten.xml", "https://rss.orf.at/tirol.xml",
                  "https://rss.orf.at/vorarlberg.xml"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        # last_modified = response.xpath
        # urls = response.xpath("//a[contains(@href, '/stories/')]/@href")
        xml = response.body.decode("utf-8")
        urls = set()
        for url in re.findall(r'(https?://[^&"<>]+)', xml):
            if "orf.at/stories" in url and url not in urls:
                urls.add(url)
                article_item = ArticleItem()
                article_item["url"] = url
                article_item["publisher"] = "ORF.at"
                yield response.follow(url, self.parse_article, meta={'article_item': article_item})

        # go to Next page
        # for a in response.css('li.next a'):
        # yield response.follow(a, self.parse)

    def parse_article(self, response):
        article_item = response.meta['article_item']
        article = Article(article_item["url"])
        article.download(input_html=response.body)
        article.parse()
        article_item["title"] = article.title
        article_item["article"] = article.text
        article_item["lang"] = "DE"
        article_item["pub_date"] = article.publish_date if article.publish_date else find_date(response.body,
                                                                                               original_date=True)
        yield article_item




