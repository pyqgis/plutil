# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from qgis.core import (
    QgsWkbTypes, QgsProject, QgsVectorLayer, QgsGeometry, QgsPointXY
)

logger = logging.getLogger('plutil.geom')


def geometry_flat_name(wkb_type):
    """
    Return the "flat" name of a geometry type.

    https://stackoverflow.com/a/45818097/1742064
    """
    return QgsWkbTypes.displayString(
        int(
            QgsWkbTypes.flatType(
                int(wkb_type)
            )
        )
    )


def geometry_name(wkb_type):
    """
    Return the name of a geometry type.

    https://stackoverflow.com/a/45818097/1742064
    """
    return QgsWkbTypes.displayString(
        int(wkb_type)
    )


def geometry_constructor_by_type(geometry_type):
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
        def fromPointXY(value):
            return QgsGeometry.fromPointXY(QgsPointXY(*value))
        return fromPointXY
    if geometry_type == QgsWkbTypes.MultiPoint:
        def fromMultiPointXY(value):
            return QgsGeometry.fromMultiPointXY(
                [QgsPointXY(*point) for point in value])
        return fromMultiPointXY
    elif geometry_type == QgsWkbTypes.LineString:
        def fromPolylineXY(value):
            return QgsGeometry.fromPolylineXY(
                [QgsPointXY(*point) for point in value])
        return fromPolylineXY
    elif geometry_type == QgsWkbTypes.Polygon:
        def fromPolygonXY(value):
            return QgsGeometry.fromPolygonXY(
                [[QgsPointXY(*point) for point in ring] for ring in value])
        return fromPolygonXY
    elif geometry_type == QgsWkbTypes.MultiPolygon:
        def fromMultiPolygonXY(value):
            return QgsGeometry.fromMultiPolygonXY(
                [[[QgsPointXY(*point) for point in ring] for ring in polyg] for polyg in value])
        return fromMultiPolygonXY
    else:
        raise NotImplementedError


def geometry_from_data(geometry_type, data):
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
    constructor = geometry_constructor_by_type(geometry_type)
    return constructor(data)
