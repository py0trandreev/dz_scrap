# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy0209


    def process_item(self, item, spider):
        # dict_item = dict(item)
        # Определяем домен, в котором ползает паук
        domain = spider.allowed_domains[0]
        if domain == 'hh.ru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary_hh(item['salary'])
        elif domain == 'superjob.ru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary_sj(item['salary'])

        item['site'] = domain
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def process_salary_hh(self, salary:str):
        ls_salary = salary.replace("\xa0", "").split()
        digits_in_list = len([s for s in ls_salary if s.isdigit()])
        min = max = 0

        if digits_in_list == 0:
            # нет данных о з/п
            return 0, 0, ''

        try:
            for i in range(len(ls_salary)):
                if ls_salary[i] == "от":
                    min = int(ls_salary[i + 1])
                elif ls_salary[i] == "до":
                    max = int(ls_salary[i + 1])
                elif i == len(ls_salary) - 1 and not (ls_salary[i].isdigit()):
                    cur = ls_salary[i]
            return min, max, cur
        except Exception as e:
            print("Не удалось распознать з/п. " + str(e))
            return 0, 0, ''


    def process_salary_sj(self, salary:list):
        ls_salary = [x.replace("\xa0", "") for x in salary if x != '\xa0']
        min = max = 0
        cur = ''

        try:
            for i in range(len(ls_salary)):
                if ls_salary[i].isdigit() and ls_salary[i + 1].isdigit():
                    min = int(ls_salary[i])
                    max = int(ls_salary[i + 1])
                    cur = ls_salary[-1]

                elif ls_salary[i] == "от":
                    st_salary = ls_salary[i + 1]
                    st_wo_currency = "".join(filter(str.isdigit, st_salary))
                    st_currency = st_salary[len(st_wo_currency):]
                    min = int(st_wo_currency)
                    cur = st_currency
                    break
                elif ls_salary[i] == "до":
                    st_salary = ls_salary[i + 1]
                    st_wo_currency = "".join(filter(str.isdigit, st_salary))
                    st_currency = st_salary[len(st_wo_currency):]
                    max = int(st_wo_currency)
                    cur = st_currency
                    break
                else:
                    # нет данных о з/п
                    break
            return min, max, cur
        except Exception as e:
            print("Не удалось распознать з/п. " + str(e))
            return 0, 0, ''


