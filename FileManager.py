# -*- encoding: utf-8 -*-
import sys

import sublime
import sublime_plugin

# Clear module cache to force reloading all modules of this package.
prefix = __package__ + "."  # don't clear the base package
for module_name in [
    module_name
    for module_name in sys.modules
    if module_name.startswith(prefix) and module_name != __name__
]:
    del sys.modules[module_name]
prefix = None

from .libs.constants import SETTINGS, VIEW_SETTINGS

from .commands.copy import FmCopyCommand
from .commands.create import FmCreaterCommand, FmCreateCommand
from .commands.create_from_selection import FmCreateFileFromSelectionCommand
from .commands.delete import FmDeleteCommand
from .commands.duplicate import FmDuplicateCommand
from .commands.editto import FmEditToTheLeftCommand, FmEditToTheRightCommand
from .commands.find_in_files import FmFindInFilesCommand
from .commands.move import FmMoveCommand
from .commands.open_all import FmOpenAllCommand
from .commands.open_in_browser import FmOpenInBrowserCommand
from .commands.open_in_explorer import FmOpenInExplorerCommand
from .commands.open_terminal import FmOpenTerminalCommand
from .commands.rename import FmRenameCommand, FmRenamePathCommand


def plugin_loaded():
    # this use to be a supported setting, but we dropped it. (see #27)
    if sublime.load_settings(SETTINGS.file).get("auto_close_empty_groups") is not None:
        # we could remove the setting automatically, and install the
        # package if it was set to true, but it'd be an extra source
        # of bugs, and it doesn't take that much effort (it's a one
        # time thing, so it doesn't need to be automated)
        sublime.error_message(
            "FileManager\n\n"
            "auto_close_empty_groups is set, but this setting is no longer "
            "supported.\n\n"
            "Auto closing empty groups (in the layout) use to be a feature "
            "of FileManager, but it has now moved to it's own package.\n\n"
            "If you still want this behaviour, you can install "
            "AutoCloseEmptyGroup, it's available on package control.\n\n"
            "To disable this warning, unset the setting "
            "auto_close_empty_groups in FileManager.sublime-settings (search "
            "for Preferences: FileManager Settings in the command palette)"
        )


class FmEditReplace(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        kwargs.get("view", self.view).replace(
            edit, sublime.Region(*kwargs["region"]), kwargs["text"]
        )


class FmListener(sublime_plugin.EventListener):
    def on_load(self, view):
        settings = view.settings()
        snippet = settings.get(VIEW_SETTINGS.insert_snippet_on_load, None)
        if snippet:
            view.run_command("insert_snippet", {"contents": snippet})
            settings.erase(VIEW_SETTINGS.insert_snippet_on_load)
            if sublime.load_settins(SETTINGS.File).get(SETTINGS.save_after_creating):
                view.run_command("save")
            if settings.get(VIEW_SETTINGS.reveal_in_sidebar):
                view.window().run_command("reveal_in_side_bar")

    def on_text_command(self, view, command, args):
        if (
            command not in ["undo", "unindent"]
            or view.name() != "FileManager::input-for-path"
        ):
            return

        settings = view.settings()

        if command == "unindent":
            index = settings.get("completions_index")
            settings.set("go_backwards", True)
            view.run_command("insert", {"characters": "\t"})
            return

        # command_history: (command, args, times)
        first = view.command_history(0)
        if first[0] != "fm_edit_replace" or first[2] != 1:
            return

        second = view.command_history(-1)
        if (second[0] != "reindent") and not (
            second[0] == "insert" and second[1] == {"characters": "\t"}
        ):
            return

        settings.set("ran_undo", True)
        view.run_command("undo")

        index = settings.get("completions_index")
        if index == 0 or index is None:
            settings.erase("completions")
            settings.erase("completions_index")
        else:
            settings.set("completions_index", index - 1)
