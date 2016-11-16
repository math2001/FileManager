# -*- encoding: utf-8 -*-
import sublime, sublime_plugin
import webbrowser
import os
try:
    from .send2trash import send2trash
    from .input_for_path import InputForPath
    from . import pathhelper as ph
    from .sublimefunctions import *
except (ImportError, ValueError):
    from send2trash import send2trash
    from input_for_path import InputForPath
    import pathhelper as ph
    from sublimefunctions import *

def makedirs(path, exist_ok=False):
    if exist_ok is False:
        os.makedirs(path)
    else:
        try:
            os.makedirs(path)
        except OSError:
            pass

def log_path_in_status_bar(path):
    path = path.replace('/', os.path.sep)
    if os.path.isdir(os.path.dirname(path) if path[-1] != os.path.sep else path):
        path += ' ✓'
    else:
        path += ' ✗ (path to file does not exists)'
    sm(path)

def quote(s):
    return '"{0}"'.format(s)

def valid(*args):
    args = [arg for arg in args if arg != ''] or []
    path = os.path.normpath(os.path.join(*args))
    if args[-1][-1] in [os.path.sep, '/']: path += args[-1][-1]
    return path

os.path.valid = valid

def get_window():
    return sublime.active_window()

def get_view():
    window = get_window()
    if not window: return
    return window.active_view()

def copy(el):
    return sublime.set_clipboard(el)

def file_get_content(path):
    with open(path, 'r') as fp:
        return fp.read()

def get_template(path, TEMPLATE_FILES, TEMPLATE_FOLDER):
    for item in TEMPLATE_FILES:
        if os.path.splitext(item)[0] == 'template' and os.path.splitext(item)[1] == os.path.splitext(path)[1]:
            return file_get_content(os.path.join(TEMPLATE_FOLDER, item))
    return ''

def isdigit(string):
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True

def yes_no_cancel_panel(message, yes, no, cancel, yes_text='Yes', no_text='No', cancel_text='Cancel', **kwargs):
    loc = locals()
    if isinstance(message, list):
        message.append('Do not select this item')
    else:
        message = [message, 'Do not select this item']
    items = [message, yes_text, no_text, cancel_text]

    def get_max(item):
        return len(item)

    maxi = len(max(items, key=get_max))
    for i, item in enumerate(items):
        while len(items[i]) < maxi:
            items[i].append('')


    def on_done(index):
        if index in [-1, 3]:
            return cancel(*kwargs.get('args', []), **kwargs.get('kwargs', {}))
        elif index == 1:
            return yes(*kwargs.get('args', []), **kwargs.get('kwargs', {}))
        elif index == 2:
            return no(*kwargs.get('args', []), **kwargs.get('kwargs', {}))
        elif index == 0:
            return yes_no_cancel_panel(**loc)
    window = get_window()
    window.show_quick_panel(items, on_done)

class StdClass: pass

if not hasattr(get_view(), 'close'):
    def close_file_poyfill(view):
        window = get_window()
        window.focus_view(view)
        window.run_command('close')

    # get_view().__class__.close = lambda x: sublime.error_message('Sublime text 2 does\' not support closing from API. Please switch to Sublime Text 3')
    sublime.View.close = close_file_poyfill

class FmEditReplace(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        kwargs.get('view', self.view).replace(edit, sublime.Region(*kwargs['region']), kwargs['text'])

class FmCreateCommand(sublime_plugin.ApplicationCommand):

    def run(self, paths=None):
        self.window = sublime.active_window()
        self.settings = sublime.load_settings('FileManager.sublime-settings')
        self.index_folder_separator = self.settings.get('index_folder_separator')
        self.default_index_folder = self.settings.get('default_index_folder')

        self.TEMPLATE_FOLDER = os.path.join(sublime.packages_path(), 'User', '.FileManager')

        if not os.path.exists(self.TEMPLATE_FOLDER):
            makedirs(self.TEMPLATE_FOLDER)

        self.TEMPLATE_FILES = os.listdir(self.TEMPLATE_FOLDER)

        self.folders = self.window.folders()

        self.view = get_view()

        self.know_where_to_create_from = paths is not None

        if paths is not None:
            # creating from the sidebar
            create_from = paths[0]
            # you can right-click on a file, and run `New...`
            if os.path.isfile(create_from):
                create_from = os.path.dirname(create_from)
        elif self.folders:
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
                                  log_in_status_bar=self.settings.get('log_in_status_bar'),
                                  log_template='Creating at {0}',
                                  enable_browser=True)

    def on_done(self, abspath, input_path):
        input_path = ph.user_friendly(input_path)
        if not os.path.isfile(abspath):
            makedirs(os.path.dirname(abspath), exist_ok=True)
            with open(abspath, 'w') as fp:
                fp.write(get_template(abspath, self.TEMPLATE_FILES, self.TEMPLATE_FOLDER))
        if input_path[-1] == '/':
            return makedirs(abspath, exist_ok=True)
        view = self.window.open_file(abspath)

    def on_change(self, input_path, path_to_create_choosed_from_browsing):
        if path_to_create_choosed_from_browsing:
            # The user has browsed, we let InputForPath select the path
            return
        if self.know_where_to_create_from:
            return
        elif self.folders:
            mess = input_path.split(self.index_folder_separator, 1)
            if len(mess) == 1:
                index = self.default_index_folder
            elif isdigit(mess[0]):
                index = int(mess[0])
            return self.folders[index], mess[-1]
        return '~', input_path

