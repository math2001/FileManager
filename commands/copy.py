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

        sublime.set_clipboard("\n".join(bit.replace(os.path.sep, "/") for bit in text))
