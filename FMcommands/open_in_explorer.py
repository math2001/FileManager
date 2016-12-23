# -*- encoding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function, division

from ..sublimefunctions import *
from .appcommand import AppCommand

class FmOpenInExplorerCommand(AppCommand):

    def run(self, paths=None, *args, **kwargs):
        self.window = get_window()
        self.view = get_view()

        if paths is None:
            paths = [self.view.file_name()]

        for path in paths:
            if os.path.isdir(path):
                self.window.run_command('open_dir', { 'dir': path })
            else:
                self.window.run_command("open_dir", { "dir": os.path.dirname(path), "file": os.path.basename(path) })

    def is_visisble(self, **args):
        return True
