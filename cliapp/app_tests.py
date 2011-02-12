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
import StringIO
import unittest

import cliapp


class ApplicationTests(unittest.TestCase):

    def setUp(self):
        self.app = cliapp.Application()

    def test_creates_option_parser(self):
        self.assert_(isinstance(self.app.parser, optparse.OptionParser))
        
    def test_adds_default_options(self):
        self.assert_(self.app.parser.has_option('--version'))
        self.assert_(self.app.parser.has_option('--help'))
        
    def test_gets_version(self):
        app = cliapp.Application(version='1.2.3')
        self.assertEqual(app.parser.get_version(), '1.2.3')
        
    def test_calls_add_settings_only_in_run(self):
    
        class Foo(cliapp.Application):
            def add_settings(self):
                self.add_string_setting(['foo'], '')
        foo = Foo()
        self.assertFalse(foo.parser.has_option('--foo'))
        foo.run(args=[])
        self.assert_(foo.parser.has_option('--foo'))
    
    def test_run_calls_process_args(self):
        self.called = None
        self.app.process_args = lambda args: setattr(self, 'called', args)
        self.app.run(args=['foo', 'bar'])
        self.assertEqual(self.called, ['foo', 'bar'])
    
    def test_processes_input_files(self):
        self.inputs = []
        self.app.process_input = lambda name: self.inputs.append(name)
        self.app.run(args=['foo', 'bar'])
        self.assertEqual(self.inputs, ['foo', 'bar'])
        
    def test_sets_options_attribute(self):
        self.app.run(args=[])
        self.assert_(hasattr(self.app, 'options'))

    def test_parses_options(self):
        self.app.add_string_setting(['foo'], 'foo help')
        self.app.add_boolean_setting(['bar'], 'bar help')
        self.app.run(args=['--foo=foovalue', '--bar'])
        self.assertEqual(self.app['foo'], 'foovalue')
        self.assertEqual(self.app['bar'], True)

    def test_open_input_opens_file(self):
        f = self.app.open_input('/dev/null')
        self.assert_(isinstance(f, file))
        self.assertEqual(f.mode, 'r')
        
    def test_open_input_opens_file_in_binary_mode_when_requested(self):
        f = self.app.open_input('/dev/null', mode='rb')
        self.assertEqual(f.mode, 'rb')

    def test_process_input_calls_open_input(self):
        self.called = None
        def open_input(name):
            self.called = name
            return StringIO.StringIO('')
        self.app.open_input = open_input
        self.app.process_input('foo')
        self.assertEqual(self.called, 'foo')

    def test_processes_input_lines(self):

        lines = []
        class Foo(cliapp.Application):
            def open_input(self, name):
                return StringIO.StringIO(''.join('%s%d\n' % (name, i)
                                                 for i in range(2)))
            def process_input_line(self, name, line):
                lines.append(line)

        foo = Foo()
        foo.run(args=['foo', 'bar'])
        self.assertEqual(lines, ['foo0\n', 'foo1\n', 'bar0\n', 'bar1\n'])

    def test_adds_string_setting(self):
        self.app.add_string_setting(['foo'], 'foo help')
        self.assert_(self.app.parser.has_option('--foo'))
        option = self.app.parser.get_option('--foo')
        self.assertEqual(option.help, 'foo help')

    def test_adds_boolean_setting(self):
        self.app.add_boolean_setting(['foo'], 'foo help')
        self.assert_(self.app.parser.has_option('--foo'))
        option = self.app.parser.get_option('--foo')
        self.assertEqual(option.help, 'foo help')
        
    def test_adds_bytesize_setting(self):
        self.app.add_bytesize_setting(['foo'], 'foo help')
        self.assert_(self.app.parser.has_option('--foo'))
        option = self.app.parser.get_option('--foo')
        self.assertEqual(option.help, 'foo help')

    def test_parses_bytesize_option(self):
        self.app.add_bytesize_setting(['foo'], 'foo help')

        self.app.run(args=['--foo=xyzzy'])
        self.assertEqual(self.app['foo'], 0)

        self.app.run(args=['--foo=123'])
        self.assertEqual(self.app['foo'], 123)

        self.app.run(args=['--foo=123k'])
        self.assertEqual(self.app['foo'], 123 * 1000)

        self.app.run(args=['--foo=123m'])
        self.assertEqual(self.app['foo'], 123 * 1000**2)

        self.app.run(args=['--foo=123g'])
        self.assertEqual(self.app['foo'], 123 * 1000**3)

        self.app.run(args=['--foo=123t'])
        self.assertEqual(self.app['foo'], 123 * 1000**4)

        self.app.run(args=['--foo=123kib'])
        self.assertEqual(self.app['foo'], 123 * 1024)

        self.app.run(args=['--foo=123mib'])
        self.assertEqual(self.app['foo'], 123 * 1024**2)

        self.app.run(args=['--foo=123gib'])
        self.assertEqual(self.app['foo'], 123 * 1024**3)

        self.app.run(args=['--foo=123tib'])
        self.assertEqual(self.app['foo'], 123 * 1024**4)
        
    def test_adds_integer_setting(self):
        self.app.add_integer_setting(['foo'], 'foo help')
        self.assert_(self.app.parser.has_option('--foo'))
        option = self.app.parser.get_option('--foo')
        self.assertEqual(option.help, 'foo help')

    def test_parses_integer_option(self):
        self.app.add_integer_setting(['foo'], 'foo help', default=123)

        self.app.run(args=[])
        self.assertEqual(self.app['foo'], 123)

        self.app.run(args=['--foo=123'])
        self.assertEqual(self.app['foo'], 123)

    def test_run_prints_out_error_for_exception(self):
        def raise_error(args):
            raise Exception('xxx')
        self.app.process_args = raise_error
        f = StringIO.StringIO()
        self.assertRaises(SystemExit, self.app.run, [], stderr=f)
        self.assert_('xxx' in f.getvalue())

