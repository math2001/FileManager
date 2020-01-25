# -*- encoding: utf-8 -*-
import os

import sublime

from .fmcommand import FmWindowCommand


class FmOpenInBrowserCommand(FmWindowCommand):
    def run(self, paths=None, *args, **kwargs):
        folders = self.window.folders()

        view = self.window.active_view()
        url = view.settings().get("url")
        if url is not None:
            url = url.strip("/")

        for path in paths or [view.file_name()]:
            if url is None:
                self.open_url("file:///" + path)
            else:
                for folder in folders:
                    if folder in path:
                        if os.path.splitext(os.path.basename(path))[0] == "index":
                            path = os.path.dirname(path)
                        self.open_url(url + path.replace(folder, ""))
                        break
                    else:
                        self.open_url("file:///" + path)

    def open_url(self, url):
        sublime.run_command("open_url", {"url": url})
