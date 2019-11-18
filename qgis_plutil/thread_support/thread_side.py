# -*- coding: utf-8 -*-
"""
Contains the definition of the ThreadSide class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from PyQt5.QtCore import QObject, pyqtSignal

from qgis_plutil.thread_support.messages.hello import HelloMessage
from .side import Side

logger = logging.getLogger('plutil.th-side')


class ThreadSide(Side):
    """
    This class .

    Attributes:

    """

    # We use this to tell something to the other side.
    sig = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Arguments:

        """
        super().__init__(*args, **kwargs)
        self.gui_side = None

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'ThreadSide()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'ThreadSide()'

    def thread_side_started(self):
        """
        One time started event.

        This should be called only once from thread after it hs been tied with
        the gui side so that the connection is finalized.
        """
        self.state = self.STATE_CONNECTING
        self.send_to_gui(HelloMessage())

    def send_to_gui(self, message):
        """
        Will send a message to the other side.
        """
        message.on_thread_side()
        self.sig.emit(message)
