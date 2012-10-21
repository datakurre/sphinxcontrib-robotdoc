This extension is not a much past *proof-of-concept* yet. Rendering of
generated documentation may still change in the future, but API should remain
backwards compatible.

Usage
-----

Add ``sphinxcontrib_robotdoc`` into the extensions list of your Sphinx
configuration (``conf.py``)::

    extensions = [
        "sphinxcontrib_robotdoc",
    ]

Embed test cases and user keywords into your documentation with the
following custom Docutils-directives::

    .. robot_tests:: Test case title or RegExp.*
       :source: ../src/my_package/tests/acceptance/my_suite.txt
       :tags: bugs, new

    .. robot_keywords:: Keyword title or RegExp.*
       :source: ../src/my_package/tests/acceptance/my_suite.txt

Both directives (``robot_tests`` and ``robot_keywords``) take a regular
expression as their main option (or *content* in Docutils' terms) to filter
the embeded test cases or keywords found from the given ``source``-file. If
no regular expression is given, all found tests or keywords will be embedded
(like having ``.*`` as the default).

Path given to the mandatory ``source``-option must be a relative path from
the current document. (There's no support for package module paths yet.)

The test case directive (``robot_tests``) accepts also an option ``tags``,
which is optional. It should inclue a comma separated list of the tags to be
used when filtering the tests to be embedded.

.. note::

   The documentation found from the embedded tests and keywords is parsed using
   Docutils, as a part of the target document. This is different from `Robot
   Framework`_'s own documentation tools, which support their custom markup.

.. _Robot Framework: http://pypi.python.org/pypi/robotframework
