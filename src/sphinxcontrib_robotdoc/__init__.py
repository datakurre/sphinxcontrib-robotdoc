# -*- coding: utf-8 -*-
"""Robot Framework AutoDoc for Sphinx"""

import re
import os

from docutils import statemachine
from docutils.parsers.rst import directives

from sphinx.util.compat import (
    nodes,
    Directive
)

import robot


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

    def __init__(self, context):
        self.context = context


class StepNode(Adapter):

    def __call__(self, obj):
        assert isinstance(obj, robot.parsing.model.Step)
        return nodes.inline(text='  '.join(obj.as_list()))


class TestCaseNode(Adapter):

    def __call__(self, obj):
        assert isinstance(obj, robot.parsing.model.TestCase)

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

        not_comment = lambda x: not re.compile("^\s*#.*").match(x.as_list()[0])
        all_steps = filter(not_comment, obj.steps)

        steps = nodes.literal_block()
        steps.extend(map(StepNode(self.context), all_steps))

        # Insert newlines between steps:
        for i in range(len(all_steps[:-1]), 0, -1):
            steps.insert(i, nodes.inline(text='\n'))
        node.append(steps)

        return node


class KeywordNode(Adapter):

    def __call__(self, obj):
        assert isinstance(obj, robot.parsing.model.UserKeyword)

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

        not_comment = lambda x: not re.compile("^\s*#.*").match(x.as_list()[0])
        all_steps = filter(not_comment, obj.steps)

        steps = nodes.literal_block()
        steps.extend(map(StepNode(self.context), all_steps))

        # Insert newlines between steps:
        for i in range(len(all_steps[:-1]), 0, -1):
            steps.insert(i, nodes.inline(text='\n'))
        node.append(steps)

        return node


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
        return map(TestCaseNode(self), tests)


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

        return map(KeywordNode(self), keywords)


def setup(app):
    app.add_directive('robot_tests', TestCasesDirective)
    app.add_directive('robot_keywords', KeywordsDirective)
