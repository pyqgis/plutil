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
from unittest import TestCase, SkipTest
from unittest.mock import MagicMock

from qgis_plutil.thread_support.gui_side import GuiSide

logger = logging.getLogger('tests.plutil.thread_support.gui_side')


class TestGuiSide(TestCase):
    def setUp(self):
        self.testee = GuiSide()

    def tearDown(self):
        self.testee = None

    def test_init(self):
        self.testee = GuiSide()
