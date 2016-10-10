import sublime, sublime_plugin
import os
from .send2trash import send2trash

def md(*t, **kwargs): sublime.message_dialog(kwargs.get('sep', '\n').join([str(el) for el in t]))

def sm(*t, **kwargs): sublime.status_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def em(*t, **kwargs): sublime.error_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def log_path_in_status_bar(path):
	if os.path.isdir(os.path.dirname(path)):
		path += ' ✓'
	else:
		path += ' ✗'
	sm(path)

def quote(s):
	return '"{}"'.format(s)

class FmCreateFileCommand(sublime_plugin.TextCommand):
	
	def log_path_in_status_bar(self, name):
		log_path_in_status_bar(os.path.join(self.path, name.replace('/', os.path.sep)))

	def create_file(self, name):
		name = name.replace('/', os.path.sep)
		path = os.path.join(self.path, name)
		if os.path.isfile(path):
			return self.window.open_file(path)
		if not os.path.isdir(os.path.dirname(path)):
			os.makedirs(os.path.dirname(path))
		open(path, 'w').close()
		self.window.open_file(path)


	def run(self, edit, paths=[None], *args, **kwargs):
		self.window = self.view.window()
		self.selection = sublime.Selection(self.view.id())
		self.settings = self.view.settings()

		self.path = paths[0]

		self.window.show_input_panel('New file name: ', '', self.create_file, self.log_path_in_status_bar, None)



class FmRenameFileCommand(sublime_plugin.TextCommand):
	
	def log_path_in_status_bar(self, name):
		log_path_in_status_bar(os.path.join(self.dirname, name.replace('/', os.path.sep)))

	def rename_file(self, filename):
		path = os.path.join(self.dirname, filename)
		if os.path.isfile(path):
			return em('This file {} alredy exists.'.format(path))

		dirname = os.path.dirname(path)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
		os.rename(self.path, path)

		if self.reopen:
			self.view.close()
			self.window.open_file(path)


	def run(self, edit, paths=[None], *args, **kwargs):
		self.window = self.view.window()
		self.selection = sublime.Selection(self.view.id())
		self.settings = self.view.settings()

		self.reopen = True
		self.path = paths[0]

		if os.path.isdir(self.path):
			self.reopen = False

		if self.path is not None:
			basename = os.path.basename(self.path)
			self.dirname = os.path.dirname(self.path)
		else:
			self.path = self.view.file_name()
			self.dirname = os.path.dirname(self.path)
			self.reopen = True

			
		view = self.window.show_input_panel('New name: ', basename, self.rename_file, self.log_path_in_status_bar, None)
		view.sel().clear()
		view.sel().add(sublime.Region(0, len(os.path.splitext(basename)[0])))



class FmDeleteFileCommand(sublime_plugin.TextCommand):

	def delete_file(self, index):
		if index == 0:
			for path in self.paths:
				view = self.window.find_open_file(path)
				if view is not None:
					view.close()
				try:
					send2trash(path)
				except OSError as e:
					return em('Unable to send to trash: ', e.msg)


	def run(self, edit, paths=None, *args, **kwargs):
		self.window = self.view.window()
		self.paths = paths or [self.view.file_name()]
		self.window.show_quick_panel([
			['Send item{} to trash'.format(('s' if len(self.paths) > 1 else ''))] + self.paths,
			'Cancel'
		], self.delete_file)