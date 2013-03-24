# -*- coding: utf-8 -*-
"""Robot Framework AutoDoc for Sphinx
"""

import re
import os

from docutils import statemachine
from docutils.parsers.rst import directives

from sphinx.util.compat import (
    nodes,
    Directive
)

from pygments import highlight
from pygments.formatters import (
    HtmlFormatter,
    LatexFormatter
)
from robotframeworklexer import RobotFrameworkLexer

import robot


def flatten(list_):
    return [item for sublist in list_ for item in sublist]


def get_title_style(used_styles=[], level=1):
    if len(used_styles) >= level:
        return used_styles[level - 1]
    else:
        # The following list of rst title styles has been copied from docutils:
        rst_title_styles = [
            '=', '-', '`', ':' '\'', '"', '~',
            '^', '_', '*', '+', '#', '<', '>'
        ]
        available_styles = filter(lambda x: x not in used_styles,
                                  rst_title_styles)
        assert available_styles, ("Maximum section depth has been reached. "
                                  "No more title styles available.")
        return available_styles[0]


class Adapter(object):

    registry = {}

    def __init__(self, context, *args):
        self.context = context
        self.args = args

    def __call__(self, obj):
        return self.registry[obj.__class__](self.context, *self.args)(obj)

    @classmethod
    def register(cls, klass, adapter):
        cls.registry[klass] = adapter


class StepNode(Adapter):

    def __init__(self, context, prefix=''):
        super(StepNode, self).__init__(context)
        self.prefix = prefix

    def __call__(self, obj):
        prefix = self.prefix
        value = '  '.join(obj.as_list())
        if value.startswith('When ') or value.startswith('Then '):
            prefix = ' ' + prefix
        elif value.startswith('And '):
            prefix = '  ' + prefix
        return [nodes.inline(text=prefix + value)]

Adapter.register(robot.parsing.model.Step, StepNode)


class ForLoopNode(Adapter):

    def __call__(self, obj):
        all_steps = filter(lambda x: not x.is_comment(), obj.steps)
        return StepNode(self.context)(obj) + flatten(
            map(Adapter(self.context, '\\    '), all_steps))

Adapter.register(robot.parsing.model.ForLoop, ForLoopNode)


class TestCaseNode(Adapter):

    def __call__(self, obj):

        used_title_styles = self.context.state.memo.title_styles
        section_level = self.context.state.memo.section_level + 1
        title_style = get_title_style(used_title_styles, section_level)
        title = obj.name + '\n' + title_style * len(obj.name) + '\n\n'
        documentation = obj.doc.value.replace('\\n', '\n')  # fix linebreaks

        temp = nodes.Element()
        lines = statemachine.string2lines(title + documentation)
        self.context.content.data = lines
        self.context.state.nested_parse(
            self.context.content,
            self.context.content_offset,
            temp, match_titles=True
        )

        node = temp.children.pop()

        all_steps = filter(lambda x: not x.is_comment(), obj.steps)

        steps = u'***Test Cases***\n\n%s\n' % obj.name
        for step in flatten(map(Adapter(self.context), all_steps)):
            steps += ' ' * 4 + step.astext() + '\n'

        lexer = RobotFrameworkLexer()
        formatter = HtmlFormatter(noclasses=False)
        parsed = highlight(steps, lexer, formatter)
        if self.context.options.get('style', 'default') == 'default':
            parsed = re.sub('<span class="gh">[^\n]+\n\n', '', parsed)
            parsed = re.sub('<span class="gu">[^<]+</span>', '', parsed)
            parsed = re.sub('<pre><span class="p"></span>', '<pre>', parsed)
            parsed = re.sub('<span class="p">    ', '<span class="p">', parsed)
        node.append(nodes.raw('', parsed, format='html'))

        formatter = LatexFormatter()
        parsed = highlight(steps, lexer, formatter)
        if self.context.options.get('style', 'default') == 'default':
            parsed = re.sub('\\\PY{g\+gh}{[^}]+}\n\n', '', parsed)
            parsed = re.sub('\\\PY{g\+gu}{[^}]+}\n', '', parsed)
        node.append(nodes.raw('', parsed, format='latex'))

        return [node]

