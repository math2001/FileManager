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
        if index > 1:
            view = self.window.find_open_file(self.paths[index - 2])
            if view is not None:
                close_view(view)

            # We substract two, because 0, 1 are populated by Confirm, Cancel
            self.paths.remove(self.paths[index - 2])

            if self.paths:
                refresh_sidebar(self.settings, self.window)
                self.run(self.paths)

        refresh_sidebar(self.settings, self.window)

    def run(self, paths=None, *args, **kwargs):
        self.settings = get_settings()
        self.window = get_window()
        self.view = get_view()

        self.paths = paths or [self.view.file_name()]
        if get_settings().get("ask_for_confirmation_on_delete") is not False:
            nitems = "{0} ".format(len(self.paths)) if len(self.paths) > 1 else ""
            extras = "s" if len(self.paths) > 1 else ""

            confirm_title = "Confirm"
            confirm_subtitle = "Send {}item{} to trash".format(nitems, extras)
            cancel_title = "Cancel All (Select an individual item to remove it from the deletion list)"
            cancel_subtitle = "Cancel deletion of {}item{}".format(nitems, extras)

            paths_to_display = [
                [confirm_title, confirm_subtitle],
                [cancel_title, cancel_subtitle],
            ]
            for path in self.paths:
                paths_to_display.append([os.path.basename(path), path])

            self.window.show_quick_panel(
                paths_to_display, self.delete,
            )
        else:
            # index 0 is like clicking on the first option of the panel
            # ie. confirming the deletion
            self.delete(index=0)
