# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyMangaItem(scrapy.Item):
    # Compulsory ones
    file_urls = scrapy.Field()
    files = scrapy.Field()
    # My information
    folder = scrapy.Field()
    name = scrapy.Field()
    file_name = scrapy.Field()


class MetaFileItem(scrapy.Item):
    # Compulsory ones
    file_urls = scrapy.Field()
    files = scrapy.Field()
    file_path = scrapy.Field()
    verbose = scrapy.Field()


class MetaMasterNode(scrapy.Item):
    # Compulsory ones
    url = scrapy.Field()
    wallet = scrapy.Field()




