# -*- encoding: utf-8 -*-
import os

import sublime

from ..libs.sublimefunctions import refresh_sidebar
from ..libs.send2trash import send2trash
from .fmcommand import FmWindowCommand


class FmDeleteCommand(FmWindowCommand):
    def run(self, paths=None):
        self.paths = paths or [self.window.active_view().file_name()]

        if self.settings.get("ask_for_confirmation_on_delete"):
            paths_to_display = [
                [
                    "Confirm",
                    "Send {0} items to trash".format(len(self.paths))
                    if len(self.paths) > 1
                    else "Send item to trash",
                ],
                [
                    "Cancel All",
                    "Select an individual item to remove it from the deletion list",
                ],
            ]
            paths_to_display.extend(
                [os.path.basename(path), path] for path in self.paths
            )

            self.window.show_quick_panel(paths_to_display, self.delete)

        else:
            # index 0 is like clicking on the first option of the panel
            # ie. confirming the deletion
            self.delete(index=0)

    def delete(self, index):
        if index == 0:
            for path in self.paths:
                for window in sublime.windows():
                    view = window.find_open_file(path)
                    while view is not None:
                        view.set_scratch(True)
                        view.close()
                        view = window.find_open_file(path)

                try:
                    send2trash(path)
                except OSError as e:
                    sublime.error_message("Unable to send to trash: {}".format(e))
                    raise OSError("Unable to send {0!r} to trash: {1}".format(path, e))

            refresh_sidebar(self.settings, self.window)

        elif index > 1:
            self.paths.pop(index - 2)
            if self.paths:
                self.run(self.paths)
