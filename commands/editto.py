# -*- encoding: utf-8 -*-
from .fmcommand import FmWindowCommand


class FmEditToTheRightCommand(FmWindowCommand):
    def run(self, files=None):
        self.window.set_layout(
            {
                "cols": [0.0, 0.5, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
            }
        )
        for file in files or [self.window.active_view().file_name()]:
            self.window.set_view_index(self.window.open_file(file), 1, 0)

        self.window.focus_group(1)

    def is_enabled(self, files=None):
        return (files is None or len(files) >= 1) and self.window.active_group() != 1


class FmEditToTheLeftCommand(FmWindowCommand):
    def run(self, files=None):
        self.window.set_layout(
            {
                "cols": [0.0, 0.5, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
            }
        )
        for file in files or [self.window.active_view().file_name()]:
            self.window.set_view_index(self.window.open_file(file), 0, 0)

        self.window.focus_group(0)

    def is_enabled(self, files=None):
        return (files is None or len(files) >= 1) and self.window.active_group() != 1
