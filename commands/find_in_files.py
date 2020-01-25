# -*- encoding: utf-8 -*-
import os

from .fmcommand import FmWindowCommand


class FmFindInFilesCommand(FmWindowCommand):
    def run(self, paths=None):
        valid_paths = set()
        for path in paths or self.windows.active_view().file_name():
            if os.path.isfile(path):
                valid_paths.add(os.path.dirname(path))
            else:
                valid_paths.add(path)

        self.window.run_command(
            "show_panel", {"panel": "find_in_files", "where": ", ".join(valid_paths)}
        )
