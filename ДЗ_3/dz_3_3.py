# https://hh.ru/search/vacancy?clusters=true&area=113&no_magic=true&ored_clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=Python
from pprint import pprint

from bs4 import BeautifulSoup as bs
import requests
import json
from pymongo import MongoClient


def get_salary_range(str: str) -> tuple:
    ls_params = str.split(" ")

    if len(ls_params) == 4:
        return int(ls_params[0].replace("\u202f", "")), int(ls_params[2].replace("\u202f", "")), ls_params[3]

    elif len(ls_params) == 3:
        if ls_params[0] == "от":
            return int(ls_params[1].replace("\u202f", "")), None, ls_params[2]
        elif ls_params[0] == "до":
            return None, int(ls_params[1].replace("\u202f", "")), ls_params[2]
        else:
            return None
    else:
        return None


client = MongoClient('127.0.0.1', 27017)

db = client['vacancies'] # БД
vacs = db.vacs   # Таблица вакансий


url = 'https://hh.ru'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 YaBrowser/21.6.4.786 Yowser/2.5 Safari/537.36'}

page = 0
ls_vacancies = []

while True:

    params = {
        'clusters': 'true',
        'area': '113',
        'no_magic': 'true',
        'ored_clusters': 'true',
        'enable_snippets': 'true',
        'salary': '',
        'st': 'searchVacancy',
        'text': 'python',
        'page': str(page)
    }

    response = requests.get(url + '/search/vacancy', params=params, headers=headers)

    soup = bs(response.text, 'html.parser')
    vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})

    # Button more pages
    div_button_more = soup.find_all('div', {'data-qa': 'pager-block'})
    button_more = div_button_more[0].findChild('a', {'data-qa': 'pager-next'})

    for vacancy in vacancies:
        name = vacancy.find('a', {'class': 'bloko-link'}).text
        # salary_block =  vacancy.find('div',{'vacancy-serp-item__sidebar'})
        # ls_salary_block_child = list(salary_block.findChildren(recursive=False))

        # Header with vacancy name and salary
        header = vacancy.find('div', {'class': 'vacancy-serp-item__row_header'})
        vacancy_name = header.findChild('div', {'class': 'vacancy-serp-item__info'}).text
        vacancy_ref = header.findChild('a', {'class': 'bloko-link'}).attrs['href']

        header_sal = header.findChild('div', {'class': 'vacancy-serp-item__sidebar'})

        salary_from = None
        salary_to = None
        salary_currency = None

        if header_sal is not None:
            salary_tup = get_salary_range(header_sal.text)
            salary_from = salary_tup[0]
            salary_to = salary_tup[1]
            salary_currency = salary_tup[2]

        # assembling
        ls_vacancies.append({
            'Вакансия': vacancy_name,
            'Зарплата': {'от': salary_from, 'до': salary_to, 'валюта': salary_currency},
            'Ссылка': vacancy_ref,
            'Сайт': url
        })

    my_query = {"_id": vacancy_ref}
    new_values = {"$set": {
        '_id': vacancy_ref,
        'Вакансия': vacancy_name,
        'Зарплата_от': salary_from,
        'Зарплата_до': salary_to,
        'Валюта': salary_currency,
        'Сайт': url
    }}

    vacs.update_one(my_query, new_values, upsert=True)

    if button_more is None:
        break
    page += 1


# pprint(ls_vacancies)
pprint(len(ls_vacancies))

# with open('data.json', 'w', encoding='utf-8') as f:
#     json.dump(ls_vacancies, f, ensure_ascii=False)
