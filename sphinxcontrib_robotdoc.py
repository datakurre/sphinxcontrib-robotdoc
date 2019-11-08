# -*- coding: utf-8 -*-
"""Robot Framework AutoDoc for Sphinx"""
from docutils import statemachine
from docutils.parsers.rst import directives
from pygments import highlight
# noinspection PyUnresolvedReferences
from pygments.formatters import HtmlFormatter
# noinspection PyUnresolvedReferences
from pygments.formatters import LatexFormatter
from pygments.lexers import get_lexer_by_name
from docutils.parsers.rst import Directive
from docutils import nodes
import os
import pkg_resources
import re
import robot


def flatten(list_):
    return [item for sub_list in list_ for item in sub_list]


def resolve_path(spec, cwd):
    if os.path.isfile(os.path.normpath(os.path.join(cwd, spec))):
        return os.path.normpath(os.path.join(cwd, spec))
    elif spec.count(':') and pkg_resources.resource_exists(
            *spec.split(':', 1)):
        return pkg_resources.resource_filename(*spec.split(':', 1))
    else:
        return spec


def get_title_style(used_styles=None, level=1):
    if used_styles is None:
        used_styles = []
    if len(used_styles) >= level:
        return used_styles[level - 1]
    else:
        # The following list of rst title styles has been copied from docutils:
        rst_title_styles = [
            '=', '-', '`', ':' '\'', '"', '~',
            '^', '_', '*', '+', '#', '<', '>'
        ]
        available_styles = [x for x in rst_title_styles if x not in used_styles]
        assert available_styles, ("Maximum section depth has been reached. "
                                  "No more title styles available.")
        return available_styles[0]


def get_tags_information(obj, tags):
    tags_info = ''
    for tag in tags:
        tag_object = getattr(obj, tag.lower(), None)
        if tag_object and len(tag_object.as_list()) > 1:
            tag_list = tag_object.as_list()
            tags_info += ' ' * 4 + tag_list[0] + '  ' + '  '.join(
                tag_list[1:]) + '\n'

    return tags_info


class Adapter(object):
    TAGS_LIST = []
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
        all_steps = [x for x in obj.steps if not x.is_comment()]
        return StepNode(self.context)(obj) + flatten(
            list(map(Adapter(self.context, '\\    '), all_steps)))


Adapter.register(robot.parsing.model.ForLoop, ForLoopNode)


class TestCaseNode(Adapter):
    TAGS_LIST = ["setup", "teardown", "tags", "documentation", "template",
                 "timeout"]

    def __call__(self, obj):

        used_title_styles = self.context.state.memo.title_styles
        section_level = self.context.state.memo.section_level + 1
        title_style = get_title_style(used_title_styles, section_level)
        title = obj.name + '\n' + title_style * len(obj.name) + '\n\n'
        documentation = obj.doc.value.replace('\\n', '\n')  # fix linebreaks
        documentation = documentation.replace('\\t', '    ')  # fix tabs

        temp = nodes.Element()
        lines = statemachine.string2lines(title + documentation)
        self.context.content.data = lines
        self.context.state.nested_parse(
            self.context.content,
            self.context.content_offset,
            temp, match_titles=True
        )

        node = temp.children.pop()

        if self.context.options.get('style', 'default') == 'minimal':
            return [node]

        tags_info = get_tags_information(obj,
                                         TestCaseNode.TAGS_LIST) if self.context.options.get(
            'style', 'default') == "expanded" else ''

        all_steps = [x for x in obj.steps if not x.is_comment()]

        steps = '***Test Cases***\n\n%s\n' % obj.name
        steps += tags_info
        for step in flatten(list(map(Adapter(self.context), all_steps))):
            steps += ' ' * 4 + step.astext() + '\n'

        lexer = get_lexer_by_name('robotframework')
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
    TAGS_LIST = ["docs", "args", "return_", "teardown", "timeout"]

    def __call__(self, obj):

        used_title_styles = self.context.state.memo.title_styles
        section_level = self.context.state.memo.section_level + 1
        title_style = get_title_style(used_title_styles, section_level)
        title = obj.name + '\n' + title_style * len(obj.name) + '\n\n'
        documentation = obj.doc.value.replace('\\n', '\n')  # fix linebreaks
        documentation = documentation.replace('\\t', '    ')  # fix tabs

        temp = nodes.Element()
        lines = statemachine.string2lines(title + documentation)
        self.context.content.data = lines
        self.context.state.nested_parse(
            self.context.content,
            self.context.content_offset,
            temp, match_titles=True
        )

        node = temp.children.pop()

        if self.context.options.get('style', 'default') == 'minimal':
            return [node]

        tags_info = get_tags_information(obj,
                                         UserKeywordNode.TAGS_LIST) if self.context.options.get(
            'style', 'default') == "expanded" else ''

        all_steps = [x for x in obj.steps if not x.is_comment()]

        steps = '***Keywords***\n\n%s\n' % obj.name
        steps += tags_info
        for step in flatten(list(map(Adapter(self.context), all_steps))):
            steps += ' ' * 4 + step.astext() + '\n'

        lexer = get_lexer_by_name('robotframework')
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
        return directives.choice(
            argument, ('minimal', 'default', 'expanded'))
    except ValueError:
        return 'default'


