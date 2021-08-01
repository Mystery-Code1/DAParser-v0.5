import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QLabel, QTextEdit, QSpacerItem, QRadioButton
from itertools import count
import parser_design
import site_parser
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os



class ParserApp(QtWidgets.QMainWindow, parser_design.Ui_MainWindow, site_parser.Parser):
	def __init__(self):

		super().__init__()
		self.setupUi(self)
		#Until the end
		self.endless = False
		#Dump data
		self.import_data_method = ''
		# Activate database input fields
		self.active_fields = False
		#Activate --headless mode
		self.headless_mode = "--headless"
		#Parsing type
		self.parser_type = "dns"
		#Styling
		self.colors = {"dns" : { "first" : "orange", "second" : "rgb(210, 105, 30)" }, "avito" : { "first" : "#009cf0", "second" : "#0272af" }}
		#Messages
		self.message = "successfully"
		
		#events
		self.selected_dns.clicked.connect(self.select_dns_mode)
		self.selected_avito.clicked.connect(self.select_avito_mode)
		self.start_parse.clicked.connect(self.parsing)

		self.untilcheck.stateChanged.connect(self.everlasting_page)
		self.headless_check.stateChanged.connect(self.browserstatus)

		self.tojsonmark.toggled.connect(self.importmethod)
		self.todatabasemark.toggled.connect(self.importmethod)



	def everlasting_page(self, state):
		#checking the user choice
		if state == Qt.Checked:	
			self.spin_count.setEnabled(False)
			self.endless = True
			self.spin_count.setStyleSheet("font-size:25px; color:black; background:grey;")

		else:
			self.spin_count.setEnabled(True)
			self.endless = False
			self.spin_count.setStyleSheet("font-size:25px; color:{0}; background:silver; ".format(self.colors[parser_type]["second"]))

	def browserstatus(self, state):
		#open a browser
		if state == Qt.Checked:
			self.headless_mode = "--headless"

		else:
			self.headless_mode = ""

	def importmethod(self, value):

		method = self.sender()
		if method.isChecked() == True:
			self.import_data_method = method.text()

		if method.text() == "to the MySQL database":
			activate_fields = True
			self.jsonname_field.setEnabled(False)
		else:
			self.jsonname_field.setEnabled(True)
			activate_fields = False
			
		self.database_field.setEnabled(activate_fields)
		self.password_field.setEnabled(activate_fields)
		self.host_field.setEnabled(activate_fields)
		self.port_field.setEnabled(activate_fields)
		self.username_field.setEnabled(activate_fields)
		self.tablename_field.setEnabled(activate_fields)

	def changedesign(self, firstcolor, secondcolor):
		#change styles
		self.setting_label.setStyleSheet("font-size:25px; color:{0}; font-weight:bold;".format(firstcolor))
		self.dump_label.setStyleSheet("font-size:25px; color:{0}; font-weight:bold;".format(firstcolor))

		self.spin_startpage.setStyleSheet("font-size:25px; color:{0}; background:silver;".format(secondcolor))
		self.spin_count.setStyleSheet("font-size:25px; color:{0}; background:silver; ".format(secondcolor))
		self.url_field.setStyleSheet("background:silver; color:{0};".format(secondcolor))

		self.log_field.setStyleSheet("border:5px solid {0}; padding-left:20px; color:{0}; background:black;".format(firstcolor))
		self.start_parse.setStyleSheet("background:{0}; font-size:20px; font-weight:bold; color:black; border:2px solid black;".format(secondcolor))


	def select_dns_mode(self):
		self.selected_dns.setStyleSheet("font-weight:bold; font-size:15px; background:rgb(220, 220, 220); color:black; border-bottom:15px solid black;")
		self.selected_avito.setStyleSheet("font-weight:bold; font-size:15px; background:dimgrey; color:white; border-bottom:15px solid black;")
		self.url_example_label.setText("example of a url address: \n  https://www.dns-shop.ru/catalog/17a/smartfony/")

		self.changedesign(self.colors["dns"]["first"], self.colors["dns"]["second"])
		self.headless_check.show()
		self.parser_type = "dns"



	def select_avito_mode(self):
		self.selected_avito.setStyleSheet("font-weight:bold; font-size:15px; background:rgb(220, 220, 220); color:black; border-bottom:15px solid black;")
		self.selected_dns.setStyleSheet("font-weight:bold; font-size:15px; background:dimgrey; color:white; border-bottom:15px solid black;")
		self.url_example_label.setText("example of a url address: \n  https://www.avito.ru/moskva/noutbuki/")

		self.changedesign(self.colors["avito"]["first"], self.colors["avito"]["second"])
		self.headless_check.hide()
		self.parser_type = "avito"


	def parsing_proccess(self):
		try:

			data = None
			num_of_site = int(self.spin_startpage.value())
			connector = None
			url_string = self.url_field.text()
			check_page = int(self.spin_count.value())
			JSONname = self.jsonname_field.text()

			host = self.host_field.text()
			port = self.port_field.text()
			database = self.database_field.text()
			password = self.password_field.text()
			username = self.username_field.text()
			tablename = self.tablename_field.text()

			check_page_count = range(check_page)

			if self.import_data_method == 'to the MySQL database':
				#connect to the database
				connector = self._connect_(host, port, username, password, database)


			if self.endless == True:
				#if site don't have a pagination (DNS.site)
				if self.parser_type == "dns":
					check_page_count = count(0)
				#else site have any pagination (Avito.site)
				else:
					check_page_count = data["pagination"]

			#URL valid checking
			if url_string != "" and (url_string.find("https://www.avito.ru") == 0 or url_string.find("https://www.dns-shop.ru") == 0):
				#Page parsing cycle
				for index_of_site in check_page_count:

					data = None
					try:
						urls = "{0}?p={1}".format(url_string, num_of_site)
						#check user site
						if self.parser_type == "dns":
							#dns-shop
							data = self._parsedns_(self.headless_mode, urls)
						else:
							#avito
							data = self._parseavito_(urls)
						
						#if page don't have any elements
						if data['count'] == 0:
							break


					except Exception as ex:
						#if page does not exist
						self.log_field.append("Parser Error 404: Unexpected URL address \n system message: {0}".format(data["value"]))
						self.message = "with errors"
					
					#adding to json
					if self.import_data_method == 'to a JSON file':
						self._addJSON_(data, JSONname)

					#adding to database
					elif self.import_data_method == 'to the MySQL database':
					
						#create a table
						#change database
						try:
							self._changetable_(database, tablename, connector["connect"], data)
							self._addsql_(database, tablename, connector["connect"], data)

							
						except Exception as ex:
							#check database
							self.log_field.append("Connecting Error: {0}".format(connector["output"]))
							self.message = "with error"


					#next page
					self.log_field.append("#{0} - Done".format(num_of_site))
					print("#{0} - Done".format(num_of_site))
					num_of_site = num_of_site + 1

			else:
				#if the URL address incorrect
				self.log_field.append("Scraping Error: Incorrect URL address")
				self.message = "with error"

			#finish the process message
			self.log_field.append("The process finished {0}".format(self.message))

		finally:
			#return styles
			self.start_parse.setStyleSheet("background:{0}; font-size:20px; font-weight:bold; color:black; border:2px solid black;".format(self.colors[self.parser_type]["second"]))
			self.start_parse.setEnabled(True)


	def parsing(self):
		#change styles and starting scraping
		self.log_field.append("The process started successfully. Please wait a few minutes")
		self.start_parse.setStyleSheet("background:gray; font-size:20px; font-weight:bold; color:white; border:2px solid black;")
		self.start_parse.setEnabled(False)

		QTimer.singleShot(100, self.parsing_proccess)


	






def main():
	app = QtWidgets.QApplication(sys.argv)
	window = ParserApp()
	window.show()
	app.exec_()

if __name__ == '__main__':
	main()

