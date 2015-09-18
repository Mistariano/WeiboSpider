import scrapy

class WeiboItem(scrapy.Item):
    user=scrapy.Field()
    text = scrapy.Field()
