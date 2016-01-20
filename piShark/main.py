from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, StringProperty
class MainWidget(Widget):
	my_data = ListProperty([])
	selected_value = StringProperty('Select a button')
	def change(self,change):
		self.selected_value = 'Selected: {}'.format(change.text)
class PiSharkApp(App):
		def build(self):
			return MainWidget()

if __name__ == '__main__':
	PiSharkApp().run()
