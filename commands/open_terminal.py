# -*- encoding: utf-8 -*-
import os
import subprocess

import sublime

from ..libs.pathhelper import user_friendly
from .fmcommand import FmWindowCommand


class FmOpenTerminalCommand(FmWindowCommand):
    def run(self, paths=None):
        current_platform = sublime.platform()
        self.terminals = [
            terminal
            for terminal in self.settings.get("terminals")
            if self.is_available(terminal, current_platform)
        ]

        if paths is not None:
            cwd = paths[0]
        elif self.window.folders() != []:
            cwd = self.window.folders()[0]
        else:
            cwd = self.window.active_view().file_name()

        def open_terminal_callback(index):
            if index == -1:
                return
            self.open_terminal(
                self.terminals[index]["cmd"], cwd, self.terminals[index]["name"]
            )

        if len(self.terminals) == 1:
            open_terminal_callback(0)
        else:
            self.window.show_quick_panel(
                [term_infos["name"] for term_infos in self.terminals],
                open_terminal_callback,
            )

    def is_enabled(self, paths=None):
        return paths is None or len(paths) == 1

    def is_available(self, terminal, current_platform):
        try:
            terminal["platform"]
        except KeyError:
            return True
        if not isinstance(terminal["platform"], str):
            return False

        platforms = terminal["platform"].lower().split(" ")
        return current_platform in platforms

    def open_terminal(self, cmd, cwd, name):
        if os.path.isfile(cwd):
            cwd = os.path.dirname(cwd)

        for j, bit in enumerate(cmd):
            cmd[j] = bit.replace("$cwd", cwd)
        sublime.status_message('Opening "{0}" at {1}'.format(name, user_friendly(cwd)))
        return subprocess.Popen(cmd, cwd=cwd)
