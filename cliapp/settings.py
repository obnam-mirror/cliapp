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


class Settings(object):

    '''Settings for a cliapp application.
    
    Settings are read from configuration files, and parsed from the
    command line. Every setting has a name, and a type.
    
    '''

    def __init__(self, progname, version):
        self._names = list()
        self._progname = progname
        self._version = version
        self._init_parser(progname, version)
        
    def _init_parser(self, progname, version):
        '''Initialize the option parser with default options and values.'''
        self.parser = optparse.OptionParser(prog=progname, version=version)
        
        self.add_string_setting(['output'], 
                                'write output to named file, '
                                    'instead of standard output')

        self.add_string_setting(['log'], 'write log entries to file')
        self.add_string_setting(['log-level'], 
                                'log at given level, one of '
                                    'debug, info, warning, error, critical, '
                                    'fatal (default: %default)',
                                default='info')

        self.add_callback_setting(['dump-setting-names'],
                                  'write out all names of settings and quit',
                                  self._dump_setting_names, nargs=0)

    @property
    def version(self):
        return self._version

    def get_progname(self):
        return self._progname
    def set_progname(self, progname):
        self._progname = progname
        self.parser.prog = progname
    progname = property(get_progname, set_progname)

    def _dump_setting_names(self): # pragma: no cover
        for option in self.parser.option_list:
            if option.dest:
                print option.dest
            else:
                x = option._long_opts[0]
                if x.startswith('--'):
                    x = x[2:]
                print x
        sys.exit(0)

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
        self._names += names
        self.parser.add_option(*self._option_names(names), 
                               action='store', 
                               help=help)
        self._set_default_value(names, default)

    def add_string_list_setting(self, names, help, default=None):
        '''Add a setting which have multiple string values.
        
        An example would be an option that can be given multiple times
        on the command line, e.g., "--exclude=foo --exclude=bar".
        
        '''

        self._names += names
        self.parser.add_option(*self._option_names(names), 
                               action='append', 
                               help=help)
        self._set_default_value(names, default or [])

    def add_choice_setting(self, names, possibilities, help, default=None):
        '''Add a setting which chooses from list of acceptable values.
        
        An example would be an option to set debugging level to be
        one of a set of accepted names: debug, info, warning, etc.
        
        The default value is the first possibility.
        
        '''

        self._names += names
        self.parser.add_option(*self._option_names(names), 
                               action='store', 
                               type='choice',
                               choices=possibilities,
                               help=help)
        self._set_default_value(names, possibilities[0])

    def add_boolean_setting(self, names, help, default=False):
        '''Add a setting with a boolean value (defaults to false).'''
        self._names += names
        self.parser.add_option(*self._option_names(names), 
                               action='store_true', 
                               help=help)
        self._set_default_value(names, default)

    def add_callback_setting(self, names, help, callback, nargs=1, 
                             default=None):
        '''Add a setting processed by a callback. 
        
        The callback will receive nargs argument strings, and will return
        the actual value of the setting.
        
        '''
        
        def callback_wrapper(option, opt_str, value, parser):
            if type(value) == str:
                value = (value,)
            setattr(parser.values, option.dest, callback(*value))

        self._names += names
        self.parser.add_option(*self._option_names(names), 
                               action='callback',
                               callback=callback_wrapper,
                               nargs=nargs,
                               type='string',
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

    def add_bytesize_setting(self, names, help, default=0):
        '''Add a setting with a size in bytes.
        
        The user can use suffixes for kilo/mega/giga/tera/kibi/mibi/gibi/tibi.
        
        '''

        self.add_callback_setting(names, help, self._parse_human_size,
                                  default=default, nargs=1)

    def add_integer_setting(self, names, help, default=None):
        '''Add an integer setting.'''

        self._names += names
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
        
    def __contains__(self, setting_name):
        return setting_name in self._names

    def parse_args(self, args):
        '''Parse the command line.
        
        Set self.options to a value like the options returned by
        OptionParser. Return list of non-option arguments.
        
        '''

        self.options, args = self.parser.parse_args(args)
        return args

