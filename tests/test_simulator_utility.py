#!/usr/bin/env python3

import nose.tools as nose

from cachesimulator.bin_addr import BinaryAddress
from cachesimulator.word_addr import WordAddress


def test_get_bin_addr_unpadded():
    """get_bin_addr should return unpadded binary address of word address"""
    nose.assert_equal(
        BinaryAddress(word_addr=WordAddress(180)),
        '10110100')


def test_get_bin_addr_padded():
    """get_bin_addr should return padded binary address of word address"""
    nose.assert_equal(
        BinaryAddress(word_addr=WordAddress(44), num_addr_bits=8),
        '00101100')


def test_prettify_bin_addr_16_bit():
    """prettify_bin_addr should prettify 8-bit string into groups of 3"""
    nose.assert_equal(
        BinaryAddress.prettify('1010101110101011', min_bits_per_group=3),
        '1010 1011 1010 1011')


def test_prettify_bin_addr_8_bit():
    """prettify_bin_addr should prettify 8-bit string into groups of 3"""
    nose.assert_equal(
        BinaryAddress.prettify('10101011', min_bits_per_group=3),
        '1010 1011')


def test_prettify_bin_addr_7_bit():
    """prettify_bin_addr should prettify 7-bit string into groups of 3"""
    nose.assert_equal(
        BinaryAddress.prettify('1011010', min_bits_per_group=3),
        '101 1010')


def test_prettify_bin_addr_6_bit():
    """prettify_bin_addr should prettify 6-bit string into groups of 3"""
    nose.assert_equal(
        BinaryAddress.prettify('101011', min_bits_per_group=3),
        '101 011')


def test_prettify_bin_addr_5_bit():
    """prettify_bin_addr should prettify 5-bit string into groups of 3"""
    nose.assert_equal(
        BinaryAddress.prettify('10110', min_bits_per_group=3),
        '10110')


def test_get_tag_5_bit():
    """get_tag should return correct 5 tag bits for an address"""
    nose.assert_equal(
        BinaryAddress('10110100').get_tag(num_tag_bits=5),
        '10110')


def test_get_tag_0_bit():
    """get_tag should return None if no bits are allocated to a tag"""
    nose.assert_is_none(
        BinaryAddress('10110100').get_tag(num_tag_bits=0))


def test_get_index_2_bit():
    """get_index should return correct 2 index bits for an address"""
    nose.assert_equal(
        BinaryAddress('11111101').get_index(
            num_offset_bits=1, num_index_bits=2), '10')


def test_get_index_0_bit():
    """get_index should return None if no bits are allocated to an index"""
    nose.assert_is_none(
        BinaryAddress('11111111').get_index(
            num_offset_bits=1, num_index_bits=0))


def test_get_offset_2_bit():
    """get_offset should return correct 2 offset bits for an address"""
    nose.assert_equal(
        BinaryAddress('11111101').get_offset(num_offset_bits=2), '01')


def test_get_offset_0_bit():
    """get_offset should return None if no bits are allocated to an offset"""
    nose.assert_is_none(
        BinaryAddress('10110100').get_offset(num_offset_bits=0))


def test_get_consecutive_words_1_word():
    """get_consecutive_words should return same word for 1-word blocks"""
    nose.assert_equal(
        WordAddress(23).get_consecutive_words(num_words_per_block=1),
        [23])


def test_get_consecutive_words_2_word():
    """get_consecutive_words should return correct words for 2-word blocks"""
    nose.assert_equal(
        WordAddress(22).get_consecutive_words(num_words_per_block=2),
        [22, 23])


def test_get_consecutive_words_4_word():
    """get_consecutive_words should return correct words for 4-word blocks"""
    nose.assert_equal(
        WordAddress(21).get_consecutive_words(num_words_per_block=4),
        [20, 21, 22, 23])
