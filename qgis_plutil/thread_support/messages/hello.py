# -*- coding: utf-8 -*-
"""
Contains the definition of the HelloMessage class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from .base import TsMessage

logger = logging.getLogger('HelloMessage')


class HelloMessage(TsMessage):
    """
    This class .

    Attributes:

    """

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        super(HelloMessage, self).__init__(*args, **kwargs)

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'HelloMessage()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'HelloMessage()'

    def on_gui_side(self):
        self.thread_side.state = self.thread_side.STATE_CONNECTED
        logger.debug("Hello %r hass been send to GUI", self.message_id)
