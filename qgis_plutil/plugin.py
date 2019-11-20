# -*- coding: utf-8 -*-
"""
Contains the definition of the PlUtilPlugin class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import os

from PyQt5.QtCore import QObject, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu
from qgis.core import (
    QgsSettings, Qgis, QgsMessageLog
)
import logging

from .qlog import PlUtilHandler, install_file_logger
from .constants import TRACE, UCAKE, __package_name__


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
        menus (list):
            The list of menus created by this plugin.
        toolbars (list):
            The list of toolbars created by this plugin.
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
        super(PlUtilPlugin, self).__init__()

        # Save reference to the QGIS interface
        self.iface = iface
        self.plugin_name = plugin_name
        self.plugin_dir = plugin_dir

        self.translator = None
        self.menus = []
        self.toolbars = []
        self.actions = []

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'PlUtilPlugin()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'PlUtilPlugin()'

    def locale_path(self):
        """ Returns the path of the file. """
        locale = QgsSettings().value('locale/userLocale')[0:2]

        path = self.get(
            'locale/%s/file' % locale,
            os.path.join(
                self.plugin_dir,
                'i18n',
                '%s_%s.qm' % (self.plugin_name, locale))
        )

        return path

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
        locale_path = self.locale_path()

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def unload(self):
        """ Removes the menus and toolbars and stop everything else. """
        self.logger.debug("Plugin %s is being unloaded", self.plugin_name)
        self.translator = None
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers =[]
        logging.getLogger(__package_name__).handlers =[]
        for menu in self.menus:
            menu.clear()
            menu.deleteLater()
        for toolbar in self.toolbars:
            toolbar.clear()
            toolbar.deleteLater()
        for action in self.actions:
            action.deleteLater()

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

    def create_action(
            self,
            text,
            callback,
            icon_path=None,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """
        Create an action and insert it in appropriate container.

        Arguments:
            text (str):
                Text that should be shown in menu items for this action.
            callback (function):
                Function to be called when the action is triggered.
            icon_path (str, None):
                Path to the icon for this action. Can be a resource
                path (e.g. ':/plugins/foo/bar.png') or a normal file
                system path.
            enabled_flag (bool):
                A flag indicating if the action should be enabled
                by default. Defaults to True.
            add_to_menu (bool, int, QMenu, list):
                Indicate if this action should be added to a menu.
                - can be a bool, and, if True, is added to the first menu:
                - an int, in which case it indicates the index of the
                menu to add it to:
                - or an actual QMenu instance;
                - a list of any of the above, mixed at will, can also be used.
                Defaults to True, so add it to first menu.
            add_to_toolbar (bool, int, QToolbar, list):
                Indicate if this action should be added to a toolbar.
                - can be a bool, and, if True, is added to the first toolbar:
                - an int, in which case it indicates the index of the
                toolbar to add it to:
                - or an actual QToolbar instance;
                - a list of any of the above, mixed at will, can also be used.
                Defaults to False, so don't ad it anywhere.
            status_tip (str):
                Optional text to show in a popup when mouse pointer
                hovers over the action.
            whats_this (str):
                Optional text to show in the status bar when the
                mouse pointer hovers over the action.
            parent (QWidget):
                Parent widget for the new action. If None (default)
                the action is added to the main window of the QGis application.

        Returns:
            The action that was created. Note that the action is also
            added to self.actions list.

        """

        icon = QIcon(icon_path) if icon_path else QIcon()
        action = QAction(icon, text,
                         parent if parent else self.iface.mainWindow())
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        self.add_action_to_toolbar(action, add_to_toolbar)
        self.add_action_to_menu(action, add_to_menu)
        self.actions.append(action)
        self.logger.debug("Action %s has been created and inserted", text)
        return action

    def create_toolbar(self, name=None):
        """
        Creates a toolbar.

        Arguments:
            name (str):
                The text to display to the user. Defaults to plugin name.

        """
        name = name if name else self.plugin_name
        result = self.iface.addToolBar(name)
        self.logger.debug("Toolbar %s has been created and inserted", name)
        self.toolbars.append(result)
        return result

    def add_action_to_toolbar(self, action, destination):
        # Add it to one or more toolbars.
        if not isinstance(destination, (list, set, tuple)):
            destination = (destination, )

        for toolbar in destination:
            if not toolbar:
                continue
            elif toolbar == True:
                toolbar = self.toolbars[0]
            elif isinstance(toolbar,int):
                toolbar = self.toolbars[toolbar]
            elif isinstance(toolbar, str):
                if toolbar=='mapNavTool':
                    toolbar = self.iface.mapNavToolToolBar()
                elif toolbar=='plugin':
                    toolbar = self.iface.pluginToolBar()
                elif toolbar=='raster':
                    toolbar = self.iface.rasterToolBar()
                elif toolbar=='shapeDigitize':
                    toolbar = self.iface.shapeDigitizeToolBar()
                elif toolbar=='vector':
                    toolbar = self.iface.vectorToolBar()
                elif toolbar=='web':
                    toolbar = self.iface.webToolBar()
                elif toolbar=='advancedDigitize':
                    toolbar = self.iface.advancedDigitizeToolBar()
                elif toolbar=='attributes':
                    toolbar = self.iface.attributesToolBar()
                elif toolbar=='dataSourceManager':
                    toolbar = self.iface.dataSourceManagerToolBar()
                elif toolbar=='database':
                    toolbar = self.iface.databaseToolBar()
                elif toolbar=='digitize':
                    toolbar = self.iface.digitizeToolBar()
                elif toolbar=='file':
                    toolbar = self.iface.fileToolBar()
                elif toolbar=='help':
                    toolbar = self.iface.helpToolBar()
                else:
                    raise ValueError
            else:
                # assert isinstance(toolbar, QToolbar)
                pass
            toolbar.addAction(action)

    def create_menu(self, name=None, parent=None, icon=None):
        """
        Creates a menu.

        Examples:
            If you have a simple plugin just:
            >>> self.create_menu()
            No need to store the value, as it gets deposited in self.menus
            It will create a new menu insde Plugins menu.

        Arguments:
            name (str):
                The text to display to the user. Defaults to plugin name.
            parent (None, QMenu, str):
                Where to place this menu. Can be:
                - None, in which case it will be inserted in Plugins menu.
                - QMenu, in which case a submenu will be added
                - str: can be one of:
                    - database
                    - edit
                    - help
                    - layer
                    - pluginHelp
                    - plugin
                    - project
                    - raster
                    - settings
                    - top - will be inserted at the top level,
                    before the Help menu; please consider adding it under
                    Plugins menu.
            icon (str):
                The path for menu's icon when added as submenu.

        """
        name = name if name else self.plugin_name

        while True:
            if parent is None:
                parent = self.iface.pluginMenu()
            elif isinstance(parent, QMenu):
                pass
            else:
                assert isinstance(parent, str)
                if parent == "database":
                    parent = self.iface.databaseMenu()
                elif parent == "edit":
                    parent = self.iface.editMenu()
                elif parent == "help":
                    parent = self.iface.helpMenu()
                elif parent == "layer":
                    parent = self.iface.layerMenu()
                elif parent == "plugin":
                    parent = self.iface.pluginMenu()
                elif parent == "project":
                    parent = self.iface.projectMenu()
                elif parent == "raster":
                    parent = self.iface.rasterMenu()
                elif parent == "settings":
                    parent = self.iface.settingsMenu()
                elif parent == "top":
                    result = QMenu(name)
                    self.iface.mainWindow().menuBar().insertMenu(
                        self.iface.firstRightStandardMenu().menuAction(), result)
                    break
                else:
                    raise ValueError

            result = parent.addMenu(name) if icon is None \
                else parent.addMenu(QIcon(icon), name)
            break

        self.logger.debug("Menu %s has been created and inserted", name)
        self.menus.append(result)
        return result

    def add_action_to_menu(self, action, destination):
        # Add it to one or more menus.
        if not isinstance(destination, (list, set, tuple)):
            destination = (destination, )
        for menu in destination:
            if not menu:
                continue
            elif menu == True:
                menu = self.menus[0]
            elif isinstance(menu,int):
                menu = self.menus[menu]
            else:
                assert isinstance(menu, QMenu)
            menu.addAction(action)
