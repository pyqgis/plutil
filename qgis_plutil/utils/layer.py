# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from qgis.core import (
    QgsWkbTypes, QgsProject, QgsVectorLayer, QgsGeometry, QgsMapLayer,
    QgsVectorDataProvider
)

from qgis_plutil.constants import UERROR

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

    geometry_type = QgsWkbTypes.displayString(int(
        QgsWkbTypes.flatType(int(in_layer.wkbType()))))
    crs_id = in_layer.crs().authid()
    out_layer=QgsVectorLayer(
        "%s?crs=%s" % (geometry_type, crs_id), name, provider)
    fields=in_layer.dataProvider().fields().toList()
    out_layer.dataProvider().addAttributes(fields)
    out_layer.updateFields()
    out_layer.dataProvider().addFeatures([
        f for f in in_layer.getFeatures() if condition(f)])
    return out_layer


def check_layer(plugin, layer=None,
                validity=True, vector=True,
                point=False, linestring=False, polygon=False,
                must_edit=True, add_features=True, delete_features=True,
                start_edit=True):
    """
    Performs checks and shows appropriate error messages.

    Arguments:
        plugin:
            The instance of the plugin that is requesting this.
        layer:
            Input layer. If None, current layer will be used. If
            there is no current layer an error is shown.
        validity:
            Checks the layer for validity.Shows error if not valid.
        vector:
            Checks if this is an vector layer and shows an error if not.
        point:
            Checks if this is a point layer and shows an error if not.
        linestring:
            Checks if this is a line layer and shows an error if not.
        polygon:
            Checks if this is a polygon layer and shows an error if not.
        must_edit:
            Checks if features can be added and deleted and shows an
            error if not.
        add_features:
            Checks if features can be added and shows an
            error if not.
        delete_features:
            Checks if features can be deleted and shows an
            error if not.
        start_edit:
            For layers that are not in the process of being edited this
            starts the editing process. If something goes wrong it shows
            an error.

    Returns:
        The layer if all went well, None otherwise
    """
    b_ok = False
    if layer is None:
        layer = plugin.iface.layerTreeView().currentLayer()

    while True:

        if layer is None:
            logger.log(UERROR, plugin.tr("Needs an active layer"))
            break

        if validity and not layer.isValid():
            logger.log(UERROR, plugin.tr("The layer is invalid"))
            break

        if vector and layer.LayerType() != QgsMapLayer.VectorLayer:
            logger.log(UERROR, plugin.tr("Needs a vector layer"))
            break

        if point and layer.wkbType() != QgsWkbTypes.Point:
            logger.log(UERROR, plugin.tr("Needs a point layer"))
            break

        if linestring and layer.wkbType() != QgsWkbTypes.LineString:
            logger.log(UERROR, plugin.tr("Needs a line-string layer"))
            break

        if polygon and layer.wkbType() != QgsWkbTypes.Polygon:
            logger.log(UERROR, plugin.tr("Needs a polygon layer"))
            break

        if must_edit:
            caps = layer.dataProvider().capabilities()
            if add_features:
                if caps & QgsVectorDataProvider.AddFeatures == 0:
                    logger.log(UERROR, plugin.tr(
                        "Adding features to this layer "
                        "is prohibited"))
                    break
            if delete_features:
                if caps & QgsVectorDataProvider.DeleteFeatures == 0:
                    logger.log(UERROR, plugin.tr(
                        "Removing features from this layer "
                        "is prohibited"))
                    break

            if not layer.isEditable():
                if start_edit and not layer.startEditing():
                    logger.log(UERROR, plugin.tr(
                            "The layer is not editable"))
                    break

        b_ok = True
        break

    return layer if b_ok else None
