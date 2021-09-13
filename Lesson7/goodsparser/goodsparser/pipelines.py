# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

def normalize_str(s : str) -> str:
    """
    Удаляет лишние пробелы в строке
    """
    ls = s.split()
    return " ".join([x for x in ls if len(x) > 1])

class GoodsparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroy1309



    def process_item(self, item, spider):
        # Словарь данных о товаре
        prod_data = item['data']
        for k, v in prod_data.items():
            prod_data[k] = normalize_str(v)

        #  Приводим цену к числу
        item['price'] = int(item['price'])

        print()
        return item
