# -*- encoding: utf-8 -*-

from ..libs.input_for_path import InputForPath
from ..libs.sublimefunctions import *
from .appcommand import AppCommand


class FmMoveCommand(AppCommand):
    def run(self, paths=None):
        self.settings = get_settings()
        self.window = get_window()
        self.view = self.window.active_view()

        if paths is not None:
            self.origins = paths
        else:
            self.origins = [self.view.file_name()]

        if len(self.origins) > 1:
            initial_text = commonpath(self.origins)
        else:
            initial_text = os.path.dirname(self.origins[0])
        initial_text = user_friendly(initial_text) + "/"

        ipt = InputForPath(
            caption="Move to",
            initial_text=initial_text,
            on_done=self.move,
            on_change=None,
            on_cancel=None,
            create_from="",
            with_files=self.settings.get("complete_with_files_too"),
            pick_first=self.settings.get("pick_first"),
            case_sensitive=self.settings.get("case_sensitive"),
            log_in_status_bar=self.settings.get("log_in_status_bar"),
            log_template="Moving at {0}",
            browser_action={"title": "Move here", "func": self.move},
            browser_index=0,
        )

    def move(self, path, input_path):
        makedirs(path, exist_ok=True)
        for origin in self.origins:
            view = self.window.find_open_file(origin)
            new_name = os.path.join(path, os.path.basename(origin))
            try:
                os.rename(origin, new_name)
            except Exception as e:
                sublime.error_message(
                    "An error occured while moving the file " "{}".format(e)
                )
                raise OSError(
                    "An error occured while moving the file {0!r} "
                    "to {1!r}".format(origin, new_name)
                )
            if view:
                view.retarget(new_name)

        refresh_sidebar(self.settings, self.window)
