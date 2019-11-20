# -*- coding: utf-8 -*-
"""
Contains the definition of the TsMessage class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from uuid import uuid4
from qgis_plutil.constants import TRACE

logger = logging.getLogger('plutil.th-msg')


class TsMessage(object):
    """
    Base class for messages exchanged between a thread and GUI thread .

    Attributes:
        message_id
    """
    def __init__(self, plugin, thread_side, *args, **kwargs):
        """
        Constructor.

        Arguments:

        """
        super(TsMessage, self).__init__(*args, **kwargs)

        self.message_id = uuid4().hex
        self.plugin = plugin
        self.thread_side = thread_side

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'TsMessage()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'TsMessage()'

    def on_thread_side(self):
        """ Executed just before the messages leaves the thread side. """
        logger.log(TRACE, "Message %r is being send from thread side",
                   self.message_id)

    def on_gui_side(self):
        """ Executed when the message has reached GUI side. """
        logger.log(TRACE, "Message %r has been received on GUI side",
                   self.message_id)
