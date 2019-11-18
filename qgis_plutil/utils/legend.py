# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from qgis.core import (
    QgsProject, QgsLayerTreeGroup, QgsLayerTreeLayer, QgsVectorLayer,
    QgsVectorLayerJoinInfo
)

from qgis_plutil.utils.geometry import geometry_flat_name

logger = logging.getLogger('plutil.legend')


def get_path(path, parent=None, prj=None):
    """
    Finds or creates a group at a certain path.

    Arguments:
        path:
            The name of the object.
        parent:
            The top level group to search.
        prj:
            The project to add if parent is None.
    """
    if prj is None:
        prj = QgsProject.instance()

    if parent is None:
        parent = prj.layerTreeRoot()

    if path is None:
        return parent
    if not isinstance(path, (list, tuple)):
        path = path.split("/")

    for part in path:
        if len(path) > 0:
            parent = get_group(part, parent)

    return parent


def get_group(name, parent):
    """
    Finds or creates a group.

    Arguments:
        name:
            The name of the object.
        parent:
            The object to add the group to if not found.
    """
    result = parent.findGroup(name)
    if result is None:
        result = parent.addGroup(name)
    return result


def all_groups(parent=None):
    """
    Iterator that yields each group in provided parent and all its kids.

    Arguments:
        parent:
            The object to iterate. If None will iterate the whole legend.
    """
    if parent is None:
        parent = QgsProject.instance().layerTreeRoot()

    def do_a_group(grp, level=0):
        for child in grp.children():
            if isinstance(child, QgsLayerTreeGroup):
                yield child
                do_a_group(child, level=level + 1)

    do_a_group(parent)


def all_layers(parent=None):
    """
    Iterator that yields each layer in provided parent and all its kids.

    Arguments:
        parent:
            The object to iterate. If None will iterate the whole legend.
    """
    if parent is None:
        parent = QgsProject.instance().layerTreeRoot()
    result = []
    def do_a_group(grp, level=0):
        for child in grp.children():
            if isinstance(child, QgsLayerTreeGroup):
                do_a_group(child, level=level + 1)
            elif isinstance(child, QgsLayerTreeLayer):
                result.append(child)

    do_a_group(parent)
    return result

def all_layers_with_name(name, parent=None):
    """
    Iterator that yields each layer in provided parent and all its kids.

    Arguments:
        parent:
            The object to iterate. If None will iterate the whole legend.
    """
    if parent is None:
        parent = QgsProject.instance().layerTreeRoot()
    result = []
    def do_a_group(grp, level=0):
        for child in grp.children():
            if isinstance(child, QgsLayerTreeGroup):
                do_a_group(child, level=level + 1)
            elif isinstance(child, QgsLayerTreeLayer):
                if child.name() == name:
                    result.append(child)

    do_a_group(parent)
    return result

def locate_own_layer(name, group):
    """ Attempts to locate a layer only as a direct child of the group."""
    for child in group.children():
        if isinstance(child, QgsLayerTreeLayer):
            if child.name() == name:
                return child
    return None


def all_tree_items(parent=None):
    """
    Iterator that yields each layer and group in provided parent
    and all its kids.

    Arguments:
        parent:
            The object to iterate. If None will iterate the whole legend.
    """
    if parent is None:
        parent = QgsProject.instance().layerTreeRoot()

    def do_a_group(grp, level=0):
        for child in grp.children():
            if isinstance(child, QgsLayerTreeGroup):
                yield child
                do_a_group(child, level=level + 1)
            elif isinstance(child, QgsLayerTreeLayer):
                yield child

    do_a_group(parent)


def add_layer_to_legend(layer, group=None, prj=None):
    """ Adds a layer to a project in specified group. """
    if prj is None:
        prj = QgsProject.instance()
    if isinstance(group, str):
        group = get_path(path=group, prj=prj)
    QgsProject.instance().addMapLayer(layer, addToLegend=False)
    result = group.addLayer(layer)
    layer.setCrs(prj.crs())
    # QgsCoordinateReferenceSystem
    logger.debug("layer crs: %r", prj.crs().description())
    layer.updateExtents()
    return result


def get_layer(legend_name, iface, geom_type, default_group=None):
    """
    Finds or creates a layer.

    If the name is empty it will attempt to locate the current layer in
    the legend. If there is none it will error out with ValueError.

    If the name is provided:
    - and contains path separators (/) the specific location is searched
    - and no separators are present it is searched in the entire legend.

    If the layer is nowhere to be found a new layer is created.

    Arguments:
        legend_name (str):
            The name of the layer to get or create.
        iface (QgsInterface):
            QGis interface.
        geom_type (QgsWkbTypes, str):
            The type of geometry for a new layer. If it is a name it
            will be convened to a string.
        default_group(str, None):
            Where to place a new layer. By default it is placed at the
            top level.

    Returns:
        QgsLayerTreeLayer, QgsVectorLayer
    """
    is_new = False
    assert legend_name is not None
    if len(legend_name) == 0:
        logger.debug("No layer name provided; locating current layer...")
        map_layer = iface.layerTreeView().currentLayer()
        if map_layer is None:
            raise ValueError("No layer was provided and there "
                             "is no current layer")
        layer = map_layer.layer()
        logger.debug("current layer is %s", layer.name())
    else:
        logger.debug("Requesting to locate layer %s", legend_name)
        path = list(part for part in legend_name.split('/') if len(part) > 0)

        if len(path) > 1:
            logger.debug("The path has %d components", len(path))
            legend_name = path[-1]
            group = get_path(path[:-1])
            map_layer = locate_own_layer(name=legend_name, group=group)
            if map_layer:
                layers = [map_layer]
            else:
                layers = []
        else:
            logger.debug("The path has a single name; searching entire tree")
            layers = all_layers_with_name(legend_name)
            if len(layers) == 0:
                map_layers = QgsProject.instance().mapLayersByName(legend_name)
                layers = [QgsProject.instance().layerTreeRoot().findLayer(ly)
                          for ly in map_layers]
            group = None
            logger.debug("found %d layers", len(layers))

        if len(layers) == 0:
            logger.debug("no layer has been located and default group is %r",
                         default_group)
            if group is None and default_group:
                logger.debug("locating default group")
                group = get_path(default_group)

            if isinstance(geom_type, int):
                geom_type = geometry_flat_name(geom_type)
                logger.debug("geometry type parsed to %r", geom_type)
            else:
                logger.debug("geometry type is %r", geom_type)

            layer = QgsVectorLayer(geom_type, legend_name, "memory")
            map_layer = add_layer_to_legend(layer, group=group)
            is_new = True
            logger.debug("layer was created and added to legend")
        else:
            logger.debug("selecting first layer among %d", len(layers))
            map_layer = layers[0]
            layer = map_layer.layer()

    return map_layer, layer, is_new


def current_layer(iface):
    """ This here is just a remainder. """
    return iface.layerTreeView().currentLayer()
