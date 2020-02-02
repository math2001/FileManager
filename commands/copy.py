# -*- encoding: utf-8 -*-
from ..libs.sublimefunctions import *
from .appcommand import AppCommand


class FmCopyCommand(AppCommand):
    def run(self, which, paths=None):
        self.view = get_view()
        self.window = get_window()

        if paths is None:
            paths = [self.view.file_name()]

        text = []
        folders = self.window.folders()

        for path in paths:
            if which == "name":
                text.append(os.path.basename(path))
            elif which == "absolute path":
                text.append(os.path.abspath(path))
            elif which == "relative path":
                for folder in folders:
                    if folder in path:
                        text.append(os.path.relpath(path, folder))
                        break
            elif which == "path from root":
                for folder in folders:
                    if folder in path:
                        norm_path = os.path.relpath(path, folder)
                        text.append("/" + norm_path.replace(os.path.sep, "/"))
                        break

        sublime.set_clipboard("\n".join(text))
