import json
import re
import scrapy


class Scraper(scrapy.spiders.Spider):
    name = 'generic_scraper_test'

    def __init__(self, page=None, config=None, mandatory=None, *args, **kwargs):
        self.page = page
        self.config = json.loads(config)
        self.mandatory_fields = mandatory.split(',')
        super(Scraper, self).__init__(*args, **kwargs)

    def start_requests(self):
        self.logger.info('Start url: %s' % self.page)
        yield scrapy.Request(url=self.page, callback=self.parse)

    def parse(self, response):
        item = dict(url=response.url)
        # iterate over all keys in config and extract value for each of them
        for key in self.config:
            # extract the data for the key from the html response
            res = response.css(self.config[key]).extract()
            # if the label is any type of url then make sure we have an absolute url instead of a relative one
            if bool(re.search('url', key.lower())):
                res = self.get_absolute_url(response, res)
            item[key] = ' '.join(elem for elem in res).strip()

        # ensure that all mandatory fields are present, else discard this scrape
        mandatory_fields_present = True
        for key in self.mandatory_fields:
            if not item[key]:
                mandatory_fields_present = False

        if mandatory_fields_present:
            yield dict(data=item)

    @staticmethod
    def get_absolute_url(response, urls):
        final_url = []
        for url in urls:
            if not bool(re.match('^http', url)):
                final_url.append(response.urljoin(url))
            else:
                final_url.append(url)
        return final_url
