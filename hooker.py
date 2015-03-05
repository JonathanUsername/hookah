#!/usr/bin/python
# -*- coding: utf-8 -*-


# --------------------------------------- Globals --------------------------------------

import ipdb
import subprocess as sub
import re
from urllib2 import urlopen

# to read API's xml response
from lxml import objectify
import os

from kivy.app import App
# from kivy.animation import Animation
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from threading import Thread
# from kivy.properties import NumericProperty
# from kivy.clock import Clock
# from kivy.graphics import Rectangle, Color, Ellipse, Line
# from kivy.utils import get_color_from_hex

PWD = os.path.dirname(os.path.realpath(__file__))

# --------------------------------------- Config --------------------------------------

# Configure this yourself
my_number = "2422435" 
just_called = []
browser = "/usr/bin/google-chrome"


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
		return stripZero(num[1:])
	else:
		return num

# --------------------------------------- Functions -----------------------------------

def displayClients(clients, GUI, num):
	print "displayClients", clients, GUI, num
	# sub.call(["notify-send", "Call information retrieved!"])
	GUI.removeAllContacts()
	GUI.addContacts(clients=clients, num=num)

def parseXML(query, num, field):
	print "parseXML", query, num, field
	obj = objectify.fromstring(query)
	if obj.Result.Status == 0:
		result = {}
		contacts = obj.Contacts.getchildren()
		for i in contacts:
			contact = i
			ID = getInfo("Id", contact)
			RSSID = getInfo("AccountId", contact)
			result[ID] = { 
				"data": " -- MATCHING CALLER -- \nAccountId:%s\nName: %s %s\nEmail: %s\nZone: %s\nCountry: %s" % (getInfo("AccountId", contact), getInfo("First", contact), getInfo("Last", contact), getInfo("Email", contact), getInfo("Custom16", contact), getInfo("ContactAddressCountry", contact)),
				"RSSID" : RSSID
			}
		return result
	return False

def getInfo(field, obj):
	try: 
		return obj[field]
	except:
		return "** UNKNOWN **"

def queryAPI(num, field):
	print "queryAPI",num,field
	query = urlopen("http://webtrans.reallysimplesystems.com/api/api.v2.asmx/GetContacts?CustomerId=1107&APIPassword=elasticcloud.47&SearchField=%s&SearchValue=%s" % (field, num)).read()
	return parseXML(query, num, field)

def getContact(num, GUI):
	print "getContact", num, GUI
	# RSS phone fields:
	RSS_fields = {
		"phone" : "Custom05",
		"mobile" : "Custom07"
	}
	stripped = stripZero(num)
	mobile = queryAPI(stripped, RSS_fields["mobile"])
	phone = queryAPI(stripped, RSS_fields["phone"])
	if mobile: 
		displayClients(mobile, GUI, num)
	elif phone: 
		displayClients(phone, GUI, num)

def listenForSIP(GUI):
	global just_called
	p = sub.Popen(["cat", "sniff_logs.txt"], stdout=sub.PIPE)
	for line in iter(p.stdout.readline, b''):
		sip_flag = "From: <sip:"
		if sip_flag in line:
			num_start = len(sip_flag)
			num_end = line.index("@sip.gradwell")
			num = line[num_start:num_end]
			if isANumber(num) and num != my_number and num not in just_called:
				print num, just_called
				just_called.append(num)
				print "CALL!"
				GUI.headline.text = "Analysing call from %s" % num
				p.terminate()
				getContact(num, GUI)

class CentreLabel(Button):
	def __init__(self, **kwargs):
		super(CentreLabel, self).__init__(**kwargs)
		self.x = Window.width/2 - self.width/2
		self.font_name=PWD + "/assets/Montserrat-Regular.ttf"
		self.size = (300,300)
		for key, value in kwargs.iteritems():
			if key == "rss_id":
				self.rss_id = value
		self.bind(on_press=self.goToRSS)
	# def on_touch_down(self, touch):
	# 	ipdb.set_trace()
	def goToRSS(self, *args):
		rssURL = "https://system6.reallysimplesystems.com/page.asp?p=account&id=%s" % self.rss_id
		print rssURL
		sub.Popen([browser, rssURL])


class GUI(GridLayout):
	def __init__(self, **kwargs):
		super(GUI, self).__init__(**kwargs)
		self.root = kwargs["root"]
		self.app = kwargs["app"]
		self.contacts = []
		self.buttons = []
		self.headline = Label(text="", font_size="40sp", font_name=PWD + "/assets/Montserrat-Bold.ttf")
		self.add_widget(self.headline)
	def addContacts(self, **kwargs):
		obj = kwargs["clients"]
		num = kwargs["num"]
		self.headline.text = num
		for id in obj:
			account_id = id
			client = obj[id]
			rss_id = client["RSSID"]
			print rss_id
			label = CentreLabel(text=client["data"], font_size="15sp", rss_id=rss_id, size=(200,200))
			self.contacts.append(label)
			self.add_widget(label)
	def removeAllContacts(self):
		for i in self.contacts:
			self.remove_widget(i)
		for i in self.buttons:
			self.remove_widget(i)
		
		

class CRMHookerApp(App):
	def build(self):
		root = ScrollView(size_hint=(None, None), size=Window.size, bar_width=20, scroll_type=["bars"], scroll_y=1)
		self.layout = GUI(cols=1, padding=30, spacing=50, size_hint_y=None, root=root, app=self, row_force_default=True, row_default_height=200)
		self.layout.bind(minimum_height=self.layout.setter('height'))
		root.add_widget(self.layout)
		self.last_num = ""
		# getContact("07714204512", self.layout)
		Clock.schedule_interval(self.update, 1) 
		return root
	def update(self, other):
		listenForSIP(self.layout)
		print "echo"



if __name__ == '__main__' :
	CRMHookerApp().run()

