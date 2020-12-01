from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging


filter_ = r"(\/stories\/)"
start_url = "https://rss.orf.at/"
allow_domains = ["orf.at", "burgenland.orf.at", "salzburg.orf.at", "steiermark.orf.at", "wien.orf.at",
                 "vorarlberg.orf.at", "noe.orf.at", "ooe.orf.at", "tirol.orf.at", "kaernten.orf.at"]


default_params = {"crawler_or_spidercls": None,
          "start_url": None,
          "depth": 1,
          "allow_domains": None,
          "deny_domains": None,
          "allow": None,
          "deny": None,
          "filter_": None}

    # load topic_id dictionary
    #with open(use_cases) as f:
    #    topic_dict = json.load(f)


domain = {"orf":
              {"crawler_or_spidercls": "fetcher",
              "start_url": start_url,
              "depth": 1,
              "allow_domains": allow_domains,
              "filter_": filter_},
          "noen":
             {"crawler_or_spidercls": "fetcher",
              "start_url": "https://www.noen.at/",
              "depth": 1,
              "allow_domains": "noen.at/niederoesterreich",
              "filter_": None},
          "meinbezirk":
             {"crawler_or_spidercls": "fetcher",
              "start_url": "https://www.meinbezirk.at/niederoesterreich",
              "depth": 1,
              "allow_domains": "meinbezirk.at",
              "filter_": None}
          }


process = CrawlerProcess(get_project_settings())

for domain in domain.values():
    kwargs = dict()
    for key, value in default_params.items():
        kwargs[key] = domain.get(key, value)
    logging.info("Add domain dict to process.crawl: %s", kwargs)
    process.crawl(**kwargs)
process.crawl("content_scraper")
process.start()

"""
process.crawl(crawler_or_spidercls="fetcher", start_url=start_url, depth=1,  allow_domains=allow_domains,  # deny_domains="science.orf.at",
              allow=r"(orf\.at)", filter_=r"(\/stories\/)")



#process.crawl(NextSpider)
process.start()

def func(t=None, *args, **kwargs):
    for arg in args:
        print("args:", arg)
    for key, value in kwargs.items():
        print("kwargs:", key, ":", value)


args = {"start_url": "www.test.at", "depth": 1}
func(**args)

help(process.crawl)"""