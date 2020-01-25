# -*- encoding: utf-8 -*-
import os

import sublime

from .fmcommand import FmWindowCommand


class FmOpenInExplorerCommand(FmWindowCommand):
    def run(self, visible_on_platforms=None, paths=None):
        # visible_on_platforms is just used by is_visible
        for path in paths or [self.window.active_view().file_name()]:
            if os.path.isdir(path):
                self.window.run_command("open_dir", {"dir": path})
            else:
                dirname, basename = os.path.splitext(path)
                self.window.run_command(
                    "open_dir", {"dir": dirname, "file": basename},
                )

    def is_visible(self, visible_on_platforms=None, paths=None):
        return (
            visible_on_platforms is None or sublime.platform() in visible_on_platforms
        ) and super().is_visible()
