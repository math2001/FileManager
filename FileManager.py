# -*- encoding: utf-8 -*-
import sublime
import sublime_plugin
import os
import subprocess
import shutil
import re

import imp
import sys


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

# auto reload sub files - for dev

BASE_NAME = os.path.dirname(__file__)
PYTHON_NAME = os.path.basename(BASE_NAME)

TEMPLATE_FOLDER = os.path.join(sublime.packages_path(), 'User', '.FileManager')

FIND_PATH = re.compile(r'[^\^<>\?\"\'\n\t]+')

def isSt3():
    return int(sublime.version()) > 3000

def _reload(file):
    filename, ext = os.path.splitext(file)
    if ext != '.py':
        raise ValueError('The file must be a python file! (with a .py ext). {0}'.format(file))

    module = sys.modules.get('.'.join([PYTHON_NAME, filename]))
    if module:
        imp.reload(module)

class FmDevListener(sublime_plugin.EventListener):

    def on_post_save(self, view):
        if BASE_NAME in view.file_name() and os.path.splitext(view.file_name())[1] == '.py':
            # reload the file
            _reload(os.path.basename(view.file_name()))
            # reload the main file (this one)
            file = __file__
            if file.endswith('.pyc'):
                file = file[:-1]
            _reload(os.path.basename(file))

# Now comes the funny part!

def remove_duplicate(arr):
    new = []
    for el in arr:
        if not el in new:
            new.append(el)
    return new

def get_settings():
    return sublime.load_settings('FileManager.sublime-settings')

def refresh_sidebar(settings, window):
    if settings.get('explicitly_refresh_sidebar') is True:
        window.run_command('refresh_folder_list')

def makedirs(path, exist_ok=False):
    if exist_ok is False:
        os.makedirs(path)
    else:
        try:
            os.makedirs(path)
        except OSError:
            pass

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

def get_template(created_file):
    """Return the right template for the create file"""
    template_files = os.listdir(TEMPLATE_FOLDER)
    for item in template_files:
        if os.path.splitext(item)[0] == 'template' and os.path.splitext(item)[1] == os.path.splitext(created_file)[1]:
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
        if index in [-1, 3] and cancel:
            return cancel(*kwargs.get('args', []), **kwargs.get('kwargs', {}))
        elif index == 1 and yes:
            return yes(*kwargs.get('args', []), **kwargs.get('kwargs', {}))
        elif index == 2 and no:
            return no(*kwargs.get('args', []), **kwargs.get('kwargs', {}))
        elif index == 0:
            return yes_no_cancel_panel(**loc)
    window = get_window()
    window.show_quick_panel(items, on_done, 0, 1)

def close_view(window, view_to_close):
    if isSt3():
        view_to_close.close()
        return
    window.focus_view(view_to_close)
    window.run_command('close')

class StdClass:
    pass

def to_snake_case(camelCaseString):
    snake = ''
    for char in camelCaseString:
        if char.isupper():
            if snake == '':
                snake += char.lower()
            else:
                snake += '_' + char.lower()
        else:
            snake += char
    return snake


class AppCommand(sublime_plugin.ApplicationCommand):

    def is_visible(self, *args, **kwargs):
        settings = get_settings()
        return (settings.get('show_' +
                             to_snake_case(self.__class__.__name__.replace('Fm', ''))) and
                (self.is_enabled(*args, **kwargs) or not settings.get('menu_without_dirstraction')))

if not hasattr(get_view(), 'close'):
    def close_file_poyfill(view):
        window = get_window()
        window.focus_view(view)
        window.run_command('close')

    sublime.View.close = close_file_poyfill

