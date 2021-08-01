#-*- coding: utf-8 -*-
import requests
import os
import time
import json
from itertools import count
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QTextEdit
from bs4 import BeautifulSoup
from selenium import webdriver
from lxml import html
import pymysql



class Parser(object):

    def _connect_(self, hostname, port, useradmin, password, database):
        try:
            #Подключение к базе данных
            self.connection = pymysql.connect(
                host = hostname,
                port = port,
                user = useradmin,
                password = password,
                database = database,
                cursorclass = pymysql.cursors.DictCursor
            )

            return {
                "connect" : self.connection, 
                "host" : hostname, 
                "port" : port, 
                "user" : useradmin, 
                "password" : password, 
                "database" : database,
                "output" : "Connection successful..."
                }
        except Exception as ex:
            return {"output" : "Connection refused.. {0}".format(ex)}
            
 


    def _parseavito_(self, urls):
        #----- __init__ -----
        head = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
        }

        response_avito = requests.get(urls, headers=head)
        content = response_avito.content.decode("utf-8")

        with open("site_index_1.html", "w", encoding="utf-8") as browser_file:
            browser_file.write(content.replace("&quot", '"'))

        html_content = open("site_index_1.html", "r", encoding="utf-8").read() 
        soup = BeautifulSoup(html_content, "lxml")
        self.pagination = 100

        self.avito_title = []
        self.avito_price = []
        self.avito_locate = []
        self.avito_date = []
        self.avito_description = []
        #----- \__init__\ -----
        print("Successful")
        
        html_product_container = soup.find_all("div", attrs={"data-marker" : "item"})

        for product_index in range(len(html_product_container)):

            container_items = BeautifulSoup(str(html_product_container[product_index]), "lxml")

            html_product_title = container_items.find("h3", attrs={"itemprop" : "name"})
            product_title = html_product_title.get_text().replace("'", "")
            self.avito_title.append(r"%s" %product_title)

            html_product_price = container_items.find("meta", attrs={"itemprop" : "price"})
            html_product_price_currency = container_items.find("meta", attrs={"itemprop" : "priceCurrency"})
            content_price = html_product_price["content"]
            content_currency = " " + html_product_price_currency["content"]
            if content_price == "":
                content_price = "Бесплатно"
                content_currency = ""
            elif content_price == "...":
                content_price = "Цена не указана"
                content_currency = ""
            self.avito_price.append("{0}{1}".format(content_price, content_currency))

            html_product_locate = container_items.find_all("div", attrs={"class" : ""})
            locate_index = 0
            while locate_index < len(html_product_locate):
                text_locate = html_product_locate[locate_index].get_text().lower()
                    
                if text_locate == "компания" or text_locate == "написать":
                    del html_product_locate[locate_index]
                    locate_index = locate_index - 1
                locate_index = locate_index + 1

            if html_product_locate == None:
                html_product_locate = container_items.find("div", attrs={"data-marker":"item-address"})
            product_locate = html_product_locate[0].get_text().replace("\xa0", " ")

            self.avito_locate.append(product_locate)

            try:
                html_product_description = container_items.find("meta", attrs={"itemprop" : "description"})
                product_description = html_product_description["content"].replace("\n", "  ")
            except:
                product_description = ""
            finally:
                self.avito_description.append(product_description)

            html_product_date = container_items.find("div", attrs={"data-marker" : "item-date"})
            product_date = html_product_date.get_text()
            self.avito_date.append(product_date)
        time.sleep(5)

        return {
            "pagination" : int(self.pagination),
            "count" : len(html_product_container),
            "value" : [self.avito_title, self.avito_price, self.avito_locate, self.avito_date, self.avito_description],
            "name" : ["title", "price", "locate", "date", "description"]
        }



    def _parsedns_(self, head, urls):

        #----- __init__ -----

        #user bot
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        #driver
        self.driver = ''

        #product id
        self.DNSid_count = 0
        
        self.DNSprice_list = []
        
        self.DNSname_list = []
        
        self.DNSin_stock_list = []
        
        self.DNSparameter_list = []
        
        self.DNSdata = None
        #product blocks
        self.block = 0

        #----- \__init__\ -----

        try:

            #options and headless mode
            self.options = webdriver.FirefoxOptions()
            self.options.add_argument(head)
            self.options.set_preference("general.useragent.override", self.USER_AGENT)

            print("Launching the browser")
            #browser
            self.driver = webdriver.Firefox(executable_path="driver/geckodriver.exe", options=self.options)

            
            self.driver.get(urls)
            #Sleep for loading a site
            time.sleep(7)
            with open("site_index.html", "w", encoding="utf-8") as file:
                file.write(self.driver.page_source)

            self.driver.close()
            self.driver.quit()




            with open("site_index.html", encoding="utf-8") as read_file:
                src = read_file.read()




            #Collecting the data
            soup = BeautifulSoup(src, "lxml")



            html_price_list = soup.find_all("div", class_="product-buy__price")

            for index_price_list in range(len(html_price_list)):
                price = html_price_list[index_price_list].get_text().split("₽")
                self.DNSprice_list.append(int(price[0].replace(' ', '')))

            html_name_list = soup.find_all("a", class_="catalog-product__name ui-link ui-link_black")

            for index_name_list in range(len(html_name_list)):
                name = html_name_list[index_name_list].get_text().split("[")
                self.DNSname_list.append(r"%s" %name[0].replace("'", " "))

                parameter = ''

                if len(name) > 1:
                    parameter = name[1].split("]")[0]
                self.DNSparameter_list.append(parameter)




                
            html_product_avails = soup.find_all("span", class_="catalog-product__avails avails-container")

            for index_avail_list in range(len(html_product_avails)):

                #find all the elements, check and add them
                avails = html_product_avails[index_avail_list].get_text().replace("\n", "").replace("\t", "")
                if avails == "Товара нет в наличии":
                    self.DNSin_stock_list.append("Нет в наличии")

                elif avails == "Цифровая версия":
                    self.DNSin_stock_list.append("Цифровая версия")

                elif avails == "":
                    self.DNSin_stock_list.append("")

                else:

                    html_product = BeautifulSoup(str(html_product_avails[index_avail_list]), "lxml")
                    order_list = html_product.find_all("div", class_="order-avail-wrap")
                    avail_list = BeautifulSoup(str(order_list[0]), "lxml")
                    html_count_list = avail_list.find("a", class_="order-avail-wrap__link ui-link ui-link_blue ui-link_pseudolink", tabindex="0")

                    self.DNSin_stock_list.append(html_count_list.get_text())





            self.block = self.block = soup.find_all("div", class_="catalog-product ui-button-widget")

            return {
                'pagination' : None,
                'count' : len(self.block),
                'value' : [self.DNSname_list, self.DNSparameter_list, self.DNSprice_list, self.DNSin_stock_list],
                'name' : ["name", "parameter", "price", "availability"]
            }

        except Exception as ex:
           return {"value" : "Parser Proccess Error: {0}".format(ex)}





    def _addJSON_(self, data, name):
        
        try:
            JSONform = []
            LOADform = None
            max_index = data['count']
            _id = None

            if os.path.isfile("json_files\\" + str(name) + ".json") == False:

                with open("json_files\\" + str(name) + ".json", "w", encoding="utf-8") as json_file:

                    _id = 0
            else:
                with open("json_files\\" + str(name) + ".json", "r", encoding="utf-8") as read_file:

                    LOADform = json.load(read_file)
                    #Узнаём последнее id
                    _id = LOADform[-1]["id"]

            file = open("json_files\\" + str(name) + ".json", "w", encoding="utf-8")

            for table_index in range(max_index):
                stroke_form = {}
                #collect data
                for stroke_index in range(len(data["name"])):
                    stroke_form[data["name"][stroke_index]] = data["value"][stroke_index][table_index]

                _id = _id + 1

                stroke_form["id"] = _id

                #JSON object
                if _id > max_index:
                    LOADform.append(stroke_form)
                else:
                    JSONform.append(stroke_form)
            if _id > max_index:
                load_obj = json.dumps(LOADform, sort_keys=True, indent=4, ensure_ascii=False)
                file.write(load_obj)

            else:
                json_obj = json.dumps(JSONform, sort_keys=True, indent=4, ensure_ascii=False)
                file.write(json_obj)

        except Exception as ex:
            print(ex)


            










    def _addsql_(self, database, tablename, connection, data):
        
        max_index = data['count']

        with connection.cursor() as cursor:
            for table_index in range(max_index):
                stroke_value_form = []
                stroke_name_form = []
                #collect data
                for stroke_index in range(len(data["name"])):
                    stroke_name_form.append(data["name"][stroke_index])
                    stroke_value_form.append("'" + str(data["value"][stroke_index][table_index]) + "'")


                add_value = "INSERT INTO `{0}`.`{1}` ({2}) VALUES ({3});".format(database, tablename, ", ".join(stroke_name_form), ", ".join(stroke_value_form))
                cursor.execute(add_value)
            connection.commit()






    def _changetable_(self, database, tablename, connection, data):

        names = []

        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES FROM `{0}` LIKE '{1}'".format(database, tablename))
            result_set = cursor.fetchall()
            for index in range(len(data["name"])):
                names.append(data["name"][index] + " VARCHAR(500)")

            if len(result_set) == 0:
                cursor.execute("CREATE TABLE {0}.{1} (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, {2})".format(database, tablename, ", ".join(names)))
                connection.commit()



