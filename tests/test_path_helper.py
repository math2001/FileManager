# -*- encoding: utf-8 -*-
import unittest
import sys
import os

sys.path.append("C:/Users/math/AppData/Roaming/Sublime Text 3/Packages/FileManager")
from pathhelper import *

sys.path.pop()


class PathHelperTest(unittest.TestCase):
    def test_computer_friendly(self):
        home = os.path.expanduser("~")
        tests = [
            ("~", home),
            ("~/", home + os.path.sep),
            ("~/hello/world", os.path.sep.join([home, "hello", "world"])),
            (
                "~/hello/world/",
                os.path.sep.join([home, "hello", "world"]) + os.path.sep,
            ),
            ("C:/hello/~/hi", os.path.sep.join([home, "hi"])),
            ("C:/hello/~/hi/~/yep", os.path.sep.join([home, "yep"])),
            ("C:/hello/~/hi/C:/hello/yep", os.path.sep.join(["C:", "hello", "yep"])),
            ("/hello/C:/hi/~/hey", os.path.sep.join([home, "hey"])),
            ("\\\\shared\\folder", "\\\\shared\\folder"),
            (
                "C:/courses/sublime text 3/",
                os.path.sep.join(["C:", "courses", "sublime text 3", ""]),
            ),
        ]
        for base, result in tests:
            if result is None:
                result = base
            self.assertEqual(computer_friendly(base), result)

    def test_user_friendly(self):
        home = os.path.expanduser("~")
        tests = [
            (home, "~"),
            ("C:/courses/sublime text 3/", None),
            ("C:/courses/sublime text 3/", None),
        ]

        for base, result in tests:
            if result is None:
                result = base
            self.assertEqual(user_friendly(base), result)


unittest.main()
