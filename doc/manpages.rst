Manual pages
============

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

