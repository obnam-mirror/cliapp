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


import logging
import logging.handlers
import os
import subprocess
import sys
import traceback

import cliapp


class AppException(Exception):

    '''Base class for application specific exceptions.
    
    Any exceptions that are subclasses of this one get printed as
    nice errors to the user. Any other exceptions cause a Python
    stack trace to be written to stderr.
    
    '''


class Application(object):

    '''A framework for Unix-like command line programs.
    
    The user should subclass this base class for each application.
    The subclass does not need code for the mundane, boilerplate
    parts that are the same in every utility, and can concentrate on the 
    interesting part that is unique to it.

    To start the application, call the `run` method.
    
    The ``progname`` argument sets tne name of the program, which is
    used for various purposes, such as determining the name of the
    configuration file.
    
    Similarly, ``version`` sets the version number of the program.
    
    ``description`` and ``epilog`` are included in the output of
    ``--help``. They are formatted to fit the screen. Unlike the
    default behavior of ``optparse``, empty lines separate
    paragraphs.
    
    '''

    def __init__(self, progname=None, version='0.0.0', description=None,
                 epilog=None):
        self.fileno = 0
        self.global_lineno = 0
        self.lineno = 0
        self._description = description

        self.subcommands = {}
        for method_name in self._subcommand_methodnames():
            cmd = self._unnormalize_cmd(method_name)
            self.subcommands[cmd] = getattr(self, method_name)
        
        self.settings = cliapp.Settings(progname, version, 
                                        usage=self._format_usage,
                                        description=self._format_description,
                                        epilog=epilog)
        
    def add_settings(self):
        '''Add application specific settings.'''

    def run(self, args=None, stderr=sys.stderr, sysargv=sys.argv, 
            log=logging.critical):
        '''Run the application.'''
        
        def run_it():
            self._run(args=args, stderr=stderr, log=log)

        if self.settings.progname is None and sysargv:
            self.settings.progname = os.path.basename(sysargv[0])
        envname = '%s_PROFILE' % self._envname(self.settings.progname)
        profname = os.environ.get(envname, '')
        if profname: # pragma: no cover
            import cProfile
            cProfile.runctx('run_it()', globals(), locals(), profname)
        else:
            run_it()

    def _envname(self, progname):
        '''Create an environment variable name of the name of a program.'''
        
        basename = os.path.basename(progname)
        if '.' in basename:
            basename = basename.split('.')[0]
        
        ok = 'abcdefghijklmnopqrstuvwxyz0123456789'
        ok += ok.upper()
        
        return ''.join(x.upper() if x in ok else '_' for x in basename)

    def _run(self, args=None, stderr=sys.stderr, log=logging.critical):
        try:
            self.add_settings()
            self.settings.load_configs()
            args = sys.argv[1:] if args is None else args
            
            args = self.parse_args(args)
            self.setup_logging()
            logging.info('%s version %s starts' % 
                         (self.settings.progname, self.settings.version))
            
            if self.settings['output']:
                self.output = open(self.settings['output'], 'w')
            else:
                self.output = sys.stdout

            self.process_args(args)
        except AppException, e:
            log(traceback.format_exc())
            stderr.write('ERROR: %s\n' % str(e))
            sys.exit(1)
        except SystemExit, e:
            sys.exit(e.code)
        except KeyboardInterrupt, e:
            sys.exit(255)
        except BaseException, e:
            log(traceback.format_exc())
            stderr.write(traceback.format_exc())
            sys.exit(1)

        logging.info('%s version %s ends normally' % 
                     (self.settings.progname, self.settings.version))
    
    def add_subcommand(self, name, func):
        '''Add a subcommand.
        
        Normally, subcommands are defined by add ``cmd_foo`` methods
        to the application class. However, sometimes it is more convenient
        to have them elsewhere (e.g., in plugins). This method allows
        doing that.
        
        The callback function must accept a list of command line
        non-option arguments.
        
        '''
        
        if name not in self.subcommands:
            self.subcommands[name] = func
    
    def _subcommand_methodnames(self):
        return [x for x in dir(self) if x.startswith('cmd_')]

    def _normalize_cmd(self, cmd):
        return 'cmd_%s' % cmd.replace('-', '_')

    def _unnormalize_cmd(self, method):
        assert method.startswith('cmd_')
        return method[len('cmd_'):].replace('_', '-')

    def _format_usage(self):
        '''Format usage, possibly also subcommands, if any.'''
        if self.subcommands:
            lines = []
            prefix = 'Usage:'
            for cmd in sorted(self.subcommands.keys()):
                lines.append('%s %%prog [options] %s' % (prefix, cmd))
                prefix = ' ' * len(prefix)
            return '\n'.join(lines)
        else:
            return None

    def _format_description(self):
        '''Format OptionParser description, with subcommand support.'''
        if self.subcommands:
            paras = []
            for cmd in sorted(self.subcommands.keys()):
                method = self.subcommands[cmd]
                doc = method.__doc__ or ''
                paras.append('%s: %s' % (cmd, doc.strip()))
            cmd_desc = '\n\n'.join(paras)
            return '%s\n\n%s' % (self._description or '', cmd_desc)
        else:
            return self._description

    def setup_logging(self): # pragma: no cover
        '''Set up logging.'''
        
        level_name = self.settings['log-level']
        levels = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
            'fatal': logging.FATAL,
        }
        level = levels.get(level_name, logging.INFO)

        if self.settings['log']:
            handler = logging.handlers.RotatingFileHandler(
                            self.settings['log'],
                            maxBytes=self.settings['log-max'], 
                            backupCount=self.settings['log-keep'],
                            delay=False)
        else:
            handler = logging.FileHandler('/dev/null')
            # reduce amount of pointless I/O
            level = logging.FATAL

        fmt = '%(asctime)s %(levelname)s %(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(fmt, datefmt)
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(level)

    def parse_args(self, args):
        '''Parse the command line.
        
        Return list of non-option arguments.
        
        '''

        return self.settings.parse_args(args)

    def process_args(self, args):
        '''Process command line non-option arguments.
        
        The default is to call process_inputs with the argument list,
        or to invoke the requested subcommand, if subcommands have
        been defined.
        
        '''
        
            
        if self.subcommands:
            if not args:
                raise SystemExit('must give subcommand')
            if args[0] in self.subcommands:
                method = self.subcommands[args[0]]
                method(args[1:])
            else:
                raise SystemExit('unknown subcommand %s' % args[0])
        else:
            self.process_inputs(args)

    def process_inputs(self, args):
        '''Process all arguments as input filenames.
        
        The default implementation calls process_input for each
        input filename. If no filenames were given, then 
        process_input is called with ``-`` as the argument name.
        This implements the usual Unix command line practice of
        reading from stdin if no inputs are named.
        
        The attributes ``fileno``, ``global_lineno``, and ``lineno`` are set,
        and count files and lines. The global line number is the
        line number as if all input files were one.
        
        '''

        for arg in args or ['-']:
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
        '''Process a particular input file.
        
        The ``stdin`` argument is meant for unit test only.
        
        '''

        self.fileno += 1
        self.lineno = 0
        f = self.open_input(name)
        for line in f:
            self.global_lineno += 1
            self.lineno += 1
            self.process_input_line(name, line)
        if f != stdin:
            f.close()

    def process_input_line(self, name, f):
        '''Process one line of the input file.
        
        Applications that are line-oriented can redefine only this method in
        a subclass, and should not need to care about the other methods.
        
        '''
        
    def runcmd(self, argv, ignore_fail=False, *args, **kwargs):
        '''Run external command.

        Return the standard output of the command.
        
        Raise ``cliapp.AppException`` if external command returns
        non-zero exit code. ``*args`` and ``**kwargs`` are passed
        onto ``subprocess.Popen``.
        
        '''

        exit, out, err = self.runcmd_unchecked(argv, *args, **kwargs)
        if exit != 0:
            msg = 'Command failed: %s\n%s' % (' '.join(argv), err)
            if ignore_fail:
                logging.info(msg)
            else:
                logging.error(msg)
                raise cliapp.AppException(msg)
        return out
        
    def runcmd_unchecked(self, argv, stdin=None, ignore_fail=False, *args, 
                         **kwargs):
        '''Run external command.

        Return the exit code, and contents of standard output and error
        of the command.
        
        '''

        logging.debug('run external command: %s' % ' '.join(argv))
        p = subprocess.Popen(argv, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE,
                             *args, **kwargs)
        out, err = p.communicate(stdin)
        return p.returncode, out, err

