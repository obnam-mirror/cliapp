# Copyright 2011  Lars Wirzenius
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import optparse
import unittest

import cliapp


class ApplicationTests(unittest.TestCase):

    def setUp(self):
        self.app = cliapp.Application()

    def test_creates_option_parser(self):
        self.assert_(isinstance(self.app.parser, optparse.OptionParser))
        
    def test_adds_default_options(self):
        self.assert_(self.app.parser.has_option('--version'))
