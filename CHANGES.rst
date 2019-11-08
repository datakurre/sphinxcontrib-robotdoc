Changelog
=========

0.11.0 (2019-11-08)
-------------------

- Fix bad escape
  [Jasper Craeghs]


0.10.0 (2018-05-11)
-------------------

- Add to release as universal wheel
  [Asko Soukka]
- Changes for newer sphinx versions
  [Stein Heselmans]


0.9.1 (2017-05-31)
------------------

- Allow for tabs in documentation of robot files
  [Stein Heselmans]


0.9.0 (2017-05-21)
------------------

- Python 3 support
  [Stein Heselmans]


0.8.0 (2015-10-09)
------------------

- Change to separate tags with double space instead comma
  [Asko Soukka]


0.7.3 (2014-06-13)
------------------

- Added documentation generating for test-cases, keywords tags in expanded style.
  [Tomasz Kolek]


0.7.2 (2013-10-19)
------------------

- Fix to use RobotFrameworkLexer from Pygments. Require Pygments >= 1.6rc1
  [Asko Soukka]
- Drop dependency on robotframeworklexer, because it's included in Pygments
  [Asko Soukka]

0.7.0 (2013-10-16)
------------------

- Rename directives to ``robot-source``, ``robot-settings``,
  ``robot-variables``, ``robot-tests`` and ``robot-keywords``, but keep
  the old directives for backwards compatibility.

0.6.0 (2013-09-28)
------------------

- Add 'minimal' style for keywords directive to show keywords without
  their step definitions
  [Asko Soukka]

0.5.1 (2013-08-13)
------------------

- Fix bug where multiline documentation in settings-part was not completely
  included
  [Pawel Sabat]

0.5.0 (2013-05-17)
------------------

- Add support for resolving 'package:filename.robot'-paths using
  pkg_resources.resource_filename-method
  [Asko Soukka]
- Fix bug where source directive resulted escaped html markup
  [Asko Soukka]

0.4.1 (2013-03-24)
------------------

- Add Pygments-formatted output also for LaTex output [fixes #4]

0.4.0 (2013-03-10)
------------------

- Add new directives robot_source, robot_settings and robot_variables
- Fix relative path issue [fixes #2]
- Refactor and add support for ForLoop-nodes [fixes #1]
- Add align for BDD-keywords
- Add syntax highlighting

0.3.4 (2012-10-21)
------------------

- Fixed to use correct title style for test case and keyword titles.

0.3.3 (2012-10-21)
------------------

- Fixed a bug where an empty/missing tags option is not parsed correctly.

0.3.2 (2012-10-20)
------------------

- Refactored to use Docutils' nested_parse instead of publish_string (no more
  lxml and some support for inter-linking).

0.3.1 (2012-10-18)
------------------

- Refactored to parse test/keyword documentation with
  docutils.core.publish_string (and append them as raw nodes) instead of trying
  to parse them into sphinx document tree.

0.3.0 (2012-10-18)
------------------

- Added support for inline rst in test and keyword  documentations.
- Added support for *tags*.
- Added alternative *source* option as an alias for *suite* option in tests.
- Added alternative *source* and *resource* options as an alias for *suite*
  option in keywords.
- Fixed to filter comment lines from steps.

0.2.0 (2012-10-14)
------------------

- Fixed node adapters to return section instead of topics.

0.1.1 (2012-10-14)
------------------

- Fixed parsing of resource-only files for keywords.

0.1.0 (2012-10-14)
------------------

- Proof of concept.
