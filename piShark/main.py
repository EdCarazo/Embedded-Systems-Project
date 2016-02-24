from kivy.uix.textinput import TextInput 
from kivy.app import App 
from kivy.clock import Clock 
from kivy.lang import Builder 
from kivy.uix.widget import Widget 
from kivy.properties import ListProperty, StringProperty, NumericProperty 
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition 
from kivy.storage.jsonstore import JsonStore 
import os 
import posix_ipc
#Global functions
count = 0 
protocol = '0' 
cls = '0' 
log = JsonStore('log.json') 

class ScreenManagement(ScreenManager):
	pass 

writePipe = "/tmp/pipe" 
messageQueue = "/msg_que" 
mq = posix_ipc.MessageQueue(messageQueue) 

try:
	os.mkfifo(writePipe) 
except OSError:
	pass 
class TriggeredCapture(Screen):
	my_data1 = ListProperty([])
	my_data2 = ListProperty([])
	my_data3 = ListProperty([])
	my_data4 = ListProperty([])
	my_data5 = ListProperty([])
	my_data6 = ListProperty([])
	my_data7 = ListProperty([])
	def change2(self):
		self.selected_value = 'Selected: {}'.format(change.text)
		
	def protocol1(self):
		global protocol
		protocol = '1'
		
	def protocol2(self):
		global protocol
		protocol = '2'
		
	def protocol3(self):
		global protocol
		protocol = '3'
		
	def protocol4(self):
		global protocol
		protocol = '4'
		
	def receive(self, *args):
		global count
		try:
			#if message is recieved the messages is split into an array with "," as the 
			#separator
			f, _ = mq.receive(5)
			f_string = str(f)
			f_list = f_string.split(',')
			#Write the message into a json file with a running number
			count +=1
			log.put(count,nro=f_list[0], protocol=f_list[1], src=f_list[2],dst=f_list[3],ttl=f_list[4],srcPort=f_list[5],dstPort=f_list[6])
			
			self.ids.noti.text = 'Running'
			self.my_data1.append(f_list[0])
			self.my_data2.append(f_list[1])
			self.my_data3.append(f_list[2])
			self.my_data4.append(f_list[3])
			self.my_data5.append(f_list[4])
			self.my_data6.append(f_list[5])
			self.my_data7.append(f_list[6])
			self.ids.stop.disabled = False
		except:
			self.ids.noti.text = 'Nothing received Click Stop to Clear'
			
			pass
	def send_parameters(self, params):
		p = open(writePipe, 'w')
		params_send = str(params)
		p.write(params_send)
		p.close()
	def start(self):
		global cls
		global count
		global log
		
		self.ids.mms.disabled = True
		self.ids.sv.disabled = True
		self.ids.ts.disabled = True
		self.ids.amount.disabled = True
		self.ids.track.disabled = True
		self.ids.src.disabled = True
		self.ids.dst.disabled = True
		self.ids.goose.disabled = True
		
		#Clear the log.json file to make room for another capture
		for key in log:
			log.delete(key)
			print "deleted"
			
		cls = '0'
#		self.ids.start.text = 'Started capture with filter'
		self.ids.noti.text = 'Starting capture'
		src = self.ids.src.text
		dst = self.ids.dst.text
		amount=self.ids.amount.text
		
#		if self.ids.amount.text=="":
#			amount="0"
			
		global protocol
		params = protocol+","+src+","+dst+","+amount
#		self.send_parameters(params)
		
		print params
		self.ids.start.disabled = True
		self.ids.stop.disabled = False
		if self.ids.amount.text==""or protocol == "":
			self.ids.noti.text = 'No message amount or protocol set'
		elif self.ids.amount.text!="":
			Clock.schedule_interval(self.receive, 1/1000.)
			self.send_parameters(params)
	def stop(self):
		global cls
		global count
#		if cls == '0':
#			cls = '1' self.ids.noti.text = 'Click Start to Continue or Stop to Clear' 
#		self.ids.start.text = 'Start' Clock.unschedule(self.receive) elif cls == '1':
		if cls == '0':
			Clock.unschedule(self.receive)
			self.ids.noti.text = 'Paused'
			self.ids.start.disabled = False
			self.ids.mms.disabled = False
			self.ids.sv.disabled = False
			self.ids.ts.disabled = False
			self.ids.amount.disabled = False
			self.ids.track.disabled = False
			self.ids.src.disabled = False
			self.ids.dst.disabled = False
			self.ids.goose.disabled = False
			cls = '1'
		elif cls == '1':
			Clock.unschedule(self.receive)
			del self.my_data1[:]
			del self.my_data2[:]
			del self.my_data3[:]
			del self.my_data4[:]
			del self.my_data5[:]
			del self.my_data6[:]
			del self.my_data7[:]
			self.ids.noti.text = 'Cleared'
			self.ids.start.disabled = False
			self.ids.mms.disabled = False
			self.ids.sv.disabled = False
			self.ids.ts.disabled = False
			self.ids.amount.disabled = False
			self.ids.track.disabled = False
			self.ids.src.disabled = False
			self.ids.dst.disabled = False
			self.ids.goose.disabled = False
			cls = '0' 
class TrackingLog(Screen):
	listjson = JsonStore('log.json')
	
	def readJson(self):
		self.listjson = JsonStore('log.json')
		return self.listjson
#Add the layout file pishark.kv into the program
presentation = Builder.load_file("pishark.kv")
					
class PiSharkApp(App):
		def build(self):
			return presentation 
if __name__ == '__main__':
	PiSharkApp().run()
