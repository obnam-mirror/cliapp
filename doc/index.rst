Welcome to cliapp's documentation!
==================================

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
The scaffolding to set up a command line parser, open each input
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


    if __name__ == '__main__':
        ExampleApp().run()


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


Logging
-------

Logging support: by default, no log file is written, it must be
requested explicitly by the user. The default log level is info.
    
Subcommands
-----------

Sometimes a command line tool needs to support subcommands.
For example, version control tools often do this:
``git commit``, ``git clone``, etc. To do this with ``cliapp``,
you need to add methods with names like ``cmd_commit`` and
``cmd_clone``::

    class VersionControlTool(cliapp.Application):
    
        def cmd_commit(self, args):
            '''commit command description'''
            pass
        def cmd_clone(self, args):
            '''clone command description'''
            pass
            
If any such methods exist, ``cliapp`` automatically supports
subcommands. The name of the method, without the ``cmd_`` prefix,
forms the name of the subcommand. Any underscores in the method
name get converted to dashes in the command line. Case is
preserved.

Subcommands may also be added using the ``add_subcommand`` method.

All options are global, not specific to the subcommand.
All non-option arguments are passed to the method in its only
argument.

Subcommands are implemented by the ``process_args`` method.
If you override that method, you need to support subcommands
yourself (perhaps by calling the ``cliapp`` implementation).


Manual pages
------------

``cliapp`` provides a way to fill in a manual page template, in
**troff** format, with information about all options. This
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


Profiling support
-----------------
    
If ``sys.argv[0]`` is ``foo``, and the environment
variable ``FOO_PROFILE`` is set, then the execution of the 
application (the ``run`` method) is profiled, using ``cProfile``, and
the profile written to the file named in the environment variable.



Reference manual
================

.. automodule:: cliapp
   :members:
   :undoc-members:
   :exclude-members: add_boolean_setting, add_bytesize_setting,
        add_choice_setting, add_integer_setting, add_string_list_setting,
        add_string_setting, config_files

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

