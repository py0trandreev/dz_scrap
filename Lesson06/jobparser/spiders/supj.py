import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SupjSpider(scrapy.Spider):
    name = 'supj'
    allowed_domains = ['superjob.ru']
    page = 0
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Bt%5D%5B0%5D=4',
                  'https://spb.superjob.ru/vacancy/search/?keywords=Python']


    # Парс ссыллок на вакансии
    def parse(self, response: HtmlResponse):
        # Список ссылок вакансий
        links = response.xpath("//a[contains(@class, '_2JivQ _1UJAN')]/@href").getall()

        # Кнопка "Далее"
        next_page = response.xpath("(//a[@rel='next']/@href)[2]").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for i, link in enumerate(links):
            yield response.follow(link, callback=self.parse_vacancy)


    # Парс самой вакансии (вакансия по конкретной ссылке)
    def parse_vacancy(self, response: HtmlResponse):
        # Заголовок h1 как правило на странице один - название вакансии
        vac_name = response.xpath("//h1/text()").get()

        # З/п по данной вакансии
        vac_salary = response.xpath("//span[@class='_1h3Zg _2Wp8I _2rfUm _2hCDz']/text()").getall()
        print(vac_salary)
        # Ссылка на данную вакансию
        vac_url = response.url

        # Передаем полученные данне в JobparserItem
        yield JobparserItem(name=vac_name, salary=vac_salary, url=vac_url)
