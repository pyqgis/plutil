# -*- coding: utf-8 -*-
"""
Contains the definition of the PlUtilPlugin class.
"""
from __future__ import unicode_literals
from __future__ import print_function

from PyQt5.QtCore import QObject
import logging

logger = logging.getLogger('PlUtilPlugin')


class PlUtilPlugin(QObject):
    """
    This class can be used as a base class for your plugin.

    Attributes:
        iface (QgsInterface):
            An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.

    """

    def __init__(self, iface):
        """
        Constructor.

        Arguments:
            iface (QgsInterface):
                An interface instance that will be passed to this class
                which provides the hook by which you can manipulate the QGIS
                application at run time.
        """
        super().__init__()

        # Save reference to the QGIS interface
        self.iface = iface

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'PlUtilPlugin()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'PlUtilPlugin()'

    def setup_logging(self):
        """ Prepare the logging system. """
        pass

    def setup_translation(self):
        """ Prepare the translation system. """
        pass
