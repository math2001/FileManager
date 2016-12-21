# -*- encoding: utf-8 -*-
import sublime
import sublime_plugin
import os
import subprocess
import shutil
import re

import imp
import sys

from .send2trash import send2trash
from .input_for_path import InputForPath
from .sublimefunctions import *

from .commands.copy import FmCopyCommand
from .commands.create import FmCreaterCommand, FmCreateCommand
from .commands.create_from_selection import FmCreateFileFromSelectionCommand
from .commands.delete import FmDeleteCommand
from .commands.duplicate import FmDuplicateCommand
from .commands.editto import FmEditToTheLeftCommand, FmEditToTheRightCommand
from .commands.find_in_files import FmFindInFilesCommand
from .commands.move import FmMoveCommand
from .commands.open_in_explorer import FmOpenInExplorerCommand
from .commands.open_in_browser import FmOpenInBrowserCommand
from .commands.open_terminal import FmOpenTerminalCommand
from .commands.rename import FmRenameCommand

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
        if BASE_NAME in view.file_name() and os.path.splitext(view.file_name())[1] == '.py':
            if view.file_name() == __file__:
                return
            else:
                _reload(view.file_name()[len(os.path.dirname(BASE_NAME)) + 1:])
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

# Now comes the funny part!

class FmEditReplace(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        kwargs.get('view', self.view).replace(edit, sublime.Region(*kwargs['region']), kwargs['text'])



# --- Extra ---

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
        snippet = view.settings().get('fm_insert_snippet_on_load', None)
        if snippet:
            view.run_command('insert_snippet', {'contents': snippet})
            view.settings().erase('fm_insert_snippet_on_load')
