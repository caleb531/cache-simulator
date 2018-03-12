#!/usr/bin/env python3

import copy

import nose.tools as nose

from cachesimulator.cache import Cache


class TestSetBlock(object):
    """set_block should behave correctly in all cases"""

    def reset(self):
        self.cache = Cache({
            '010': [
                {'tag': '1000'},
                {'tag': '1100'},
                {'tag': '1101'},
                {'tag': '1110'}
            ]
        })
        self.recently_used_addrs = [
            ('100', '1100'),
            ('010', '1101'),
            ('010', '1110')
        ]
        self.new_entry = {'tag': '1111'}

    def test_empty_set(self):
        """set_block should add new block if index set is empty"""
        self.reset()
        self.cache['010'][:] = []
        self.cache.recently_used_addrs = []
        self.cache.set_block(
            replacement_policy='lru',
            num_blocks_per_set=4,
            addr_index='010',
            new_entry=self.new_entry)
        nose.assert_equal(self.cache, {
            '010': [{'tag': '1111'}]
        })

    def test_lru_replacement(self):
        """set_block should perform LRU replacement as needed"""
        self.reset()
        self.cache.recently_used_addrs = self.recently_used_addrs
        self.cache.set_block(
            replacement_policy='lru',
            num_blocks_per_set=4,
            addr_index='010',
            new_entry=self.new_entry)
        nose.assert_equal(self.cache, {
            '010': [
                {'tag': '1000'},
                {'tag': '1100'},
                {'tag': '1111'},
                {'tag': '1110'}
            ]
        })

    def test_mru_replacement(self):
        """set_block should optionally perform MRU replacement as needed"""
        self.reset()
        self.cache.recently_used_addrs = self.recently_used_addrs
        self.cache.set_block(
            replacement_policy='mru',
            num_blocks_per_set=4,
            addr_index='010',
            new_entry=self.new_entry)
        nose.assert_equal(self.cache, {
            '010': [
                {'tag': '1000'},
                {'tag': '1100'},
                {'tag': '1101'},
                {'tag': '1111'}
            ]
        })

    def test_no_replacement(self):
        """set_block should not perform replacement if there are no recents"""
        self.reset()
        original_cache = copy.deepcopy(self.cache)
        self.cache.recently_used_addrs = []
        self.cache.set_block(
            replacement_policy='lru',
            num_blocks_per_set=4,
            addr_index='010',
            new_entry=self.new_entry)
        nose.assert_is_not(self.cache, original_cache)
        nose.assert_equal(self.cache, original_cache)
