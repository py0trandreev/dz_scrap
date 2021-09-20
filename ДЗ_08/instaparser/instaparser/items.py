# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id=scrapy.Field()
    user = scrapy.Field()
    user_id = scrapy.Field()
    user_status = scrapy.Field()
    f_username = scrapy.Field()
    id_f = scrapy.Field()
    f_user_photo = scrapy.Field()





