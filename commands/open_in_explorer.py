# -*- encoding: utf-8 -*-
from ..libs.sublimefunctions import *
from .appcommand import AppCommand


class FmOpenInExplorerCommand(AppCommand):
    def run(self, visible_on_platforms=None, paths=None):
        # visible_on_platforms is just used by is_visible
        self.window = get_window()
        self.view = get_view()

        if paths is None:
            paths = [self.view.file_name()]

        for path in paths:
            if os.path.isdir(path):
                self.window.run_command("open_dir", {"dir": path})
            else:
                self.window.run_command(
                    "open_dir",
                    {"dir": os.path.dirname(path), "file": os.path.basename(path)},
                )

    def is_visible(self, visible_on_platforms=None, paths=None):
        return super().is_visible() and (visible_on_platforms is None or sublime.platform() in visible_on_platforms)