Adapter.register(robot.parsing.model.TestCase, TestCaseNode)


class UserKeywordNode(Adapter):

    def __call__(self, obj):

        used_title_styles = self.context.state.memo.title_styles
        section_level = self.context.state.memo.section_level + 1
        title_style = get_title_style(used_title_styles, section_level)
        title = obj.name + '\n' + title_style * len(obj.name) + '\n\n'
        documentation = obj.doc.value.replace('\\n', '\n')  # fix linebreaks

        temp = nodes.Element()
        lines = statemachine.string2lines(title + documentation)
        self.context.content.data = lines
        self.context.state.nested_parse(
            self.context.content,
            self.context.content_offset,
            temp, match_titles=True
        )

        node = temp.children.pop()

        all_steps = filter(lambda x: not x.is_comment(), obj.steps)

        steps = u'***Keywords***\n\n%s\n' % obj.name
        for step in flatten(map(Adapter(self.context), all_steps)):
            steps += ' ' * 4 + step.astext() + '\n'

        lexer = RobotFrameworkLexer()
        formatter = HtmlFormatter(noclasses=False)
        parsed = highlight(steps, lexer, formatter)
        if self.context.options.get('style', 'default') == 'default':
            parsed = re.sub('<span class="gh">[^\n]+\n\n', '', parsed)
            parsed = re.sub('<span class="gu">[^<]+</span>', '', parsed)
            parsed = re.sub('<pre><span class="p"></span>', '<pre>', parsed)
            parsed = re.sub('<span class="p">    ', '<span class="p">', parsed)
        node.append(nodes.raw('', parsed, format='html'))

        formatter = LatexFormatter()
        parsed = highlight(steps, lexer, formatter)
        if self.context.options.get('style', 'default') == 'default':
            parsed = re.sub('\\\PY{g\+gh}{[^}]+}\n\n', '', parsed)
            parsed = re.sub('\\\PY{g\+gu}{[^}]+}\n', '', parsed)
        node.append(nodes.raw('', parsed, format='latex'))

        return [node]

Adapter.register(robot.parsing.model.UserKeyword, UserKeywordNode)


def style(argument):
    try:
        return directives.choice(argument, ('default', 'expanded'))
    except ValueError:
        return 'default'


class SourceDirective(Directive):
    """Robot test suite directive
    """
    has_content = False

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
    }

    def run(self):
        source_directory = os.path.dirname(self.state.document.current_source)
        path = self.options.get('source', self.options.get('suite'))
        filename = os.path.normpath(os.path.join(source_directory, path))

        lexer = RobotFrameworkLexer()

        with open(filename, 'r') as source:
            formatter = HtmlFormatter(noclasses=False)
            parsed = highlight(source.read(), lexer, formatter)
        html_node = nodes.raw('', parsed, format='html')

        with open(filename, 'r') as source:
            formatter = LatexFormatter()
            parsed = highlight(source.read(), lexer, formatter)
        latex_node = nodes.raw('', parsed, format='latex')

        return html_node + latex_node


