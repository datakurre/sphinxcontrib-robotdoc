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

import robot


def flatten(list_):
    return [item for sublist in list_ for item in sublist]


def get_title_style(used_styles=[], level=1):
    if len(used_styles) >= level:
        return used_styles[level - 1]
    else:
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

        steps = nodes.literal_block()
        steps.extend(flatten(map(Adapter(self.context), all_steps)))

        # Insert newlines between steps:
        for i in range(len(steps[:-1]), 0, -1):
            steps.insert(i, nodes.inline(text='\n'))
        node.append(steps)

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

        steps = nodes.literal_block()
        steps.extend(flatten(map(Adapter(self.context), all_steps)))

        # Insert newlines between steps:
        for i in range(len(steps[:-1]), 0, -1):
            steps.insert(i, nodes.inline(text='\n'))
        node.append(steps)

        return [node]

Adapter.register(robot.parsing.model.UserKeyword, UserKeywordNode)


class TestCasesDirective(Directive):
    """Robot test cases directive"""

    has_content = True

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
        'tags': directives.unchanged,
    }

    def run(self):
        source_directory = os.path.dirname(self.state.document.current_source)
        to_cwd = os.path.relpath(os.getcwd(), source_directory)

        path = self.options.get('source', self.options.get('suite'))
        filename = os.path.relpath(path, to_cwd)
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
    """Robot user keywords directive"""

    has_content = True

    option_spec = {
        'source': directives.path,
        'suite': directives.path,  # alias for 'source'
        'resource': directives.path,  # alias for 'source'
    }

    def run(self):
        source_directory = os.path.dirname(self.state.document.current_source)
        to_cwd = os.path.relpath(os.getcwd(), source_directory)

        path = self.options.get(
            'source', self.options.get('suite', self.options.get('resource')))
        filename = os.path.relpath(path, to_cwd)
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
    app.add_directive('robot_tests', TestCasesDirective)
    app.add_directive('robot_keywords', KeywordsDirective)
