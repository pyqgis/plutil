# -*- coding: utf-8 -*-
"""
Unit tests for Attributes.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import shutil
import tempfile
from unittest import TestCase, SkipTest
from unittest.mock import MagicMock

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsWkbTypes, QgsProject, QgsVectorLayer, QgsField,
    QgsVectorDataProvider
)
from qgis_plutil.utils.attributes import (
    variant_ctor_for_object, fields_from_data,
    merge_fields_in_provider,
)

logger = logging.getLogger('tests.attributes')


class TestVariantCtorForObject(TestCase):
    def test_invalid_params(self):
        with self.assertRaises(NotImplementedError):
            variant_ctor_for_object(None)
        with self.assertRaises(NotImplementedError):
            variant_ctor_for_object({})
        with self.assertRaises(NotImplementedError):
            variant_ctor_for_object(b'dd')

    def test_valid_params(self):
        self.assertEqual(variant_ctor_for_object(0.5), QVariant.Double)
        self.assertEqual(variant_ctor_for_object(1), QVariant.Int)
        self.assertEqual(variant_ctor_for_object(""), QVariant.String)
        self.assertEqual(variant_ctor_for_object("test"), QVariant.String)


class TestFieldsFromData(TestCase):
    def test_invalid(self):
        with self.assertRaises(ValueError):
            fields_from_data("abc")
        with self.assertRaises(TypeError):
            fields_from_data(1)
        with self.assertRaises(ValueError):
            fields_from_data(["abc"])
        with self.assertRaises(ValueError):
            fields_from_data([1])

    def test_mixed_dict(self):
        with self.assertRaises(ValueError):
            fields, are_dicts = fields_from_data([{1: 1, 2: 1, 3: 1}, [1]])
        with self.assertRaises(ValueError):
            fields, are_dicts = fields_from_data([[1, 4, 6], {1: 1, 6: 9}])

    def test_valid_list_of_one(self):
        fields, are_dicts = fields_from_data([[1]])
        self.assertFalse(are_dicts)
        self.assertEqual(len(fields), 1)
        self.assertIsInstance(fields["Field 1"], QgsField)
        self.assertEqual(fields["Field 1"].type(), QVariant.Int)
        self.assertEqual(fields["Field 1"].name(), "Field 1")

    def test_valid_lists(self):
        fields, are_dicts = fields_from_data([[1, "2", 3.5]])
        self.assertFalse(are_dicts)
        self.assertEqual(len(fields), 3)
        self.assertIsInstance(fields["Field 1"], QgsField)
        self.assertIsInstance(fields["Field 2"], QgsField)
        self.assertIsInstance(fields["Field 3"], QgsField)
        self.assertEqual(fields["Field 1"].type(), QVariant.Int)
        self.assertEqual(fields["Field 1"].name(), "Field 1")
        self.assertEqual(fields["Field 2"].type(), QVariant.String)
        self.assertEqual(fields["Field 2"].name(), "Field 2")
        self.assertEqual(fields["Field 3"].type(), QVariant.Double)
        self.assertEqual(fields["Field 3"].name(), "Field 3")

    def test_two_valid_lists(self):
        fields, are_dicts = fields_from_data([
            [1, "2", 3.5], [4, 5, 6, 7]
        ])
        self.assertFalse(are_dicts)
        self.assertEqual(len(fields), 4)
        self.assertIsInstance(fields["Field 1"], QgsField)
        self.assertIsInstance(fields["Field 2"], QgsField)
        self.assertIsInstance(fields["Field 3"], QgsField)
        self.assertIsInstance(fields["Field 4"], QgsField)
        self.assertEqual(fields["Field 1"].type(), QVariant.Int)
        self.assertEqual(fields["Field 1"].name(), "Field 1")
        self.assertEqual(fields["Field 2"].type(), QVariant.String)
        self.assertEqual(fields["Field 2"].name(), "Field 2")
        self.assertEqual(fields["Field 3"].type(), QVariant.Double)
        self.assertEqual(fields["Field 3"].name(), "Field 3")
        self.assertEqual(fields["Field 4"].type(), QVariant.Int)
        self.assertEqual(fields["Field 4"].name(), "Field 4")

    def test_valid_dict_of_one(self):
        fields, are_dicts = fields_from_data([{1: 2}])
        self.assertTrue(are_dicts)
        self.assertEqual(len(fields), 1)
        self.assertIsInstance(fields['1'], QgsField)
        self.assertEqual(fields['1'].type(), QVariant.Int)

    def test_valid_dicts(self):
        fields, are_dicts = fields_from_data([{1: 'a', "2": 4, 3: 3.5}])
        self.assertTrue(are_dicts)
        self.assertEqual(len(fields), 3)
        self.assertIsInstance(fields["1"], QgsField)
        self.assertIsInstance(fields["2"], QgsField)
        self.assertIsInstance(fields["3"], QgsField)
        self.assertEqual(fields["1"].type(), QVariant.String)
        self.assertEqual(fields["1"].name(), "1")
        self.assertEqual(fields["2"].type(), QVariant.Int)
        self.assertEqual(fields["2"].name(), "2")
        self.assertEqual(fields["3"].type(), QVariant.Double)
        self.assertEqual(fields["3"].name(), "3")

    def test_two_valid_dicts(self):
        fields, are_dicts = fields_from_data([
            {1: 'a', "2": 4, 3: 3.5},
            {1: 'a', "2": 4, 3: 3.5, "some other": 5},
        ])
        self.assertTrue(are_dicts)
        self.assertEqual(len(fields), 4)
        self.assertIsInstance(fields["1"], QgsField)
        self.assertIsInstance(fields["2"], QgsField)
        self.assertIsInstance(fields["3"], QgsField)
        self.assertIsInstance(fields["some other"], QgsField)
        self.assertEqual(fields["1"].type(), QVariant.String)
        self.assertEqual(fields["1"].name(), "1")
        self.assertEqual(fields["2"].type(), QVariant.Int)
        self.assertEqual(fields["2"].name(), "2")
        self.assertEqual(fields["3"].type(), QVariant.Double)
        self.assertEqual(fields["3"].name(), "3")
        self.assertEqual(fields["some other"].type(), QVariant.Int)
        self.assertEqual(fields["some other"].name(), "some other")


class TestMergeFieldsInProvider(TestCase):
    def test_no_layer(self):
        provider = MagicMock(spec=QgsVectorDataProvider)
        pf1 = MagicMock(spec=QgsField)
        pf1.name.return_value = "1"
        pf2 = MagicMock(spec=QgsField)
        pf2.name.return_value = "2"
        pf3 = MagicMock(spec=QgsField)
        pf3.name.return_value = "3"
        provider.fields.return_value = [pf1, pf2, pf3]

        pn1 = MagicMock(spec=QgsField)
        pn1.name.return_value = "1"
        pn4 = MagicMock(spec=QgsField)
        pn4.name.return_value = "4"
        pn9 = MagicMock(spec=QgsField)
        pn9.name.return_value = "9"

        merge_fields_in_provider(
            provider,
            fields={'1': pn1, '4': pn4, '9': pn9},
            layer=None)
        provider.addAttributes.assert_called_once_with([pn4, pn9])

    def test_layer(self):
        pf1 = MagicMock(spec=QgsField)
        pf1.name.return_value = "1"
        pf2 = MagicMock(spec=QgsField)
        pf2.name.return_value = "2"
        pf3 = MagicMock(spec=QgsField)
        pf3.name.return_value = "3"

        provider = MagicMock(spec=QgsVectorDataProvider)
        provider.fields.return_value = [pf1, pf2, pf3]
        layer = MagicMock(spec=QgsVectorLayer)
        merge_fields_in_provider(
            provider,
            fields={'1': pf1, '2': pf2, '3': pf3},
            layer=layer)
        provider.addAttributes.assert_called_once_with([])
        layer.updateFields.assert_called_once()
