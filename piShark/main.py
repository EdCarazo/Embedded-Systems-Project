from kivy.app import App 
from kivy.clock import Clock
from kivy.uix.widget import Widget 
from kivy.properties import ListProperty, StringProperty, NumericProperty
protocol = '0'
stopbit = '0'
import os
import posix_ipc

writePipe = "/tmp/pipe"
messageQueue = "/msg_que"
mq = posix_ipc.MessageQueue(messageQueue)

try:
	os.mkfifo(writePipe)
except OSError:
	pass

class MainWidget(Widget):
	my_data = ListProperty([])
	selected_value = StringProperty('Select a packet')
	def change(self,change):
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

	def receive(self, *args):
		f, _ = mq.receive()
		self.my_data.append(f)
		
	def start(self):
		self.ids.start.text = 'Started capture with filter'
		src = self.ids.src.text
		dst = self.ids.dst.text
		global protocol
		message=protocol+","+src+","+dst
		print message
		Clock.schedule_interval(self.receive, 1/1.)		
	def stop(self):
		global stopbit
		stopbit = '1'
		self.ids.start.text = 'Start'
#		mq.close()
		Clock.unschedule(self.receive)
class PiSharkApp(App):
		def build(self):
			return MainWidget()

if __name__ == '__main__':
	PiSharkApp().run()


