from scrapy.spiders import Spider
from scrapy import Request
from scrapy.linkextractors import LinkExtractor

class UrlExtractor(Spider):
    name = 'url-extractor'
    start_urls = []

    def __init__(self, root=None, depth=0, *args, **kwargs):
        self.logger.info("[LE] Source: %s Depth: %s Kwargs: %s", root, depth, kwargs)
        self.source = root
        self.options = kwargs
        self.depth = depth
        UrlExtractor.start_urls.append(root)
        UrlExtractor.allowed_domains = [self.options.get('allow_domains')]
        self.clean_options()
        self.le = LinkExtractor(allow=self.options.get('allow'),
                                deny=self.options.get('deny'),
                                allow_domains=self.options.get('allow_domains'),
                                deny_domains=self.options.get('deny_domains'),
                                #restrict_xpaths=self.options.get('restrict_xpaths'),
                                canonicalize=False,
                                unique=True, process_value=None, deny_extensions=None,
                                #restrict_css=self.options.get('restrict_css'),
                                strip=True)
        super(UrlExtractor, self).__init__(*args, **kwargs)

    def start_requests(self, *args, **kwargs):
        yield Request('%s' % self.source, callback=self.parse_req)

    def parse_req(self, response):
        all_urls = []
        if int(response.meta['depth']) <= int(self.depth):
            all_urls = self.get_all_links(response)
            for url in all_urls:
                yield Request('%s' % url, callback=self.parse_req)
        if len(all_urls) > 0:
            for url in all_urls:
                yield dict(link=url, meta=dict(source=self.source, depth=response.meta['depth']))

    def get_all_links(self, response):
        links = self.le.extract_links(response)
        str_links = []
        for link in links:
            str_links.append(link.url)
        return str_links

    def clean_options(self):
        allowed_options = ['allow', 'deny', 'allow_domains', 'deny_domains', 'restrict_xpaths', 'restrict_css']
        for key in allowed_options:
            if self.options.get(key, None) is None:
                self.options[key] = []
            else:
                self.options[key] = self.options.get(key).split(',')