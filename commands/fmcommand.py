# -*- encoding: utf-8 -*-
import sublime
import sublime_plugin


class FmWindowCommand(sublime_plugin.WindowCommand):

    settings = sublime.load_settings("FileManager.sublime-settings")

    def is_visible(self, *args, **kwargs):
        show = self.settings.get(
            "show_{}_command".format(self.name().replace("fm_", ""))
        )
        if show is None:
            # this should never happen, this is an error
            # we could nag the user to get him to report that issue,
            # but that's going to make this plugin really painful to use
            # So, I just print something to the console, and hope someone
            # sees and reports it
            print(
                "FileManager: No setting available for the command {!r}. This is an internal error, please report it".format(
                    type(self).__name__
                )
            )
            show = True

        return bool(
            show
            and (
                not self.settings.get("menu_without_distraction")
                or self.is_enabled(*args, **kwargs)
            )
        )
