# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GoodreadsItem(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    rating = scrapy.Field()
    num_reviews = scrapy.Field()
    num_ratings = scrapy.Field()
    genres = scrapy.Field()
    pages = scrapy.Field()
    isbn = scrapy.Field()
