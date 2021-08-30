from pymongo import MongoClient
from pprint import pprint


def print_vacancy():
    client = MongoClient('127.0.0.1', 27017)
    db = client['vacancies']  # см. dz_3_3
    vacs = db.vacs  # Таблица вакансий

    try:
        user_value = int(input("Введите минимальную зарплату в руб.: "))

        # Поиск документов
        for vac in vacs.find({'Валюта': 'руб.'}):
            if vac['Зарплата_от'] is None:
                if user_value < vac['Зарплата_до']:
                    pprint(vac)
            elif vac['Зарплата_от'] is not None:
                if user_value < vac['Зарплата_от']:
                    pprint(vac)

    except ValueError:
        print("Введено неверное значение. \nВведите целое число.")
        return


if __name__ == "__main__":
    print_vacancy()