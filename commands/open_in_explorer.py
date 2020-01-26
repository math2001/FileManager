# -*- encoding: utf-8 -*-
import os

from .fmcommand import FmWindowCommand


class FmOpenInExplorerCommand(FmWindowCommand):
    def run(self, paths=None):
        # visible_on_platforms is just used by is_visible
        for path in paths or [self.window.active_view().file_name()]:
            if os.path.isdir(path):
                self.window.run_command("open_dir", {"dir": path})
            else:
                dirname, basename = os.path.split(path)
                self.window.run_command(
                    "open_dir", {"dir": dirname, "file": basename},
                )
