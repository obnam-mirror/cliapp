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

import genman

class Setting(object):

    action = 'store'
    type = 'string'
    nargs = 1
    choices = None

    def __init__(self, names, default, help, metavar=None):
        self.names = names
        self.set_value(default)
        self.help = help
        self.metavar = metavar

    def get_value(self):
        return self._string_value
        
    def set_value(self, value):
        self._string_value = value
        
    def call_get_value(self):
        return self.get_value()
        
    def call_set_value(self, value):
        self.set_value(value)

    value = property(call_get_value, call_set_value)


class StringSetting(Setting):

    pass


class StringListSetting(Setting):

    action = 'append'
    
    def get_value(self):
        if self._string_value.strip():
            return [s.strip() for s in self._string_value.split(',')]
        else:
            return []
        
    def set_value(self, strings):
        self._string_value = ','.join(strings)


class ChoiceSetting(Setting):

    type = 'choice'
    
    def __init__(self, names, choices, help, metavar=None):
        Setting.__init__(self, names, choices[0], help, metavar=metavar)
        self.choices = choices

    
class BooleanSetting(Setting):

    action = 'store_true'
    nargs = None
    type = None

    _trues = ['yes', 'on', '1', 'true']
    _false = 'no'

    def get_value(self):
        return self._string_value.lower() in self._trues
        
    def set_value(self, value):
        if value:
            self._string_value = self._trues[0]
        else:
            self._string_value = self._false


class ByteSizeSetting(Setting):

    def parse_human_size(self, size):
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
            return long(number * units.get(unit, 1))

    def get_value(self):
        return long(self._string_value)
        
    def set_value(self, value):
        if type(value) == str:
            value = self.parse_human_size(value)
        self._string_value = str(value)


class IntegerSetting(Setting):

    type = 'int'

    def get_value(self):
        return long(self._string_value)
        
    def set_value(self, value):
        self._string_value = str(value)