class FmRenameCommand(sublime_plugin.ApplicationCommand):

    def log_path_in_status_bar(self, name):
        log_path_in_status_bar(os.path.join(self.dirname, name.replace('/', os.path.sep)))

    def rename_file(self, filename):
        path = os.path.join(self.dirname, filename)
        if os.path.isfile(path):
            return em('This file {0} already exists.'.format(path))

        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            makedirs(dirname)
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

    def run(self, paths=None):
        self.settings = sublime.load_settings('FileManager.sublime-settings')
        self.window = get_window()
        self.view = self.window.active_view()

        if paths is not None:
            self.origins = paths
        else:
            self.origins = [self.view.file_name()]

        if len(self.origins) > 1:
            initial_text = ph.commonpath(self.origins)
        else:
            initial_text = os.path.dirname(self.origins[0])
        initial_text = ph.user_friendly(initial_text) + '/'

        ipt = InputForPath(caption='Move to',
                           initial_text=initial_text,
                           on_done=self.move,
                           on_change=None,
                           on_cancel=None,
                           create_from='',
                           with_files=self.settings.get('complete_with_files_too'),
                           pick_first=self.settings.get('pick_first'),
                           case_sensitive=self.settings.get('case_sensitive'),
                           log_in_status_bar=self.settings.get('log_in_status_bar'),
                           log_template='Moving at {0}',
                           enable_browser=False)

    def move(self, path, input_path):
        makedirs(path, exist_ok=True)
        for origin in self.origins:
            view = self.window.find_open_file(origin)
            new_name = os.path.join(path, os.path.basename(origin))
            if view:
                view.close()
            try:
                os.rename(origin, new_name)
            except Exception as e:
                em(e)
            if view:
                self.window.open_file(new_name)

class FmDuplicate(sublime_plugin.ApplicationCommand):

    def run(self, paths=None):

        self.settings = sublime.load_settings('FileManager.sublime-settings')
        self.window = get_window()

        if paths is None:
            self.origin = self.window.active_view().file_name()
        else:
            self.origin = paths[0]

        if os.path.isdir(self.origin):
            return em('Duplicating folders is not implemented yet.')

        initial_path = ph.user_friendly(self.origin)

        self.input = InputForPath(caption='Duplicate to: ',
                                  initial_text=initial_path,
                                  on_done=self.duplicate,
                                  on_change=None,
                                  on_cancel=None,
                                  create_from='',
                                  with_files=self.settings.get('complete_with_files_too'),
                                  pick_first=self.settings.get('pick_first'),
                                  case_sensitive=self.settings.get('case_sensitive'),
                                  log_in_status_bar=self.settings.get('log_in_status_bar'),
                                  log_template='Duplicating at {0}',
                                  enable_browser=True)

        head = len(os.path.dirname(initial_path)) + 1
        filename = len(os.path.splitext(os.path.basename(initial_path))[0])
        self.input.input.view.selection = self.input.input.view.sel()
        self.input.input.view.selection.clear()
        self.input.input.view.selection.add(sublime.Region(head, head + filename))

    def duplicate(self, path, input_path):
        user_friendly_path = ph.user_friendly(path)
        if os.path.exists(path):
            def overwrite():
                try:
                    send2trash(path)
                except OSError as e:
                    em('Unable to send to trash: ', e)

                with open(path, 'w') as fp:
                    with open(self.origin, 'r') as fpread:
                        fp.write(fpread.read())
                self.window.open_file(path)

            def open_file():
                return self.window.open_file(path)

            def cancel():
                pass

            yes_no_cancel_panel(message=['This file already exists. Overwrite?', user_friendly_path],
                                yes=overwrite,
                                no=open_file,
                                cancel=cancel,
                                yes_text=['Yes. Overwrite', user_friendly_path, 'will be sent to the trash, and then written'],
                                no_text=['Just open the target file', user_friendly_path],
                                cancel_text=["No, don't do anything"])
            return

        with open(path, 'w') as fp:
            with open(self.origin, 'r') as fpread:
                fp.write(fpread.read())
        self.window.open_file(path)

    def is_enabled(self, paths=None):

        return paths is None or len(paths) == 1

    def is_visible(self, *args, **kwargs):
        return self.is_enabled(*args, **kwargs)

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

    def delete(self, index):
        if index == 0:
            for path in self.paths:
                view = self.window.find_open_file(path)
                if view is not None:
                    view.close()
                try:
                    send2trash(path)
                except OSError as e:
                    return em('Unable to send to trash: ', e)

    def run(self, paths=None, *args, **kwargs):
        self.window = get_window()
        self.view = get_view()

        self.paths = paths or [self.view.file_name()]
        self.window.show_quick_panel([
            ['Send item {0} to trash'.format(('s' if len(self.paths) > 1 else ''))] + self.paths,
            'Cancel'
        ], self.delete)

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

        return em('this command is shit for now')

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
