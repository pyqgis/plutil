# -*- coding: utf-8 -*-
"""
Unit tests for GuiSide.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import shutil
import tempfile
import threading
from queue import Queue
from unittest import TestCase, SkipTest
from unittest.mock import MagicMock

from PyQt5.QtCore import QBasicTimer

from qgis_plutil.thread_support.gui_side import GuiSide
from qgis_plutil.thread_support.messages.base import TsMessage
from qgis_plutil.thread_support.messages.hello import HelloMessage

logger = logging.getLogger('tests.plutil.thread_support.gui_side')


class TestGuiSide(TestCase):
    def setUp(self):
        self.testee = GuiSide()
        self.plugin = MagicMock()
        self.thread_side = MagicMock()
        self.thread_side.sig = MagicMock(spec=threading.Event)
        self.testee.side_workers.append(self.thread_side)
        self.thread_side.queue = Queue()

    def tearDown(self):
        self.testee = None

    def test_init(self):
        self.assertIsInstance(self.testee.side_workers, list)
        self.assertIsInstance(self.testee.timer, QBasicTimer)

    def test_message_accepted(self):
        message = MagicMock()
        self.testee.message_accepted(message)
        message.on_gui_side.assert_called_once()

    def test_receiver(self):
        self.testee.message_accepted = MagicMock()
        self.thread_side.sig.is_set.return_value=False
        self.testee.receiver()
        self.thread_side.sig.clear.assert_not_called()

        self.thread_side.sig.is_set.return_value = True
        self.testee.receiver()
        self.thread_side.sig.clear.assert_called_once()

        message = MagicMock(spec=TsMessage)
        message.plugin = self.plugin
        message.thread_side = self.thread_side
        self.thread_side.queue.put(message)

        self.testee.state = self.testee.STATE_DISCONNECTED
        with self.assertRaises(AssertionError):
            self.testee.receiver()

        message = HelloMessage(self.plugin, self.thread_side)
        self.thread_side.queue.put(message)
        self.testee.state = self.testee.STATE_CONNECTING
        logger.debug("is --------------- STATE_CONNECTING")
        self.testee.receiver()
        logger.debug("should be --------------- STATE_CONNECTED")
        self.assertEqual(self.testee.state, self.testee.STATE_CONNECTED)
        self.testee.message_accepted.assert_called_once_with(message)

    def test_receiver_unknown_state(self):
        self.testee.state = 99999
        self.thread_side.sig.is_set.return_value = True

        message = MagicMock(spec=TsMessage)
        message.plugin = self.plugin
        message.thread_side = self.thread_side
        self.thread_side.queue.put(message)

        with self.assertRaises(ValueError):
            self.testee.receiver()

    def test_receiver_connected(self):
        self.testee.message_accepted = MagicMock()
        self.testee.state = self.testee.STATE_CONNECTED
        self.thread_side.sig.is_set.return_value = True

        message = MagicMock(spec=TsMessage)
        message.plugin = self.plugin
        message.thread_side = self.thread_side
        self.thread_side.queue.put(message)

        self.testee.receiver()
        self.testee.message_accepted.assert_called_once_with(message)

    def test_receiver_bad_message(self):
        self.testee.message_accepted = MagicMock()
        self.thread_side.sig.is_set.return_value = True

        message = MagicMock(spec=TsMessage)
        message.plugin = self.plugin
        message.thread_side = self.thread_side
        self.thread_side.queue.put(message)

        # State expects HelloMessage
        self.testee.state = self.testee.STATE_CONNECTING
        with self.assertRaises(AssertionError):
            self.testee.receiver()
