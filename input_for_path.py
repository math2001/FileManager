import sublime
import sublime_plugin
import os
from . import pathhelper as ph
from .sublimefunctions import *

def isdigit(string):
    try:
        int(string);
    except ValueError:
        return False
    else:
        return True

class StdClass: pass

class InputForPath(object):

    STATUS_KEY = 'input_for_path'

    def __init__(self, caption, initial_text, on_done, on_change, on_cancel, create_from,
                 with_files, pick_first, case_sensitive, log_in_status_bar):

        self.user_on_done = on_done
        self.user_on_change = on_change
        self.user_on_cancel = on_cancel
        self.caption = caption
        self.initial_text = initial_text


        self.create_from = create_from
        if self.create_from is not None:
            self.create_from = ph.computer_friendly(self.create_from)
            if not os.path.isdir(self.create_from):
                em('The path `create_from` should exists. {!r} does not.'.format(self.create_from))

        self.browser = StdClass()
        self.browser.path = self.create_from
        self.browser.items = []

        self.with_files = with_files
        self.pick_first = pick_first
        self.case_sensitive = case_sensitive

        self.path_to_create_choosed_from_browsing = False

        self.window = sublime.active_window()
        self.view = self.window.active_view()

        self.log_in_status_bar = log_in_status_bar

        self.create_input()

    def create_input(self):

        self.input = StdClass()
        self.input.view = self.window.show_input_panel(self.caption, self.initial_text,
                                                       self.input_on_done, self.input_on_change,
                                                       self.input_on_cancel)
        self.input.settings = self.input.view.settings()
        self.input.settings.set('tab_completion', False)

    def __get_completion_for(self, abspath:str, with_files:bool, pick_first:str, case_sensitive:bool):
        abspath = ph.computer_friendly(abspath)
        if abspath.endswith(os.path.sep):
            return '', ''
        prefix = abspath.split(os.path.sep)[-1]
        abspath = os.path.dirname(abspath)
        items = os.listdir(abspath)
        posibilities = []
        for item in items:
            if ((case_sensitive and item.startswith(prefix)) or
                 (not case_sensitive and item.lower().startswith(prefix.lower()))):
                posibilities.append([item, os.path.isdir(os.path.join(abspath, item))])
        backup = None
        for completion, isdir in posibilities:
            if with_files:
                if pick_first == 'files':
                    if not isdir: # is file
                        return prefix, completion
                    else:
                        backup = completion + '/'
                elif pick_first == 'folder':
                    if isdir:
                        return prefix, completion + '/'
                    else:
                        backup = completion
                else:
                    return prefix, completion + ('/' if isdir else '')
            else:
                if isdir:
                    return prefix, completion + '/'

        if backup is None: return
        return prefix, backup

    def input_on_change(self, input_path):
        input_path = ph.user_friendly(input_path)
        if self.user_on_change:
            mess = self.user_on_change(input_path, self.path_to_create_choosed_from_browsing)
            if mess is not None:
                create_from, input_path = mess
                self.create_from = ph.computer_friendly(create_from)

        # complete and log in status bar
        mess = input_path.split('\t', 1)
        if len(mess) == 2:
            # complete
            before, after = mess
            mess = self.__get_completion_for(abspath=ph.computer_friendly(os.path.join(self.create_from, before)),
                                             with_files=self.with_files,
                                             pick_first=self.pick_first,
                                             case_sensitive=self.case_sensitive)
            if mess is None:
                return
            prefix, completion = mess
            # + 1 because of the \t
            for i in range(len(prefix) + 1):
                self.input.view.run_command('left_delete')
            self.input.view.run_command('insert', {'characters': completion})

        else:
            if self.log_in_status_bar is False:
                return

            path = os.path.normpath(os.path.join(self.create_from, ph.computer_friendly(input_path)))
            if input_path != '' and input_path[-1] == '/':
                path += os.path.sep
            if self.log_in_status_bar == 'user':
                path = ph.user_friendly(path)
            self.view.set_status(self.STATUS_KEY, 'Creating at: {}'.format(path))

    def input_on_done(self, input_path):
        if self.log_in_status_bar:
            self.view.set_status(self.STATUS_KEY, '')
        computer_path = ph.computer_friendly(os.path.join(self.create_from, input_path))
        # open browser
        if os.path.isdir(computer_path):
            self.browser.path = computer_path
            return self.browsing_on_done()
        else:
            self.user_on_done(computer_path, input_path)


    def input_on_cancel(self):
        self.view.set_status(self.STATUS_KEY, '')
        if self.user_on_cancel:
            self.user_on_cancel()

    def browsing_on_done(self, index=None):
        if index == -1:
            return

        if index == 0:
            # create from the position in the browser
            self.create_from = self.browser.path
            self.path_to_create_choosed_from_browsing = True
            return self.create_input()
        elif index == 1:
            self.browser.path = os.path.normpath(os.path.join(self.browser.path, '..'))
        elif index is not None:
            self.browser.path = os.path.join(self.browser.path, self.browser.items[index])

        if os.path.isfile(self.browser.path):
            self.window.open_file(self.browser.path)

        self.browser.items = ['[cmd] Create from here', '[cmd] ..']
        # self.browser.items += os.listdir(self.browser.path)
        for item in os.listdir(self.browser.path):
            if os.path.isdir(os.path.join(self.browser.path, item)):
                item += '/'
            self.browser.items.append(item)

        self.view.set_status(self.STATUS_KEY, 'Browsing at: {}'.format(ph.user_friendly(self.browser.path)))

        self.window.show_quick_panel(self.browser.items, self.browsing_on_done, selected_index=2)

class FmTestCommand(sublime_plugin.ApplicationCommand):

    def run(self):

        def on_done(text):
            md('create file at {!r}'.format(text))

        def on_change(text):
            print(text)

        self.complete_input = InputForPath(caption='',
                                           initial_text='',
                                           on_done=on_done,
                                           on_change=on_change,
                                           on_cancel=None,
                                           create_from='~',
                                           with_files=True,
                                           pick_first=None,
                                           case_sensitive=False)
