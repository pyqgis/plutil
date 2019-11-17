# -*- coding: utf-8 -*-
"""
Contains the definition of the PluHandler class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os

from .constants import UERROR, UWARN, UINFO, TRACE, UCAKE, __package_name__


class PlUtilHandler(logging.StreamHandler):
    """
    This class .

    Attributes:
        plugin (PlUtilPlugin):
            The plugin where we belong to
        qgis_log_level (int):
            The threshold for messages to go to QGis log panel.
    """

    def __init__(self, plugin, qgis_log_level=logging.INFO, *args, **kwargs):
        """
        Constructor.

        Arguments:
            plugin (PlUtilPlugin):
                The plugin where we belong to
            qgis_log_level (int):
                The threshold for messages to go to QGis log panel.
        """
        super().__init__(*args, **kwargs)
        self.plugin = plugin
        self.qgis_log_level = qgis_log_level

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'PluHandler()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'PluHandler()'

    def emit(self, record):
        """ Reimplemented method to filter messages. """
        super().emit(record)
        if record.levelno == UERROR:
            self.plugin.show_error(record.message)
        elif record.levelno == UWARN:
            self.plugin.show_warn(record.message)
        elif record.levelno == UINFO:
            self.plugin.show_info(record.message)
        elif record.levelno == UCAKE:
            self.plugin.show_success(record.message)

        if record.levelno >= self.qgis_log_level:
            self.plugin.log_message(record.message, record.levelno)

    @staticmethod
    def install(plugin, qgis_log_level, fmt=None, include_lib_log=True,
                *args, **kwargs):
        """
        Creates the handler and installs it.

        Arguments:
            plugin (PlUtilPlugin):
                The plugin where we belong to
            qgis_log_level (int):
                The threshold for messages to go to QGis log panel.
            fmt (logging.Formatter):
                The format to be used with the logger.
            include_lib_log (bool):
                Should we install the handler for this library's own logging?.

        Return:
            Newly created handler.
        """
        if fmt is None:
            fmt = logging.Formatter(
                "[%(asctime)s.%(msecs)03d] [%(levelname)-7s] [%(name)-19s] "
                "[%(threadName)-15s] "
                "[%(funcName)-25s] %(message)s",
                datefmt='%M:%S')

        result = PlUtilHandler(plugin, qgis_log_level, *args, **kwargs)
        result.setFormatter(fmt)
        result.setLevel(
            min(
                qgis_log_level,
                int(plugin.get('logging/console/level', logging.INFO))
            )
        )

        plugin.logger.addHandler(result)
        if include_lib_log:
            logging.getLogger(__package_name__).addHandler(result)
        return result


def install_file_logger(plugin, fmt=None, force_create: bool = False,
                        log_file: str = None,
                        include_lib_log: bool = True):
    """
    Creates the handler and installs it.

    Arguments:
        plugin (PlUtilPlugin):
            The plugin where we belong to
        fmt (logging.Formatter):
            The format to be used with the logger.
        force_create (bool):
            Create even if settings say otherwise.
        log_file (str):
            The file where we log to.
        include_lib_log (bool):
            Should we install the handler for this library's own logging?.

    Return:
        Newly created handler.
    """
    settings_create = bool(plugin.get('logging/file/disabled', True))
    if (not force_create) and (not settings_create):
        return None

    if fmt is None:
        fmt = logging.Formatter(
            "[%(asctime)s.%(msecs)03d] [%(levelname)-7s] [%(name)-19s] "
            "[%(filename)15s:%(lineno)-4d] [%(threadName)-15s] "
            "[%(funcName)-25s] | %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S')

    if not log_file:
        log_file = plugin.get('logging/file/logfile',
                              os.path.join(
                                  plugin.plugin_dir,
                                  '%s.log' % plugin.plugin_name
                              ))

    file_path, file_name = os.path.split(log_file)
    if not os.path.isdir(file_path):
        os.makedirs(file_path)

    result = logging.FileHandler(log_file)
    result.setFormatter(fmt)
    result.setLevel(
        min(
            TRACE,
            int(plugin.get('logging/file/level', logging.INFO))
        )
    )

    plugin.logger.addHandler(result)
    if include_lib_log:
        logging.getLogger(__package_name__).addHandler(result)
    return result
