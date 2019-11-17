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
from qgis.gui import QgisInterface

logger = logging.getLogger('tests.plugin')


class TestTestee(TestCase):
    def setUp(self):
        self.iface = MagicMock(spec=QgisInterface)
        self.plugin_dir = tempfile.mkdtemp(suffix=None, prefix=None)
        self.testee = PlUtilPlugin(
            iface=self.iface, plugin_name="test_plugin",
            plugin_dir=self.plugin_dir)

    def tearDown(self):
        if os.path.isdir(self.plugin_dir):
            shutil.rmtree(self.plugin_dir)
        self.testee = None

    def test_init(self):
        self.testee = PlUtilPlugin(
            iface=None, plugin_name=None,
            plugin_dir=None)
