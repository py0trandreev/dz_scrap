import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from dotenv import load_dotenv

from instaparser.spiders.instagram import InstagramSpider
from instaparser import settings

if __name__ == '__main__':
    load_dotenv(r'C:\Users\petr\my_env\.env')
    login = os.getenv('LOGIN_INSTA')
    password = os.getenv('PASSENC_INSTA')
    user_to_parse = ['cori_ca_cotaro', 'siaorifly']

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)

    kwargs={
        'login':login,
        'password':password,
        'user_to_parse':user_to_parse
    }
    process.crawl(InstagramSpider, **kwargs)

    process.start()