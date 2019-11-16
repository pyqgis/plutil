# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from plutil.impl import plutil
from nose.tools import (assert_equals, assert_false, assert_true)

logger = logging.getLogger('test.plutil')


class HelperShell(plutil):
    """Overrides text output procedures for easier testing."""

    def __init__(self, *args, **kwargs):
        super(HelperShell, self).__init__(*args, **kwargs)
        self.error_messages = []
        self.info_messages = []
        self.warning_messages = []
        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0
        self.stop = False
        self.preloop()

    def assert_msg(self, errors=0, warnings=0, info=0):
        assert_equals(self.error_count, errors)
        assert_equals(self.warning_count, warnings)
        assert_equals(self.info_count, info)

    def assert_name(self):
        self.assert_missing_arg('name')

    def assert_missing_arg(self, arg_name):
        self.assert_msg(errors=1, warnings=0, info=0)
        assert_true(self.has_error('Required argument %s is missing' % arg_name))

    def commandme(self, line):
        line = self.precmd(line)
        stop = self.onecmd(line)
        self.stop = self.postcmd(stop, line)

    def clear_saved_messages(self):
        """Removes all messages that were cached by this instance."""
        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0
        self.error_messages = []
        self.info_messages = []
        self.warning_messages = []

    def needs_subcommand_helper(self, command):
        self.commandme(command)
        self.assert_msg(errors=1, warnings=0, info=0)
        assert_true(self.has_error('needs a subcommand'))
        self.clear_saved_messages()

    def unknown_argument_helper(self, argument=None):
        assert_true(self.has_error('Arguments could not be parsed:'))
        assert_true(self.has_error('Unrecognized arguments:'))
        if argument:
            assert_true(self.has_error(argument))

    def example_01(self, store="mongo", agent_name="ag1", input_name="txt1in",
                   output_name="txt1out", core_name="core",
                   i2c_path="i2c", c2o_name="c2o"):
        self.commandme("use store %s" % store)
        self.assert_msg(errors=0, warnings=0, info=0)
        self.commandme("new agent %s" % agent_name)
        self.assert_msg(errors=0, warnings=0, info=0)
        self.commandme("use agent %s" % agent_name)
        self.assert_msg(errors=0, warnings=0, info=0)
        self.commandme("new inad %s text" % input_name)
        self.assert_msg(errors=0, warnings=0, info=0)
        self.commandme("new outad %s text" % output_name)
        self.assert_msg(errors=0, warnings=0, info=0)
        self.commandme("new region %s region" % core_name)
        self.assert_msg(errors=0, warnings=0, info=0)
        self.commandme("new path %s local  %s > %s" % (
            i2c_path, input_name, core_name))
        self.assert_msg(errors=0, warnings=0, info=0)
        self.commandme("new path %s local  %s > %s" % (
            c2o_name, core_name, output_name))
        self.assert_msg(errors=0, warnings=0, info=0)

    @staticmethod
    def has_text(text, input_list, index):

        def find_in_item(item, to_search):
            if isinstance(item, (list, tuple, set)):
                for o3o in item:
                    if find_in_item(o3o, to_search):
                        return True
            elif to_search in item:
                return True
            return False

        if index is None:
            return find_in_item(input_list, text)
        else:
            return find_in_item(input_list[index], text)

    def has_info(self, text, index=None):
        return HelperShell.has_text(text, self.info_messages, index)

    def has_error(self, text, index=None):
        return HelperShell.has_text(text, self.error_messages, index)

    def has_warning(self, text, index=None):
        return HelperShell.has_text(text, self.warning_messages, index)

    def assert_has_info(self, text, index=None):
        assert_true(self.has_info(text, index=None))

    def assert_has_error(self, text, index=None):
        assert_true(self.has_error(text, index=None))

    def assert_has_warning(self, text, index=None):
        assert_true(self.has_warning(text, index=None))

    def assert_not_info(self, text, index=None):
        assert_false(self.has_info(text, index=None))

    def assert_not_error(self, text, index=None):
        assert_false(self.has_error(text, index=None))

    def assert_not_warning(self, text, index=None):
        assert_false(self.has_warning(text, index=None))

    def assert_has_help(self, the_command):
        self.commandme("help %s" % the_command)
        self.assert_has_info("Example")
        self.assert_has_info("$: %s" % the_command)
        self.clear_saved_messages()

    @staticmethod
    def tokenize_message(the_msg):
        if isinstance(the_msg, (list, set, tuple)):
            return the_msg

        parts = the_msg.split("\n")
        result = []
        for o1o in parts:
            o1o = o1o.strip()
            if len(o1o) > 0:
                result.append(o1o)
        return result

    def error(self, message, description=''):
        """Print an error message."""
        self.error_messages.append((
            message, HelperShell.tokenize_message(description)))
        super(HelperShell, self).error(message, description)

    def warning(self, message, description=''):
        """Print an warning message."""
        self.warning_messages.append((
            message, HelperShell.tokenize_message(description)))
        super(HelperShell, self).warning(message, description)

    def info(self, message):
        """Print an informative message."""
        self.info_count = self.info_count + 1
        self.info_messages.append(
            HelperShell.tokenize_message(message))
        super(HelperShell, self).info(message)

    def info_start(self, message):
        """The beginning of an informative."""
        self.info_count = self.info_count + 1
        self.info_messages.append(
            HelperShell.tokenize_message(message))
        super(HelperShell, self).info_start(message)

    def info_line(self, message):
        """An informative line."""
        self.info_messages[-1].extend(
            HelperShell.tokenize_message(message))
        super(HelperShell, self).info_line(message)

    def info_end(self, message):
        """The end of an informative."""
        self.info_messages[-1].extend(
            HelperShell.tokenize_message(message))
        super(HelperShell, self).info_end(message)
