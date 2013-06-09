Profiling support
=================

If ``sys.argv[0]`` is ``foo``, and the environment
variable ``FOO_PROFILE`` is set, then the execution of the
application (the ``run`` method) is profiled, using ``cProfile``, and
the profile written to the file named in the environment variable.

