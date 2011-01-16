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


import cliapp


class ExampleApp(cliapp.Application):

    '''A little fgrep-like tool.'''
    
    def add_options(self):
        self.add_string_setting('pattern', '-e', action='store',
                               help='the pattern to search for')

    def process_input_line(self, name, line):
        if self.options.pattern in line:
            print line,
    
    
ExampleApp().run()

