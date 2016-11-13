import sublime, sublime_plugin
import webbrowser
import os
from .send2trash import send2trash
from .input_for_path import InputForPath

from . import pathhelper as ph

def md(*t, **kwargs): sublime.message_dialog(kwargs.get('sep', '\n').join([str(el) for el in t]))

def sm(*t, **kwargs): sublime.status_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def em(*t, **kwargs): sublime.error_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def log_path_in_status_bar(path):
    path = path.replace('/', os.path.sep)
    if os.path.isdir(os.path.dirname(path) if path[-1] != os.path.sep else path):
        path += ' ✓'
    else:
        path += ' ✗ (path to file does not exists)'
    sm(path)

def quote(s):
    return '"{}"'.format(s)

def valid(*args):
    args = [arg for arg in args if arg != ''] or []
    path = os.path.normpath(os.path.join(*args))
    if args[-1][-1] in [os.path.sep, '/']: path += args[-1][-1]
    return path

os.path.valid = valid

def get_window():
    return sublime.active_window()

def get_view():
    return get_window().active_view()

def copy(el):
    return sublime.set_clipboard(el)

def valid_path(path):
    path = path.split(os.path.sep)
    for i, bit in enumerate(path):
        if not bit:
            continue
        path[i] = bit + (os.path.sep if bit[-1] == ':' else '')
    return os.path.join(*path)

def user_friendly_path(path):
    path = computer_friendly_path(path)
    return valid_path(path).replace(os.path.expanduser('~'), '~').replace(os.path.sep, '/')

def computer_friendly_path(path):
    path = path.replace('~', os.path.expanduser('~'))
    path = path.replace('/', os.path.sep)
    path = valid_path(path)
    return path

def get_place_to_complete(text):
    for i, char in enumerate(text):
        if char == '\t':
            return text[:i], text[i+1:]
    return None, None

def get_autocomplete_path(abspath:str, withfiles:bool, pick_first:str) -> str:
    """ Takes a computer friendly path """
    abspath = computer_friendly_path(abspath)
    if abspath.endswith(os.path.sep):
        return ''
    prefix = abspath.split(os.path.sep)[-1]
    abspath = os.path.dirname(abspath)
    items = os.listdir(abspath)
    posibilities = []
    for item in items:
        if item.startswith(prefix):
            posibilities.append([item[len(prefix):], os.path.isdir(os.path.join(abspath, item))])
    backup = ''
    for completion, isdir in posibilities:
        if withfiles:
            if pick_first == 'files':
                if not isdir: # is file
                    return completion
                else:
                    backup = completion + '/'
            elif pick_first == 'folder':
                if isdir:
                    return completion + '/'
                else:
                    backup = completion
            else:
                return completion + ('/' if isdir else '')
        else:
            if isdir:
                return completion + '/'


    return backup

def multisplit(string:str, separators:iter) -> list:
    def remove_deep_lists(list_of_list):
        list_of_elements = []
        for elements in list_of_list:
            for element in elements:
                list_of_elements.append(element)

        return list_of_elements

    pieces = string.split(separators[0])
    for separator in separators[1:]:
        for i, piece in enumerate(pieces):
            pieces[i] = piece.split(separator)
        pieces = remove_deep_lists(pieces)
    return pieces

def isdigit(string):
    try: int(string);
    except ValueError: return False;
    else: return True

def struntil(string, looked_for_char):
    for i, char in enumerate(string):
        if char == looked_for_char:
            return i

class StdClass: pass

class FmEditReplace(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        kwargs.get('view', self.view).replace(edit, sublime.Region(*kwargs['region']), kwargs['text'])

class FmCreateCommand(sublime_plugin.ApplicationCommand):


    def run(self, paths=None):

        self.window = sublime.active_window()
        self.settings = sublime.load_settings('FileManager.sublime-settings')
        self.index_folder_separator = self.settings.get('index_folder_separator')
        self.default_index_folder = self.settings.get('default_index_folder')

        self.project_data = self.window.project_data()

        self.view = get_view()

        self.know_where_to_create_from = paths is not None

        if paths is not None:
            # creating from the sidebar
            create_from = paths[0]
            # you can right-click on a file, and run `New...`
            if os.path.isfile(create_from):
                create_from = os.path.dirname(create_from)
        elif self.project_data:
             # it is going to be interactive, so it'll be
             # understood from the input itself
            create_from = None
        elif self.view.file_name() is not None:
            create_from = os.path.dirname(self.view.file_name())
            self.know_where_to_create_from = True
        else:
            # from home
            create_from = '~'

        self.input = InputForPath(caption='New: ',
                                  initial_text='',
                                  on_done=self.on_done,
                                  on_change=self.on_change,
                                  on_cancel=None,
                                  create_from=create_from,
                                  with_files=self.settings.get('complete_with_files_too'),
                                  pick_first=self.settings.get('pick_first'),
                                  case_sensitive=self.settings.get('case_sensitive'),
                                  log_in_status_bar=self.settings.get('log_in_status_bar'))

    def on_done(self, abspath, input_path):
        input_path = ph.user_friendly(input_path)
        if not os.path.isfile(abspath):
            os.makedirs(os.path.dirname(abspath), exist_ok=True)
            open(abspath, 'w').close()
        if input_path[-1] == '/':
            return os.makedirs(abspath, exist_ok=True)
        return self.window.open_file(abspath)

    def on_change(self, input_path, path_to_create_choosed_from_browsing):
        if path_to_create_choosed_from_browsing:
            # The user has browsed, we let InputForPath select the path
            return
        if self.know_where_to_create_from:
            return
        elif self.project_data:
            mess = input_path.split(self.index_folder_separator, 1)
            if len(mess) == 1:
                index = self.default_index_folder
            elif isdigit(mess[0]):
                index = int(mess[0])
            return self.project_data['folders'][index]['path'], mess[-1]
        return '~', input_path


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

        view = self.window.show_input_panel('New location: ', self.path.replace(os.path.sep, '/'), self.move_file,
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
            if os.path.isdir(path):
                self.window.run_command('open_dir', { 'dir': path })
            else:
                self.azerwindow.run_command("open_dir", { "dir": os.path.dirname(path), "file": os.path.basename(path) })

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

class FmCopyCommand(sublime_plugin.ApplicationCommand):

    def run(self, paths=[None], *args, **kwargs):

        self.view = get_view()
        self.window = get_window()

        path = paths[0] or self.view.file_name()

        _type = kwargs.get('type', False)
        if not _type:
            return em('No type: cannot copy.')

        if _type == 'name':
            copy(os.path.basename(path))
        elif _type == 'absolute-path':
            copy(path if not ' ' in path else '"' + path + '"')
        elif _type == 'relative-path':
            project_data = self.window.project_data()
            if project_data is None:
                return em('No (explicit) project is open. Impossible to copy the relative path from it.')
            raise_error = True
            for group in project_data['folders']:
                if group['path'] in path:
                    copy(path.replace(group['path'], '').replace(os.path.sep, '/'))
                    raise_error = False
            if raise_error:
                return em('This file is not in your project. Impossible to copy the relative path from it.')
        elif _type == 'relative-from-current-view':
            if paths[0] is None:
                return em('Needs to be called from the sidebar')
            copy(os.path.relpath(paths[0], self.view.file_name()))
