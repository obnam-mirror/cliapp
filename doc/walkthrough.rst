Walkthrough
===========

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

