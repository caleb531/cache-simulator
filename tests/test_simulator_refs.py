#!/usr/bin/env python3

from collections import OrderedDict

import nose.tools as nose

from cachesimulator.cache import Cache
from cachesimulator.reference import Reference, ReferenceCacheStatus
from cachesimulator.simulator import Simulator


def test_get_addr_refs():
    """get_addr_refs should return correct reference data"""
    word_addrs = [3, 180, 44, 253]
    sim = Simulator()
    refs = sim.get_addr_refs(
        word_addrs=word_addrs, num_addr_bits=8,
        num_tag_bits=4, num_index_bits=3, num_offset_bits=1)
    ref = refs[1]
    nose.assert_equal(len(refs), len(word_addrs))
    nose.assert_equal(ref.word_addr, 180)
    nose.assert_equal(ref.bin_addr, '10110100')
    nose.assert_equal(ref.tag, '1011')
    nose.assert_equal(ref.index, '010')
    nose.assert_equal(ref.offset, '0')


class TestReadRefs(object):
    """all simulator functions should behave correctly in all cases"""

    WORD_ADDRS = [3, 180, 43, 2, 191, 88, 190, 14, 181, 44, 186, 253]

    def get_hits(self, refs):
        """retrieves all indices where hits occur in a list of ref statuses"""
        return {
            i for i, ref in enumerate(refs)
            if ref.cache_status == ReferenceCacheStatus.hit}

    def test_read_refs_into_cache_direct_mapped_lru(self):
        """read_refs_into_cache should work for direct-mapped LRU cache"""
        word_addrs = [0, 8, 0, 6, 8]
        sim = Simulator()
        refs = sim.get_addr_refs(
            word_addrs=word_addrs, num_addr_bits=4,
            num_tag_bits=2, num_index_bits=2, num_offset_bits=0)
        cache = Cache(num_sets=4, num_index_bits=2)
        cache.read_refs(
            refs=refs, num_blocks_per_set=1,
            num_words_per_block=1, replacement_policy='lru')
        nose.assert_equal(cache, {
            '00': [
                {'tag': '10', 'data': [8]}
            ],
            '01': [],
            '10': [
                {'tag': '01', 'data': [6]},
            ],
            '11': []
        })
        nose.assert_equal(self.get_hits(refs), set())

    def test_read_refs_into_cache_set_associative_lru(self):
        """read_refs_into_cache should work for set associative LRU cache"""
        sim = Simulator()
        refs = sim.get_addr_refs(
            word_addrs=TestReadRefs.WORD_ADDRS, num_addr_bits=8,
            num_tag_bits=5, num_index_bits=2, num_offset_bits=1)
        cache = Cache(num_sets=4, num_index_bits=2)
        cache.read_refs(
            refs=refs, num_blocks_per_set=3,
            num_words_per_block=2, replacement_policy='lru')
        nose.assert_equal(cache, {
            '00': [
                {'tag': '01011', 'data': [88, 89]}
            ],
            '01': [
                {'tag': '00000', 'data': [2, 3]},
                {'tag': '00101', 'data': [42, 43]},
                {'tag': '10111', 'data': [186, 187]}
            ],
            '10': [
                {'tag': '10110', 'data': [180, 181]},
                {'tag': '00101', 'data': [44, 45]},
                {'tag': '11111', 'data': [252, 253]}
            ],
            '11': [
                {'tag': '10111', 'data': [190, 191]},
                {'tag': '00001', 'data': [14, 15]},
            ]
        })
        nose.assert_equal(self.get_hits(refs), {3, 6, 8})

    def test_read_refs_into_cache_fully_associative_lru(self):
        """read_refs_into_cache should work for fully associative LRU cache"""
        sim = Simulator()
        refs = sim.get_addr_refs(
            word_addrs=TestReadRefs.WORD_ADDRS, num_addr_bits=8,
            num_tag_bits=7, num_index_bits=0, num_offset_bits=1)
        cache = Cache(num_sets=1, num_index_bits=0)
        cache.read_refs(
            refs=refs, num_blocks_per_set=4,
            num_words_per_block=2, replacement_policy='lru')
        nose.assert_equal(cache, {
            '0': [
                {'tag': '1011010', 'data': [180, 181]},
                {'tag': '0010110', 'data': [44, 45]},
                {'tag': '1111110', 'data': [252, 253]},
                {'tag': '1011101', 'data': [186, 187]}
            ]
        })
        nose.assert_equal(self.get_hits(refs), {3, 6})

    def test_read_refs_into_cache_fully_associative_mru(self):
        """read_refs_into_cache should work for fully associative MRU cache"""
        sim = Simulator()
        refs = sim.get_addr_refs(
            word_addrs=TestReadRefs.WORD_ADDRS, num_addr_bits=8,
            num_tag_bits=7, num_index_bits=0, num_offset_bits=1)
        cache = Cache(num_sets=1, num_index_bits=0)
        cache.read_refs(
            refs=refs, num_blocks_per_set=4,
            num_words_per_block=2, replacement_policy='mru')
        nose.assert_equal(cache, Cache({
            '0': [
                {'tag': '0000001', 'data': [2, 3]},
                {'tag': '1111110', 'data': [252, 253]},
                {'tag': '0010101', 'data': [42, 43]},
                {'tag': '0000111', 'data': [14, 15]}
            ]
        }))
        nose.assert_equal(self.get_hits(refs), {3, 8})


def test_get_ref_str():
    """should return string representation of Reference"""
    ref = Reference(word_addr=180, num_addr_bits=8,
                    num_tag_bits=4, num_index_bits=3, num_offset_bits=1)
    nose.assert_equal(str(ref), str(OrderedDict(sorted(ref.__dict__.items()))))
