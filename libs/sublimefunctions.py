import os

import sublime

from .pathhelper import *

TEMPLATE_FOLDER = None


def md(*t, **kwargs):
    sublime.message_dialog(kwargs.get("sep", "\n").join([str(el) for el in t]))


def sm(*t, **kwargs):
    sublime.status_message(kwargs.get("sep", " ").join([str(el) for el in t]))


def em(*t, **kwargs):
    sublime.error_message(kwargs.get("sep", " ").join([str(el) for el in t]))


def isST3():
    return int(sublime.version()) > 3000


def get_settings():
    return sublime.load_settings("FileManager.sublime-settings")


def refresh_sidebar(settings=None, window=None):
    if window is None:
        window = active_window()
    if settings is None:
        settings = window.active_view().settings()
    if settings.get("explicitly_refresh_sidebar") is True:
        window.run_command("refresh_folder_list")


def makedirs(path, exist_ok=True):
    if exist_ok is False:
        os.makedirs(path)
    else:
        try:
            os.makedirs(path)
        except OSError:
            pass


def quote(s):
    return '"{0}"'.format(s)


def get_window():
    return sublime.active_window()


def get_view():
    window = get_window()
    if not window:
        return
    return window.active_view()


def copy(el):
    return sublime.set_clipboard(el)


def file_get_content(path):
    with open(path, "r") as fp:
        return fp.read()


def get_template(created_file):
    """Return the right template for the create file"""
    global TEMPLATE_FOLDER

    if TEMPLATE_FOLDER is None:
        TEMPLATE_FOLDER = os.path.join(sublime.packages_path(), "User", ".FileManager")
        makedirs(TEMPLATE_FOLDER, exist_ok=True)

    template_files = os.listdir(TEMPLATE_FOLDER)
    for item in template_files:
        if (
            os.path.splitext(item)[0] == "template"
            and os.path.splitext(item)[1] == os.path.splitext(created_file)[1]
        ):
            return file_get_content(os.path.join(TEMPLATE_FOLDER, item))
    return ""


def isdigit(string):
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True


def yes_no_cancel_panel(
    message,
    yes,
    no,
    cancel,
    yes_text="Yes",
    no_text="No",
    cancel_text="Cancel",
    **kwargs
):
    loc = locals()
    if isinstance(message, list):
        message.append("Do not select this item")
    else:
        message = [message, "Do not select this item"]
    items = [message, yes_text, no_text, cancel_text]

    def get_max(item):
        return len(item)

    maxi = len(max(items, key=get_max))
    for i, item in enumerate(items):
        while len(items[i]) < maxi:
            items[i].append("")

    def on_done(index):
        if index in [-1, 3] and cancel:
            return cancel(*kwargs.get("args", []), **kwargs.get("kwargs", {}))
        elif index == 1 and yes:
            return yes(*kwargs.get("args", []), **kwargs.get("kwargs", {}))
        elif index == 2 and no:
            return no(*kwargs.get("args", []), **kwargs.get("kwargs", {}))
        elif index == 0:
            return yes_no_cancel_panel(**loc)

    window = get_window()
    window.show_quick_panel(items, on_done, 0, 1)


def close_view(view_to_close, dont_prompt_save=False):
    if dont_prompt_save:
        view_to_close.set_scratch(True)
    if isST3():
        view_to_close.close()
        return
    window = view_to_close.window()
    window.focus_view(view_to_close)
    window.run_command("close")


def to_snake_case(camelCaseString):
    snake = ""
    for char in camelCaseString:
        if char.isupper():
            if snake == "":
                snake += char.lower()
            else:
                snake += "_" + char.lower()
        else:
            snake += char
    return snake


def StdClass(name="Unknown"):
    # add the str() function because of the unicode in Python 2
    return type(str(name).title(), (), {})


def transform_aliases(window, string):
    """Transform aliases using the settings and the default variables
    It's recursive, so you can use aliases *in* your aliases' values
    """

    vars = window.extract_variables()
    vars.update(get_settings().get("aliases"))

    def has_unescaped_dollar(string):
        start = 0
        while True:
            index = string.find("$", start)
            if index < 0:
                return False
            elif string[index - 1] == "\\":
                start = index + 1
            else:
                return True

    string = string.replace("$$", "\\$")

    inifinite_loop_counter = 0
    while has_unescaped_dollar(string):
        inifinite_loop_counter += 1
        if inifinite_loop_counter > 100:
            sublime.error_message(
                "Infinite loop: you better check your "
                "aliases, they're calling each other "
                "over and over again."
            )
            if get_settings().get("open_help_on_alias_infinite_loop", True) is True:

                sublime.run_command(
                    "open_url",
                    {
                        "url": "https://github.com/math2001/ "
                        "FileManager/wiki/Aliases "
                        "#watch-out-for-infinite-loops"
                    },
                )
            return string
        string = sublime.expand_variables(string, vars)

    return string
