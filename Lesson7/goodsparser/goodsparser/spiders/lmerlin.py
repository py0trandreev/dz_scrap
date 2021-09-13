import scrapy
from scrapy.http import HtmlResponse

from goodsparser.goodsparser.items import GoodsparserItem


class LmerlinSpider(scrapy.Spider):
    name = 'lmerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://kazan.leroymerlin.ru/search/?q={query}'
                      '&family=00b9b5a0-faeb-11e9-810b-878d0b27ea5b&suggest=true&fromRegion=34&eligibilityByStores=Казань']



    # Парсим страницу с общим списком товаров
    def parse(self, response: HtmlResponse):
        links = response.xpath('//a[@data-qa="product-name"]/@href').getall()
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for i, link in enumerate(links):
            yield response.follow(link, callback=self.parse_product)
        print()

    # Парсим страницу с конкретным товаром
    def parse_product(self, response: HtmlResponse):
        # Заголовок h1 как правило на странице один - название
        prod_name = response.xpath("//h1/text()").get()

        # Ссылка конкретную единицу товара
        prod_url = response.url

        # Цена товара
        price_str = response.xpath('(//span[@slot="price"])[1]/text()').get()

        # Ед.измерения
        unit_str = response.xpath('(//span[@slot="unit"])[1]/text()').get()


        # Характеристики
        # Ключи характеристик
        keys_data = response.xpath('//dt[@class="def-list__term"]/text()').getall()
        # Значения характеристик
        vals_data = response.xpath('//dd[@class="def-list__definition"]/text()').getall()
        if len(keys_data) != len(vals_data):
            raise Exception('Характеристики. Несовпадение количество ключей и значений.')

        # Сборка словаря характеристик товара
        prod_data = {keys_data[i]:vals_data[i] for i in range(len(keys_data))}

        # фотки
        photos = response.xpath('//img[@slot="thumbs"]/@src').getall()


        print()
        # Передаем полученные данне в GoodsparserItem
        yield GoodsparserItem(name=prod_name, url=prod_url, price=price_str, unit=unit_str, data=prod_data, photos=photos)
        print()

