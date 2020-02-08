# -*- encoding: utf-8 -*-
import sublime
import sublime_plugin


class FmWindowCommand(sublime_plugin.WindowCommand):

    @property
    def settings(cls):
        try:
            return cls.settings_
        except AttributeError:
            cls.settings_ = sublime.load_settings("FileManager.sublime-settings")
            return cls.settings_

    def is_visible(self, *args, **kwargs):
        name = "show_{}_command".format(self.name().replace("fm_", ""))
        show = self.settings.get(name)
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
