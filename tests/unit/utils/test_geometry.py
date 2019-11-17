# -*- coding: utf-8 -*-
"""
Unit tests for Geometry.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import shutil
import tempfile
from unittest import TestCase, SkipTest
from unittest.mock import MagicMock
from qgis.core import QgsWkbTypes, QgsProject, QgsVectorLayer, QgsGeometry

from qgis_plutil.utils.geometry import (
    geometry_flat_name, geometry_name, geometry_constructor_by_type,
    geometry_from_data
)

logger = logging.getLogger('tests.qgis_plutil.util.geometry')


class TestFlatName(TestCase):
    def test_one(self):
        with self.assertRaises(ValueError):
            geometry_flat_name("abc")
        self.assertEqual(geometry_flat_name(QgsWkbTypes.Point), "Point")
        self.assertEqual(geometry_flat_name(QgsWkbTypes.Point25D), "Point")
        self.assertEqual(geometry_flat_name(QgsWkbTypes.PointZ), "Point")
        self.assertEqual(geometry_flat_name(QgsWkbTypes.PointM), "Point")
        self.assertEqual(geometry_flat_name(QgsWkbTypes.PointZM), "Point")
        self.assertEqual(geometry_flat_name(QgsWkbTypes.Point), "Point")
        self.assertEqual(
            geometry_flat_name(QgsWkbTypes.LineString), "LineString")
        self.assertEqual(
            geometry_flat_name(QgsWkbTypes.Polygon), "Polygon")
        self.assertEqual(
            geometry_flat_name(QgsWkbTypes.MultiLineString25D), "MultiLineString")
        self.assertEqual(
            geometry_flat_name(QgsWkbTypes.CompoundCurveZM), "CompoundCurve")


class TestName(TestCase):
    def test_one(self):
        with self.assertRaises(ValueError):
            geometry_name("abc")
        self.assertEqual(geometry_name(QgsWkbTypes.Point), "Point")
        self.assertEqual(geometry_name(QgsWkbTypes.Point25D), "Point25D")
        self.assertEqual(geometry_name(QgsWkbTypes.PointZ), "PointZ")
        self.assertEqual(geometry_name(QgsWkbTypes.PointM), "PointM")
        self.assertEqual(geometry_name(QgsWkbTypes.PointZM), "PointZM")


class TestGeometryConstructorByName(TestCase):
    def test_point(self):
        cons = geometry_constructor_by_type(QgsWkbTypes.Point)
        result = cons([1, 2])
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(), "Point (1 2)")
        result = cons((1, 2))
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(), "Point (1 2)")
        with self.assertRaises(TypeError):
            cons([1, 2, 3])

    def test_multi_point(self):
        cons = geometry_constructor_by_type(QgsWkbTypes.MultiPoint)
        result = cons([[1, 2], [3, 4]])
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(), "MultiPoint ((1 2),(3 4))")

        with self.assertRaises(TypeError):
            cons([[1, 2], [3, 4, 5]])

    def test_line_string(self):
        cons = geometry_constructor_by_type(QgsWkbTypes.LineString)
        result = cons([[1, 2], [3, 4]])
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(), "LineString (1 2, 3 4)")

        with self.assertRaises(TypeError):
            cons([[1, 2], [3, 4, 5]])

    def test_polygon(self):
        cons = geometry_constructor_by_type(QgsWkbTypes.Polygon)
        result = cons([[[1, 2], [3, 4]]])
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(), "Polygon ((1 2, 3 4, 1 2))")

        result = cons([[[1, 2]]])
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(), "Polygon ((1 2))")

        cons = geometry_constructor_by_type(QgsWkbTypes.Polygon)
        result = cons([[
            [10, 20], [30, 40]],
            [[1, 2], [3, 4]],
            [[1, 2], [3, 4]]])
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(),
                         "Polygon ("
                         "(10 20, 30 40, 10 20),"
                         "(1 2, 3 4, 1 2),"
                         "(1 2, 3 4, 1 2))")

        with self.assertRaises(TypeError):
            cons([[1, 2], [3, 4, 5]])
        with self.assertRaises(TypeError):
            cons([[[1, 2], [3, 4, 5]]])

    def test_multi_polygon(self):
        cons = geometry_constructor_by_type(QgsWkbTypes.MultiPolygon)
        result = cons([[[[1, 2], [3, 4]]]])
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(), "MultiPolygon (((1 2, 3 4, 1 2)))")

        result = cons([[[[1, 2]]]])
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(), "MultiPolygon (((1 2)))")

        with self.assertRaises(TypeError):
            cons([[1, 2], [3, 4, 5]])
        with self.assertRaises(TypeError):
            cons([[[1, 2], [3, 4, 5]]])
        with self.assertRaises(TypeError):
            cons([[[[1, 2], [3, 4, 5]]]])


class TestGeometryFromData(TestCase):
    def test_point(self):
        result = geometry_from_data(QgsWkbTypes.Point, [1, 2])
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(), "Point (1 2)")

        result = geometry_from_data(QgsWkbTypes.Point, (1, 2))
        self.assertIsInstance(result, QgsGeometry)
        self.assertEqual(result.asWkt(), "Point (1 2)")
        with self.assertRaises(TypeError):
            result = geometry_from_data(QgsWkbTypes.Point, [1, 2, 3])

