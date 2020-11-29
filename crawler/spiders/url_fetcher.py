from scrapy.spiders import Spider
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from crawler.items import UrlItem
from datetime import datetime
from urllib.parse import urlparse
import re
import logging
from scrapy.linkextractors import IGNORED_EXTENSIONS


class UrlFetcher(Spider):
    name = 'fetcher'
    start_urls = []
    custom_settings = {"ITEM_PIPELINES": {"crawler.pipelines.URLFilterPipeline": 100,
                                          "crawler.pipelines.SQLDuplicatedPipeline": 200,
                                          "crawler.pipelines.SQLitePipeline": 300}}

    def __init__(self, start_url=None, depth=1, *args, **kwargs):
        #self.logger.info("[LE] Source: %s Depth: %s Kwargs: %s", root, depth)
        self.start_url = start_url
        self.options = kwargs
        self.depth = depth
        self.clean_options()
        UrlFetcher.start_urls += [start_url]
        allow_domains = self.options.get('allow_domains')
        UrlFetcher.allowed_domains = allow_domains if isinstance(allow_domains, list) else [allow_domains]
        self.extractor = LinkExtractor(
            allow=self.options.get('allow'),
            deny=self.options.get('deny'),
            allow_domains=allow_domains,
            deny_domains=self.options.get('deny_domains'),
            # restrict_xpaths=self.options.get('restrict_xpaths'),
            canonicalize=True,  # ATTENTION True can alter urls
            unique=True, process_value=None, deny_extensions=None,
            # restrict_css=self.options.get('restrict_css'),
            strip=True
        )

        # super calls first the subclass, sencond it's instance so default: super() == super(subclass, self)
        super(UrlFetcher, self).__init__(*args, **kwargs)

    def start_requests(self, *args, **kwargs):
        # first function stat is started when spider is called
        yield Request(self.start_url, callback=self.parse, meta={"previous": None})

    def parse(self, response):
        all_urls = self.get_html_links(response)
        all_urls += self.get_rss_links(response.body.decode("utf-8"))
        all_urls = self.clean_urls(all_urls)

        if response.meta['depth'] <= self.depth:
            for url in all_urls:
                yield Request(url, callback=self.parse, meta={"previous": response.url})
        for url in all_urls:
            url_item = UrlItem()
            url_item["url"] = url
            url_item["start_url"] = self.start_url
            url_item["previous_url"] = response.meta.get("previous", None)
            url_item["fetch_date"] = datetime.now()
            url_item["depth"] = response.meta["depth"]
            url_item["retrieved"] = 0
            yield url_item  #dict(link=url, meta=dict(source=self.source, depth=response.meta['depth']))

    def get_html_links(self, resp):
        return [link.url for link in self.extractor.extract_links(resp)]

    def get_rss_links(self, resp):
        # https://trafilatura.readthedocs.io/en/latest/_modules/trafilatura/feeds.html#find_feed_urls
        feed_links = []
        # Atom
        for link in re.findall(r'<link .*?href=".+?"', resp):
            if 'atom+xml' in link or 'rel="self"' in link:
                continue
            match = re.search(r'<link .*?href="(.+?)"', link)
            if match:
                feed_links.append(match.group(1))
        # RSS
        for item in re.findall(r'<link>(.+?)</link>', resp):
            feed_links.append(item)
        return feed_links

    def clean_options(self):
        # allowed_options = ['allow', 'deny', 'allow_domains', 'deny_domains']
        self.options["allow"] = self.options.get("allow")
        self.options["deny"] = self.options.get("deny")
       # self.options["allow_domains"] = self.options.get("allow_domains", [])
        #self.options["deny_domains"] = self.options.get("deny_domains", [])

    def clean_urls(self, urls):
        # take unique urls
        urls = list(set(urls))
        # check if urls are valid
        valid_urls = []
        for url in urls:
            drop = False
            if self.validate_url(url) is False:
                drop = True
            elif self.allow_regex(self.options.get('allow'), url) is False:
                drop = True
            elif self.deny_regex(self.options.get('deny'), url) is False:
                drop = True
            elif self.allow_domains_func(self.options.get("allow_domains"), url) is False:
                drop = True
            elif self.deny_domains_func(self.options.get('deny_domains'), url) is False:
                drop = True
            if drop is False:
                valid_urls += [url]
            else:
                logging.warning("clean_urls(): dropped URL: %s", url)
        return valid_urls

    @staticmethod
    def allow_regex(pattern=None, url=None):
        if not pattern:
            return True
        if isinstance(url, str) and isinstance(pattern, str):
            if re.search(pattern, url):
                return True
        return False

    @staticmethod
    def deny_regex(pattern=None, url=None):
        if not pattern:
            return True
        if isinstance(url, str) and isinstance(pattern, str):
            if not re.search(pattern, url):
                return True
        return False

    @staticmethod
    def allow_domains_func(domains=None, url=None):
        if domains is None or url is None or not domains or not url:
            return True
        if isinstance(domains, str):
            domains = [domains]
        if isinstance(url, str):
            if isinstance(domains, list):
                for domain in domains:
                    if domain in url:
                        return True
        return False


    @staticmethod
    def deny_domains_func(domains=None, url=None):
        if domains is None or url is None or not domains or not url:
            return True
        if isinstance(domains, str):
            domains = [domains]
        if isinstance(domains, list):
            for domain in domains:
                if domain in url:
                    return False
        return True

    @staticmethod
    def validate_url(url):
        '''
        Parse and validate the input
        '''
        try:
            parsed_url = urlparse(url)
        except ValueError:
            return False
        if bool(parsed_url.scheme) is False or parsed_url.scheme not in ('http', 'https'):
            return False
        if len(parsed_url.netloc) < 5 or \
                (parsed_url.netloc.startswith('www.') and len(parsed_url.netloc) < 8):
            return False
        if url.endswith(tuple(IGNORED_EXTENSIONS)):
            return False
        return True

"""def determine_feed(htmlstring):
    '''Try to extract the feed URL from the home page'''
    feed_urls = []
    # try to find RSS URL
    for feed_url in re.findall(r'type="application/rss\+xml".+?href="(.+?)"', htmlstring):
        feed_urls.append(feed_url)
    for feed_url in re.findall(r'href="(.+?)".+?type="application/rss\+xml"', htmlstring):
        feed_urls.append(feed_url)
    # try to find Atom URL
    if len(feed_urls) == 0:
        for feed_url in re.findall(r'type="application/atom\+xml".+?href="(.+?)"', htmlstring):
            feed_urls.append(feed_url)
        for feed_url in re.findall(r'href="(.+?)".+?type="application/atom\+xml"', htmlstring):
            feed_urls.append(feed_url)
    for item in feed_urls:
        if 'comments' in item:
            feed_urls.remove(item)
    return feed_urls"""
