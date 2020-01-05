# -*- encoding: utf-8 -*-
import sublime_plugin
from ..sublimefunctions import get_settings, to_snake_case


class AppCommand(sublime_plugin.ApplicationCommand):
    def is_visible(self, *args, **kwargs):
        settings = get_settings()
        show = settings.get(
            "show_" + to_snake_case(type(self).__name__.replace("Fm", ""))
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
                not settings.get("menu_without_distraction")
                or self.is_enabled(*args, **kwargs)
            )
        )
