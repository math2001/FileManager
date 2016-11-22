import sublime
import sublime_plugin
import os
try:
    from . import pathhelper as ph
    from .sublimefunctions import *
except (ImportError, ValueError):
    import pathhelper as ph
    from sublimefunctions import *

def isdigit(string):
    try:
        int(string);
    except ValueError:
        return False
    else:
        return True

class StdClass:
    def __init__(self, name="Unnamed"):
        self.__class__.__name__ = name.title()

def set_status(view, key, value):
    if view:
        view.set_status(key, value)
    else:
        sm(value)

def get_entire_text(view):
    return view.substr(sublime.Region(0, view.size()))

class InputForPath(object):

    STATUS_KEY = 'input_for_path'

    def __init__(self, caption, initial_text, on_done, on_change, on_cancel, create_from,
                 with_files, pick_first, case_sensitive, log_in_status_bar, log_template,
                 enable_browser):


        self.user_on_done = on_done
        self.user_on_change = on_change
        self.user_on_cancel = on_cancel
        self.caption = caption
        self.initial_text = initial_text
        self.log_template = log_template
        self.enable_browser = enable_browser


        self.create_from = create_from
        if self.create_from:
            self.create_from = ph.computer_friendly(self.create_from)
            if not os.path.isdir(self.create_from):
                em('The path `create_from` should exists. {0!r} does not exists.'.format(self.create_from))

        self.browser = StdClass('Browser')
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

        self.prev_input_path = None

        self.input = StdClass('input')
        self.input.view = self.window.show_input_panel(self.caption, self.initial_text,
                                                       self.input_on_done, self.input_on_change,
                                                       self.input_on_cancel)
        self.input.settings = self.input.view.settings()
        self.input.settings.set('tab_completion', False)
        if not isST3():
            self.input.view.selection = self.input.view.sel()

    def __get_completion_for(self, abspath, with_files, pick_first, case_sensitive, can_add_slash):
        """Return a string and list: the prefix, and the list
        of available completion in the right order"""

        def sort_in_two_list(items, key):
            first, second = [], []
            for item in items:
                first_list, item = key(item)
                if first_list:
                    first.append(item)
                else:
                    second.append(item)
            return first, second


        abspath = ph.computer_friendly(abspath)

        if abspath.endswith(os.path.sep):
            prefix = ''
            load_items_from = abspath
        else:
            load_items_from = os.path.dirname(abspath)
            prefix = os.path.basename(abspath)

        items = sorted(os.listdir(load_items_from))
        items_with_right_prefix = []

        if not case_sensitive:
            prefix = prefix.lower()

        for i, item in enumerate(items):
            if not case_sensitive:
                item = item.lower()
            if item.startswith(prefix):
                # I add items[i] because it's case is never changed
                items_with_right_prefix.append([items[i],
                                                os.path.isdir(os.path.join(load_items_from, items[i]))])


        folders, files = sort_in_two_list(items_with_right_prefix, lambda item: [item[1], item[0]])
        if can_add_slash:
            folders = [folder + '/' for folder in folders]
        if with_files:
            if pick_first == 'folders':
                return prefix, folders + files
            elif pick_first == 'files':
                return prefix, files + folders
            elif pick_first == 'alphabetic':
                return prefix, sorted(files + folders)
            else:
                sublime.error_message('The keyword {0!r} to define the order of completions is not valid. See the default settings.'.format(pick_first))
                raise ValueError('The keyword {0!r} to define the order of completions is not valid. See the default settings.'.format(pick_first))
        else:
            return prefix, folders

    def input_on_change(self, input_path):
        self.input_path = ph.user_friendly(input_path)
        # get changed inputs and create_from from the on_change user function
        if self.user_on_change:
            new_values = self.user_on_change(self.input_path, self.path_to_create_choosed_from_browsing)
            if new_values is not None:
                create_from, self.input_path = new_values
                self.create_from = ph.computer_friendly(create_from)

        def reset_settings():
            self.input.settings.erase('completions')
            self.input.settings.erase('completions_index')

        def replace_with_completion(completions, index, prefix=None):
            # replace the previous completion
            # with the new one (completions[index+1])
            region = [self.input.view.sel()[0].begin()]
            # -1 because of the \t
            region.append(region[0] - len(prefix if prefix is not None else completions[index]) - 1)
            index += 1
            self.input.settings.set('completions_index', index)
            # Running edit_replace will trigger this function
            # and because it is not going to find any \t
            # it's going to erase the settings
            # Adding this will prevent this behaviour
            self.input.settings.set('just_completed', True)
            self.input.view.run_command('edit_replace', {'region': region, 'text': completions[index]})
            self.prev_input_path = self.input.view.substr(sublime.Region(0, self.input.view.size()))


        if not hasattr(self.input, 'settings'):
            return

        completions = self.input.settings.get('completions', None)
        index = self.input.settings.get('completions_index', None)

        if completions is not None and index is not None:
            # check if the user typed something after the completion
            text = input_path
            if text[-1] == '\t':
                text = text[:-1]
            if not text.endswith(tuple(completions)):
                return reset_settings()
            if '\t' in input_path:

                # there is still some completions available
                if len(completions) - 1 > index:
                    return replace_with_completion(completions, index)
        if '\t' in input_path:
            before, after = self.input_path.split('\t')
            prefix, completions = self.__get_completion_for(abspath=ph.computer_friendly(os.path.join(self.create_from, before)),
                                                            with_files=self.with_files,
                                                            pick_first=self.pick_first,
                                                            case_sensitive=self.case_sensitive,
                                                            can_add_slash=after == '' or after[0] != '/'
                                                            )
            if not completions:
                return

            self.input.settings.set('completions', completions)
            self.input.settings.set('completions_index', -1)

            replace_with_completion(completions, -1, prefix)

    def input_on_done(self, input_path):
        if self.log_in_status_bar:
            set_status(self.view, self.STATUS_KEY, '')
        # use the one returned by the on change function
        input_path = self.input_path
        computer_path = ph.computer_friendly(os.path.join(self.create_from, input_path))
        # open browser
        if self.enable_browser and os.path.isdir(computer_path):
            self.browser.path = computer_path
            return self.browsing_on_done()
        else:
            self.user_on_done(computer_path, input_path)

    def input_on_cancel(self):
        set_status(self.view, self.STATUS_KEY, '')
        if self.user_on_cancel:
            self.user_on_cancel()

    def browsing_on_done(self, index=None):
        if index == -1:
            return set_status(self.view, self.STATUS_KEY, '')

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

        folders, files = [], []
        for item in os.listdir(self.browser.path):
            if os.path.isdir(os.path.join(self.browser.path, item)):
                folders.append(item + '/')
            else:
                files.append(item)

        self.browser.items = ['[cmd] Create from here', '[cmd] ..'] + folders + files

        set_status(self.view, self.STATUS_KEY, 'Browsing at: {0}'.format(ph.user_friendly(self.browser.path)))

        self.window.show_quick_panel(self.browser.items, self.browsing_on_done, 0, 2)
