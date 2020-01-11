# -*- encoding: utf-8 -*-
from ..sublimefunctions import *
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
                text.append(path)
            elif which in ("path from root", "relative path"):
                for folder in folders:
                    if folder not in path:
                        continue

                    text.append(os.path.join("/", path.replace(folder, "")))
                    if which == "relative path":
                        # remove the initial /
                        text[-1] = text[-1][1:]
                    break

        copy("\n".join(bit.replace(os.path.sep, "/") for bit in text))
