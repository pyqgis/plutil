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

    def __init__(self):
        """
        Constructor.

        Arguments:

        """
        super().__init__()

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'HelloMessage()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'HelloMessage()'
