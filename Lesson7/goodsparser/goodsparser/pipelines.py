# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import re
from urllib.parse import urlparse

import cs
import pymongo
import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


def normalize_str(s : str) -> str:
    """
    Удаляет лишние пробелы в строке
    """
    ls = s.split()
    return " ".join([x for x in ls if len(x) > 1])

def photo_enlarge(str_pic_url:str, size:int):
    """
    e.g.
    'https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_82,h_82,c_pad,b_white,d_photoiscoming.png/LMCode/16639378.jpg',
     ↓
    'https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_1200,h_1200,c_pad,b_white,d_photoiscoming.png/LMCode/16639378.jpg'
    """
    substitute = f"w_{size},h_{size}"

    result = re.sub("w_\d+,h_\d+", substitute, str_pic_url)
    return result








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
        collection = self.mongo_base[spider.name]
        collection.insert_one(dict(item))
        return item

class ProdPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    big_img = photo_enlarge(img, 1200)
                    yield scrapy.Request(big_img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        print()
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item





