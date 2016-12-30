# -*- encoding: utf-8 -*-
import sublime
import sublime_plugin
import os

import imp
import sys

from .sublimefunctions import *
from .FMcommands.copy import FmCopyCommand
from .FMcommands.create import FmCreaterCommand, FmCreateCommand
from .FMcommands.create_from_selection import FmCreateFileFromSelectionCommand
from .FMcommands.delete import FmDeleteCommand
from .FMcommands.duplicate import FmDuplicateCommand
from .FMcommands.editto import FmEditToTheLeftCommand, FmEditToTheRightCommand
from .FMcommands.find_in_files import FmFindInFilesCommand
from .FMcommands.move import FmMoveCommand
from .FMcommands.open_in_explorer import FmOpenInExplorerCommand
from .FMcommands.open_in_browser import FmOpenInBrowserCommand
from .FMcommands.open_terminal import FmOpenTerminalCommand
from .FMcommands.rename import FmRenameCommand

BASE_NAME = os.path.dirname(__file__)


def _reload(file):
    if file.endswith('.pyc'):
        file = file[:-1]
    file = file[:-3]
    module = sys.modules.get(file.replace(os.path.sep, '.'))
    if module:
        imp.reload(module)

# auto reload sub files - for dev


class FmDevListener(sublime_plugin.EventListener):

    def on_post_save(self, view):
        """Reload FileManager
        To use this, you need to have this plugin:
        https://github.com/math2001/sublime-plugin-reloader"""
        if not (os.path.dirname(__file__) in view.file_name() and
            view.file_name().endswith('.py')):
            return
        sublime.run_command('reload_plugin', {
            'main': __file__,
            'folders': ["FMcommands"],
            'scripts': ["input_for_path", "sublimefunctions",
                    "pathhelper"],
        })




class FmEditReplace(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        kwargs.get('view', self.view).replace(edit,
                                              sublime.Region(*kwargs['region']),
                                              kwargs['text'])

# --- Listener --- (pathetic, right?) :D


class FmListener(sublime_plugin.EventListener):

    def on_close(self, view):
        if view.settings().get('auto_close_empty_groups') is not True:
            return

        def run():
            w = get_window()
            reset_layouts = False
            for group in range(w.num_groups()):
                if len(w.views_in_group(group)) == 0:
                    reset_layouts = True

            if reset_layouts:
                w.set_layout({
                    "cols": [0.0, 1.0],
                    "rows": [0.0, 1.0],
                    "cells": [[0, 0, 1, 1]]
                })

        sublime.set_timeout(run, 50)

    def on_load(self, view):
        settings = view.settings()
        snippet = settings.get('fm_insert_snippet_on_load', None)
        if snippet:
            view.run_command('insert_snippet', {'contents': snippet})
            settings.erase('fm_insert_snippet_on_load')
            if get_settings().get('save_after_creating'):
                view.run_command('save')
            if settings.get('fm_reveal_in_sidebar'):
                view.window().run_command('reveal_in_side_bar')

    def on_text_command(self, view, command, args):
        if command != 'undo' or view.name() != 'FileManager::input-for-path':
            return

        settings = view.settings()

        # command_history: (command, args, times)
        first = view.command_history(0)
        if first[0] != 'fm_edit_replace' or first[2] != 1:
            return

        second = view.command_history(-1)
        if ((second[0] != 'reindent') and
            not (second[0] == 'insert' and second[1] == {'characters': '\t'})):
            return

        settings.set('ran_undo', True)
        view.run_command('undo')

        index = settings.get('completions_index')
        if index == 0 or index is None:
            settings.erase('completions')
            settings.erase('completions_index')
        else:
            settings.set('completions_index', index - 1)
