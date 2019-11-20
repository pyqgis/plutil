# -*- coding: utf-8 -*-
"""
Contains the definition of the GuiSide class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from queue import Empty

from PyQt5.QtCore import QObject, QBasicTimer

from qgis_plutil.thread_support.messages.hello import HelloMessage
from .side import Side

logger = logging.getLogger('plutil.gui-side')


class GuiSide(Side, QObject):
    """
    The part of the system living in the gui (main) thread.

    At this point the implementation requires that an event loop is present
    in the thread hosting this instance. This can be used directly
    with the plugin class as a mixin.

    Attributes:
        side_workers (list):
            The list of associated thread instances.
        timer (QBasicTimer):
            The timer that we use to regularly check for messages.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        super(GuiSide, self).__init__(*args, **kwargs)
        self.side_workers = []
        self.timer = QBasicTimer()

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'GuiSide()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'GuiSide()'

    def message_accepted(self, message):
        """ Re-implement this to handle the message. """
        message.on_gui_side()

    def receiver(self):
        """ The slot where we receive messages emitted by the other side. """
        for thread_side in self.side_workers:
            if not thread_side.sig.is_set():
                continue
            thread_side.sig.clear()

            for i in range(10):
                try:
                    message = thread_side.queue.get(block=False)
                except Empty:
                    break
                logger.debug("Received message %r in state %r",
                             message, self.state)
                if self.state == self.STATE_DISCONNECTED:
                    assert False, "Should not receive a message in " \
                                  "disconnected state"
                elif self.state == self.STATE_CONNECTING:
                    assert isinstance(message, HelloMessage)
                    self.state = self.STATE_CONNECTED
                    thread_side.state = self.STATE_CONNECTED
                    self.message_accepted(message)
                elif self.state == self.STATE_CONNECTED:
                    self.message_accepted(message)
                else:
                    raise ValueError("Unknown state: %r", self.state)

    def tie(self, thread_side):
        """
        Connects to our peer.

        After this method is executed the peer should send a first message
        to check the link.
        """
        thread_side.gui_side = self
        self.side_workers.append(thread_side)
        self.state = self.STATE_CONNECTING
        if not self.timer.isActive():
            milliseconds = thread_side.plugin.get('thread/gui-pool-interval',
                                                  1000)
            self.timer.start(milliseconds, self)
            logger.debug("Gui timer started at %d milliseconds", milliseconds)

    def timerEvent(self, event):
        self.receiver()
