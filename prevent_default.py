import sublime_plugin
from Default.side_bar import RenamePathCommand


class NewFileAtCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        return False

    def is_enabled(self):
        return False


class DeleteFileCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        return False

    def is_enabled(self):
        return False


class NewFolderCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        return False

    def is_enabled(self):
        return False


class DeleteFolderCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        return False

    def is_enabled(self):
        return False


class RenamePathCommand(RenamePathCommand):
    def is_visible(self):
        return False


class FindInFolderCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        return False

    def is_enabled(self):
        return False


class OpenContainingFolderCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        return False

    def is_enabled(self):
        return False


class OpenInBrowserCommand(sublime_plugin.TextCommand):
    def is_visible(self):
        return False

    def is_enabled(self):
        return False
