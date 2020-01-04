# -*- encoding: utf-8 -*-
import os.path
from ..sublimefunctions import *
from .appcommand import AppCommand
from ..input_for_path import InputForPath


class FmCreaterCommand(AppCommand):
    """Create folder(s)/files that might be required and the
    final ones if it doesn't exists. Finaly, opens the file"""

    def run(self, abspath, input_path):
        input_path = user_friendly(input_path)
        if input_path[-1] == "/":
            return makedirs(abspath, exist_ok=True)
        if not os.path.isfile(abspath):
            makedirs(os.path.dirname(abspath), exist_ok=True)
            with open(abspath, "w") as fp:
                pass
            template = get_template(abspath)
        else:
            template = None
        window = get_window()
        view = window.open_file(abspath)
        settings = view.settings()
        if template:
            settings.set("fm_insert_snippet_on_load", template)
        refresh_sidebar(settings, window)
        if get_settings().get("reveal_in_sidebar"):
            settings.set("fm_reveal_in_sidebar", True)
            sublime.set_timeout_async(
                lambda: window.run_command("reveal_in_side_bar"), 500
            )


class FmCreateCommand(AppCommand):
    def run(
        self,
        paths=None,
        initial_text="",
        start_with_browser=False,
        no_browser_action=False,
    ):
        self.settings = get_settings()
        self.window = sublime.active_window()
        self.index_folder_separator = self.settings.get("index_folder_" + "separator")
        self.default_index = self.settings.get("default_index")

        self.folders = self.window.folders()

        self.view = get_view()

        self.know_where_to_create_from = paths is not None

        if paths is not None:
            # creating from the sidebar
            create_from = paths[0].replace("${packages}", sublime.packages_path())
            # you can right-click on a file, and run `New...`
            if os.path.isfile(create_from):
                create_from = os.path.dirname(create_from)
        elif self.folders:
            # it is going to be interactive, so it'll be
            # understood from the input itself
            create_from = None
        elif self.view.file_name() is not None:
            create_from = os.path.dirname(self.view.file_name())
            self.know_where_to_create_from = True
        else:
            # from home
            create_from = "~"

        self.input = InputForPath(
            caption="New: ",
            initial_text=initial_text,
            on_done=self.on_done,
            on_change=self.on_change,
            on_cancel=None,
            create_from=create_from,
            with_files=self.settings.get("complete_with_files_too"),
            pick_first=self.settings.get("pick_first"),
            case_sensitive=self.settings.get("case_sensitive"),
            log_in_status_bar=self.settings.get("log_in_status_bar"),
            log_template="Creating at {0}",
            start_with_browser=start_with_browser,
            no_browser_action=no_browser_action,
        )

    def on_change(self, input_path, path_to_create_choosed_from_browsing):
        if path_to_create_choosed_from_browsing:
            # The user has browsed, we let InputForPath select the path
            return
        if self.know_where_to_create_from:
            return
        elif self.folders:
            splited_input = input_path.split(self.index_folder_separator, 1)
            if len(splited_input) == 1:
                index = self.default_index
            elif isdigit(splited_input[0]):
                index = int(splited_input[0])
            else:
                return None, input_path
            return self.folders[index], splited_input[-1]
        return "~", input_path

    def is_enabled(self, paths=None):
        return paths is None or len(paths) == 1

    def on_done(self, abspath, input_path):
        sublime.run_command(
            "fm_creater", {"abspath": abspath, "input_path": input_path}
        )
