# -*- encoding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function, division

from .sublimefunctions import *
from .FMcommands.appcommand import AppCommand

class FmEditToTheRightCommand(AppCommand):

    def run(self, files=None):
        v = get_view()
        w = get_window()

        if files is None:
            files = [v.file_name()]

        w.set_layout({
            "cols": [0.0, 0.5, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
        })
        for i, file in enumerate(files, 1):
            w.set_view_index(w.open_file(file), 1, 0)
        w.focus_group(1)

    def is_enabled(self, files=None):
        return (files is None or len(files) >= 1) and get_window().active_group() != 1


class FmEditToTheLeftCommand(AppCommand):

    def run(self, files=None):
        v = get_view()
        w = get_window()

        if files is None:
            files = [v.file_name()]

        w.set_layout({
            "cols": [0.0, 0.5, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
        })
        for file in files:
            w.set_view_index(w.open_file(file), 0, 0)

        w.focus_group(0)

    def is_enabled(self, files=None):
        return (files is None or len(files) >= 1) and get_window().active_group() != 0
