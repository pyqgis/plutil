# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from collections import OrderedDict
from qgis.core import QgsWkbTypes, QgsProject, QgsVectorLayer, QgsField

from qgis.PyQt.QtCore import QVariant

logger = logging.getLogger('plutil.attribs')

class_to_type = {
    "float": QVariant.Double,
    "int": QVariant.Int,
    "str": QVariant.String,
}


def variant_ctor_for_object(instance):
    """
    Gets the constructor of an object based on its class.
    """
    try:
        return class_to_type[instance.__class__.__name__]
    except KeyError:
        raise NotImplementedError


def fields_from_data(data):
    """
    Generates a set of fields based on the data provided.

    The data is expected to be a list of items. If your data
    consists of a list of items and each has it's attribute stored in a distinct
    member you can use a generator:
    >>> item[0] for item in items
    """

    fields = OrderedDict()
    are_dicts = None
    for attributes in data:
        if isinstance(attributes, dict):
            if are_dicts is None:
                are_dicts = True
            elif are_dicts == False:
                raise ValueError(
                    "Data should all be dictionaries "
                    "or all lists")
            for attrib_name in attributes:
                attrib_name_str = str(attrib_name)
                if attrib_name_str not in fields:
                    fields[attrib_name_str] = QgsField(
                        attrib_name_str,
                        variant_ctor_for_object(
                            attributes[attrib_name]))
        elif not isinstance(attributes, (list, set, tuple)):
            raise ValueError("Attributes should be lists or dictionaries")
        else:
            if are_dicts is None:
                are_dicts = False
            elif are_dicts == True:
                raise ValueError(
                    "Data should all be dictionaries "
                    "or all lists")
            for i, attrib in enumerate(attributes):
                attrib_name = "Field %d" % (i + 1)
                if attrib_name not in fields:
                    fields[attrib_name] = \
                        QgsField(
                            attrib_name,
                            variant_ctor_for_object(
                                attrib))
    return fields, are_dicts


def merge_fields_in_provider(provider, fields, layer=None):
    """
    Updates the provider to include the fields.
    """
    provider_fields = dict((field.name(), field) for field in provider.fields())
    provider.addAttributes(list(
        fields[field_name]
        for field_name in fields
        if field_name not in provider_fields))
    if layer is not None:
        layer.updateFields()
