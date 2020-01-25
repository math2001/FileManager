# -*- encoding: utf-8 -*-
from .fmcommand import FmWindowCommand


class FmOpenAllCommand(FmWindowCommand):
    def run(self, files=[]):
        for file in files:
            self.window.open_file(file)

    def is_enabled(self, files=[]):
        return len(files) > 1
