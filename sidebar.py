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

class FmCreateCommand(sublime_plugin.TextCommand):
	
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
		if os.path.isfile(self.path):
			self.path = os.path.dirname(self.path)


		self.window.show_input_panel('New: ', '', self.create_file, self.log_path_in_status_bar, None)


class FmRenameCommand(sublime_plugin.TextCommand):
	
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

   
class FmMoveCommand(sublime_plugin.TextCommand):
	
	def log_path_in_status_bar(self, path):
		log_path_in_status_bar(path.replace('/', os.path.sep))

	def move_file(self, path):
		try:
			os.makedirs(os.path.dirname(path), True)
		except OSError:
			pass
		os.rename(self.path, path)

		if self.view.file_name() == self.path:
			self.view.close()
			self.window.open_file(path)


	def run(self, edit, paths=[None], *args, **kwargs):
		self.window = self.view.window()
		self.selection = sublime.Selection(self.view.id())
		self.settings = self.view.settings()

		self.path = paths[0] or self.view.file_name()

		view = self.window.show_input_panel('New location: ', self.path, self.move_file, 
			self.log_path_in_status_bar, None)
		view.sel().clear()
		view.sel().add(sublime.Region( len(os.path.dirname(self.path)) + 1, len(self.path) - len(os.path.splitext(self.path)[1]) ))


class FmRevealCommand(sublime_plugin.TextCommand):
	
	def run(self, edit, paths=None, *args, **kwargs):
		self.window = self.view.window()
		self.selection = sublime.Selection(self.view.id())
		self.settings = self.view.settings()

		if paths is None:
			paths = [self.view.file_name()]

		for path in paths:
			self.window.run_command("open_dir", { "dir": os.path.dirname(path), "file": os.path.basename(path) })




class FmDeleteCommand(sublime_plugin.TextCommand):

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



