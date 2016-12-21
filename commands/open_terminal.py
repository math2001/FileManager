# -*- encoding: utf-8 -*-

from FileManager.sublimefunctions import *
from FileManager.commands.appcommand import AppCommand

class FmOpenTerminalCommand(AppCommand):

    def open_terminal(self, cmd, cwd, name):
        if os.path.isfile(cwd):
            cwd = os.path.dirname(cwd)

        for j, bit in enumerate(cmd):
            cmd[j] = bit.replace('$cwd', cwd)
        sm('Opening "{0}" at {1}'.format(name, user_friendly(cwd)))
        return subprocess.Popen(cmd, cwd=cwd)

    def run(self, paths=None):

        self.settings = get_settings()
        self.window = get_window()
        self.view = self.window.active_view()
        self.terminals = self.settings.get('terminals')

        if paths is not None:
            cwd = paths[0]
        elif self.window.folders() != []:
            cwd = self.window.folders()[0]
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
