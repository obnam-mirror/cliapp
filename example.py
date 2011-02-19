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


'''Example for cliapp framework.'''


import cliapp


class ExampleApp(cliapp.Application):

    '''A little fgrep-like tool.'''
    
    def add_settings(self):
        self.add_string_list_setting(['pattern', 'e'], 'pattern to search for')

    def process_input_line(self, name, line):
        for pattern in self['pattern']:
            if pattern in line:
                self.output.write(line)
    
    
ExampleApp(version='0.1.2').run()

