# -*- encoding: utf-8 -*-
from ..libs.sublimefunctions import *
from ..libs.send2trash import send2trash
from .appcommand import AppCommand


class FmDeleteCommand(AppCommand):
    def delete(self, index):
        if index == 0:
            for path in self.paths:
                view = self.window.find_open_file(path)
                if view is not None:
                    close_view(view)
                try:
                    send2trash(path)
                except OSError as e:
                    sublime.error_message("Unable to send to trash: {}".format(e))
                    raise OSError("Unable to send {0!r} to trash: {1}".format(path, e))
        refresh_sidebar(self.settings, self.window)

    def run(self, paths=None, *args, **kwargs):
        self.settings = get_settings()
        self.window = get_window()
        self.view = get_view()

        self.paths = paths or [self.view.file_name()]
        if get_settings().get("ask_for_confirmation_on_delete") is not False:
            self.window.show_quick_panel(
                [
                    [
                        "Send item{0} to trash".format(
                            ("s" if len(self.paths) > 1 else "")
                        )
                    ]
                    + self.paths,
                    "Cancel",
                ],
                self.delete,
            )
        else:
            # index 0 is like clicking on the first option of the panel
            # ie. confirming the deletion
            self.delete(index=0)
