# -*- encoding: utf-8 -*-
import re
import json
from ..libs.input_for_path import InputForPath
from ..libs.sublimefunctions import *
from .appcommand import AppCommand

def getComposerJson(path):
    # add slash to path
    path = path.replace(r"\/$", "") + "/"

    try:
        return json.load(open(path + "composer.json", "r"))
    except Exception as e:
        return False

def getNamespaceByFolder(namespaces, folder, path):

    # check if namespaces is type of `dict`
    if type(namespaces) is not dict:
        return False

    # remove filename from path
    # remove folder path from path
    #
    # keep path from folder where file will be created
    path = re.sub(r'\/[A-z_\-0-9]+\.php$', "", path.replace(folder, ""))

    # loop trough all namespaces
    for key in namespaces:
        # get namespace path
        value = [namespaces[key]][0]

        # check if path starts with namespace path
        if path.startswith("/" + value):
            # return namespace
            return key + re.sub(r"^\\", "", path.replace(value, "").replace("/", "\\"))

    return False

class FmCreaterPhpClassCommand(AppCommand):

    """Create PHP class"""
    def run(self, abspath, className, type):
        # clear abspath
        abspath = abspath.replace(".php", "") + ".php"

        # get class name
        className = toCamelCase(user_friendly(className))

        # make sure that input has `.php` extension
        className = className.replace(".php", "")

        folders = get_window().folders()

        # define namespace
        namespace = False

        # loop trough all folders
        for folder in folders:
            # when file will be made inside this folder
            if folder in abspath:
                # get composer json
                data = getComposerJson(folder)

                # when there was no composer.json found
                if data == False:
                    continue

                try:
                    # check if is inside unit/feature tests folder
                    if '/test/' in abspath.replace(folder, "").lower() or '/tests/' in abspath.replace(folder, "").lower():
                        namespaces = data['autoload-dev']['psr-4']
                    else:
                        namespaces = data['autoload']['psr-4']

                    # get namespace from `composer.json`
                    namespace = getNamespaceByFolder(namespaces, folder, abspath)
                except Exception as e:
                    continue

        # check if file(class) already exists
        if os.path.isfile(abspath):
            sublime.error_message(f"Class {className} already exists!")
            return

        # check if classname contains seperator
        if os.sep in className:
            sublime.error_message("You can't have {os.sep} inside class name")
            return

        # define namespace
        namespace = "\nnamespace " + namespace + ";\n" if namespace != False else ""

        # define class file content
        classFileContent = f"<?php\n\ndeclare(strict_types=1);\n{namespace}\n{type} {className}\n{{\n}}"

        # create file
        with open(abspath, "w") as f:
            # write base class structure to file
            f.write(classFileContent)

        f.close()

        # open file inside window
        view = get_window().open_file(abspath)

        # set default extension
        view.settings().set('default_extension', 'php')


class FmCreatePhpClassCommand(AppCommand):
    def run(
        self,
        type,
        paths=None,
        initial_text="",
        start_with_browser=False,
        no_browser_action=False
    ):
        self.settings = get_settings()
        self.window = sublime.active_window()
        self.index_folder_separator = self.settings.get("index_folder_" + "separator")
        self.default_index = self.settings.get("default_index")

        self.folders = self.window.folders()

        self.view = get_view()

        self.know_where_to_create_from = paths is not None

        if paths is not None:
            # creating from the sidebar
            create_from = paths[0].replace("${packages}", sublime.packages_path())

            create_from = transform_aliases(self.window, create_from)

            # you can right-click on a file, and run `New...`
            if os.path.isfile(create_from):
                create_from = os.path.dirname(create_from)
        elif self.folders:
            # it is going to be interactive, so it'll be
            # understood from the input itself
            create_from = None
        elif self.view.file_name() is not None:
            create_from = os.path.dirname(self.view.file_name())
            self.know_where_to_create_from = True
        else:
            # from home
            create_from = "~"

        self.input = InputForPath(
            caption=f"New PHP {type}: ",
            type=type,
            initial_text=initial_text,
            on_done=self.on_done,
            on_change=self.on_change,
            on_cancel=None,
            create_from=create_from,
            with_files=self.settings.get("complete_with_files_too"),
            pick_first=self.settings.get("pick_first"),
            case_sensitive=self.settings.get("case_sensitive"),
            log_in_status_bar=self.settings.get("log_in_status_bar"),
            log_template="Creating at {0}",
            start_with_browser=start_with_browser,
            no_browser_action=no_browser_action,
        )

    def on_change(self, input_path, path_to_create_choosed_from_browsing):
        if path_to_create_choosed_from_browsing:
            # The user has browsed, we let InputForPath select the path
            return
        if self.know_where_to_create_from:
            return
        elif self.folders:
            splited_input = input_path.split(self.index_folder_separator, 1)
            if len(splited_input) == 1:
                index = self.default_index
            elif isdigit(splited_input[0]):
                index = int(splited_input[0])
            else:
                return None, input_path
            return self.folders[index], splited_input[-1]
        return "~", input_path

    def is_enabled(self, paths=None):
        return paths is None or len(paths) == 1

    def on_done(self, abspath, input_path, type):
        sublime.run_command(
            "fm_creater_php_class", {"abspath": abspath, "className": input_path, "type": type}
        )
