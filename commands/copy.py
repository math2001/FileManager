# -*- encoding: utf-8 -*-
import os

import sublime

from .fmcommand import FmWindowCommand


class FmCopyCommand(FmWindowCommand):
    def run(self, which, paths=None):
        text = []
        folders = self.window.folders()

        for path in paths or [self.window.active_view().file_name()]:
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
