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
        
    def test_calls_add_options(self):
    
        class Foo(cliapp.Application):
            def add_options(self):
                self.parser.add_option('--foo')
        foo = Foo()
        self.assert_(foo.parser.has_option('--foo'))
    
    def test_processes_input_files(self):
        self.inputs = []
        self.app.process_input = lambda name: self.inputs.append(name)
        self.app.run(args=['foo', 'bar'])
        self.assertEqual(self.inputs, ['foo', 'bar'])
        
    def test_sets_options_attribute(self):
        self.app.run(args=[])
        self.assert_(hasattr(self.app, 'options'))

