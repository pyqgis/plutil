
# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from qgis.core import QgsWkbTypes, QgsProject, QgsVectorLayer, QgsGeometry

logger = logging.getLogger('plutil.feat')


def constructor_by_type(geometry_type):
    """
    Locates the constructor based on provided geometry type.

    The format of the data depends on the geometry being build.

    Arguments:
        geometry_type (str, int):
            The kind of geometry to create.
            - If it is a string, it should
            be one that QgsWkbTypes.parseType() can parse.
            - If it is an integer, it should be one of those defined by
            QgsWkbTypes.

    Raises:
        ValueError:
            if the string could not be parsed
        NotImplementedError:
            if the type is unknown
    """
    if isinstance(geometry_type, str):
        geometry_type = QgsWkbTypes.parseType(geometry_type)
        if geometry_type == QgsWkbTypes.Unknown:
            raise ValueError("Not a valid geometry type")

    if geometry_type == QgsWkbTypes.Point:
        return QgsGeometry.fromPointXY
    if geometry_type == QgsWkbTypes.MultiPoint:
        return QgsGeometry.fromMultiPointXY
    elif geometry_type == QgsWkbTypes.LineString:
        return QgsGeometry.fromMultiPolylineXY
    elif geometry_type == QgsWkbTypes.Polygon:
        return QgsGeometry.fromPolygonXY
    elif geometry_type == QgsWkbTypes.MultiPolygon:
        return QgsGeometry.fromMultiPolygonXY
    else:
        raise NotImplementedError


def feature_from_data(geometry_type, data):
    """
    Creates a geometry from raw data.

    The format of the data depends on the geometry being build.

    Arguments:
        geometry_type (str, int):
            The kind of geometry to create.
            - If it is a string, it should
            be one that QgsWkbTypes.parseType() can parse.
            - If it is an integer, it should be one of those defined by
            QgsWkbTypes.
        data (list, set, tuple):
            The data as simple structures.
    """
    constructor = constructor_by_type(geometry_type)
    return constructor(data)
