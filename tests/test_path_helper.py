# -*- encoding: utf-8 -*-

import unittest
import sys
import os

sys.path.append('C:/Users/math/AppData/Roaming/Sublime Text 3/Packages/FileManager')
from pathhelper import *
sys.path.pop()

class PathHelperTest(unittest.TestCase):

    def test_computer_friendly(self):
        home = os.path.expanduser('~')
        tests = [
            ('~', home),
            ('~/', home + os.path.sep),
            ('~/hello/world', os.path.sep.join([home, 'hello', 'world'])),
            ('~/hello/world/', os.path.sep.join([home, 'hello', 'world']) + os.path.sep),
            ('C:/hello/~/hi', os.path.sep.join([home, 'hi'])),
            ('C:/hello/~/hi/~/yep', os.path.sep.join([home, 'yep'])),
            ('C:/hello/~/hi/C:/hello/yep', os.path.sep.join(['C:', 'hello', 'yep'])),
            ('/hello/C:/hi/~/hey', os.path.sep.join([home, 'hey'])),
            ('\\\\shared\\folder', '\\\\shared\\folder')
        ]
        for base, result in tests:
            self.assertEqual(computer_friendly(base), result)


unittest.main()
