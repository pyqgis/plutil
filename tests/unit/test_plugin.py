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
from unittest.mock import MagicMock, patch

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

    def test_locale_path(self):
        with patch('qgis_plutil.plugin.QgsSettings') as QgsSettings:
            self.testee.plugin_dir = 'XXX'
            self.testee.get = MagicMock()

            QgsSettings.return_value.value.return_value = None
            self.testee.locale_path()
            self.testee.get.assert_called_with(
                'locale/en/file', 'XXX\\i18n\\test_plugin_en.qm')

            QgsSettings.return_value.value.return_value = ''
            self.testee.locale_path()
            self.testee.get.assert_called_with(
                'locale/en/file', 'XXX\\i18n\\test_plugin_en.qm')

            QgsSettings.return_value.value.return_value = 'l'
            self.testee.locale_path()
            self.testee.get.assert_called_with(
                'locale/l/file', 'XXX\\i18n\\test_plugin_l.qm')

            QgsSettings.return_value.value.return_value = 'lx'
            self.testee.locale_path()
            self.testee.get.assert_called_with(
                'locale/lx/file', 'XXX\\i18n\\test_plugin_lx.qm')

            QgsSettings.return_value.value.return_value = 'lxy'
            self.testee.locale_path()
            self.testee.get.assert_called_with(
                'locale/lx/file', 'XXX\\i18n\\test_plugin_lx.qm')

    def test_init_gui(self):
        self.testee.setup_logging = MagicMock()
        self.testee.setup_translation = MagicMock()
        self.testee.initGui()
        self.testee.setup_logging.assert_called_once()
        self.testee.setup_translation.assert_called_once()

    def test_setup_translation(self):
        self.testee.locale_path = MagicMock()
        self.testee.locale_path.return_value = 'XXX'
        self.testee.setup_translation()
        with patch('qgis_plutil.plugin.os') as os_:
            with patch('qgis_plutil.plugin.QTranslator') as QTranslator:
                with patch('qgis_plutil.plugin.QCoreApplication') as QCoreApplication:
                    os_.path.exists.return_value = False
                    self.testee.setup_translation()
                    QTranslator.assert_not_called()

                    os_.path.exists.return_value = True
                    self.testee.setup_translation()
                    QTranslator.assert_called_once()
                    QTranslator.return_value.load.assert_called_once_with('XXX')
                    QCoreApplication.installTranslator.assert_called_once()

    def test_unload(self):
        with patch('qgis_plutil.plugin.logging.getLogger') as getLogger:
            logger_ = MagicMock()
            logger_.handlers = [MagicMock()]
            getLogger.return_value = logger_

            self.testee.translator = 'sss'
            menu = MagicMock()
            self.testee.menus = [menu]
            toolbar = MagicMock()
            self.testee.toolbars = [toolbar]
            action = MagicMock()
            self.testee.actions = [action]

            self.testee.unload()

            self.assertIsNone(self.testee.translator)
            self.assertEqual(len(self.testee.logger.handlers), 0)
            menu.clear.assert_called_once()
            toolbar.clear.assert_called_once()
            action.deleteLater.assert_called_once()
