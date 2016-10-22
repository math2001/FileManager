import sublime, sublime_plugin
import webbrowser
import os
from .send2trash import send2trash

def md(*t, **kwargs): sublime.message_dialog(kwargs.get('sep', '\n').join([str(el) for el in t]))

def sm(*t, **kwargs): sublime.status_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def em(*t, **kwargs): sublime.error_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def log_path_in_status_bar(path):
	path = path.replace('/', os.path.sep)
	print(os.path.dirname(path) if path[-1] != os.path.sep else path)
	if os.path.isdir(os.path.dirname(path) if path[-1] != os.path.sep else path):
		path += ' ✓'
	else:
		path += ' ✗'
	sm(path)

def quote(s):
	return '"{}"'.format(s)

def valid(*args):
	return os.path.normpath(os.path.join(*args)).replace('/', os.path.sep) + \
	(os.path.sep if args[-1][-1] in [os.path.sep, '/'] else '')

os.path.valid = valid

def get_window():
	return sublime.active_window()

def get_view():
	return get_window().active_view()

class FmCreateCommand(sublime_plugin.ApplicationCommand):
	
	def log_path_in_status_bar(self, name):
		log_path_in_status_bar(self.__get_path(name))

	def create_file(self, name):
		name = name.replace('/', os.path.sep)
		# path = os.path.join(self.path, name)
		path = self.__get_path(name)
		if os.path.isfile(path):
			return self.window.open_file(path)
		if not os.path.isdir(os.path.dirname(path)):
			os.makedirs(os.path.dirname(path))
		if name[-1] in ('/', os.path.sep):
			os.makedirs(path)
		else:
			open(path, 'w').close()
			self.window.open_file(path)

	def __get_path(self, path):
		if self.from_project:
			path = path.split(' ')
			try:
				nb = int(path[0])
			except ValueError:
				base = self.project_data["folders"][0]['path']
				path = ' '.join(path)
			else:
				base = self.project_data["folders"][nb]['path']
				path = ' '.join(path[1:])
				
			return os.path.valid(base, path)
		else:
			return os.path.valid(self.path,path)
			# return md(base, path); os.path.valid(base, path)


	def run(self, paths=[None], *args, **kwargs):

		# paths[0] is not None when it's called from the sidebar
		self.path = paths[0]
		self.from_project = False

		self.window = get_window()

		if self.path is None:
			self.project_data = self.window.project_data()
			if self.project_data:
				self.path = self.project_data["folders"][0]['path']
				self.from_project = True
			else:
				self.path = os.path.dirname(self.view.file_name())


		if os.path.isfile(self.path):
			self.path = os.path.dirname(self.path)


		self.window.show_input_panel('New: ', '', self.create_file, self.log_path_in_status_bar, None)

	def is_enabled(self, paths=None):
		return paths is None or len(paths) == 1

class FmRenameCommand(sublime_plugin.ApplicationCommand):
	
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


	def run(self, paths=[None], *args, **kwargs):
		self.window = get_window()
		self.view = get_view()

		self.reopen = True
		self.path = paths[0] or self.view.file_name()

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

	def is_enabled(self, paths=None):
		return paths is None or len(paths) == 1
 
class FmMoveCommand(sublime_plugin.ApplicationCommand):
	
	def log_path_in_status_bar(self, path):
		log_path_in_status_bar(path.replace('/', os.path.sep))

	def move_file(self, path):
		try:
			os.makedirs(os.path.dirname(path))
		except OSError:
			pass
		os.rename(self.path, path)

		if self.view.file_name() == self.path:
			self.view.close()
			self.window.open_file(path)


	def run(self, paths=[None], *args, **kwargs):
		self.window = get_window()
		self.view = get_view()

		self.path = paths[0] or self.view.file_name()

		view = self.window.show_input_panel('New location: ', self.path, self.move_file, 
			self.log_path_in_status_bar, None)
		view.sel().clear()
		# view.sel().add(sublime.Region(0, 5))
		view.sel().add(sublime.Region( len(os.path.dirname(self.path)) + 1, len(self.path) - len(os.path.splitext(self.path)[1]) ))

	def is_enabled(self, paths=None):
		return paths is None or len(paths) == 1

class FmDuplicateCommand(sublime_plugin.ApplicationCommand):
	
	def log_path_in_status_bar(self, path):
		log_path_in_status_bar(path.replace('/', os.path.sep))

	def duplicate(self, path):
		if os.path.isfile(path):
			return em('This file alredy exists!')
		try:
			os.makedirs(os.path.dirname(path))
		except OSError:
			pass
		with open(self.path, 'r') as fp:
			content = fp.read()
		with open(path, 'w') as fp:
			fp.write(content)

		self.window.open_file(path)


	def run(self, paths=[None], *args, **kwargs):
		self.window = get_window()
		self.view = get_view()

		self.path = paths[0] or self.view.file_name()

		view = self.window.show_input_panel('Duplicate to: ', self.path, self.duplicate, 
			self.log_path_in_status_bar, None)
		view.sel().clear()
		view.sel().add(sublime.Region( len(os.path.dirname(self.path)) + 1, len(self.path) - len(os.path.splitext(self.path)[1]) ))

	def is_enabled(self, paths=None):
		return paths is None or len(paths) == 1

class FmRevealCommand(sublime_plugin.ApplicationCommand):
	
	def run(self, paths=None, *args, **kwargs):
		self.window = get_window()
		self.view = get_view()

		if paths is None:
			paths = [self.view.file_name()]

		for path in paths:
			self.window.run_command("open_dir", { "dir": os.path.dirname(path), "file": os.path.basename(path) })

class FmDeleteCommand(sublime_plugin.ApplicationCommand):

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


	def run(self, paths=None, *args, **kwargs):
		self.window = get_window()
		self.view = get_view()

		self.paths = paths or [self.view.file_name()]
		self.window.show_quick_panel([
			['Send item{} to trash'.format(('s' if len(self.paths) > 1 else ''))] + self.paths,
			'Cancel'
		], self.delete_file)

class FmOpenInBrowserCommand(sublime_plugin.ApplicationCommand):

	def run(self, paths=None, *args, **kwargs):
		self.window = get_window()
		self.view = get_view()

		paths = paths or [self.view.file_name()]
		for path in paths:
			path = path.replace(os.path.sep, '/')
			if 'C:/wamp/www' in path:
				path = 'http://' + path.replace('C:/wamp/www', self.view.settings().get('localhost', 'localhost'))
			else:
				path = 'file:///' + path
			
			webbrowser.open_new(path)


