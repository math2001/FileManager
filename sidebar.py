import sublime, sublime_plugin
import os
from Edit import Edit as Edit

def md(*t, **kwargs): sublime.message_dialog(kwargs.get('sep', ' ').join([str(el) for el in t]))

def sm(*t, **kwargs): sublime.status_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def em(*t, **kwargs): sublime.error_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def log_path_in_status_bar(self, path):
	msg = path
	if os.path.isdir(os.path.dirname(path)):
		path += ' ✓'
	else:
		path += ' ✗'

class FmCreateFileCommand(sublime_plugin.TextCommand):
	
	def log_path_in_status_bar(self, name):
		log_path_in_status_bar(os.path.join(self.path, name))

	def create_file(self, name):
		path = os.path.join(self.path, name)
		

	def run(self, edit, paths=[None], *args, **kwargs):
		self.window = self.view.window()
		self.selection = sublime.Selection(self.view.id())
		self.settings = self.view.settings()

		self.paths = paths[0]

		self.window.show_input_panel('New file name: ', '', self.create_file, self.log_path_in_status_bar)

		

