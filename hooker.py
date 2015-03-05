#!/usr/bin/python
# -*- coding: utf-8 -*-

import ipdb
import subprocess as sub
import re
from urllib2 import urlopen

# to read API's xml response
from lxml import objectify
import os

from kivy.app import App
# from kivy.animation import Animation
# from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from threading import Thread
# from kivy.properties import NumericProperty
# from kivy.clock import Clock
# from kivy.graphics import Rectangle, Color, Ellipse, Line
# from kivy.utils import get_color_from_hex

# --------------------------------------- Config --------------------------------------

# Configure this yourself
my_number = "2422435" 
PWD = os.path.dirname(os.path.realpath(__file__))

# --------------------------------------- Utils ---------------------------------------

# Is every char a number?
def isANumber(num):
	if re.match("^[0-9]*$", num):
		return True
	else:
		return False
		
# We ask for number with country code, so strip the zero before search
def stripZero(num):
	if num[0] == "0":
		return num[1:]
	else:
		return num

# --------------------------------------- Functions -----------------------------------

def displayClients(clients, GUI, num):
	# sub.call(["notify-send", "Call information retrieved!"])
	GUI.removeAllContacts()
	GUI.addContacts(clients=clients, num=num)

def parseXML(query):
	obj = objectify.fromstring(query)
	if obj.Result.Status == 0:
		result = []
		contacts = obj.Contacts.getchildren()
		for i in contacts:
			contact = i
			result.append(" -- MATCHING CALLER -- \nName: %s %s\nEmail: %s\nZone: %s\nCountry: %s" % (getInfo("First", contact), getInfo("Last", contact), getInfo("Email", contact), getInfo("Custom16", contact), getInfo("ContactAddressCountry", contact)))
		return result
	return False

def getInfo(field, obj):
	try: 
		return obj[field]
	except:
		return "** UNKNOWN **"

def readQuery():
	process1 = sub.Popen(["cat", "LastCallNumber"], stdout=sub.PIPE, stderr=sub.PIPE)
	num = process1.communicate()[0]
	process2 = sub.Popen(["cat", "last_query_mobile.xml"], stdout=sub.PIPE, stderr=sub.PIPE)
	output = process2.communicate()[0]
	return output, num

class CentreLabel(Label):
	def __init__(self, **kwargs):
		super(CentreLabel, self).__init__(**kwargs)
		self.x = Window.width/2 - self.width/2
		self.font_name= PWD + "/assets/Montserrat-Bold.ttf"

class GUI(GridLayout):
	def __init__(self, **kwargs):
		super(GUI, self).__init__(**kwargs)
		self.root = kwargs["root"]
		self.app = kwargs["app"]
		self.contacts = []
		self.headline = CentreLabel(text="", font_size="40sp")
		self.add_widget(self.headline)
		# self.reset_btn = Button(text="Start listening")
		# self.reset_btn.bind(on_press=self.restartListen)
		# self.add_widget(self.reset_btn)
	def addContacts(self, **kwargs):
		array = kwargs["clients"]
		num = kwargs["num"]
		self.headline.text = num
		for ind,txt in enumerate(array):
			print ind,txt
			label = CentreLabel(text=txt, label_index=ind, font_size="15sp")
			self.contacts.append(label)
			self.add_widget(label)
	def removeAllContacts(self):
		for i in self.contacts:
			print i
			self.remove_widget(i)
	# def restartListen(self):
	# 	self.app.listening = False
		

class CRMHookerApp(App):
	def build(self):
		root = ScrollView(size_hint=(None, None), size=Window.size, bar_width=20, scroll_type=["bars"], scroll_y=1)
		self.layout = GUI(cols=1, padding=200, spacing=150, size_hint_y=None, root=root, app=self)
		self.layout.bind(minimum_height=self.layout.setter('height'))
		root.add_widget(self.layout)
		self.last_num = ""
		Clock.schedule_interval(self.update, 1) 
		return root
	def update(self, other):
		query, num = readQuery()
		if num != self.last_num:
			self.last_num = num
			print "hey"
			try:
				print "trying"
				print num
				arr = parseXML(query)
				displayClients(arr, self.layout, num)
			except:
				print "failed"
				# try again
				self.last_num = ""



if __name__ == '__main__' :
	CRMHookerApp().run()

