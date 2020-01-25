# -*- encoding: utf-8 -*-
import os
import shutil

import sublime

from ..libs.input_for_path import InputForPath
from ..libs.sublimefunctions import refresh_sidebar, yes_no_cancel_panel
from ..libs.pathhelper import user_friendly
from ..libs.send2trash import send2trash
from .fmcommand import FmWindowCommand


class FmDuplicateCommand(FmWindowCommand):
    def run(self, paths=None):
        if paths is None:
            self.origin = self.window.active_view().file_name()
        else:
            self.origin = paths[0]

        initial_path = user_friendly(self.origin)

        self.input = InputForPath(
            caption="Duplicate to: ",
            initial_text=initial_path,
            on_done=self.duplicate,
            on_change=None,
            on_cancel=None,
            create_from="",
            with_files=False,
            pick_first=self.settings.get("pick_first"),
            case_sensitive=self.settings.get("case_sensitive"),
            log_in_status_bar=self.settings.get("log_in_status_bar"),
            log_template="Duplicating at {0}",
        )

        head = len(os.path.dirname(initial_path)) + 1
        filename = len(os.path.splitext(os.path.basename(initial_path))[0])
        self.input.input.view.selection.clear()
        self.input.input.view.selection.add(sublime.Region(head, head + filename))

    def duplicate(self, dst, input_path):
        user_friendly_path = user_friendly(dst)

        if os.path.abspath(self.origin) == os.path.abspath(dst):
            sublime.error_message("Destination is the same with the source.")
            return

        # remove right trailing slashes, because os.path.dirname('foo/bar/')
        # returns foo/bar rather foo/
        dst = dst.rstrip("/")

        os.makedirs(os.path.dirname(dst), exist_ok=True)

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
