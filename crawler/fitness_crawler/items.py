# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EKPItem(scrapy.Item):
    uid = scrapy.Field()


class MensHealthItem(EKPItem):
    """맨즈헬스 Item
    """
    uid = scrapy.Field()
    board_id = scrapy.Field()
    article_id = scrapy.Field()
    title = scrapy.Field()
    subtitle = scrapy.Field()
    lead = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
