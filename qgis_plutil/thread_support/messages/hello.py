# -*- coding: utf-8 -*-
"""
Contains the definition of the HelloMessage class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from qgis_plutil.constants import DONT_ADD_TO_QUEUE
from .base import TsMessage

logger = logging.getLogger('HelloMessage')


class HelloMessage(TsMessage):
    """
    A message send when the thread comes online.

    The gui side will create the thread then call GuiSide.tie()
    where the state of the thread is set to connecting. The thread is then
    started by the caller, enters run function which calls
    ThreadSide.thread_side_started(). The default implementation
    creates a HelloMessage which is posted to the gui thread.
    At some later time the gui side picks the message in
    GuiSide.receiver() and calls on_gui_side() on it. The state of the thread
    is then changed from  connecting to connected.
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
        logger.debug("Hello %r has been send to GUI", self.message_id)
        return DONT_ADD_TO_QUEUE