class FmEditReplace(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        kwargs.get('view', self.view).replace(edit, sublime.Region(*kwargs['region']), kwargs['text'])


# --- Commands Affecting File ---

class FmCreateCommand(AppCommand):

    def run(self, paths=None, initial_text=''):
        self.settings = get_settings()
        self.window = sublime.active_window()
        self.index_folder_separator = self.settings.get('index_folder_separator')
        self.default_index = self.settings.get('default_index')

        self.TEMPLATE_FOLDER = os.path.join(sublime.packages_path(), 'User', '.FileManager')

        if not os.path.exists(self.TEMPLATE_FOLDER):
            makedirs(self.TEMPLATE_FOLDER)

        self.TEMPLATE_FILES = os.listdir(self.TEMPLATE_FOLDER)

        self.folders = self.window.folders()

        self.view = get_view()

        self.know_where_to_create_from = paths is not None

        if paths is not None:
            # creating from the sidebar
            create_from = paths[0].replace('${packages}', sublime.packages_path())
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
                                  initial_text=initial_text,
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
        if input_path[-1] == '/':
            return makedirs(abspath, exist_ok=True)
        if not os.path.isfile(abspath):
            makedirs(os.path.dirname(abspath), exist_ok=True)
            with open(abspath, 'w') as fp:
                pass
            template = get_template(abspath)
        else:
            template = None
        view = self.window.open_file(abspath)
        if template:
            view.settings().set('fm_insert_snippet_on_load', template)
        refresh_sidebar(self.settings, self.window)

    def on_change(self, input_path, path_to_create_choosed_from_browsing):
        if path_to_create_choosed_from_browsing:
            # The user has browsed, we let InputForPath select the path
            return
        if self.know_where_to_create_from:
            return
        elif self.folders:
            splited_input = input_path.split(self.index_folder_separator, 1)
            if len(splited_input) == 1:
                index = self.default_index
            elif isdigit(splited_input[0]):
                index = int(splited_input[0])
            else:
                index = self.default_index
            return self.folders[index], splited_input[-1]
        return '~', input_path

    def is_enabled(self, paths=None):
        return paths is None or len(paths) == 1


class FmRenameCommand(AppCommand):

    def run(self, paths=None):
        self.settings = get_settings()
        self.window = get_window()
        self.view = self.window.active_view()

        if paths is None:
            self.origin = self.view.file_name()
        else:
            self.origin = paths[0]

        filename, ext = os.path.splitext(os.path.basename(self.origin))

        self.input = InputForPath(caption='Rename to: ',
                                       initial_text='{0}{1}'.format(filename, ext),
                                       on_done=self.rename,
                                       on_change=None,
                                       on_cancel=None,
                                       create_from=os.path.dirname(self.origin),
                                       with_files=self.settings.get('complete_with_files_too'),
                                       pick_first=self.settings.get('pick_first'),
                                       case_sensitive=self.settings.get('case_sensitive'),
                                       log_in_status_bar=self.settings.get('log_in_status_bar'),
                                       log_template='Renaming to {0}',
                                       enable_browser=True)
        self.input.input.view.selection.clear()
        self.input.input.view.selection.add(sublime.Region(0, len(filename)))

    def rename(self, dst, input_dst):

        def rename():
            makedirs(os.path.dirname(dst), exist_ok=True)
            os.rename(self.origin, dst)
            view = self.window.find_open_file(self.origin)
            if view:
                close_view(view)
            if os.path.isfile(dst):
                self.window.open_file(dst)


        if os.path.exists(dst):

            def open_file(self):
                return self.window.open_file(dst)

            def overwrite():
                try:
                    send2trash(dst)
                except OSError as e:
                    sublime.error_message('Unable to send to trash: ', e)
                    raise OSError('Unable to send the item {0!r} to the trash! Error {1!r}'.format(dst, e))

                rename()
            user_friendly_path = ph.user_friendly(dst)
            return yes_no_cancel_panel(message=['This file already exists. Overwrite?',
                                                 user_friendly_path],
                                       yes=overwrite,
                                       no=open_file,
                                       cancel=None,
                                       yes_text=['Yes. Overwrite', user_friendly_path, 'will be sent to the trash, and then written'],
                                       no_text=['Just open the target file', user_friendly_path],
                                       cancel_text=["No, don't do anything"])

        rename()
        refresh_sidebar(self.settings, self.window)

    def is_enabled(self, paths=None):
        return paths is None or len(paths) == 1


class FmMoveCommand(AppCommand):

    def run(self, paths=None):
        self.settings = get_settings()
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
                close_view(view)
            try:
                os.rename(origin, new_name)
            except Exception as e:
                sublime.error_message('An error occured while moving the file', e)
                raise OSError('An error occured while moving the file {0!r} to {1!r}'.format(origin, new_name))
            if view:
                self.window.open_file(new_name)
        refresh_sidebar(self.settings, self.window)


class FmDuplicateCommand(AppCommand):

    def run(self, paths=None):
        self.settings = get_settings()

        self.window = get_window()

        if paths is None:
            self.origin = self.window.active_view().file_name()
        else:
            self.origin = paths[0]


        initial_path = ph.user_friendly(self.origin)

        self.input = InputForPath(caption='Duplicate to: ',
                                  initial_text=initial_path,
                                  on_done=self.duplicate,
                                  on_change=None,
                                  on_cancel=None,
                                  create_from='',
                                  with_files=False,
                                  pick_first=self.settings.get('pick_first'),
                                  case_sensitive=self.settings.get('case_sensitive'),
                                  log_in_status_bar=self.settings.get('log_in_status_bar'),
                                  log_template='Duplicating at {0}',
                                  enable_browser=True)

        head = len(os.path.dirname(initial_path)) + 1
        filename = len(os.path.splitext(os.path.basename(initial_path))[0])
        self.input.input.view.selection.clear()
        self.input.input.view.selection.add(sublime.Region(head, head + filename))

    def duplicate(self, dst, input_path):
        user_friendly_path = ph.user_friendly(dst)

        if os.path.isdir(self.origin):
            if not os.path.exists(dst):
                shutil.copytree(self.origin, dst)
            else:
                sublime.error_message('This path already exists!')
                raise ValueError('Cannot move the directory {0!r} because it already exists {1!r}'.format(self.origin, dst))
        else:
            if not os.path.exists(dst):
                with open(dst, 'w') as fp:
                    with open(self.origin, 'r') as fpread:
                        fp.write(fpread.read())
                self.window.open_file(dst)
            else:
                def overwrite():
                    try:
                        send2trash(dst)
                    except OSError as e:
                        sublime.error_message('Unable to send to trash: ', e)
                        raise OSError('Unable to send to the trash the item {0}'.format(e))

                    with open(dst, 'w') as fp:
                        with open(self.origin, 'r') as fpread:
                            fp.write(fpread.read())
                    self.window.open_file(dst)

                def open_file():
                    return self.window.open_file(dst)

                yes_no_cancel_panel(message=['This file already exists. Overwrite?', user_friendly_path],
                                    yes=overwrite,
                                    no=open_file,
                                    cancel=None,
                                    yes_text=['Yes. Overwrite', user_friendly_path, 'will be sent to the trash, and then written'],
                                    no_text=['Just open the target file', user_friendly_path],
                                    cancel_text=["No, don't do anything"])

        refresh_sidebar(self.settings, self.window)
        return

    def is_enabled(self, paths=None):
        return paths is None or len(paths) == 1


class FmDeleteCommand(AppCommand):

    def delete(self, index):
        if index == 0:
            for path in self.paths:
                view = self.window.find_open_file(path)
                if view is not None:
                    close_view(view)
                try:
                    send2trash(path)
                except OSError as e:
                    sublime.error_message('Unable to send to trash: ', e)
                    raise OSError('Unable to send {0!r} to trash: {1}'.format(path, e))
        refresh_sidebar(self.settings, self.window)

    def run(self, paths=None, *args, **kwargs):
        self.settings = get_settings()
        self.window = get_window()
        self.view = get_view()

        self.paths = paths or [self.view.file_name()]
        self.window.show_quick_panel([
            ['Send item {0} to trash'.format(('s' if len(self.paths) > 1 else ''))] + self.paths,
            'Cancel'
        ], self.delete)


# --- Extra ---

class FmOpenInBrowserCommand(AppCommand):

    def run(self, paths=None, *args, **kwargs):
        self.window = get_window()
        self.view = get_view()

        if paths is None:
            paths = [self.view.file_name()]

        url = self.view.settings().get('url')
        if url is not None:
            url = url.strip('/')
        files = []
        folders = self.window.folders()

        for path in paths:

            if url is None:
                sublime.run_command('open_url', {'url': 'file:///' + path})
            else:
                for folder in folders:
                    if folder in path:
                        if os.path.splitext(os.path.basename(path))[0] == 'index':
                            path = os.path.dirname(path)
                        sublime.run_command('open_url', {'url': url + path.replace(folder, '') })
                        break
                    else:
                        sublime.run_command('open_url', {'url': 'file:///' + path})


class FmCopyCommand(AppCommand):

    def run(self, which, paths=None):
        self.view = get_view()
        self.window = get_window()

        if paths is None:
            paths = [self.view.file_name()]

        text = []
        folders = self.window.folders()

        for path in paths:
            if which == 'name':
                text.append(os.path.basename(path))
            elif which == 'absolute path':
                text.append(path)
            elif which == 'relative path':
                for folder in folders:
                    if folder not in path:
                        continue
                    text.append(path.replace(folder, ''))
                    break

        copy('\n'.join(bit.replace(os.path.sep, '/') for bit in text))


class FmOpenTerminalCommand(AppCommand):

    def open_terminal(self, cmd, cwd, name):
        if os.path.isfile(cwd):
            cwd = os.path.dirname(cwd)

        for j, bit in enumerate(cmd):
            cmd[j] = bit.replace('$cwd', cwd)
        sm('Opening "{0}" at {1}'.format(name, ph.user_friendly(cwd)))
        return subprocess.Popen(cmd, cwd=cwd)

    def run(self, paths=None):

        self.settings = get_settings()
        self.window = get_window()
        self.view = self.window.active_view()
        self.terminals = self.settings.get('terminals')

        if paths is not None:
            cwd = paths[0]
        else:
            cwd = self.view.file_name()

        def open_terminal_callback(index):
            if index == -1:
                return
            self.open_terminal(self.terminals[index]['cmd'], cwd, self.terminals[index]['name'])

        if len(self.terminals) == 1:
            open_terminal_callback(0)
        else:
            self.window.show_quick_panel([terminal_options['name'] for terminal_options in self.terminals], open_terminal_callback)

    def is_enabled(self, paths=None):
        return paths is None or len(paths) == 1


class FmRevealCommand(AppCommand):

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



class FmEditToTheRightCommand(AppCommand):

    def run(self, files=None):
        v = get_view()
        w = get_window()

        if files is None:
            files = [v.file_name()]

        w.set_layout({
            "cols": [0.0, 0.5, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
        })
        for i, file in enumerate(files, 1):
            w.set_view_index(w.open_file(file), 1, 0)
        w.focus_group(1)

    def is_enabled(self, files=None):
        return (files is None or len(files) >= 1) and get_window().active_group() != 1


class FmEditToTheLeftCommand(AppCommand):

    def run(self, files=None):
        v = get_view()
        w = get_window()

        if files is None:
            files = [v.file_name()]

        w.set_layout({
            "cols": [0.0, 0.5, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
        })
        for file in files:
            w.set_view_index(w.open_file(file), 0, 0)

        w.focus_group(0)

    def is_enabled(self, files=None):
        return (files is None or len(files) >= 1) and get_window().active_group() != 0

# disabled command
class FmCreateFileFromSelectionCommand:

    """Right click on a file and create the realative path to it.
    Inspired a lot by Default.open_context_menu. Thanks John!"""

    CONTEXT_MAX_LENGTH = 20

    def run(self, edit, event):
        md(self.get_path(event))

    def want_event(self):
        return True

    def get_path(self, event, for_context_menu=False):
        if self.view.file_name() is None:
            return
        pt = self.view.window_to_text((event["x"], event["y"]))
        if not 'string' in self.view.scope_name(pt):
            return

        line = self.view.line(pt)

        line.a = max(line.a, pt - 1024)
        line.b = min(line.b, pt + 1024)

        text = self.view.substr(line)

        it = FIND_PATH.finditer(text)

        for match in it:
            if match.start() <= (pt - line.a) and match.end() >= (pt - line.a):
                path = text[match.start():match.end()]
                if for_context_menu:
                    return os.path.dirname(self.view.file_name()), ph.computer_friendly(path)
                return os.path.join(os.path.dirname(self.view.file_name()), ph.computer_friendly(path))
        return None

    def description(self, event):
        base, filename = self.get_path(event, True)
        if len(base) + len(filename) > self.CONTEXT_MAX_LENGTH:
            path = base[:len(filename) - 3] + '...' + filename
        else:
            path = os.path.join(base, filename)
        return "Create " + path

    def is_visible(self, event):
        return self.get_path(event) is not None


class FmFindInFilesCommand(AppCommand):

    def run(self, paths=None):
        if paths is None:
            paths = [get_view().file_name()]
        for i, path in enumerate(paths):
            if os.path.isfile(path):
                paths[i] = os.path.dirname(path)
        paths = remove_duplicate(paths)
        w = get_window()
        w.run_command('show_panel', {
            "panel": "find_in_files",
            "where": ', '.join(paths)
        })

# --- Listener --- (pathetic, right?) :D

class FmListener(sublime_plugin.EventListener):

    def on_close(self, view):
        if get_settings().get('auto_close_empty_groups') is not True:
            return
        def run():
            w = get_window()
            reset_layouts = False
            for group in range(w.num_groups()):
                if len(w.views_in_group(group)) == 0:
                    reset_layouts = True

            if reset_layouts:
                w.set_layout({
                    "cols": [0.0, 1.0],
                    "rows": [0.0, 1.0],
                    "cells": [[0, 0, 1, 1]]
                })

        sublime.set_timeout(run, 50)

    def on_load(self, view):
        snippet = view.settings().get('fm_insert_snippet_on_load', None)
        if snippet:
            view.run_command('insert_snippet', {'contents': snippet})
            view.settings().erase('fm_insert_snippet_on_load')
