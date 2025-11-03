#!/usr/bin/env python3

from cachesimulator.cache import Cache
from cachesimulator.reference import ReferenceCacheStatus


def get_cache():
    return Cache({"010": [{"tag": "1011", "data": [180, 181]}]})


def test_ref_status_str():
    """cache status enum members should display correct string values"""
    assert str(ReferenceCacheStatus.hit) == "HIT"
    assert str(ReferenceCacheStatus.miss) == "miss"


def test_is_hit_true():
    """is_hit should return True if index and tag exist in cache"""
    assert get_cache().is_hit("010", "1011")


def test_is_hit_false_index_mismatch():
    """is_hit should return False if index does not exist in cache"""
    assert not get_cache().is_hit("011", "1011")


def test_is_hit_false_tag_mismatch():
    """is_hit should return False if tag does not exist in cache"""
    assert not get_cache().is_hit("010", "1010")
