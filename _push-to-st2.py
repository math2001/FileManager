# -*- encoding: utf-8 -*-

"""
    Push FileManager to ST2 packages directory.
"""

import shutil
import os

dst = 'C:\\Users\\math\\AppData\\Roaming\\Sublime Text 2\\Packages\\' + 'FileManager'


def copy_and_overwrite(from_path, to_path):

    def ignore(path, items):
        return ['.git', 'docs']

    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path, ignore=ignore)

if __name__ == '__main__':
    print('Pushing to {0}...'.format(dst))
    try:
        copy_and_overwrite('.', dst)
    except PermissionError as e:
        print('-' * 58)
        print('!! Sublime text 2 needs to be closed to be able to push !!')
        print('-' * 58)
        print(e)
    else:   
        print('Finish copying!')
