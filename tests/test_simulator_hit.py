#!/usr/bin/env python3

import unittest

from cachesimulator.cache import Cache
from cachesimulator.reference import ReferenceCacheStatus


class TestSimulatorHit(unittest.TestCase):
    def setUp(self):
        self.cache = Cache({"010": [{"tag": "1011", "data": [180, 181]}]})

    def test_ref_status_str(self):
        """cache status enum members should display correct string values"""
        self.assertEqual(str(ReferenceCacheStatus.hit), "HIT")
        self.assertEqual(str(ReferenceCacheStatus.miss), "miss")

    def test_is_hit_true(self):
        """is_hit should return True if index and tag exist in cache"""
        self.assertTrue(self.cache.is_hit("010", "1011"))

    def test_is_hit_false_index_mismatch(self):
        """is_hit should return False if index does not exist in cache"""
        self.assertFalse(self.cache.is_hit("011", "1011"))

    def test_is_hit_false_tag_mismatch(self):
        """is_hit should return False if tag does not exist in cache"""
        self.assertFalse(self.cache.is_hit("010", "1010"))
