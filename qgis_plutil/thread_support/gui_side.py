# -*- coding: utf-8 -*-
"""
Contains the definition of the GuiSide class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from qgis_plutil.thread_support.messages.hello import HelloMessage
from .side import Side

logger = logging.getLogger('plutil.gui-side')


class GuiSide(Side):
    """
    This class .

    Attributes:

    """

    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Arguments:

        """
        super().__init__(*args, **kwargs)
        self.thread_side = None

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'GuiSide()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'GuiSide()'

    def message_accepted(self, message):
        """ Reimplement this to handle the message. """
        message.on_gui_side()

    def receiver(self, message):
        """ The slot where we receive messages emitted by the other side. """
        if self.state == self.STATE_DISCONNECTED:
            assert False, "Should not receive a message in disconnected state"
        elif self.state == self.STATE_CONNECTING:
            assert isinstance(message, HelloMessage)
            assert self.thread_side is not None
            self.state = self.STATE_CONNECTED
            self.thread_side.state = self.STATE_CONNECTED
            self.message_accepted(message)
        elif self.state == self.STATE_CONNECTED:
            assert self.thread_side is not None
            self.message_accepted(message)
        else:
            raise ValueError

    def tie(self, thread_side):
        """
        Connects to our peer.

        After this method is executed the peer should send a first message
        to check the link.
        """
        thread_side.gui_side = self
        self.thread_side = thread_side
        self.state = self.STATE_CONNECTING
        thread_side.sig.connect(self.receiver)
