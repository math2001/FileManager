# -*- encoding: utf-8 -*-
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

    CONTEXT_MAX_LENGTH = 30
    MATCH_SOURCE_ATTR = re_comp(r'(src|href) *= *$')
    MATCH_JS_REQUIRE = re_comp(r'require\(\s*$')
    MATCH_RUBY_REQUIRE = re_comp(r'require_relative\s*\(?\s*$')

    def run(self, edit, event):
        base_path, input_path = self.get_path(event)
        abspath = computer_friendly(os.path.join(base_path, input_path))
        sublime.run_command('fm_creater', {'abspath': abspath,
                                           'input_path': input_path})

    def want_event(self):
        return True

    def get_path(self, event, for_context_menu=False):
        """
            @return (base_path: str, relative_path: str)
        """
        file_name = None
        region = self.view.sel()[0]
        if not region.empty():
            file_name = self.view.substr(region)
        else:
            syntax = self.view.settings().get('syntax').lower()
            call_pos = self.view.window_to_text((event["x"], event["y"]))
            current_line = self.view.line(call_pos)
            if 'html' in syntax:
                region = self.view.extract_scope(call_pos)
                text = self.view.substr(sublime.Region(0, self.view.size()))
                text = text[:region.begin()]
                if self.MATCH_SOURCE_ATTR.search(text):
                    file_name = self.view.substr(region)[:-1]
                    # removes the " at the end, I guess this is due to the
                    # PHP syntax definition
                else:
                    return
            elif 'python' in syntax:
                current_line = self.view.substr(current_line)
                if current_line.startswith('from .'):
                    current_line = current_line[6:]
                    index = current_line.find(' import')
                    if index < 0:
                        return
                    current_line = current_line[:index].replace('.', '/')
                    if current_line.startswith('/'):
                        current_line = '..' + current_line
                    file_name = current_line + '.py'
                elif current_line.startswith('import '):
                    file_name = current_line[7:].replace('.', '/') + '.py'
                else:
                    return
            elif 'php' in syntax:
                current_line = self.view.substr(current_line)
                if not (current_line.startswith('include ') or
                        current_line.startswith('require ')):
                    return
                file_name = self.view.substr(
                                self.view.extract_scope(call_pos))
            elif 'javascript' in syntax:
                # for now, it only supports require
                region = self.view.extract_scope(call_pos)
                text = self.view.substr(sublime.Region(0, self.view.size()))
                text = text[:region.begin()]
                if self.MATCH_JS_REQUIRE.search(text) is None:
                    return
                # [1:-1] removes the quotes
                file_name = self.view.substr(region)[1:-1]
                if not file_name.endswith('.js'):
                    file_name += '.js'
            elif 'ruby' in syntax:
                region = self.view.extract_scope(call_pos)
                text = self.view.substr(sublime.Region(0, self.view.size()))
                text = text[:region.begin()]
                if self.MATCH_RUBY_REQUIRE.search(text) is None:
                    return
                # [1:-1] removes the quotes
                file_name = self.view.substr(region)[1:-1]
                if not file_name.endswith('.rb'):
                    file_name += '.rb'
            else:
                return
        return os.path.dirname(self.view.file_name()), file_name

    def description(self, event):
        base, file_name = self.get_path(event, True)
        while file_name.startswith('../'):
            file_name = file_name[3:]
            base = os.path.dirname(base)
        base, file_name = user_friendly(base), user_friendly(file_name)

        if len(base) + len(file_name) > self.CONTEXT_MAX_LENGTH:
            path = base[:self.CONTEXT_MAX_LENGTH - len(file_name) - 4]
            path += '.../' + file_name
        else:
            path = base + '/' + file_name
        return "Create " + path

    def is_visible(self, event=None):
        if event is None: return False
        return self.view.file_name() is not None and self.get_path(event) is not None
