# -*- encoding: utf-8 -*-
from ..sublimefunctions import *
from .appcommand import AppCommand
from ..send2trash import send2trash


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
                    sublime.error_message(
                        "Unable to send to trash: {}".format(e))
                    raise OSError(
                        "Unable to send {0!r} to trash: {1}".format(path, e))
        refresh_sidebar(self.settings, self.window)

    def run(self, paths=None, *args, **kwargs):
        self.settings = get_settings()
        self.window = get_window()
        self.view = get_view()

        self.paths = paths or [self.view.file_name()]
        if get_settings().get("ask_for_confirmation_on_delete") is not False:
            confirm_text = "Send {0}item{1} to trash".format(
                ("{0} ".format(
                    len(self.paths)) if len(self.paths) > 1 else ""),
                ("s" if len(
                    self.paths) > 1 else "")
            )
            cancel_text = "Cancel deletion of {0}file{1}".format(
                ("{0} ".format(
                    len(self.paths)) if len(self.paths) > 1 else ""),
                ("s" if len(
                    self.paths) > 1 else "")
            )
            paths_to_display = [
                ["Confirm", confirm_text],
                ["Cancel", cancel_text]
            ]

            for path in paths:
                paths_to_display.append([path.split(os.path.sep)[-1], path])

            self.window.show_quick_panel(
                paths_to_display,
                self.delete,
            )
        else:
            # index 0 is like clicking on the first option of the panel
            # ie. confirming the deletion
            self.delete(index=0)
