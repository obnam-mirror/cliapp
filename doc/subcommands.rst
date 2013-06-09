Subcommands
===========

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

