# -*- encoding: utf-8 -*-
import os
import imp
import sys

import sublime
import sublime_plugin

from .libs.sublimefunctions import *
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
from .commands.rename import FmRenameCommand

BASE_NAME = os.path.dirname(__file__)


def _reload(file):
    if file.endswith(".pyc"):
        file = file[:-1]
    file = file[:-3]
    module = sys.modules.get(file.replace(os.path.sep, "."))
    if module:
        imp.reload(module)


# auto reload sub files - for dev


def plugin_loaded():
    settings = get_settings()
    # this use to be a supported setting, but we dropped it. (see #27)
    if settings.get("auto_close_empty_groups") is not None:
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


class FmDevListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        """Reload FileManager
        To use this, you need to have this plugin:
        https://github.com/math2001/sublime-plugin-reloader"""
        if not (
            os.path.dirname(__file__) in view.file_name()
            and view.file_name().endswith(".py")
        ):
            return
        sublime.run_command(
            "reload_plugin",
            {
                "main": __file__,
                "folders": ["FMcommands"],
                "scripts": ["input_for_path", "sublimefunctions", "pathhelper"],
            },
        )


class FmEditReplace(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        kwargs.get("view", self.view).replace(
            edit, sublime.Region(*kwargs["region"]), kwargs["text"]
        )


class FmListener(sublime_plugin.EventListener):
    def on_load(self, view):
        settings = view.settings()
        snippet = settings.get("fm_insert_snippet_on_load", None)
        if snippet:
            view.run_command("insert_snippet", {"contents": snippet})
            settings.erase("fm_insert_snippet_on_load")
            if get_settings().get("save_after_creating"):
                view.run_command("save")
            if settings.get("fm_reveal_in_sidebar"):
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
