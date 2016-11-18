# -*- encoding: utf-8 -*-

"""
    Push FileManager to ST2 packages directory.
"""

import shutil
import os

dst = 'C:\\Users\\math\\AppData\\Roaming\\Sublime Text 2\\Packages\\' + 'FileManager\\'


def copy_and_overwrite(from_path, to_path):

    def ignore(path, items):
        return ['.git']

    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path, ignore=ignore)

if __name__ == '__main__':
    print('Pushing to {}'.format(dst))
    copy_and_overwrite('.', dst)
    print('Finish copying!')
