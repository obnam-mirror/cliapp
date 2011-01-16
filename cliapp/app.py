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
import sys


class Application(object):

    '''A framework for Unix-like command line programs.
    
    The user should subclass this class, then create an instance of the
    subclass, and call the run method.
    
    The subclass should define the version attribute to contain the
    version number of the program.
    
    Some methods are meant to be redefined by subclasses, so as to
    provide real functionality. These methods have names that do not
    start with an underscore.
    
    '''

    def __init__(self):
        self.version = '0.0.0'
        self._init_parser()
        
    def _init_parser(self):
        '''Initialize the option parser with default options and values.'''
        self.parser = optparse.OptionParser(version=self.version)
        self.add_options()

    def add_string_setting(self, primary_name, *args, **kwargs):
        '''Add a setting with a string value.'''
        self.parser.add_option('--' + primary_name, *args, **kwargs)
        
    def add_options(self):
        '''Add application specific options.'''

    def run(self, args=None):
        args = sys.argv[1:] if args is None else args
        self.options, args = self.parser.parse_args(args)
        
        for arg in args:
            self.process_input(arg)

    def open_input(self, name, mode='r'):
        '''Open an input file for reading.
        
        The default behaviour is to open a file named on the local
        filesystem. A subclass might override this behavior for URLs,
        for example.
        
        The optional mode argument speficies the mode in which the file
        gets opened. It should allow reading. Some files should perhaps
        be opened in binary mode ('rb') instead of the default text mode.
        
        '''
        
        return open(name, mode)

    def process_input(self, name):
        '''Process a particular input file.'''

        f = self.open_input(name)
        for line in f:
            self.process_input_line(name, line)
        f.close()

    def process_input_line(self, name, f):
        '''Process one line of the input file.
        
        Applications that are line-oriented can redefine only this method in
        a subclass, and should not need to care about the other methods.
        
        '''
        

