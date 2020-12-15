from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging

# default...
default_params = {"crawler_or_spidercls": None,
          "start_url": None,
          "depth": 1,
          "allow_domains": None,
          "deny_domains": None,
          "allow": None,
          "deny": None,
          "use_case": None,
          "filter_": None}

# spoe_noe
domain = {"orf":
              {"crawler_or_spidercls": "fetcher",
              "start_url": "https://rss.orf.at/",
              "depth": 1,
              "allow_domains": ["orf.at", "burgenland.orf.at", "salzburg.orf.at", "steiermark.orf.at", "wien.orf.at",
                 "vorarlberg.orf.at", "noe.orf.at", "ooe.orf.at", "tirol.orf.at", "kaernten.orf.at"],
              "use_case": "SPOE_NOE",
              "filter_": r"(\/stories\/)"},
          "noen":
             {"crawler_or_spidercls": "fetcher",
              "start_url": "https://www.noen.at/",
              "depth": 1,
              "allow_domains": "noen.at/niederoesterreich",
              "use_case": "SPOE_NOE",
              "filter_": None},
          "noen_politik":
             {"crawler_or_spidercls": "fetcher",
              "start_url": "https://www.noen.at/niederoesterreich/politik",
              "depth": 1,
              "allow_domains": "noen.at/niederoesterreich",
              "use_case": "SPOE_NOE",
              "filter_": None},
            "msn":
             {"crawler_or_spidercls": "fetcher",
              "start_url": "https://www.msn.com/de-at/",
              "depth": 1,
              "allow_domains": "msn.com",
              "use_case": "SPOE_NOE",
              "filter_": None},
            "krone":
             {"crawler_or_spidercls": "fetcher",
              "start_url": "https://www.krone.at/",
              "depth": 1,
              "allow_domains": "krone.at",
              "use_case": "SPOE_NOE",
              "filter_": None},
            "meinbezirk":
             {"crawler_or_spidercls": "fetcher",
              "start_url": "https://www.meinbezirk.at/niederoesterreich",
              "depth": 1,
              "allow_domains": "meinbezirk.at",
              "use_case": "SPOE_NOE",
              "filter_": None},
          }

# test case
test = {"test":
             {"crawler_or_spidercls": "fetcher",
              "start_url": "https://quotes.toscrape.com/",
              "depth": 0,
              #"allow_domains": "noen.at/niederoesterreich",
              "use_case": "test",
              "filter_": None, }, }

if __name__ == "__main__":
    # start crawler
    process = CrawlerProcess(get_project_settings())
    # iterate through webpages
    for domain in domain.values():
        kwargs = dict()
        for key, value in default_params.items():
            kwargs[key] = domain.get(key, value)
        logging.info("Add domain dict to process.crawl: %s", kwargs)
        # initiate url_fetcher spider
        process.crawl(**kwargs)
    # initiate content_scraper spider
    process.crawl("content_scraper", n_urls=500)
    # start all spiders in parallel
    process.start()
