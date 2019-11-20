# -*- coding: utf-8 -*-
"""
Unit tests for .
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import shutil
import tempfile
from unittest import TestCase, SkipTest
from unittest.mock import MagicMock

from qgis_plutil.constants import DONT_ADD_TO_QUEUE
from qgis_plutil.thread_support.messages.hello import HelloMessage

logger = logging.getLogger('tests.')


class TestHelloMessage(TestCase):
    def setUp(self):
        self.plugin = MagicMock()
        self.thread_side = MagicMock()
        self.testee = HelloMessage(self.plugin, self.thread_side)

    def tearDown(self):
        self.testee = None

    def test_init(self):
        self.assertEqual(self.testee.plugin, self.plugin)
        self.assertEqual(self.testee.thread_side, self.thread_side)
        self.assertIsNotNone(self.testee.message_id)

    def test_on_gui_side(self):
        result= self.testee.on_gui_side()
        self.assertEqual(self.thread_side.state, self.thread_side.STATE_CONNECTED)
        self.assertEqual(result, DONT_ADD_TO_QUEUE)
