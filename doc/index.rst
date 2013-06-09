Welcome to cliapp
=================

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

.. toctree::
   :numbered:

   example
   walkthrough
   logging
   subcommands
   manpages
   profiling
   refman


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

