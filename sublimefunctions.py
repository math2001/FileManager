from __future__ import absolute_import, unicode_literals, print_function, division
import sublime
import os
import sys

if sys.version_info[0] >= 3:
    from .pathhelper import *
else:
    from pathhelper import *

outlocals = locals()
def plugin_loaded():
    outlocals["TEMPLATE_FOLDER"] = os.path.join(sublime.packages_path(), 'User', '.FileManager')
    if not os.path.exists(outlocals["TEMPLATE_FOLDER"]):
        makedirs(TEMPLATE_FOLDER)

if sys.version_info[0] < 3:
    plugin_loaded()


def md(*t, **kwargs):
    sublime.message_dialog(kwargs.get('sep', '\n').join([str(el) for el in t]))

def sm(*t, **kwargs): sublime.status_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def em(*t, **kwargs): sublime.error_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def isST3():
    return int(sublime.version()) > 3000

def get_settings():
    return sublime.load_settings('FileManager.sublime-settings')

def refresh_sidebar(settings=None, window=None):
    if window is None:
        window = active_window()
    if settings is None:
        settings = window.active_view().settings()
    if settings.get('explicitly_refresh_sidebar') is True:
        window.run_command('refresh_folder_list')

def makedirs(path, exist_ok=True):
    if exist_ok is False:
        os.makedirs(path)
    else:
        try:
            os.makedirs(path)
        except OSError:
            pass

def quote(s):
    return '"{0}"'.format(s)

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

def close_view(view_to_close):
    if isST3():
        view_to_close.close()
        return
    window = view_to_close.window()
    window.focus_view(view_to_close)
    window.run_command('close')

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

def StdClass(name='Unknown'):
    # add the str() function because of the unicode in Python 2
    return type(str(name).title(), (), {})
