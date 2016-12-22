# -*- encoding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function, division

from .sublimefunctions import *
from .FMcommands.appcommand import AppCommand

class FmFindInFilesCommand(AppCommand):

    def run(self, paths=None):
        if paths is None:
            paths = [get_view().file_name()]
        valid_paths = set()
        for i, path in enumerate(paths):
            if os.path.isfile(path):
                valid_paths.add(os.path.dirname(path))
            else:
                valid_paths.add(path)
        get_window().run_command('show_panel', {
            "panel": "find_in_files",
            "where": ', '.join(valid_paths)
        })
