# -*- encoding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function, division

import sublime
import sublime_plugin
import os
from re import compile as re_comp
from ..sublimefunctions import *

""" This command has been inspired at 90% by the open_url_context command
AND the vintage open_file_under_selection. Thanks John!"""

def is_legal_path_char(c):
    # XXX make this platform-specific?
    return c not in " \n\"|*<>{}[]()"

def move_until(view, stop_char, increment, start):
    char = view.substr(start)
    while is_legal_path_char(char) and start >= 0:
        start += increment
        char = view.substr(start)
    return start

class FmCreateFileFromSelectionCommand(sublime_plugin.TextCommand):

    CONTEXT_MAX_LENGTH = 50
    MATCH_SOURCE_ATTR = re_comp(r'(src|href) *= *$')

    def run(self, edit, event):
        base_path, input_path = self.get_path(event)
        abspath = computer_friendly(os.path.join(base_path, input_path))
        sublime.run_command('fm_creater', {'abspath': abspath,
                                           'input_path': input_path})

    def want_event(self):
        return True

    def get_path(self, event, for_context_menu=False):
        file_name = None
        region = self.view.sel()[0]
        if not region.empty():
            file_name = self.view.substr(region)
        else:
            if 'html' in self.view.settings().get('syntax').lower():
                caret_pos = self.view.window_to_text((event["x"], event["y"]))
                current_line = self.view.line(caret_pos)
                left = move_until(self.view, '"', -1, caret_pos)
                right = move_until(self.view, '"', 1, caret_pos)
                text = self.view.substr(sublime.Region(0, self.view.size()))[:left]
                if self.MATCH_SOURCE_ATTR.search(text):
                    file_name = self.view.substr(sublime.Region(left + 1, right))
                else:
                    return None
            else:
                return None
        return os.path.dirname(self.view.file_name()), file_name

    def description(self, event):
        base, file_name = self.get_path(event, True)
        base, file_name = user_friendly(base), user_friendly(file_name)
        if len(base) + len(file_name) > self.CONTEXT_MAX_LENGTH:
            path = base[:len(file_name) - 3] + '...' + file_name
        else:
            path = base + '/' + file_name
        return "Create " + path

    def is_visible(self, event=None):
        if event is None: return False
        return self.view.file_name() is not None and self.get_path(event) is not None
