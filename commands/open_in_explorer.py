# -*- encoding: utf-8 -*-
import sublime
import os.path
from .appcommand import AppCommand


class FmOpenInExplorerCommand(AppCommand):
    def run(self, visible_on_platforms, paths=None):
        # visible_on_platforms is just used by is_visible

        window = sublime.active_window()
        view = window.active_view()

        if paths is None:
            paths = [view.file_name()]

        for path in paths:
            if os.path.isdir(path):
                window.run_command("open_dir", {"dir": path})
            else:
                window.run_command(
                    "open_dir",
                    {"dir": os.path.dirname(path), "file": os.path.basename(path)},
                )

    def is_visible(self, visible_on_platforms, paths=None):
        return sublime.platform() in visible_on_platforms and super().is_visible()
