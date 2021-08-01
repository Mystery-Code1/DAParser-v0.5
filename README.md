# DAParser
**This is a parser program that collects data from the Russian sites "dns-shop" and "avito"**</br>
With this, you can get basic data about the products: name, price, description and availability of the product. On the page you selected</br>
### This program can import data collected from websites:
* **to json**
* **to MySQL database**
___
### General information
* This program uses the **firefox browser** and **geckodriver** for scraping
* The dns-shop.ru parsing returns: *name, price, parameter and availability*
* The avito.ru parsing returns: *title, price, locate, date, description*
* Enter the URL address without the page number: "https://www.dns-shop.ru/catalog/example/example/"
* json files are written to the "json_files" folder
___
### Documentation
1. Choose the type of parser between "dns-shop" and "avito"
1. Enter the URL following the example in the program
1. Select the scraping range between the start and finish page
1. Select data import: json file or your database
1. Start parsing by clicking on the button
1. Wait until the parsing is finished (the waiting time depends on the number of pages). Parsing "dns-shop" is slower than "avito".
___
### Updates
**The program will be updated soon, there will be new functionality**</br>
This is just the beginning
