# -*- coding: utf-8 -*-
"""Robot Framework AutoDoc for Sphinx"""

import re
import os

from lxml import etree

from docutils.parsers.rst import directives
from docutils.core import publish_string

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

    test = nodes.section()

    test.append(nodes.title(text=obj.name))
    test['ids'].append(nodes.make_id(obj.name))

    doc = obj.doc.value.replace('\\n', '\n')  # fix linebreaks
    if doc:
        doc_html = publish_string(doc, writer_name="html")
        root = etree.fromstring(doc_html)
        body = root.xpath(
            "//xhtml:div[@class='document']",
            namespaces={'xhtml': 'http://www.w3.org/1999/xhtml'}
        )[0]
        # XXX: This well leave xmlns-declarations into generaed HTML-tags:
        html = ''.join(map(lambda node: etree.tostring(node),
                           body.getchildren()))
        raw = nodes.raw(text=html, format="html")
        test.append(raw)

    comment = re.compile("^\s*#.*")
    all_steps = filter(lambda x: not comment.match(x.as_list()[0]), obj.steps)

    steps = nodes.literal_block()
    steps.extend(map(StepNode, all_steps))

    # Insert newlines between steps:
    for i in range(len(all_steps[:-1]), 0, -1):
        steps.insert(i, nodes.inline(text='\n'))
    test.append(steps)

    return test


def KeywordNode(obj):
    assert isinstance(obj, robot.parsing.model.UserKeyword)

    keyword = nodes.section()

    keyword.append(nodes.title(text=obj.name))
    keyword['ids'].append(nodes.make_id(obj.name))

    doc = obj.doc.value.replace('\\n', '\n')  # fix linebreaks
    if doc:
        doc_html = publish_string(doc, writer_name="html")
        root = etree.fromstring(doc_html)
        body = root.xpath(
            "//xhtml:div[@class='document']",
            namespaces={'xhtml': 'http://www.w3.org/1999/xhtml'}
        )[0]
        # XXX: This well leave xmlns-declarations into generaed HTML-tags:
        html = ''.join(map(lambda node: etree.tostring(node),
                           body.getchildren()))
        raw = nodes.raw(text=html, format="html")
        keyword.append(raw)

    comment = re.compile("^\s*#.*")
    all_steps = filter(lambda x: not comment.match(x.as_list()[0]), obj.steps)

    steps = nodes.literal_block()
    steps.extend(map(StepNode, all_steps))

    # insert newlines:
    for i in range(len(all_steps[:-1]), 0, -1):
        steps.insert(i, nodes.inline(text='\n'))

    keyword.append(steps)

    return keyword


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
        tags = map(lambda x: x.strip(),
                   self.options.get('tags', '').split(','))
        tag_filter = lambda x: filter(lambda y: bool(y),
                                      [tag in x.tags.value for tag in tags])
        tests = filter(lambda x: tag_filter(x), tests) if tags else tests

        # Finally, return Docutils nodes for the tests
        return map(TestCaseNode, tests)


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

        keywords = filter(lambda x: needle.match(x.name),
                          resource.keywords)
        return map(KeywordNode, keywords)


def setup(app):
    app.add_directive('robot_tests', TestCasesDirective)
    app.add_directive('robot_keywords', KeywordsDirective)
