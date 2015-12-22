#!/usr/bin/env python3

import nose.tools as nose
import simulator as sim


def test_get_bin_addr_unpadded():
    """get_bin_addr should return unpadded binary address of word address"""
    nose.assert_equal(
        sim.get_bin_addr(180, num_addr_bits=8),
        '10110100')


def test_get_bin_addr_padded():
    """get_bin_addr should return padded binary address of word address"""
    nose.assert_equal(
        sim.get_bin_addr(44, num_addr_bits=8),
        '00101100')


def test_prettify_bin_addr_16_bit():
    """prettify_bin_addr should prettify 8-bit string into groups of 3"""
    nose.assert_equal(
        sim.prettify_bin_addr('1010101110101011', min_bits_per_group=3),
        '1010 1011 1010 1011')


def test_prettify_bin_addr_8_bit():
    """prettify_bin_addr should prettify 8-bit string into groups of 3"""
    nose.assert_equal(
        sim.prettify_bin_addr('10101011', min_bits_per_group=3),
        '1010 1011')


def test_prettify_bin_addr_7_bit():
    """prettify_bin_addr should prettify 7-bit string into groups of 3"""
    nose.assert_equal(
        sim.prettify_bin_addr('1011010', min_bits_per_group=3),
        '101 1010')


def test_prettify_bin_addr_6_bit():
    """prettify_bin_addr should prettify 6-bit string into groups of 3"""
    nose.assert_equal(
        sim.prettify_bin_addr('101011', min_bits_per_group=3),
        '101 011')


def test_prettify_bin_addr_5_bit():
    """prettify_bin_addr should prettify 5-bit string into groups of 3"""
    nose.assert_equal(
        sim.prettify_bin_addr('10110', min_bits_per_group=3),
        '10110')


def test_get_tag_5_bit():
    """get_tag should return correct 5 tag bits for an address"""
    nose.assert_equal(
        sim.get_tag('10110100', num_tag_bits=5),
        '10110')


def test_get_index_2_bit():
    """get_index should return correct 2 index bits for an address"""
    nose.assert_equal(
        sim.get_index('11111101', num_offset_bits=1, num_index_bits=2),
        '10')


def test_get_index_0_bit():
    """get_index should return '0' if no bits are allocated to an index"""
    nose.assert_equal(
        sim.get_index('11111111', num_offset_bits=1, num_index_bits=0),
        '0')


def test_get_offset_2_bit():
    """get_offset should return correct 2 offset bits for an address"""
    nose.assert_equal(
        sim.get_offset('11111101', num_offset_bits=2),
        '01')


def test_get_offset_0_bit():
    """get_offset should return '0' if no bits are allocated to an offset"""
    nose.assert_equal(
        sim.get_offset('10110100', num_offset_bits=1),
        '0')


def test_get_consecutive_words_1_word():
    """get_consecutive_words should return same word for 1-word blocks"""
    nose.assert_list_equal(
        sim.get_consecutive_words(23, num_words_per_block=1),
        [23])


def test_get_consecutive_words_2_word():
    """get_consecutive_words should return correct words for 2-word blocks"""
    nose.assert_list_equal(
        sim.get_consecutive_words(22, num_words_per_block=2),
        [22, 23])


def test_get_consecutive_words_4_word():
    """get_consecutive_words should return correct words for 2-word blocks"""
    nose.assert_list_equal(
        sim.get_consecutive_words(21, num_words_per_block=4),
        [20, 21, 22, 23])


class TestIsHit(object):
    """is_hit should behave correctly in all cases"""

    def __init__(self):
        self.cache = {
            '010': [{
                'tag': '1011',
                'data': [180, 181]
            }]
        }

    def test_is_hit_true(self):
        """is_hit should return True if index and tag exist in cache"""
        nose.assert_true(sim.is_hit(self.cache, '010', '1011'))

    def test_is_hit_false_index_mismatch(self):
        """is_hit should return False if index does not exist in cache"""
        nose.assert_false(sim.is_hit(self.cache, '011', '1011'))

    def test_is_hit_false_tag_mismatch(self):
        """is_hit should return False if tag does not exist in cache"""
        nose.assert_false(sim.is_hit(self.cache, '010', '1010'))


class TestSetBlock(object):
    """set_block should behave correctly in all cases"""

    def reset(self):
        self.cache = {
            '010': [
                {'tag': '1000'},
                {'tag': '1100'},
                {'tag': '1101'},
                {'tag': '1110'}
            ]
        }
        self.recently_used_addrs = [
            ('100', '1100'),
            ('010', '1101'),
            ('010', '1110')
        ]
        self.new_entry = {'tag': '1111'}

    def test_set_block_empty_set(self):
        """set_block should add new block if index set is empty"""
        self.reset()
        self.cache['010'][:] = []
        sim.set_block(
            cache=self.cache,
            recently_used_addrs=[],
            replacement_policy='lru',
            num_blocks_per_set=4,
            addr_index='010',
            new_entry=self.new_entry)
        nose.assert_dict_equal(self.cache, {
            '010': [{'tag': '1111'}]
        })

    def test_set_block_lru_replacement(self):
        """set_block should perform LRU replacement as needed"""
        self.reset()
        sim.set_block(
            cache=self.cache,
            recently_used_addrs=self.recently_used_addrs,
            replacement_policy='lru',
            num_blocks_per_set=4,
            addr_index='010',
            new_entry=self.new_entry)
        nose.assert_dict_equal(self.cache, {
            '010': [
                {'tag': '1000'},
                {'tag': '1100'},
                {'tag': '1111'},
                {'tag': '1110'}
            ]
        })

    def test_set_block_mru_replacement(self):
        """set_block should optionally perform MRU replacement as needed"""
        self.reset()
        sim.set_block(
            cache=self.cache,
            recently_used_addrs=self.recently_used_addrs,
            replacement_policy='mru',
            num_blocks_per_set=4,
            addr_index='010',
            new_entry=self.new_entry)
        nose.assert_dict_equal(self.cache, {
            '010': [
                {'tag': '1000'},
                {'tag': '1100'},
                {'tag': '1101'},
                {'tag': '1111'}
            ]
        })
