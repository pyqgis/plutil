# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from qgis.core import QgsWKBTypes

logger = logging.getLogger('plutil.geom')


def geometry_flat_name(wkb_type):
    """
    Return the "flat" name of a geometry type.

    https://stackoverflow.com/a/45818097/1742064
    """
    return QgsWKBTypes.displayString(
        int(
            QgsWKBTypes.flatType(
                int(wkb_type)
            )
        )
    )


def geometry_name(wkb_type):
    """
    Return the name of a geometry type.

    https://stackoverflow.com/a/45818097/1742064
    """
    return QgsWKBTypes.displayString(
        int(wkb_type)
    )
