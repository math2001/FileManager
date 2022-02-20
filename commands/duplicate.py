# -*- encoding: utf-8 -*-
import shutil
from ..libs.input_for_path import InputForPath
from ..libs.sublimefunctions import *
from ..libs.send2trash import send2trash
from .appcommand import AppCommand


class FmDuplicateCommand(AppCommand):
    def run(self, paths=None):
        self.settings = get_settings()

        self.window = get_window()

        if paths is None:
            self.origin = self.window.active_view().file_name()
        else:
            self.origin = paths[0]

        initial_path = user_friendly(self.origin)

        args = {}
        args["caption"] = "Duplicate to: "
        args["initial_text"] = initial_path
        args["on_done"] = self.duplicate
        args["on_change"] = None
        args["on_cancel"] = None
        args["create_from"] = ""
        args["with_files"] = False
        args["pick_first"] = self.settings.get("pick_first")
        args["case_sensitive"] = self.settings.get("case_sensitive")
        args["log_in_status_bar"] = self.settings.get("log_in_status_bar")
        args["log_template"] = "Duplicating at {0}"

        self.input = InputForPath(**args)

        head = len(os.path.dirname(initial_path)) + 1
        filename = len(os.path.splitext(os.path.basename(initial_path))[0])
        self.input.input.view.selection.clear()
        self.input.input.view.selection.add(sublime.Region(head, head + filename))

    def duplicate(self, dst, input_path):
        user_friendly_path = user_friendly(dst)

        if os.path.abspath(self.origin) == os.path.abspath(dst):
            sublime.error_message("Destination is the same with the source.")
            return

        if os.path.isdir(self.origin):
            if not os.path.exists(dst):
                shutil.copytree(self.origin, dst)
            else:
                sublime.error_message("This path already exists!")
                raise ValueError(
                    "Cannot move the directory {0!r} because it already exists "
                    "{1!r}".format(self.origin, dst)
                )
        else:
            if not os.path.exists(dst):
                shutil.copy2(self.origin, dst)
                self.window.open_file(dst)
            else:

                def overwrite():
                    try:
                        send2trash(dst)
                    except OSError as e:
                        sublime.error_message("Unable to send to trash: {}".format(e))
                        raise OSError(
                            "Unable to send to the trash the item {0}".format(e)
                        )

                    shutil.copy2(self.origin, dst)
                    self.window.open_file(dst)

                def open_file():
                    return self.window.open_file(dst)

                yes_no_cancel_panel(
                    message=[
                        "This file already exists. Overwrite?",
                        user_friendly_path,
                    ],
                    yes=overwrite,
                    no=open_file,
                    cancel=None,
                    yes_text=[
                        "Yes. Overwrite",
                        user_friendly_path,
                        "will be sent " "to the trash, and then written",
                    ],
                    no_text=["Just open the target file", user_friendly_path],
                    cancel_text=["No, don't do anything"],
                )

        refresh_sidebar(self.settings, self.window)
        return

    def is_enabled(self, paths=None):
        return paths is None or len(paths) == 1
