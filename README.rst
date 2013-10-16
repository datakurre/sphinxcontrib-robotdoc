Introduction
------------

This package provides a Sphinx-extension to embed Robot Framework test suites,
test cases, or user keywords in into Sphinx-documents in spirit of the autodoc
Sphinx-extension.


When to use?
------------

Consider not using this package.

This package was created before Robot Framework plain text syntax lexer
(highlighting support) was implemented and included into Pygments (>= 1.6rc1).
This package was also created before Robot Framework's built-in libdoc-tool got
ReST-syntax support for embedded documentation syntax (>=1.7.5) and Robot
Framework got new ReST-support (>= 1.8.2).

Nowadays, the easies way to embed Robot Framework code (plain text syntax) into
Sphinx-document should be to simply use the standard ``.. code-block::
robotframework`` or include libdoc-generated html with ``:download:``-syntax.
Yet, there may be some edge cases where this is the most convenient way to
embed external Robot examples into your documentation.


Usage
-----

Add ``sphinxcontrib_robotdoc`` into the extensions list of your Sphinx
configuration (``conf.py``)::

    extensions = [
        "sphinxcontrib_robotdoc",
    ]

Embed test cases and user keywords into your documentation with the
following custom Docutils-directives::

    .. robot-tests:: Test case title or RegExp.*
       :source: my_package:tests/acceptance/my_suite.robot
       :tags: bugs, new

    .. robot-keywords:: Keyword title or RegExp.*
       :source: my_package:tests/acceptance/my_suite.txt

Both directives (``robot-tests`` and ``robot-keywords``) take a regular
expression as their main option (or *content* in Docutils' terms) to filter the
embeded test cases or keywords found from the given ``source``-resource (or
relative path). If no regular expression is given, all found tests or keywords
will be embedded (like having ``.*`` as the default).

Path given to the mandatory ``source``-option must be either be a package
resources (using syntax *package_name:resource/path/in/package*) or a relative
path from the current document.

The test case directive (``robot-tests``) accepts also an option ``tags``,
which is optional. It should inclue a comma separated list of the tags to be
used when filtering the tests to be embedded.

Both directives take an optional ``style``-option. When ``style`` is set
to ``expanded`` the output will include headings such as the table name and
test case or keyword name. When ``style`` is set to ``minimal`` the output
will include only the target documentation strings without any robot syntax.

Please, note that he documentation found from the embedded test is parsed
using Docutils, as a part of the target document. This differs from `Robot
Framework`_'s own documentation tools, which expect its own custom markup.

.. _Robot Framework: http://pypi.python.org/pypi/robotframework


Other directives
----------------

``robot-source`` will embed a complete test suite or resource file with
syntax highlighting::

    .. robot-source::
       :source: my_package:tests/acceptance/my_suite.txt

``robot-settings`` will embed a syntax highlighted settings table (with
documentation parsed as reStructuredText) for a test suite a resource file::

    .. robot-settings::
       :source: my_package:tests/acceptance/my_suite.txt

``robot-variables`` will embed a syntax highlighted variables table (with
documentation parsed as reStructuredText) for a test suite a resource file::

    .. robot-variables::
       :source: my_package:tests/acceptance/my_suite.txt

Also directives ``robot-settings`` and ``robot-variables`` take an optional
``style``-option. When ``style`` is set to ``expanded`` the output will
include the table name.


LaTeX output
------------

LaTeX output is based on Pygments LatexFormatter, which requires custom
style definitions to be injeced into latex document preamble. That's done by
default, but when Sphinx ``latex_preamble`` setting is set manually, it
should include the following::

   from pygments.formatters import LatexFormatter

   latex_elements['latex_preamble'] = '''\
   \usepackage{fancyvrb}
   \usepackage{color}
   ''' + LatexFormatter().get_style_defs()
