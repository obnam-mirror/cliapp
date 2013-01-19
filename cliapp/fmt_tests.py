# Copyright (C) 2013  Lars Wirzenius
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import unittest

import cliapp


class TextFormatTests(unittest.TestCase):

    def setUp(self):
        self.fmt = cliapp.TextFormat(width=10)
    
    def test_returns_empty_string_for_empty_string(self):
        self.assertEqual(self.fmt.format(''), '')

    def test_returns_short_one_line_paragraph_as_is(self):
        self.assertEqual(self.fmt.format('foo bar'), 'foo bar')

    def test_wraps_long_line(self):
        self.assertEqual(self.fmt.format('foobar word'), 'foobar\nword')

    def test_retains_final_newline_on_short_input(self):
        self.assertEqual(self.fmt.format('foo bar\n'), 'foo bar\n')

    def test_retains_final_newline_on_long_input(self):
        self.assertEqual(self.fmt.format('foobar word\n'), 'foobar\nword\n')

    def test_handles_paragraphs(self):
        self.assertEqual(
            self.fmt.format('foo\nbar\n\nyo\nyo\n'),
            'foo bar\n\nyo yo\n')

