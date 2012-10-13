# -*- coding: utf-8 -*-
""" Robot Framework AutoDoc for Sphinx """

import os

from docutils.parsers.rst import directives

from sphinx.util.compat import (
    nodes,
    Directive
)

import robot


class TestCaseDirectived(Directive):
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
            tests = filter(lambda x: x.name == self.content[0].strip(),
                           suite.testcase_table.tests)
        else:
            tests = suite.testcase_table.tests

        return map(lambda x: nodes.literal_block(text=x.name), tests)


def setup(app):
    app.add_directive('robottest', TestCaseDirectived)
