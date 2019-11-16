# -*- coding: utf-8 -*-
"""
Unit tests for PlUtilPlugin.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import shutil
import tempfile
from unittest import TestCase, SkipTest
from unittest.mock import MagicMock

from qgis_plutil.plugin import PlUtilPlugin

logger = logging.getLogger('tests.plugin')


class TestTestee(TestCase):
    def setUp(self):
        self.testee = PlUtilPlugin()

    def tearDown(self):
        self.testee = None

    def test_init(self):
        self.testee = PlUtilPlugin()
