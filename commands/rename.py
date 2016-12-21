# -*- encoding: utf-8 -*-
from FileManager.sublimefunctions import *
from FileManager.commands.appcommand import AppCommand
from FileManager.input_for_path import InputForPath


class FmRenameCommand(AppCommand):

    def run(self, paths=None):
        self.settings = get_settings()
        self.window = get_window()
        self.view = self.window.active_view()

        if paths is None:
            self.origin = self.view.file_name()
        else:
            self.origin = paths[0]

        filename, ext = os.path.splitext(os.path.basename(self.origin))

        self.input = InputForPath(caption='Rename to: ',
                                initial_text='{0}{1}'.format(filename, ext),
                                on_done=self.rename,
                                on_change=None,
                                on_cancel=None,
                                create_from=os.path.dirname(self.origin),
                                with_files=self.settings.get('complete_with_files_too'),
                                pick_first=self.settings.get('pick_first'),
                                case_sensitive=self.settings.get('case_sensitive'),
                                log_in_status_bar=self.settings.get('log_in_status_bar'),
                                log_template='Renaming to {0}',
                                enable_browser=True)
        self.input.input.view.selection.clear()
        self.input.input.view.selection.add(sublime.Region(0, len(filename)))

    def rename(self, dst, input_dst):

        def rename():
            makedirs(os.path.dirname(dst), exist_ok=True)
            os.rename(self.origin, dst)
            view = self.window.find_open_file(self.origin)
            if view:
                close_view(view)
            if os.path.isfile(dst):
                self.window.open_file(dst)


        if os.path.exists(dst):

            def open_file(self):
                return self.window.open_file(dst)

            def overwrite():
                try:
                    send2trash(dst)
                except OSError as e:
                    sublime.error_message('Unable to send to trash: ', e)
                    raise OSError('Unable to send the item {0!r} to the trash! Error {1!r}'.format(dst, e))

                rename()
            user_friendly_path = user_friendly(dst)
            return yes_no_cancel_panel(message=['This file already exists. Overwrite?',
                                                 user_friendly_path],
                                       yes=overwrite,
                                       no=open_file,
                                       cancel=None,
                                       yes_text=['Yes. Overwrite', user_friendly_path, 'will be sent to the trash, and then written'],
                                       no_text=['Just open the target file', user_friendly_path],
                                       cancel_text=["No, don't do anything"])

        rename()
        refresh_sidebar(self.settings, self.window)

    def is_enabled(self, paths=None):
        return paths is None or len(paths) == 1
