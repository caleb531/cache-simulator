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
