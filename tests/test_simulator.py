#!/usr/bin/env python3

import contextlib
import copy
import io
import nose.tools as nose
import src.simulator as sim


def test_get_bin_addr_unpadded():
    """get_bin_addr should return unpadded binary address of word address"""
    nose.assert_equal(
        sim.get_bin_addr(180),
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


def test_get_tag_0_bit():
    """get_tag should return None if no bits are allocated to a tag"""
    nose.assert_is_none(
        sim.get_tag('10110100', num_tag_bits=0))


def test_get_index_2_bit():
    """get_index should return correct 2 index bits for an address"""
    nose.assert_equal(
        sim.get_index('11111101', num_offset_bits=1, num_index_bits=2),
        '10')


def test_get_index_0_bit():
    """get_index should return None if no bits are allocated to an index"""
    nose.assert_is_none(
        sim.get_index('11111111', num_offset_bits=1, num_index_bits=0))


def test_get_offset_2_bit():
    """get_offset should return correct 2 offset bits for an address"""
    nose.assert_equal(
        sim.get_offset('11111101', num_offset_bits=2),
        '01')


def test_get_offset_0_bit():
    """get_offset should return None if no bits are allocated to an offset"""
    nose.assert_is_none(
        sim.get_offset('10110100', num_offset_bits=0))


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
    """get_consecutive_words should return correct words for 4-word blocks"""
    nose.assert_list_equal(
        sim.get_consecutive_words(21, num_words_per_block=4),
        [20, 21, 22, 23])


def test_ref_status_str():
    """RefStatus enum members should display correct string values"""
    nose.assert_equal(str(sim.RefStatus.hit), 'HIT')
    nose.assert_equal(str(sim.RefStatus.miss), 'miss')


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

    def test_empty_set(self):
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

    def test_lru_replacement(self):
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

    def test_mru_replacement(self):
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

    def test_no_replacement(self):
        """set_block should not perform replacement if there are no recents"""
        self.reset()
        original_cache = copy.deepcopy(self.cache)
        sim.set_block(
            cache=self.cache,
            recently_used_addrs=[],
            replacement_policy='lru',
            num_blocks_per_set=4,
            addr_index='010',
            new_entry=self.new_entry)
        nose.assert_dict_equal(self.cache, original_cache)


class TestSimulator(object):
    """all simulator functions should behave correctly in all cases"""

    WORD_ADDRS = [3, 180, 43, 2, 191, 88, 190, 14, 181, 44, 186, 253]
    TABLE_WIDTH = 80

    def test_get_addr_refs(self):
        """get_addr_refs should return correct reference data"""
        refs = sim.get_addr_refs(
            word_addrs=self.WORD_ADDRS, num_addr_bits=8,
            num_tag_bits=4, num_index_bits=3, num_offset_bits=1)
        ref = refs[1]
        nose.assert_equal(len(refs), len(self.WORD_ADDRS))
        nose.assert_equal(ref.word_addr, 180)
        nose.assert_equal(ref.bin_addr, '10110100')
        nose.assert_equal(ref.tag, '1011')
        nose.assert_equal(ref.index, '010')
        nose.assert_equal(ref.offset, '0')

    def get_hits(self, ref_statuses):
        """retrieves all indices where hits occur in a list of ref statuses"""
        return {
            i for i, status in enumerate(ref_statuses) if status.value == 1}

    def test_read_refs_into_cache_direct_mapped_lru(self):
        """read_refs_into_cache should work for direct-mapped LRU cache"""
        refs = sim.get_addr_refs(
            word_addrs=[0, 8, 0, 6, 8], num_addr_bits=4,
            num_tag_bits=2, num_index_bits=2, num_offset_bits=0)
        cache, ref_statuses = sim.read_refs_into_cache(
            refs=refs, num_sets=4, num_blocks_per_set=1,
            num_words_per_block=1, num_index_bits=2, replacement_policy='lru')
        nose.assert_dict_equal(cache, {
            '00': [
                {'tag': '10', 'data': [8]}
            ],
            '01': [],
            '10': [
                {'tag': '01', 'data': [6]},
            ],
            '11': []
        })
        nose.assert_set_equal(self.get_hits(ref_statuses), set())

    def test_read_refs_into_cache_set_associative_lru(self):
        """read_refs_into_cache should work for set associative LRU cache"""
        refs = sim.get_addr_refs(
            word_addrs=self.WORD_ADDRS, num_addr_bits=8,
            num_tag_bits=5, num_index_bits=2, num_offset_bits=1)
        cache, ref_statuses = sim.read_refs_into_cache(
            refs=refs, num_sets=4, num_blocks_per_set=3,
            num_words_per_block=2, num_index_bits=2, replacement_policy='lru')
        nose.assert_dict_equal(cache, {
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
        nose.assert_set_equal(self.get_hits(ref_statuses), {3, 6, 8})

    def test_read_refs_into_cache_fully_associative_lru(self):
        """read_refs_into_cache should work for fully associative LRU cache"""
        refs = sim.get_addr_refs(
            word_addrs=self.WORD_ADDRS, num_addr_bits=8,
            num_tag_bits=7, num_index_bits=0, num_offset_bits=1)
        cache, ref_statuses = sim.read_refs_into_cache(
            refs=refs, num_sets=1, num_blocks_per_set=4,
            num_words_per_block=2, num_index_bits=0, replacement_policy='lru')
        nose.assert_dict_equal(cache, {
            '0': [
                {'tag': '1011010', 'data': [180, 181]},
                {'tag': '0010110', 'data': [44, 45]},
                {'tag': '1111110', 'data': [252, 253]},
                {'tag': '1011101', 'data': [186, 187]}
            ]
        })
        nose.assert_set_equal(self.get_hits(ref_statuses), {3, 6})

    def test_read_refs_into_cache_fully_associative_mru(self):
        """read_refs_into_cache should work for fully associative MRU cache"""
        refs = sim.get_addr_refs(
            word_addrs=self.WORD_ADDRS, num_addr_bits=8,
            num_tag_bits=7, num_index_bits=0, num_offset_bits=1)
        cache, ref_statuses = sim.read_refs_into_cache(
            refs=refs, num_sets=1, num_blocks_per_set=4,
            num_words_per_block=2, num_index_bits=0, replacement_policy='mru')
        nose.assert_dict_equal(cache, {
            '0': [
                {'tag': '0000001', 'data': [2, 3]},
                {'tag': '1111110', 'data': [252, 253]},
                {'tag': '0010101', 'data': [42, 43]},
                {'tag': '0000111', 'data': [14, 15]}
            ]
        })
        nose.assert_set_equal(self.get_hits(ref_statuses), {3, 8})

    def test_display_addr_refs(self):
        """should display table of address references"""
        refs = sim.get_addr_refs(
            word_addrs=self.WORD_ADDRS, num_addr_bits=8,
            num_tag_bits=5, num_index_bits=2, num_offset_bits=1)
        ref_statuses = (['miss'] * 11) + ['HIT']
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_addr_refs(refs, ref_statuses)
        table_output = out.getvalue()
        num_cols = 6
        col_width = TestSimulator.TABLE_WIDTH // num_cols
        nose.assert_regexp_matches(
            table_output, r'{}\s*{}\s*{}\s*{}\s*{}\s*{}\n{}'.format(
                'WordAddr'.rjust(col_width), 'BinAddr'.rjust(col_width),
                'Tag'.rjust(col_width), 'Index'.rjust(col_width),
                'Offset'.rjust(col_width), 'Hit/Miss'.rjust(col_width),
                ('-' * TestSimulator.TABLE_WIDTH)))
        nose.assert_regexp_matches(
            table_output, r'{}\s*{}\s*{}\s*{}\s*{}\s*{}'.format(
                '253'.rjust(col_width), '1111 1101'.rjust(col_width),
                '11111'.rjust(col_width), '10'.rjust(col_width),
                '1'.rjust(col_width), 'HIT'.rjust(col_width)))

    def test_display_addr_refs_no_index(self):
        """should display n/a for index when there are no index bits"""
        refs = sim.get_addr_refs(
            word_addrs=self.WORD_ADDRS, num_addr_bits=8,
            num_tag_bits=7, num_index_bits=0, num_offset_bits=1)
        ref_statuses = ['miss'] * 12
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_addr_refs(refs, ref_statuses)
        table_output = out.getvalue()
        nose.assert_regexp_matches(
            table_output, r'\s*{}\s*{}\s*{}'.format(
                'n/a', '\d', 'miss'))

    def test_display_addr_refs_no_offset(self):
        """should display n/a for offset when there are no offset bits"""
        refs = sim.get_addr_refs(
            word_addrs=self.WORD_ADDRS, num_addr_bits=8,
            num_tag_bits=4, num_index_bits=4, num_offset_bits=0)
        ref_statuses = ['miss'] * 12
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_addr_refs(refs, ref_statuses)
        table_output = out.getvalue()
        nose.assert_regexp_matches(
            table_output, r'\s*{}\s*{}\s*{}'.format(
                '\d\d', 'n/a', 'miss'))

    def test_display_cache(self):
        """should display table for direct-mapped/set associative cache"""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_cache({
                '000': [
                    {'tag': '0101', 'data': [88, 89]}
                ],
                '001': [
                    {'tag': '0000', 'data': [2, 3]},
                    {'tag': '0010', 'data': [42, 43]},
                ]
            })
        table_output = out.getvalue()
        num_cols = 2
        col_width = TestSimulator.TABLE_WIDTH // num_cols
        nose.assert_regexp_matches(
            table_output, '{}\n{}'.format(
                'Cache'.center(TestSimulator.TABLE_WIDTH),
                ('-' * TestSimulator.TABLE_WIDTH)))
        nose.assert_equal(
            table_output.count('-'), TestSimulator.TABLE_WIDTH * 2)
        nose.assert_regexp_matches(
            table_output, r'{}{}'.format(
                '000'.center(col_width),
                '001'.center(col_width)))
        nose.assert_regexp_matches(
            table_output, r'{}{}'.format(
                '88,89'.center(col_width),
                '2,3 42,43'.center(col_width)))

    def test_display_cache_fully_assoc(self):
        """should correctly display table for fully associative cache"""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_cache({
                '0': [
                    {'tag': '0000001', 'data': [2, 3]},
                    {'tag': '1111110', 'data': [252, 253]}
                ]
            })
        table_output = out.getvalue()
        nose.assert_regexp_matches(
            table_output, '{}\n{}'.format(
                'Cache'.center(TestSimulator.TABLE_WIDTH),
                ('-' * TestSimulator.TABLE_WIDTH)))
        nose.assert_equal(
            table_output.count('-'), TestSimulator.TABLE_WIDTH)
        nose.assert_regexp_matches(
            table_output, '2,3 252,253'.center(TestSimulator.TABLE_WIDTH))
