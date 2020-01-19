# -*- encoding: utf-8 -*-
from ..libs.sublimefunctions import *
from ..libs.send2trash import send2trash
from .appcommand import AppCommand


class FmDeleteCommand(AppCommand):
    def run(self, paths=None, *args, **kwargs):
        self.settings = get_settings()
        self.window = get_window()
        self.view = get_view()

        self.paths = paths or [self.view.file_name()]
        if get_settings().get("ask_for_confirmation_on_delete"):
            num_paths = len(self.paths)
            nitems = "{0} ".format(num_paths) if num_paths > 1 else ""
            extras = "s" if num_paths > 1 else ""

            confirm_title = "Confirm"
            confirm_subtitle = "Send {}item{} to trash".format(nitems, extras)
            cancel_title = "Cancel All (Select an individual item to remove it from the deletion list)"
            cancel_subtitle = "Cancel deletion of {}item{}".format(nitems, extras)

            paths_to_display = [
                [confirm_title, confirm_subtitle],
                [cancel_title, cancel_subtitle],
            ] + [[os.path.basename(path), path] for path in self.paths]

            self.window.show_quick_panel(paths_to_display, self.delete)

        else:
            # index 0 is like clicking on the first option of the panel
            # ie. confirming the deletion
            self.delete(index=0)

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

        elif index > 1:
            self.paths.pop(index - 2)
            if self.paths:
                self.run(self.paths)
