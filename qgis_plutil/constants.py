# -*- coding: utf-8 -*-
"""
Constants of this project.
"""
import logging

__author__ = "Nicu Tofan"
__package_name__ = "plutil"
__copyright__ = "Copyright 2019, Nicu Tofan"
__credits__ = []
__license__ = "MIT"
__maintainer__ = "Nicu Tofan"
__email__ = "nicu.tofan@gmail.com"
__package_url__ = 'https://github.com/pyqgis/%s' % __package_name__


# Used by the http server to end its eecution
ROUTE_SHUT_DOWN = 'shut-me-down'

# ---- Constants for the logging system ----
TRACE = 1
UINFO = logging.INFO+1 # Information that also shows up in the bar
UCAKE = logging.INFO+2 # Information that also shows up in the bar
UWARN = logging.WARNING+1 # Warning that also shows up in the bar
UERROR = logging.ERROR+1 # Error that also shows up in the bar
