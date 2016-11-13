import sublime
import sublime_plugin
import os

def md(*t, **kwargs): sublime.message_dialog(kwargs.get('sep', '\n').join([str(el) for el in t]))

def sm(*t, **kwargs): sublime.status_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

def em(*t, **kwargs): sublime.error_message(kwargs.get('sep', ' ').join([str(el) for el in t]))

class StdClass: pass

class ShowInputWithAutocompletionCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        def on_done(text):
            md(text)
        def on_change(text):
            if text[-1] == '\t':
                self.input.view.run_command('left_delete')
                text = text[:-1]
                if text[-1] == '/':
                    self.input.view.run

        self.input = StdClass()
        self.input.view = self.window.show_input_panel('hello', '', None, None, None)
        self.input.settings = self.input.view.settings()
        self.input.settings.set('is_input_panel', True)

        self.input.settings.set("translate_tabs_to_spaces", False)


