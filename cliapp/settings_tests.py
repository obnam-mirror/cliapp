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
        
    def test_has_progname(self):
        self.assertEqual(self.settings.progname, 'appname')
        
    def test_sets_progname(self):
        self.settings.progname = 'foo'
        self.assertEqual(self.settings.progname, 'foo')
        
    def test_has_version(self):
        self.assertEqual(self.settings.version, '1.0')

    def test_adds_default_options_and_settings(self):
        self.assert_('output' in self.settings)
        self.assert_('log' in self.settings)
        self.assert_('log-level' in self.settings)

    def test_parses_options(self):
        self.settings.add_string_setting(['foo'], 'foo help')
        self.settings.add_boolean_setting(['bar'], 'bar help')
        self.settings.parse_args(['--foo=foovalue', '--bar'])
        self.assertEqual(self.settings['foo'], 'foovalue')
        self.assertEqual(self.settings['bar'], True)

    def test_does_not_have_foo_setting_by_default(self):
        self.assertFalse('foo' in self.settings)

    def test_raises_keyerror_for_getting_unknown_setting(self):
        self.assertRaises(KeyError, self.settings.__getitem__, 'foo')

    def test_raises_keyerror_for_setting_unknown_setting(self):
        self.assertRaises(KeyError, self.settings.__setitem__, 'foo', 'bar')

    def test_adds_string_setting(self):
        self.settings.add_string_setting(['foo'], 'foo help')
        self.assert_('foo' in self.settings)

    def test_adds_string_list_setting(self):
        self.settings.add_string_list_setting(['foo'], 'foo help')
        self.assert_('foo' in self.settings)

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
        self.assert_('foo' in self.settings)

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
        self.assert_('foo' in self.settings)
        
    def test_adds_bytesize_setting(self):
        self.settings.add_bytesize_setting(['foo'], 'foo help')
        self.assert_('foo' in self.settings)

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
        self.assert_('foo' in self.settings)

    def test_parses_integer_option(self):
        self.settings.add_integer_setting(['foo'], 'foo help', default=123)

        self.settings.parse_args(args=[])
        self.assertEqual(self.settings['foo'], 123)

        self.settings.parse_args(args=['--foo=123'])
        self.assertEqual(self.settings['foo'], 123)

