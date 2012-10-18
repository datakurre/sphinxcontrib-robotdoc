sphinxcontrib-robotdoc
======================


Yes, this is **under early development** and everything, everything, may
still change.

Usage
-----

1. Add ``sphinxcontrib_robotdoc`` into your configuration (``conf.py``)::

    extensions = [
        "sphinxcontrib_robotdoc",
    ]

2. Include test suites and keywords in your documentation::

    .. robot_tests:: Test title or RegExp.*
       :source: ../src/my_package/tests/acceptance/my_suite.txt
       :tags: bugs, new

    .. robot_keywords::
       :source: ../src/my_package/tests/acceptance/my_suite.txt
