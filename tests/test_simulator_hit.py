#!/usr/bin/env python3

import nose.tools as nose

import cachesimulator.simulator as sim
from cachesimulator.cache import Cache


def test_ref_status_str():
    """RefStatus enum members should display correct string values"""
    nose.assert_equal(str(sim.RefStatus.hit), 'HIT')
    nose.assert_equal(str(sim.RefStatus.miss), 'miss')


class TestIsHit(object):
    """is_hit should behave correctly in all cases"""

    def __init__(self):
        self.cache = Cache({
            '010': [{
                'tag': '1011',
                'data': [180, 181]
            }]
        })

    def test_is_hit_true(self):
        """is_hit should return True if index and tag exist in cache"""
        nose.assert_true(self.cache.is_hit('010', '1011'))

    def test_is_hit_false_index_mismatch(self):
        """is_hit should return False if index does not exist in cache"""
        nose.assert_false(self.cache.is_hit('011', '1011'))

    def test_is_hit_false_tag_mismatch(self):
        """is_hit should return False if tag does not exist in cache"""
        nose.assert_false(self.cache.is_hit('010', '1010'))
