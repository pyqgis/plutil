# -*- coding: utf-8 -*-
"""
Contains the definition of the Side class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from PyQt5.QtCore import QObject

logger = logging.getLogger('plutil.side')


class Side(QObject):
    """
    This class .

    Attributes:

    """

    STATE_DISCONNECTED = 1
    STATE_CONNECTING = 2
    STATE_CONNECTED = 3

    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Arguments:

        """
        super().__init__(*args, **kwargs)
        self.state = self.STATE_DISCONNECTED

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'Side()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'Side()'
