# -*- coding: utf-8 -*-
"""
Contains the definition of the HttpMessage class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from ..thread_support.messages.base import TsMessage

logger = logging.getLogger('plutil.http')


class HttpMessage(TsMessage):
    """
    A base class for messages used with html server.

    Attributes:
        result_type (str):
            Either Error or OK.
        result_data (str, object):
            For errors this is the message to send to caller.
            For success the type of object depends on the message.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        super().__init__(*args, **kwargs)
        self.result_type = 'Error'
        self.result_data = None

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'HttpMessage()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'HttpMessage()'
