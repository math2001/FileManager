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
        if BASE_NAME in view.file_name() and \
            os.path.splitext(view.file_name())[1] == '.py':
            if view.file_name() == __file__:
                return
            else:
                _reload(view.file_name()[len(os.path.dirname(BASE_NAME)) + 1:])
            close = True
            if view.window().find_open_file(__file__):
                close = False
            file_view = view.window().open_file(__file__)
            file_view.run_command('save')

            def callback():
                view.window().focus_view(view)
                if close:
                    file_view.close()
            sublime.set_timeout(callback, 200)
            # reload the main file (this one)
            _reload(__file__[len(os.path.dirname(BASE_NAME)) + 1:])


if not hasattr(sublime.View, 'close'):
    def close_file_poyfill(view):
        window = get_window()
        window.focus_view(view)
        window.run_command('close')

    sublime.View.close = close_file_poyfill


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
