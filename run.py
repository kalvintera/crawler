from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
kwargs = {"allow": r"(\/stories\/)"}
start_url = "https://rss.orf.at/"
allow_domains = ["orf.at", "burgenland.orf.at", "salzburg.orf.at", "steiermark.orf.at", "wien.orf.at",
                 "vorarlberg.orf.at","noe.orf.at", "ooe.orf.at", "tirol.orf.at", "kaernten.orf.at"]
process.crawl("fetcher", start_url=start_url, depth=1,  allow_domains=allow_domains,  # deny_domains="science.orf.at",
              allow=r"(orf\.at)", filter_=r"(\/stories\/)")
#process.crawl(NextSpider)
process.start()