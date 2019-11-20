# -*- coding: utf-8 -*-
"""
Unit tests for ThreadSide.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import shutil
import tempfile
from queue import Queue
from unittest import TestCase, SkipTest
from unittest.mock import MagicMock

from qgis_plutil.thread_support.messages.base import TsMessage
from qgis_plutil.thread_support.messages.hello import HelloMessage
from qgis_plutil.thread_support.thread_side import ThreadSide

logger = logging.getLogger('tests.plutil.thread_side')


class TestThreadSide(TestCase):
    def setUp(self):
        self.plugin = MagicMock()
        self.testee = ThreadSide(plugin=self.plugin)

    def tearDown(self):
        self.testee = None

    def test_init(self):
        plugin = MagicMock()
        testee = ThreadSide(plugin=plugin)
        self.assertIsNone(testee.gui_side)
        self.assertEqual(testee.plugin, plugin)
        self.assertIsInstance(testee.queue, Queue)
        self.assertEqual(testee.state, testee.STATE_DISCONNECTED)

    def test_thread_side_started(self):
        self.assertEqual(self.testee.state, self.testee.STATE_DISCONNECTED)
        self.testee.send_to_gui = MagicMock()
        self.testee.thread_side_started()
        self.assertEqual(self.testee.state, self.testee.STATE_CONNECTING)
        self.testee.send_to_gui.assert_called_once()
        args, kwargs = self.testee.send_to_gui.call_args
        self.assertEqual(len(args), 1)
        self.assertEqual(len(kwargs), 0)
        message = args[0]
        self.assertIsInstance(message, HelloMessage)

    def test_send_to_gui(self):
        self.testee.sig.clear()
        message = MagicMock(spec=TsMessage)
        message.message_id = 999
        self.testee.send_to_gui(message)
        message.on_thread_side.assert_called_once()
        self.assertEqual(self.testee.queue.qsize(), 1)
        back = self.testee.queue.get()
        self.assertEqual(back, message)
        self.assertTrue(self.testee.sig.is_set())
