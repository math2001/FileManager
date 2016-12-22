from __future__ import absolute_import, unicode_literals, print_function, division
import os


def user_friendly(path):
    path = computer_friendly(path)
    return path.replace(os.path.expanduser('~'), '~').replace(os.path.sep, '/')
    return path.replace(os.path.expanduser('~'), '~').replace(os.path.sep, '/')

def computer_friendly(path):
    """Also makes sure the path is valid"""
    if '~' in path:
        path = path[path.rfind("~"):]
    if ':' in path:
        path = path[path.rfind(':')-1:]
    path = path.replace('~', os.path.expanduser('~'))
    path = path.replace('/', os.path.sep)
    return path

def commonpath(paths):
    """Given a sequence of path names, returns the longest common sub-path."""

    if not paths:
        raise ValueError('commonpath() arg is an empty sequence')

    sep = '\\'
    altsep = '/'
    curdir = '.'

    try:
        drivesplits = [os.path.splitdrive(p.replace(altsep, sep).lower()) for p in paths]
        split_paths = [p.split(sep) for d, p in drivesplits]

        try:
            isabs, = set(p[:1] == sep for d, p in drivesplits)
        except ValueError:
            raise ValueError("Can't mix absolute and relative paths")

        # Check that all drive letters or UNC paths match. The check is made only
        # now otherwise type errors for mixing strings and bytes would not be
        # caught.
        if len(set(d for d, p in drivesplits)) != 1:
            raise ValueError("Paths don't have the same drive")

        drive, path = os.path.splitdrive(paths[0].replace(altsep, sep))
        common = path.split(sep)
        common = [c for c in common if c and c != curdir]

        split_paths = [[c for c in s if c and c != curdir] for s in split_paths]
        s1 = min(split_paths)
        s2 = max(split_paths)
        for i, c in enumerate(s1):
            if c != s2[i]:
                common = common[:i]
                break
        else:
            common = common[:len(s1)]

        prefix = drive + sep if isabs else drive
        return prefix + sep.join(common)
    except (TypeError, AttributeError):
        genericpath._check_arg_types('commonpath', *paths)
        raise
