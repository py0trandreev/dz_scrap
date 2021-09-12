import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    page = 0
    start_urls = ['https://izhevsk.hh.ru/search/vacancy?fromSearchLine=true&st=searchVacancy&text=python&area=1',
                  'https://izhevsk.hh.ru/search/vacancy?fromSearchLine=true&st=searchVacancy&text=python&area=2']

    # Парс ссыллок на вакансии
    def parse(self, response: HtmlResponse):
        links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page:

            yield response.follow(next_page, callback=self.parse)
        for i, link in enumerate(links):

            yield response.follow(link, callback=self.parse_vacancy)

    # Парс самой вакансии (вакансия по конкретной ссылке)
    def parse_vacancy(self, response: HtmlResponse):
        # Заголовок h1 как правило на странице один - название вакансии
        vac_name = response.xpath("//h1/text()").get()

        # З/п по данной вакансии
        vac_salary = response.xpath("//p[@class='vacancy-salary']/span/text()").get()

        # Ссылка на данную вакансию
        vac_url = response.url

        # Передаем полученные данне в JobparserItem
        yield JobparserItem(name=vac_name, salary=vac_salary, url=vac_url)
