# -*- mode: python -*-

import scrapy


class AuthorMetaItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()


class WorkMetaItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    resource_total = scrapy.Field()
    tags = scrapy.Field()
    caption = scrapy.Field()
    type = scrapy.Field()
    author = scrapy.Field()
    series = scrapy.Field()


class ResourceItem(scrapy.Item):
    work = scrapy.Field()
    referer = scrapy.Field()
    resource_url = scrapy.Field()