class Settings(object):

    '''Settings for a cliapp application.
    
    Settings are read from configuration files, and parsed from the
    command line. Every setting has a name, and a type.
    
    '''

    def __init__(self, progname, version):
        self._settingses = dict()
        self._canonical_names = list()

        self.version = version
        self.progname = progname
        
        self._add_default_settings()
        
        self._config_files = None

    def _add_default_settings(self):
        self.add_string_setting(['output'], 
                                'write output to FILE, '
                                    'instead of standard output',
                                metavar='FILE')

        self.add_string_setting(['log'], 'write log entries to FILE',
                                metavar='FILE')
        self.add_string_setting(['log-level'], 
                                'log at given level, one of '
                                    'debug, info, warning, error, critical, '
                                    'fatal (default: %default)',
                                default='info',
                                metavar='LEVEL')

    def _add_setting(self, setting):
        '''Add a setting to self._cp.'''

        self._canonical_names.append(setting.names[0])
        for name in setting.names:
            self._settingses[name] = setting

    def string(self, names, help, default='', **kwargs):
        '''Add a setting with a string value.'''
        self._add_setting(StringSetting(names, default, help, **kwargs))
    add_string_setting = string

    def string_list(self, names, help, default=None, **kwargs):
        '''Add a setting which have multiple string values.
        
        An example would be an option that can be given multiple times
        on the command line, e.g., "--exclude=foo --exclude=bar".
        
        '''

        self._add_setting(StringListSetting(names, default or [], help,
                                            **kwargs))
    add_string_list_setting = string_list

    def choice(self, names, possibilities, help, **kwargs):
        '''Add a setting which chooses from list of acceptable values.
        
        An example would be an option to set debugging level to be
        one of a set of accepted names: debug, info, warning, etc.
        
        The default value is the first possibility.
        
        '''

        self._add_setting(ChoiceSetting(names, possibilities, help, **kwargs))
    add_choice_setting = choice

    def boolean(self, names, help, default=False, **kwargs):
        '''Add a setting with a boolean value (defaults to false).'''
        self._add_setting(BooleanSetting(names, default, help, **kwargs))
    add_boolean_setting = boolean

    def bytesize(self, names, help, default=0, **kwargs):
        '''Add a setting with a size in bytes.
        
        The user can use suffixes for kilo/mega/giga/tera/kibi/mibi/gibi/tibi.
        
        '''
        
        self._add_setting(ByteSizeSetting(names, default, help, **kwargs))
    add_bytesize_setting = bytesize

    def integer(self, names, help, default=0, **kwargs):
        '''Add an integer setting.'''
        self._add_setting(IntegerSetting(names, default, help, **kwargs))
    add_integer_setting = integer

    def __getitem__(self, name):
        return self._settingses[name].value

    def __setitem__(self, name, value):
        self._settingses[name].value = value

    def __contains__(self, name):
        return name in self._settingses
        
    def _option_names(self, names):
        '''Turn setting names into option names.
        
        Names with a single letter are short options, and get prefixed
        with one dash. The rest get prefixed with two dashes.
        
        '''

        return ['--%s' % name if len(name) > 1 else '-%s' % name
                for name in names]

    def _destname(self, name):
        name = '_'.join(name.split('-'))
        return name

    def parse_args(self, args, suppress_errors=False):
        '''Parse the command line.
        
        Return list of non-option arguments.
        
        '''

        p = optparse.OptionParser(prog=self.progname, version=self.version)
        
        def dump_setting_names(*args): # pragma: no cover
            for name in self._canonical_names:
                sys.stdout.write('%s\n' % name)
            sys.exit(0)

        p.add_option('--dump-setting-names',
                     action='callback',
                     nargs=0,
                     callback=dump_setting_names,
                     help='write out all names of settings and quit')

        def dump_config(*args): # pragma: no cover
            cp = ConfigParser.ConfigParser()
            cp.add_section('config')
            for name in self._canonical_names:
                cp.set('config', name, self[name])
            cp.write(sys.stdout)
            sys.exit(0)

        p.add_option('--dump-config',
                     action='callback',
                     nargs=0,
                     callback=dump_config,
                     help='write out the entire current configuration')

        p.add_option('--generate-manpage',
                     action='callback',
                     nargs=1,
                     type='string',
                     callback=self.generate_manpage,
                     help='fill in manual page TEMPLATE',
                     metavar='TEMPLATE')
        
        for name in self._canonical_names:
            s = self._settingses[name]
            option_names = self._option_names(s.names)
            p.add_option(*option_names,
                         action=s.action,
                         type=s.type,
                         nargs=s.nargs,
                         choices=s.choices,
                         help=s.help,
                         metavar=s.metavar)
            p.set_defaults(**{self._destname(name): s.value})

        if suppress_errors:
            p.error = lambda msg: sys.exit(1)

        options, args = p.parse_args(args)
        
        for name in self._canonical_names:
            s = self._settingses[name]
            value = getattr(options, self._destname(name))
            s.value = value
        
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

    def get_config_files(self):
        if self._config_files is None:
            return self.default_config_files
        else:
            return self._config_files

    def set_config_files(self, config_files):
        self._config_files = config_files
        
    config_files = property(get_config_files, set_config_files)

    def load_configs(self, open=open):
        '''Load all config files in self.config_files.
        
        Silently ignore files that do not exist.
        
        '''

        cp = ConfigParser.ConfigParser()
        cp.add_section('config')

        for pathname in self.config_files:
            try:
                f = open(pathname)
            except IOError:
                pass
            else:
                cp.readfp(f)
                f.close()

        for name in cp.options('config'):
            self._settingses[name].value = cp.get('config', name)

    def generate_manpage(self, o, os, value, p): # pragma: no cover
        template = open(value).read()
        generator = genman.ManpageGenerator(template, p)
        sys.stdout.write(generator.format_template())
        sys.exit(0)
