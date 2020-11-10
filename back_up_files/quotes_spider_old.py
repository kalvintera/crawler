import scrapy
from crawler.items import QuoteItem
from scrapy.loader import ItemLoader

class QuotesSpider(scrapy.Spider):
	name = "quotes_old"
	start_urls = ["http://quotes.toscrape.com"]

	def parse(self, response):
		self.logger.info("hello this is my first spider")
		quote_item = QuoteItem()
		quotes = response.css('div.quote')

		for quote in quotes:
			# SAVE QUOTES
			# V3 ImteLoader best, for in-between processing of items!
			loader = ItemLoader(item=QuoteItem(), selector=quote)
			loader.add_css('quote_content', '.text::text')
			loader.add_css('tags', '.tag::text')
			quote_item = loader.load_item()

			# V2 saves data in items
			# quote_item["quote_content"] = quote.css('.text::text').get()
			# quote_item["tags"] = quote.css('.tag::text').getall()

			# V1 just returns but does not safe items
			# yield {
			#	'text': quote.css('.text::text').get(),
			#	'author': quote.css('.author::text').get(),
			#	'tags': quote.css('.tag::text').getall(),
			# }

			# GET AUTHOR PAGE
			author_url = quote.css('.author + a::attr(href)').get()
			self.logger.info('get author page url')
			# go to the author page
			yield response.follow(author_url, callback=self.parse_author)

		# GOTO NEXT PAGE
		# V1
		next_page = response.css('li.next a::attr(href)').get()
		if next_page is not None:
			next_page = response.urljoin(next_page)
			# callback  calls the same parse function to get the quotes from the new page
			yield scrapy.Request(next_page, callback=self.parse)

		# V2 same as V1:
		# https://docs.scrapy.org/en/latest/intro/tutorial.html#a-shortcut-for-creating-requests
		# response.follow supports relative urls (no need for urljoin) and checks automatically uses href for <a> tags
		# for a in response.css('li.next a'):
		# 	yield response.follow(a, callback=self.parse)

	def parse_author(self, response):
		yield {
			'author_name': response.css('.author-title::text').get(),
			'author_birthday': response.css('.author-born-date::text').get(),
			'author_bornlocation': response.css('.author-born-location::text').get(),
			'author_bio': response.css('.author-description::text').get(),
		}

