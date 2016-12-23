# -*- encoding: utf-8 -*-

from ..sublimefunctions import *
from .appcommand import AppCommand

class FmOpenInBrowserCommand(AppCommand):

    def run(self, paths=None, *args, **kwargs):
        self.window = get_window()
        self.view = get_view()

        if paths is None:
            paths = [self.view.file_name()]

        url = self.view.settings().get('url')
        if url is not None:
            url = url.strip('/')
        files = []
        folders = self.window.folders()

        for path in paths:

            if url is None:
                sublime.run_command('open_url', {'url': 'file:///' + path})
            else:
                for folder in folders:
                    if folder in path:
                        if os.path.splitext(os.path.basename(path))[0] == 'index':
                            path = os.path.dirname(path)
                        sublime.run_command('open_url', {'url': url + path.replace(folder, '') })
                        break
                    else:
                        sublime.run_command('open_url', {'url': 'file:///' + path})
