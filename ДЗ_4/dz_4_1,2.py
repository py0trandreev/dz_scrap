from pprint import pprint
from lxml import html
import requests
from pymongo import MongoClient

def get_date_n_source_by_news_ref(url_to_news: str, headers_fun: dict):
    """
        Получает дату публикации и источник новостей, по заданной ссылке
    :param url_to_news: ссылка на сайт кокретной новостной статьи портала news.mail.ru
    :param headers: заголовки
    :return: кортеж вида (Дата, Источник)
    """
    response_from = requests.get(url_to_news, headers=headers_fun)
    dom_from = html.fromstring(response_from.text)

    date_of_news = dom_from.xpath("//span[@class='note__text breadcrumbs__text js-ago']")
    date_of_news = date_of_news[0].attrib['datetime']

    news_source = dom_from.xpath("//span[@class='note__text breadcrumbs__text js-ago']"
                            "/../../.."
                            "//span[contains(text(),'источник:')]"
                            "/following-sibling::a/span[@class='link__text']")
    news_source = news_source[0].text

    return date_of_news, news_source


""" 
Основной скрипт
"""

# Подключаем БД MongoDB
client = MongoClient('127.0.0.1', 27017)
db = client['news_mail_ru'] # БД
news = db.news   # Коллекция новостей


URL = 'https://news.mail.ru/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.164 YaBrowser/21.6.4.786'
                  ' Yowser/2.5 Safari/537.36'
}

# Ответ с сервера новостей
response = requests.get(URL, headers=headers)
dom = html.fromstring(response.text)  # из текста html  в DOM  объект

# Получаем элементы 5-ти основных новостей с главной страницы web-сайта (5 плиток)
main_news_objects = dom.xpath("//span[@class='photo__title "
                              "photo__title_new photo__title_new_hidden "
                              "js-topnews__notification']")
news_len = len(main_news_objects)


# Получаем все ссылки на новости
reference_to_news = dom.xpath("//span[@class='photo__title "
                              "photo__title_new "
                              "photo__title_new_hidden "
                              "js-topnews__notification']"
                              "/../..")

# Список свежих новостей
ls_news = []


for i in range(news_len):
    news_content = main_news_objects[i].text.replace('\xa0', ' ')
    url_to_article = reference_to_news[i].attrib['href']
    tpl_date_n_source = get_date_n_source_by_news_ref(url_to_article, headers)
    date_of_public = tpl_date_n_source[0]
    source_of_public = tpl_date_n_source[1]

    # Заполняем список свежими новостями
    ls_news.append({
        'News_content': news_content,
        'Url_to_article': url_to_article,
        'Source_of_public': source_of_public,
        'Date_of_public': date_of_public
    })

    # Внесение новых данных в БД
    my_query = {"_id": url_to_article}
    new_values = {"$set": {
        '_id': url_to_article,
        'Содержание': news_content,
        'Источник': source_of_public,
        'Дата': date_of_public
    }}
    news.update_one(my_query, new_values, upsert=True)

print(f'Найдено {news_len} новостей')
pprint(ls_news)





