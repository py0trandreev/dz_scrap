import time
from pprint import pprint

from pymongo import MongoClient
import ast
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.opera.options import Options


# Подключаем БД MongoDB
client = MongoClient('127.0.0.1', 27017)
db = client['mvideo_goods'] # БД
news = db.new_goods   # Коллекция новостей

opera_options = Options()
opera_options.add_argument("--start-maximized")

driver = webdriver.Opera(executable_path=r"C:\Users\petr\Portables\operadriver_win64\operadriver.exe")
driver.get("https://www.mvideo.ru/")

driver.implicitly_wait(1)

# Нажымаем "Все верно" при  предложении установить город
str_xpath = "//a[contains(text(), 'Все верно')]"
elem = driver.find_element_by_xpath(str_xpath)
elem.send_keys(Keys.ENTER)

# Опустимся к тексту "Новинки"
str_xpath = "//h2[contains(text(), 'Новинки')][1]"
elem = driver.find_element_by_xpath(str_xpath)
elem.click()

# Опустимся ниже текста "Новинки" (чтобы кнопка "Далее" появилась)
driver.execute_script("window.scrollTo(0, window.scrollY + 300);")


# Находим кнопку "Далее" в разделе "Новинки" (чтобы все данные выгрузились в html)
str_xpath_main = "//h2[contains(text(), 'Новинки')][1]/../../.."  # - Прародитель содержащий товарные позиции
str_xpath = str_xpath_main + \
            "//a[@class='next-btn c-btn c-btn_scroll-horizontal c-btn_icon i-icon-fl-arrow-right']"

while True:
    try:
        elem = driver.find_element_by_xpath(str_xpath)
        elem.send_keys(Keys.ENTER)
    except NoSuchElementException:
        print("Кнопка далее изчезла. Мы достигли конца списка")
        break

# Получаем список контейнеров товарных позиций
str_xpath = str_xpath_main + "//*[contains(@data-sel,'product_tile-div-')]//a[@data-product-info and @data-sel]"

elems = driver.find_elements_by_xpath(str_xpath)

for elem in elems:
    product_data = elem.get_attribute("data-product-info")
    dict_product_data = ast.literal_eval(product_data)

    # вытягиваем данные из словаря dict_product_data
    href = elem.get_attribute('href')
    productName = dict_product_data['productName']
    productPriceLocal = dict_product_data['productPriceLocal']
    productCategoryName = dict_product_data['productCategoryName']
    productVendorName = dict_product_data['productVendorName']


    # Внесение новых данных в БД
    my_query = {"_id": href}
    new_values = {"$set": {
        '_id': href,
        'productName': productName,
        'productPriceLocal': float(productPriceLocal),
        'productCategoryName': productCategoryName,
        'productVendorName': productVendorName
    }}
    news.update_one(my_query, new_values, upsert=True)
    # print(productName)

print()
