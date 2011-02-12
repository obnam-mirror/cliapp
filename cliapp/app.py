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
import re
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

    def __init__(self, version='0.0.0'):
        self.version = version
        self._init_parser()
        
    def _init_parser(self):
        '''Initialize the option parser with default options and values.'''
        self.parser = optparse.OptionParser(version=self.version)

    def _option_names(self, names):
        '''Turn setting names into option names.
        
        Names with a single letter are short options, and get prefixed
        with one dash. The rest get prefixed with two dashes.
        
        '''

        return ['--%s' % name if len(name) > 1 else '-%s' % name
                for name in names]

    def _attr_name(self, name):
        '''Turn setting name into attribute name.
        
        Dashes get turned into underscores.
        
        '''

        return '_'.join(name.split('-'))

    def _set_default_value(self, names, value):
        '''Set default value for a setting with names in names.'''
        self.parser.set_default(self._attr_name(names[0]), value)

    def add_string_setting(self, names, help, default=''):
        '''Add a setting with a string value.'''
        self.parser.add_option(*self._option_names(names), 
                               action='store', 
                               help=help)
        self._set_default_value(names, default)

    def add_boolean_setting(self, names, help, default=False):
        '''Add a setting with a boolean value (defaults to false).'''
        self.parser.add_option(*self._option_names(names), 
                               action='store_true', 
                               help=help)
        self._set_default_value(names, default)

    def _parse_human_size(self, size):
        '''Parse a size using suffix into plain bytes.'''
        
        m = re.match(r'''(?P<number>\d+(\.\d+)?) \s* 
                         (?P<unit>k|ki|m|mi|g|gi|t|ti)? b? \s*$''',
                     size.lower(), flags=re.X)
        if not m:
            return 0
        else:
            number = float(m.group('number'))
            unit = m.group('unit')
            units = {
                'k': 10**3,
                'm': 10**6,
                'g': 10**9,
                't': 10**12,
                'ki': 2**10,
                'mi': 2**20,
                'gi': 2**30,
                'ti': 2**40,
            }
            return int(number * units.get(unit, 1))

    def _store_bytesize_option(self, option, opt_str, value, parser):
        '''Parse value of bytesize option and store it in the parser value.'''
        setattr(parser.values, option.dest, self._parse_human_size(value))

    def add_bytesize_setting(self, names, help, default=0):
        '''Add a setting with a size in bytes.
        
        The user can use suffixes for kilo/mega/giga/tera/kibi/mibi/gibi/tibi.
        
        '''

        self.parser.add_option(*self._option_names(names), 
                               action='callback',
                               type='string',
                               callback=self._store_bytesize_option,
                               nargs=1,
                               help=help)
        self._set_default_value(names, default)

    def add_integer_setting(self, names, help, default=None):
        '''Add an integer setting.'''

        self.parser.add_option(*self._option_names(names), 
                               action='store',
                               type='long',
                               help=help)
        self._set_default_value(names, default)

    def get_setting(self, name):
        '''Return value of setting with a given name.
        
        Note that you may only call this method after the command line
        has been parsed.
        
        '''

        option = self.parser.get_option(self._option_names([name])[0])
        return getattr(self.options, option.dest)

    def __getitem__(self, setting_name):
        return self.get_setting(setting_name)
        
    def add_settings(self):
        '''Add application specific settings.'''

    def run(self, args=None, stderr=sys.stderr):
        try:
            self.add_settings()
            args = sys.argv[1:] if args is None else args
            self.options, args = self.parser.parse_args(args)
            self.process_args(args)
        except SystemExit, e:
            sys.exit(e.code)
        except KeyboardInterrupt, e:
            sys.exit(255)
        except Exception, e:
            stderr.write('%s\n' % str(e))
            sys.exit(1)
        
    def process_args(self, args):
        '''Process command line non-option arguments.
        
        The default is to treat each argument as the name of an input,
        and call process_input on it.
        
        '''
                
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
        
        if name == '-':
            return sys.stdin
        else:
            return open(name, mode)

    def process_input(self, name, stdin=sys.stdin):
        '''Process a particular input file.'''

        f = self.open_input(name)
        for line in f:
            self.process_input_line(name, line)
        if f != stdin:
            f.close()

    def process_input_line(self, name, f):
        '''Process one line of the input file.
        
        Applications that are line-oriented can redefine only this method in
        a subclass, and should not need to care about the other methods.
        
        '''
        