class SettingsDirective(Directive):
    """Robot settings directive
    """
    has_content = False

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
        'resource': directives.path,  # alias for 'source'
        'style': style
    }

    def run(self):
        source_directory = os.path.dirname(self.state.document.current_source)
        path = self.options.get(
            'source', self.options.get('suite', self.options.get('resource')))
        filename = os.path.normpath(os.path.join(source_directory, path))

        try:
            resource = robot.parsing.TestData(source=filename)
        except robot.errors.DataError:
            resource = robot.parsing.ResourceFile(source=filename)
            resource.populate()

        obj = resource.setting_table
        documentation = obj.doc.value.replace('\\n', '\n')  # fix linebreaks

        temp = nodes.Element()
        lines = statemachine.string2lines(documentation)
        self.content.data = lines
        self.state.nested_parse(
            self.content,
            self.content_offset,
            temp, match_titles=True
        )

        if temp.children:
            doc_node = temp.children.pop()
        else:
            doc_node = None
        lexer = RobotFrameworkLexer()

        with open(filename, 'r') as source:
            formatter = HtmlFormatter(noclasses=False)
            parsed = highlight(source.read(), lexer, formatter)

        # Remove everything after the settings table
        removable_sections = ['Variables', 'Test Cases', 'Keywords']
        for section in removable_sections:
            regex = re.compile(
                '<span class="gh">\*\*\* %s \*\*\*</span>.*</pre>' % section,
                re.I + re.S + re.M
            )
            parsed = regex.sub('</pre>', parsed)
        parsed = re.sub('<span class="p"></span>\n\n</pre>', '</pre>', parsed)

        # Remove documentation from the settings table
        if parsed.find('<span class="kn">Documentation') >= 0:
            start = parsed.find('<span class="kn">Documentation')
            if parsed[start + 30:].find('<span class="kn">') >= 0:
                end = parsed[start + 30:].find('<span class="kn">') + 30
            else:
                end = parsed[start:].find('</pre>')
            parsed = parsed[:start] + parsed[start + end:]

        # Remove heading from the settings table when required
        if self.options.get('style', 'default') == 'default':
            parsed = re.sub('<span class="gh">[^\n]+\n\n', '', parsed)

        html_settings_node = nodes.raw('', parsed, format='html')

        with open(filename, 'r') as source:
            formatter = LatexFormatter()
            parsed = highlight(source.read(), lexer, formatter)

        # Remove everything after the settings table
        removable_sections = ['Variables', 'Test Cases', 'Keywords']
        for section in removable_sections:
            regex = re.compile(
                '\\\PY{g\+gh}{\*\*\* %s \*\*\*}.*\\\end{Verbatim}\n*$' % (
                    section),
                re.I + re.S + re.M
            )
            parsed = regex.sub('\end{Verbatim}\n', parsed)

        # Remove documentation from the settings table
        if parsed.find('\\PY{k+kn}{Documentation}') >= 0:
            start = parsed.find('\\PY{k+kn}{Documentation}')
            if parsed[start + 24:].find('\PY{k+kn}') >= 0:
                end = parsed[start + 24:].find('\PY{k+kn}') + 24
            else:
                end = parsed[start:].find('\\end{Verbatim}')
            parsed = parsed[:start] + parsed[start + end:]

        # Remove heading from the settings table when required
        if self.options.get('style', 'default') == 'default':
            parsed = re.sub('\\\PY{g\+gh}{[^}]+}\n\n', '', parsed)
            parsed = re.sub('\\\PY{g\+gu}{[^}]+}\n', '', parsed)

        latex_settings_node = nodes.raw('', parsed, format='latex')

        if doc_node:
            return [doc_node, html_settings_node, latex_settings_node]
        else:
            return [html_settings_node, latex_settings_node]