class SourceDirective(Directive):
    """Robot  directive"""
    has_content = False

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
    }

    def run(self):
        path = resolve_path(
            self.options.get('source', self.options.get('suite')),
            os.path.dirname(self.state.document.current_source)
        )

        lexer = get_lexer_by_name('robotframework')

        with open(path, 'r') as source:
            formatter = HtmlFormatter(noclasses=False)
            parsed = highlight(source.read(), lexer, formatter)
        html_node = nodes.raw('', parsed, format='html')

        with open(path, 'r') as source:
            formatter = LatexFormatter()
            parsed = highlight(source.read(), lexer, formatter)
        latex_node = nodes.raw('', parsed, format='latex')

        return [html_node, latex_node]


class SettingsDirective(Directive):
    """Robot settings directive"""
    has_content = False

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
        'resource': directives.path,  # alias for 'source'
        'style': style
    }

    def run(self):
        path = resolve_path(
            self.options.get('source', self.options.get('suite',
                                                        self.options.get(
                                                            'resource'))
                             ),
            os.path.dirname(self.state.document.current_source)
        )

        try:
            resource = robot.parsing.TestData(source=path)
        except robot.errors.DataError:
            resource = robot.parsing.ResourceFile(source=path)
            resource.populate()

        obj = resource.setting_table
        documentation = obj.doc.value.replace('\\n', '\n')  # fix linebreaks
        documentation = documentation.replace('\\t', '    ')  # fix tabs

        temp = nodes.Element()
        lines = statemachine.string2lines(documentation)
        self.content.data = lines
        self.state.nested_parse(
            self.content,
            self.content_offset,
            temp, match_titles=True
        )

        if temp.children:
            doc_node_list = temp.children[:]
        else:
            doc_node_list = []
        lexer = get_lexer_by_name('robotframework')

        with open(path, 'r') as source:
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

        with open(path, 'r') as source:
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
            parsed = regex.sub('\\\end{Verbatim}\n', parsed)

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

        if len(doc_node_list) > 0:
            out = []

            for node in doc_node_list:
                out.append(node)
            out.append(html_settings_node)
            out.append(latex_settings_node)

            return out
        else:
            return [html_settings_node, latex_settings_node]


