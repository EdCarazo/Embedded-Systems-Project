import protocol
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, StringProperty, NumericProperty
import os
readPipe = "/tmp/pipe1"
writePipe = "/tmp/pipe2"
try:
	os.mkfifo(readPipe)
	os.mkfifo(writePipe)
except OSError:
	pass
class MainWidget(Widget):
	my_data = ListProperty([])
	selected_value = StringProperty('Select a button')
	def MMS(self, *args):
		if args[1]== "down":
			protocol.protocol = '1'
			print protocol.protocol
	def GOOSE(self, *args):
		if args[1]== "down":
			protocol.protocol = '2'
			print protocol.protocol
	def SV(self, *args):
		if args[1]== "down":
			protocol.protocol = '3'
			print protocol.protocol
				
	def change(self,change):
		self.selected_value = 'Selected: {}'.format(change.text)
	

	def teejotain(self):
		hello='Hello'
		self.ids.start.text = 'Started capture with filter'
		src = self.ids.src.text
		dst = self.ids.dst.text
		message = protocol.protocol+","+src+","+dst
		#print message
		f = open(writePipe, 'w')
		f.write(message)
		f.close()
		self.my_data.append(hello)
	def teejotain2(self):
		self.ids.start.text = 'Start'
class PiSharkApp(App):
		def build(self):
			return MainWidget()

if __name__ == '__main__':
	PiSharkApp().run()


