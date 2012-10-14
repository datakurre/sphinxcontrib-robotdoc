# -*- coding: utf-8 -*-
""" Robot Framework AutoDoc for Sphinx """

import re
import os

from docutils.parsers.rst import directives

from sphinx.util.compat import (
    nodes,
    Directive
)

import robot


def StepNode(obj):
    assert isinstance(obj, robot.parsing.model.Step)
    return nodes.inline(text='  '.join(obj.as_list()))


def TestCaseNode(obj):
    assert isinstance(obj, robot.parsing.model.TestCase)

    test = nodes.topic()

    test.append(nodes.title(text=obj.name))

    doc = obj.doc.value.replace('\\n', '\n')  # fix linebreaks
    test.append(nodes.paragraph(text=doc))

    steps = nodes.literal_block()
    steps.extend(map(StepNode, obj.steps))
    # insert newlines:
    for i in range(len(obj.steps[:-1]), 0, -1):
        steps.insert(i, nodes.inline(text="\n"))
    test.append(steps)

    return test


def KeywordNode(obj):
    assert isinstance(obj, robot.parsing.model.UserKeyword)

    test = nodes.topic()

    test.append(nodes.title(text=obj.name))

    doc = obj.doc.value.replace('\\n', '\n')  # fix linebreaks
    test.append(nodes.paragraph(text=doc))

    steps = nodes.literal_block()
    steps.extend(map(StepNode, obj.steps))
    # insert newlines:
    for i in range(len(obj.steps[:-1]), 0, -1):
        steps.insert(i, nodes.inline(text="\n"))
    test.append(steps)

    return test



class TestCasesDirective(Directive):
    """ Robot Directive """

    has_content = True

    option_spec = {
        "suite": directives.path,
    }

    def run(self):
        source_directory = os.path.dirname(self.state.document.current_source)
        to_cwd = os.path.relpath(os.getcwd(), source_directory)

        filename = os.path.relpath(self.options["suite"], to_cwd)
        suite = robot.parsing.TestData(source=filename)

        if self.content:
            needle = re.compile(self.content[0].strip(), re.U)
        else:
            needle = re.compile(".*", re.U)

        tests = []
        suite_parent = os.path.dirname(filename)

        def recurse(child_suite, suite_parent):
            tests.extend(filter(lambda x: needle.match(x.name),
                         child_suite.testcase_table.tests))
            for grandchild in getattr(child_suite, 'children', []):
                recurse(grandchild, suite_parent)
        recurse(suite, suite_parent)

        return map(TestCaseNode, tests)


class KeywordsDirective(Directive):
    """ Robot Directive """

    has_content = True

    option_spec = {
        "suite": directives.path,
    }

    def run(self):
        source_directory = os.path.dirname(self.state.document.current_source)
        to_cwd = os.path.relpath(os.getcwd(), source_directory)

        filename = os.path.relpath(self.options["suite"], to_cwd)
        try:
            resource = robot.parsing.TestData(source=filename)
        except robot.errors.DataError:
            resource = robot.parsing.ResourceFile(source=filename)
            resource.populate()

        if self.content:
            needle = re.compile(self.content[0].strip(), re.U)
        else:
            needle = re.compile(".*", re.U)

        keywords = filter(lambda x: needle.match(x.name),
                          resource.keywords)

        return map(KeywordNode, keywords)


def setup(app):
    app.add_directive('robot_tests', TestCasesDirective)
    app.add_directive('robot_keywords', KeywordsDirective)