class VariablesDirective(Directive):
    """Robot variables directive"""
    has_content = False

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
        'resource': directives.path,  # alias for 'source'
        'style': style
    }

    def run(self):
        path = resolve_path(self.options.get('source',
                                             self.options.get('suite',
                                                              self.options.get(
                                                                  'resource'))
                                             ),
                            os.path.dirname(self.state.document.current_source)
                            )

        with open(path, 'r') as source:
            lexer = get_lexer_by_name('robotframework')
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

        with open(path, 'r') as source:
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
            parsed = regex.sub('\\\end{Verbatim}\n', parsed)

        # Remove heading from the settings table when required
        if self.options.get('style', 'default') == 'default':
            parsed = re.sub('\\\PY{g\+gh}{[^}]+}\n\n', '', parsed)
            parsed = re.sub('\\\PY{g\+gu}{[^}]+}\n', '', parsed)

        latex_variables_node = nodes.raw('', parsed, format='latex')

        return [html_variables_node, latex_variables_node]


class TestCasesDirective(Directive):
    """Robot test cases directive"""
    has_content = True

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
        'tags': directives.unchanged,
        'style': style
    }

    def run(self):
        path = resolve_path(
            self.options.get('source', self.options.get('suite')),
            os.path.dirname(self.state.document.current_source)
        )

        suite = robot.parsing.TestData(source=path)

        if self.content:
            needle = re.compile(self.content[0].strip(), re.U)
        else:
            needle = re.compile('.*', re.U)

        tests = []
        suite_parent = os.path.dirname(path)

        # 1) Recurse through the test suite and filter tests by name
        def recurse(child_suite, suite_parent):
            tests.extend([x for x in child_suite.testcase_table.tests if needle.match(x.name)])

            for grandchild in getattr(child_suite, 'children', []):
                recurse(grandchild, suite_parent)

        recurse(suite, suite_parent)

        # 2) When tags option is set, filter the found tests by given tags
        tags = self.options.get('tags', '').split(',')
        tags = [x.strip() for x in tags]
        tags = [x for x in tags if bool(x)]
        tag_filter = lambda x: [y for y in [tag in x.tags.value for tag in tags] if bool(y)]

        tests = [x for x in tests if tag_filter(x)] if tags else tests

        # Finally, return Docutils nodes for the tests
        return flatten(list(map(Adapter(self), tests)))


class KeywordsDirective(Directive):
    """Robot user keywords directive"""
    has_content = True

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
        'resource': directives.path,  # alias for 'source'
        'style': style
    }

    def run(self):
        path = resolve_path(self.options.get('source',
                                             self.options.get('suite',
                                                              self.options.get(
                                                                  'resource'))
                                             ),
                            os.path.dirname(self.state.document.current_source)
                            )

        try:
            resource = robot.parsing.TestData(source=path)
        except robot.errors.DataError:
            resource = robot.parsing.ResourceFile(source=path)
            resource.populate()

        if self.content:
            needle = re.compile(self.content[0].strip(), re.U)
        else:
            needle = re.compile('.*', re.U)

        keywords = [x for x in resource.keywords if needle.match(x.name)]

        return flatten(list(map(Adapter(self), keywords)))


def setup(app):
    # Directives:
    app.add_directive('robot-source', SourceDirective)
    app.add_directive('robot-settings', SettingsDirective)
    app.add_directive('robot-variables', VariablesDirective)
    app.add_directive('robot-tests', TestCasesDirective)
    app.add_directive('robot-keywords', KeywordsDirective)

    # BBB:
    app.add_directive('robot_source', SourceDirective)
    app.add_directive('robot_settings', SettingsDirective)
    app.add_directive('robot_variables', VariablesDirective)
    app.add_directive('robot_tests', TestCasesDirective)
    app.add_directive('robot_keywords', KeywordsDirective)

    # LaTeX-support:
    if 'preamble' not in app.config.latex_elements:
        app.config.latex_elements['preamble'] = ''
    app.config.latex_elements['preamble'] += '''\
\\usepackage{fancyvrb}
\\usepackage{color}
''' + LatexFormatter().get_style_defs()
