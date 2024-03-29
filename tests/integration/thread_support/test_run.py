# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import threading
from time import sleep
from unittest import TestCase, SkipTest
from unittest.mock import MagicMock

from PyQt5.QtCore import QCoreApplication, QEventLoop

from qgis_plutil.thread_support.gui_side import GuiSide
from qgis_plutil.thread_support.messages.base import TsMessage
from qgis_plutil.thread_support.thread_side import ThreadSide

logger = logging.getLogger('tests.plutil.thread_support')


class WorkerThread(ThreadSide, threading.Thread):
    def __init__(self, *args, **kwargs):
        super(WorkerThread, self).__init__(name="WorkerThread", *args, **kwargs)

        # Set this to terminate the thread.
        self.stop = threading.Event()

    def run(self):
        self.thread_side_started()
        while not self.stop.is_set():
            pass


class AMessage(TsMessage):
    def __init__(self, *args, **kwargs):
        super(AMessage, self).__init__(*args, **kwargs)
        self.on_thread_side_called = 0
        self.on_on_gui_side = 0

    def on_thread_side(self):
        """ Executed just before the messages leaves the thread side. """
        self.on_thread_side_called = self.on_thread_side_called + 1

    def on_gui_side(self):
        """ Executed when the message has reached GUI side. """
        self.on_on_gui_side = self.on_on_gui_side + 1


class TestTestee(TestCase):
    def setUp(self):
        self.plugin = MagicMock()
        self.app = QCoreApplication([])
        self.thread = WorkerThread(self.plugin)
        self.testee = GuiSide()
        self.testee.tie(self.thread)
        self.thread.start()
        sleep(0.5)
        self.testee.receiver()

    def tearDown(self):
        self.thread.stop.set()
        self.testee = None
        self.app.exit()

    def test_init(self):
        logger.debug("Run GuiSide/ThreadSide test starting")
        self.app.processEvents(QEventLoop.AllEvents, 1)
        sleep(0.2)
        self.assertEqual(self.thread.state, self.thread.STATE_CONNECTED)
        msg = AMessage(self.plugin, self.thread)
        self.assertIsNotNone(msg.message_id)
        self.thread.send_to_gui(msg)
        sleep(0.2)
        self.testee.receiver()
        self.app.processEvents(QEventLoop.AllEvents, 1)
        self.assertEqual(msg.on_thread_side_called, 1)
        self.assertEqual(msg.on_thread_side_called, 1)
        msg = AMessage(self.plugin, self.thread)
        self.assertIsNotNone(msg.message_id)
        self.thread.send_to_gui(msg)
        sleep(0.2)
        self.testee.receiver()
        self.app.processEvents(QEventLoop.AllEvents, 1)
        self.assertEqual(msg.on_thread_side_called, 1)
        self.assertEqual(msg.on_thread_side_called, 1)
        logger.debug("Run GuiSide/ThreadSide test ends")
