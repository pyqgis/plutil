# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from qgis.core import QgsWKBTypes, QgsVectorLayer
logger = logging.getLogger('plutil.layer')


def clone_layer(in_layer, condition=None, provider="memory", name=None):
    """
    Creates a deep copy of a layer.

    https://stackoverflow.com/a/45818097/1742064

    Arguments:
        in_layer (QgsVectorLayer):
            The layer to copy.
        condition (function):
            Filter function for features.
        provider (str):
            Data provider for the new layer.
        name (str):
            The name of the new layer.

    Returns:
        Newly created layer.
    """

    if condition is None:
        condition = lambda x: True
    if name is None:
        name = in_layer.name() + "_copy"

    geometry_type = QgsWKBTypes.displayString(int(
        QgsWKBTypes.flatType(int(in_layer.wkbType()))))
    crs_id = in_layer.crs().authid()
    out_layer=QgsVectorLayer(
        "%s?crs=%s" % (geometry_type, crs_id), name, provider)
    fields=in_layer.dataProvider().fields().toList()
    out_layer.dataProvider().addAttributes(fields)
    out_layer.updateFields()
    out_layer.dataProvider().addFeatures([
        f for f in in_layer.getFeatures() if condition(f)])
    return out_layer
