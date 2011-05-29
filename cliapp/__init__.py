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


''':mod:`cliapp` -- framework for Unix command line programs
==========

``cliapp`` is a Python framework for Unix-like command line programs,
which typically have the following characteristics:

* non-interactive
* the programs read input files named on the command line, 
  or the standard input
* each line of input is processed individually
* output is to the standard output
* there are various options to modify how the program works
* certain options are common to all: ``--help``, ``--version``

Programs like the above are often used as filters in a pipeline.
The scaffoling to set up a command line parser, open each input
file, read each line of input, etc, is the same in each program.
Only the logic of what to do with each line differs.

``cliapp`` is not restricted to line-based filters, but is a more
general framework. It provides ways for its users to override
most behavior. For example:

* you can treat command line arguments as URLs, or record identfiers
  in a database, or whatever you like
* you can read input files in whatever chunks you like, or not at all,
  rather than forcing a line-based paradigm

Despite all the flexibility, writing simple line-based filters
remains very straightforward. The point is to get the framework to
do all the usual things, and avoid repeating code across users of the
framework.


Example
-------

::

    class ExampleApp(cliapp.Application):

        def add_settings(self):
            self.settings.string_list(['pattern', 'e'], 
                                      'search for regular expression PATTERN',
                                      metavar='REGEXP')
    
        # We override process_inputs to be able to do something after the last
        # input line.
        def process_inputs(self, args):
            self.matches = 0
            cliapp.Application.process_inputs(self, args)
            self.output.write('There were %s matches.\\n' % self.matches)
    
        def process_input_line(self, name, line):
            for pattern in self.settings['pattern']:
                if pattern in line:
                    self.output.write('%s:%s: %s' % (name, self.lineno, line))
                    self.matches += 1
                    logging.debug('Match: %s line %d' % (name, self.lineno))



Walkthrough
-----------

Every application should be a class that subclasses ``cliapp.Application``.
The subclass should provide specific methods. Read the documentation
for the ``cliapp.Application`` class to see all methods, but a rough
summary is here:

* the ``settings`` attribute is the ``cliapp.Settings`` instance used by
  the application
* override ``add_settings`` to add new settings for the application
* override ``process_*`` methods to override various stages in how
  arguments and input files are processed
* override ``process_args`` to decide how each argument is processed;
  by default, this called ``process_inputs`` or handles subcommands
* ``process_inputs`` calls ``process_input`` (note singular) for each 
  argument, or on ``-`` to process standard input if no files are named
  on the command line
* ``process_input`` calls ``open_input`` to open each file, then calls
  ``process_input_line`` for each input line
* ``process_input_line`` does nothing, by default

This cascade of overrideable methods is started by the `run`
method, which also sets up logging, loads configuration files,
parses the command line, and handles reporting of exceptions.
It can also run the rest of the code under the Python profiler,
if the appropriate environment variable is set.


Subcommands
-----------

Sometimes a command line tool needs to support subcommands.
For example, version control tools often do this:
``git commit``, ``git clone``, etc. To do this with ``cliapp``,
you need to add methods with names like ``cmd_commit`` and
``cmd_clone``::

    class VersionControlTool(cliapp.Application):
    
        def cmd_commit(self, args):
            pass
        def cmd_clone(self, args):
            pass
            
If any such methods exist, ``cliapp`` automatically supports
subcommands. The name of the method, without the ``cmd_`` prefix,
forms the name of the subcommand. Any underscores in the method
name get converted to dashes in the command line. Case is
preserved.

All options are global, not specific to the subcommand.
All non-option arguments are passed to the method in its only
argument.

Subcommands are implemented by the ``process_args`` method.
If you override that method, you need to support subcommands
yourself (perhaps by calling the ``cliapp`` implementation).


Manual pages
------------

``cliapp`` provides a way to fill in a manual page template, in
**troff**(1) format, with information about all options. This
allows you to write the rest of the manual page without having
to remember to update all options. This is a compromise between
ease-of-development and manual page quality.

A high quality manual page probably needs to be written from
scratch. For example, the description of each option in a manual
page should usually be longer than what is suitable for
``--help`` output. However, it is tedious to write option
descriptions many times.

To use this, use the ``--generate-manpage=TEMPLATE`` option,
where ``TEMPLATE`` is the name of the template file. See
``example.1`` in the ``cliapp`` source tree for an example.

'''


__version__ = '0.12'


from settings import Settings
from app import Application, AppException
from genman import ManpageGenerator

__all__ = locals()
