# -*- encoding: utf-8 -*-
from ..libs.sublimefunctions import *
from .appcommand import AppCommand


class FmOpenAllCommand(AppCommand):
    def run(self, files=None):
        assert files is not None, "fm_open_all called without any files (files=None)"
        for file in files:
            get_window().open_file(file)

    def is_enabled(self, **kwargs):
        return len(kwargs["files"]) > 1
