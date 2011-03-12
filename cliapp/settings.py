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


import ConfigParser
import optparse
import os
import re
import sys


class Settings(object):

    '''Settings for a cliapp application.
    
    Settings are read from configuration files, and parsed from the
    command line. Every setting has a name, and a type.
    
    '''

    def __init__(self, progname, version):
        # We store settings in a ConfigParser. Command line options will
        # be put into the ConfigParser. Settings can have aliases,
        # we store those in self._aliases, indexed by the canonical name.
        # Further, converters for value types are stored in self._getters
        # and self._setters, indexed by canonical name.
        self._cp = ConfigParser.ConfigParser()
        self._cp.add_section('config')
        self._aliases = dict()
        self._getters = dict()
        self._setters = dict()
        self._accumulators = set()
        self._helps = dict()
        self._nargs = dict()
        self._choices = dict()

        self.version = version
        self.progname = progname
        
        self._add_default_settings()

    def _add_default_settings(self):
        self.add_string_setting(['output'], 
                                'write output to named file, '
                                    'instead of standard output')

        self.add_string_setting(['log'], 'write log entries to file')
        self.add_string_setting(['log-level'], 
                                'log at given level, one of '
                                    'debug, info, warning, error, critical, '
                                    'fatal (default: %default)',
                                default='info')

    def _add_setting(self, names, help, default, getter, setter, nargs=1,
                     is_accumulator=False):
        '''Add a setting to self._cp.
        
        getter and setter convert the value when read from or written to
        self._cp.
        
        '''

        self._cp.set('config', names[0], setter(default))
        self._helps[names[0]] = help
        self._getters[names[0]] = getter
        self._setters[names[0]] = setter
        if is_accumulator:
            self._accumulators.add(names[0])
        for alias in names:
            self._aliases[alias] = names[0]
        self._nargs[names[0]] = nargs

    def add_string_setting(self, names, help, default=''):
        '''Add a setting with a string value.'''
        self._add_setting(names, help, default, str, str)

    def add_string_list_setting(self, names, help, default=None):
        '''Add a setting which have multiple string values.
        
        An example would be an option that can be given multiple times
        on the command line, e.g., "--exclude=foo --exclude=bar".
        
        '''

        def get_stringlist(encoded):
            if encoded:
                return encoded.split(',')
            else:
                return []
            
        def set_stringlist(strings):
            return ','.join(strings)

        self._add_setting(names, help, default or [], 
                          get_stringlist, set_stringlist, is_accumulator=True)

    def add_choice_setting(self, names, possibilities, help):
        '''Add a setting which chooses from list of acceptable values.
        
        An example would be an option to set debugging level to be
        one of a set of accepted names: debug, info, warning, etc.
        
        The default value is the first possibility.
        
        '''

        self._add_setting(names, help, possibilities[0], str, str)
        self._choices[names[0]] = possibilities

    def add_boolean_setting(self, names, help, default=False):
        '''Add a setting with a boolean value (defaults to false).'''
        
        def get_boolean(encoded):
            return encoded.lower() not in ['0', 'false', 'no', 'off']
        def set_boolean(boolean):
            if boolean:
                return 'yes'
            else:
                return 'no'

        self._add_setting(names, help, default, get_boolean, set_boolean, 
                          nargs=0)

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

        self._add_setting(names, help, default, self._parse_human_size, str)

    def add_integer_setting(self, names, help, default=None):
        '''Add an integer setting.'''
        self._add_setting(names, help, default, long, str)

    def __getitem__(self, name):
        if name in self._aliases:
            name = self._aliases[name]
            value = self._cp.get('config', name)
            return self._getters[name](value)
        else:
            raise KeyError(name)

    def __setitem__(self, name, value):
        if name in self._aliases:
            name = self._aliases[name]
            value = self._setters[name](value)
            self._cp.set('config', name, value)
        else:
            raise KeyError(name)

    def __contains__(self, name):
        return name in self._aliases
        
    def _option_names(self, names):
        '''Turn setting names into option names.
        
        Names with a single letter are short options, and get prefixed
        with one dash. The rest get prefixed with two dashes.
        
        '''

        return ['--%s' % name if len(name) > 1 else '-%s' % name
                for name in names]

    def _find_names(self, name):
        return [name] + [x for x in self._aliases if self._aliases[x] == name]

    def parse_args(self, args, suppress_errors=False):
        '''Parse the command line.
        
        Return list of non-option arguments.
        
        '''

        p = optparse.OptionParser(prog=self.progname, version=self.version)
        
        def dump(*args): # pragma: no cover
            for name in self._cp.options('config'):
                print self._cp.get('config', name)
            sys.exit(0)
        p.add_option('--dump-setting-names',
                     action='callback',
                     nargs=0,
                     callback=dump,
                     help='write out all names of settings and quit')
        
        for name in self._cp.options('config'):
            names = self._find_names(name)
            option_names = self._option_names(names)

            # Create a new function for callback handling.
            # We create a new function for each option. We need nested
            # functions to handle the 'name' variable correctly.
            def callback(name):
                def cb(option, opt_str, value, parser):
                    if name in self._choices:
                        choices = [x.lower() for x in self._choices[name]]
                        if value.lower() not in choices:
                            msg = ('Bad value %s for setting %s' % 
                                   (value, opt_str))
                            raise optparse.OptionValueError(msg)
                    if name in self._accumulators:
                        old = self[name]
                        value = old + [value]
                    elif self._nargs[name] == 0:
                        value = True
                    self[name] = value
                return cb

            p.add_option(*option_names,
                         action='callback',
                         callback=callback(name),
                         nargs=self._nargs[name],
                         type='string',
                         help=self._helps[name])
            p.set_default(option_names[0], self[names[0]])

        if suppress_errors:
            p.error = lambda msg: sys.exit(1)

        options, args = p.parse_args(args)
        return args

    @property
    def default_config_files(self):
        '''Return list of default config files to read.
        
        The names of the files are dependent on the name of the program,
        as set in the progname attribute.
        
        The files may or may not exist.
        
        '''
        
        configs = []
        
        configs.append('/etc/%s.conf' % self.progname)
        configs += self.listconfs('/etc/%s' % self.progname)
        configs.append(os.path.expanduser('~/.%s.conf' % self.progname))
        configs += self.listconfs(
                        os.path.expanduser('~/.config/%s' % self.progname))
        
        return configs

    def listconfs(self, dirname, listdir=os.listdir):
        '''Return list of pathnames to config files in dirname.
        
        Config files are expectd to have names ending in '.conf'.
        
        If dirname does not exist or is not a directory, 
        return empty list.
        
        '''
        
        if not os.path.isdir(dirname):
            return []

        basenames = listdir(dirname)
        basenames.sort(key=lambda s: [ord(c) for c in s])
        return [os.path.join(dirname, x)
                for x in basenames
                if x.endswith('.conf')]