class VariablesDirective(Directive):
    """Robot variables directive
    """
    has_content = False

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
        'resource': directives.path,  # alias for 'source'
        'style': style
    }

    def run(self):
        source_directory = os.path.dirname(self.state.document.current_source)
        path = self.options.get(
            'source', self.options.get('suite', self.options.get('resource')))
        filename = os.path.normpath(os.path.join(source_directory, path))

        with open(filename, 'r') as source:
            lexer = RobotFrameworkLexer()
            formatter = HtmlFormatter(noclasses=False)
            parsed = highlight(source.read(), lexer, formatter)

        # Remove everything but the variables table
        removable_sections = ['Test Cases', 'Keywords']
        regex = re.compile(
            '(<pre>).*(<span class="gh">\*\*\* Variables \*\*\*</span>)',
            re.I + re.S + re.M
        )
        parsed = regex.sub('\\1\\2', parsed)
        for section in removable_sections:
            regex = re.compile(
                '<span class="gh">\*\*\* %s \*\*\*</span>.*</pre>' % section,
                re.I + re.S + re.M
            )
            parsed = regex.sub('</pre>', parsed)
        parsed = re.sub('<span class="p"></span>\n\n</pre>', '</pre>', parsed)

        # Remove heading from the variables table when required
        if self.options.get('style', 'default') == 'default':
            parsed = re.sub('<span class="gh">[^\n]+\n\n', '', parsed)

        html_variables_node = nodes.raw('', parsed, format='html')

        with open(filename, 'r') as source:
            formatter = LatexFormatter()
            parsed = highlight(source.read(), lexer, formatter)

        # Remove everything but the variables table
        removable_sections = ['Test Cases', 'Keywords']
        regex = re.compile(
            '(\\\\begin{Verbatim}\[[^\]]*\]\n).*'
            '(\\\\PY{g\+gh}{\*\*\*\sVariables\s\*\*\*})',
            re.I + re.S + re.M
        )
        parsed = regex.sub('\\1\\2', parsed)
        for section in removable_sections:
            regex = re.compile(
                '\\\PY{g\+gh}{\*\*\* %s \*\*\*}.*\\\end{Verbatim}\n*$' % (
                    section),
                re.I + re.S + re.M
            )
            parsed = regex.sub('\end{Verbatim}\n', parsed)

        # Remove heading from the settings table when required
        if self.options.get('style', 'default') == 'default':
            parsed = re.sub('\\\PY{g\+gh}{[^}]+}\n\n', '', parsed)
            parsed = re.sub('\\\PY{g\+gu}{[^}]+}\n', '', parsed)

        latex_variables_node = nodes.raw('', parsed, format='latex')

        return [html_variables_node, latex_variables_node]


class TestCasesDirective(Directive):
    """Robot test cases directive
    """
    has_content = True

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
        'tags': directives.unchanged,
        'style': style
    }

    def run(self):
        source_directory = os.path.dirname(self.state.document.current_source)
        path = self.options.get('source', self.options.get('suite'))
        filename = os.path.normpath(os.path.join(source_directory, path))
        suite = robot.parsing.TestData(source=filename)

        if self.content:
            needle = re.compile(self.content[0].strip(), re.U)
        else:
            needle = re.compile('.*', re.U)

        tests = []
        suite_parent = os.path.dirname(filename)

        # 1) Recurse through the test suite and filter tests by name
        def recurse(child_suite, suite_parent):
            tests.extend(filter(lambda x: needle.match(x.name),
                         child_suite.testcase_table.tests))

            for grandchild in getattr(child_suite, 'children', []):
                recurse(grandchild, suite_parent)
        recurse(suite, suite_parent)

        # 2) When tags option is set, filter the found tests by given tags
        tags = self.options.get('tags', '').split(',')
        tags = map(lambda x: x.strip(), tags)
        tags = filter(lambda x: bool(x), tags)
        tag_filter = lambda x: filter(lambda y: bool(y),
                                      [tag in x.tags.value for tag in tags])

        tests = filter(lambda x: tag_filter(x), tests) if tags else tests

        # Finally, return Docutils nodes for the tests
        return flatten(map(Adapter(self), tests))


class KeywordsDirective(Directive):
    """Robot user keywords directive
    """
    has_content = True

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
        'resource': directives.path,  # alias for 'source'
        'style': style
    }

    def run(self):
        source_directory = os.path.dirname(self.state.document.current_source)
        path = self.options.get(
            'source', self.options.get('suite', self.options.get('resource')))
        filename = os.path.normpath(os.path.join(source_directory, path))
        try:
            resource = robot.parsing.TestData(source=filename)
        except robot.errors.DataError:
            resource = robot.parsing.ResourceFile(source=filename)
            resource.populate()

        if self.content:
            needle = re.compile(self.content[0].strip(), re.U)
        else:
            needle = re.compile('.*', re.U)

        keywords = filter(lambda x: needle.match(x.name), resource.keywords)

        return flatten(map(Adapter(self), keywords))


def setup(app):
    app.config.latex_preamble += '''\
\usepackage{fancyvrb}
\usepackage{color}
''' + LatexFormatter().get_style_defs()
    app.add_directive('robot_source', SourceDirective)
    app.add_directive('robot_settings', SettingsDirective)
    app.add_directive('robot_variables', VariablesDirective)
    app.add_directive('robot_tests', TestCasesDirective)
    app.add_directive('robot_keywords', KeywordsDirective)
