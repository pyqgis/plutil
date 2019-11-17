# -*- coding: utf-8 -*-
"""
Contains the definition of the PlUtilPlugin class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import os

from PyQt5.QtCore import QObject, QTranslator, qVersion, QCoreApplication
from qgis.core import QgsSettings, Qgis, QgsMessageLog
import logging

from .qlog import PlUtilHandler, install_file_logger
from .constants import TRACE, UCAKE


class PlUtilPlugin(QObject):
    """
    This class can be used as a base class for your plugin.

    Attributes:
        iface (QgsInterface):
            An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        plugin_name (str):
            The name of this plugin.
        plugin_dir (str):
            The directory where this plugin is stored.
        translator (QTranslator):
            The translator in use or None.
    """

    def __init__(self, iface, plugin_name, plugin_dir):
        """
        Constructor.

        Arguments:
            iface (QgsInterface):
                An interface instance that will be passed to this class
                which provides the hook by which you can manipulate the QGIS
                application at run time.
            plugin_name (str):
                The name of this plugin.
            plugin_dir (str):
                The directory where this plugin is stored.
        """
        super().__init__()

        # Save reference to the QGIS interface
        self.iface = iface
        self.plugin_name = plugin_name
        self.plugin_dir = plugin_dir

        self.translator = None

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'PlUtilPlugin()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'PlUtilPlugin()'

    @property
    def locale_path(self):
        """ Returns the path of the file. """
        locale = QgsSettings().value('locale/userLocale')[0:2]

        locale_path = self.plugin.get(
            'locale/%s/file' % locale,
            os.path.join(
                self.plugin_dir,
                'i18n',
                '%s_%s.qm' % (self.plugin_name, locale))
        )

        return locale_path

    @property
    def logger(self):
        return logging.getLogger(self.plugin_name)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.setup_logging()
        self.setup_translation()
        self.logger.debug("Plugin %s is being initialized", self.plugin_name)

    def setup_logging(self):
        """ Prepare the logging system. """
        install_file_logger(self)
        PlUtilHandler.install(
            self, int(self.get(['qgis/logging/level'], logging.INFO)))

        self.logger.setLevel(
            min(
                TRACE,
                int(self.get('logging/level', logging.INFO))
            )
        )

    def setup_translation(self):
        """ Prepare the translation system. """
        locale_path = self.locale_path

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def unload(self):
        """ Removes the menus and toolbars. """
        self.logger.debug("Plugin %s is being unloaded", self.plugin_name)
        self.translator = None
        self.logger.handlers =[]

    def get(self, key, default=None):
        """ Retrieves a setting. Never throws. """
        return QgsSettings().value('%s/%s' % (self.plugin_name, key), default)

    def set(self, key, value):
        """ Retrieves a setting. Never throws. """
        return QgsSettings().setValue('%s/%s' % (self.plugin_name, key), value)

    def show_error(self, message):
        """
        Presents an error message.

        Logging using the UERROR level will implicitly call this function.
        """
        self.iface.messageBar().pushMessage(
            self.tr("ERROR"), message,
            level=Qgis.Critical)

    def show_warn(self, message):
        """
        Presents a warning.

        Logging using the UWARN level will implicitly call this function.
        """
        self.iface.messageBar().pushMessage(
            self.tr("Warning"), message,
            level=Qgis.Warning)

    def show_info(self, message):
        """
        Presents an informative message.

        Logging using the UINFO level will implicitly call this function.
        """
        self.iface.messageBar().pushMessage(
            self.tr("Info"), message,
            level=Qgis.Info)

    def show_success(self, message):
        """
        Presents a success message.

        Logging using the UCAKE level will implicitly call this function.
        """
        self.iface.messageBar().pushMessage(
            self.tr("Success"), message,
            level=Qgis.Success)

    def log_message(self, message, log_level):
        """
        Adds a message to the log window of this plugin.

        Note the `<plugin-name>/qgis/logging/level` setting that decides
        which messages from the trigger this function.
        """
        QgsMessageLog.logMessage(
            message, self.plugin_name,
            level=Qgis.Critical if log_level >= logging.ERROR
            else Qgis.Success if log_level == UCAKE
            else Qgis.Warning if log_level >= logging.WARNING
            else Qgis.Info
        )
