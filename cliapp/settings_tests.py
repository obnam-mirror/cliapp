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
import sys
import unittest

import cliapp


class SettingsTests(unittest.TestCase):

    def setUp(self):
        self.settings = cliapp.Settings('appname', '1.0')

    def test_creates_option_parser(self):
        self.assert_(isinstance(self.settings.parser, optparse.OptionParser))
        
    def test_adds_default_options(self):
        self.assert_(self.settings.parser.has_option('--version'))
        self.assert_(self.settings.parser.has_option('--help'))
        self.assert_(self.settings.parser.has_option('--output'))
        self.assert_(self.settings.parser.has_option('--log'))
        self.assert_(self.settings.parser.has_option('--log-level'))

    def test_parses_options(self):
        self.settings.add_string_setting(['foo'], 'foo help')
        self.settings.add_boolean_setting(['bar'], 'bar help')
        self.settings.parse_args(['--foo=foovalue', '--bar'])
        self.assertEqual(self.settings['foo'], 'foovalue')
        self.assertEqual(self.settings['bar'], True)

    def test_does_not_have_foo_setting_by_default(self):
        self.assertFalse('foo' in self.settings)

    def test_adds_string_setting(self):
        self.settings.add_string_setting(['foo'], 'foo help')
        self.assert_(self.settings.parser.has_option('--foo'))
        self.assert_('foo' in self.settings)
        option = self.settings.parser.get_option('--foo')
        self.assertEqual(option.help, 'foo help')

    def test_adds_string_list_setting(self):
        self.settings.add_string_list_setting(['foo'], 'foo help')
        self.assert_(self.settings.parser.has_option('--foo'))
        self.assert_('foo' in self.settings)
        option = self.settings.parser.get_option('--foo')
        self.assertEqual(option.help, 'foo help')

    def test_string_list_is_empty_list_by_default(self):
        self.settings.add_string_list_setting(['foo'], '')
        self.settings.parse_args([])
        self.assertEqual(self.settings['foo'], [])

    def test_string_list_parses_one_item(self):
        self.settings.add_string_list_setting(['foo'], '')
        self.settings.parse_args(['--foo=foo'])
        self.assertEqual(self.settings['foo'], ['foo'])

    def test_string_list_parses_two_items(self):
        self.settings.add_string_list_setting(['foo'], '')
        self.settings.parse_args(['--foo=foo', '--foo', 'bar'])
        self.assertEqual(self.settings['foo'], ['foo', 'bar'])

    def test_adds_choice_setting(self):
        self.settings.add_choice_setting(['foo'], ['foo', 'bar'], 'foo help')
        self.assert_(self.settings.parser.has_option('--foo'))
        self.assert_('foo' in self.settings)
        option = self.settings.parser.get_option('--foo')
        self.assertEqual(option.help, 'foo help')

    def test_choice_defaults_to_first_one(self):
        self.settings.add_choice_setting(['foo'], ['foo', 'bar'], 'foo help')
        self.settings.parse_args([])
        self.assertEqual(self.settings['foo'], 'foo')

    def test_choice_accepts_any_valid_value(self):
        self.settings.add_choice_setting(['foo'], ['foo', 'bar'], 'foo help')
        self.settings.parse_args(['--foo=foo'])
        self.assertEqual(self.settings['foo'], 'foo')
        self.settings.parse_args(['--foo=bar'])
        self.assertEqual(self.settings['foo'], 'bar')

    def test_adds_boolean_setting(self):
        self.settings.add_boolean_setting(['foo'], 'foo help')
        self.assert_(self.settings.parser.has_option('--foo'))
        self.assert_('foo' in self.settings)
        option = self.settings.parser.get_option('--foo')
        self.assertEqual(option.help, 'foo help')
        
    def test_adds_bytesize_setting(self):
        self.settings.add_bytesize_setting(['foo'], 'foo help')
        self.assert_(self.settings.parser.has_option('--foo'))
        self.assert_('foo' in self.settings)
        option = self.settings.parser.get_option('--foo')
        self.assertEqual(option.help, 'foo help')

    def test_parses_bytesize_option(self):
        self.settings.add_bytesize_setting(['foo'], 'foo help')

        self.settings.parse_args(args=['--foo=xyzzy'])
        self.assertEqual(self.settings['foo'], 0)

        self.settings.parse_args(args=['--foo=123'])
        self.assertEqual(self.settings['foo'], 123)

        self.settings.parse_args(args=['--foo=123k'])
        self.assertEqual(self.settings['foo'], 123 * 1000)

        self.settings.parse_args(args=['--foo=123m'])
        self.assertEqual(self.settings['foo'], 123 * 1000**2)

        self.settings.parse_args(args=['--foo=123g'])
        self.assertEqual(self.settings['foo'], 123 * 1000**3)

        self.settings.parse_args(args=['--foo=123t'])
        self.assertEqual(self.settings['foo'], 123 * 1000**4)

        self.settings.parse_args(args=['--foo=123kib'])
        self.assertEqual(self.settings['foo'], 123 * 1024)

        self.settings.parse_args(args=['--foo=123mib'])
        self.assertEqual(self.settings['foo'], 123 * 1024**2)

        self.settings.parse_args(args=['--foo=123gib'])
        self.assertEqual(self.settings['foo'], 123 * 1024**3)

        self.settings.parse_args(args=['--foo=123tib'])
        self.assertEqual(self.settings['foo'], 123 * 1024**4)
        
    def test_adds_integer_setting(self):
        self.settings.add_integer_setting(['foo'], 'foo help')
        self.assert_(self.settings.parser.has_option('--foo'))
        self.assert_('foo' in self.settings)
        option = self.settings.parser.get_option('--foo')
        self.assertEqual(option.help, 'foo help')

    def test_parses_integer_option(self):
        self.settings.add_integer_setting(['foo'], 'foo help', default=123)

        self.settings.parse_args(args=[])
        self.assertEqual(self.settings['foo'], 123)

        self.settings.parse_args(args=['--foo=123'])
        self.assertEqual(self.settings['foo'], 123)

