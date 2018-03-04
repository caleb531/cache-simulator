#!/usr/bin/env python3

import argparse
import math
import shutil
from enum import Enum

from cachesimulator.word_addr import WordAddress
from cachesimulator.bin_addr import BinaryAddress
from cachesimulator.cache import Cache
from cachesimulator.table import Table

# The names of all reference table columns
REF_COL_NAMES = ('WordAddr', 'BinAddr', 'Tag', 'Index', 'Offset', 'Hit/Miss')
# The minimum number of bits required per group in a prettified binary string
MIN_BITS_PER_GROUP = 3
# The default column width of the displayed results table
DEFAULT_TABLE_WIDTH = 80


# An enum representing the cache status of a reference (i.e. hit or miss)
class RefStatus(Enum):

    miss = 0
    hit = 1

    # Define how reference statuses are displayed in simulation results
    def __str__(self):
        if self.value == RefStatus.hit.value:
            return 'HIT'
        else:
            return 'miss'


# An address reference consisting of the address and all of its components
class Reference(object):

    def __init__(self, word_addr, num_addr_bits,
                 num_offset_bits, num_index_bits, num_tag_bits):
        self.word_addr = WordAddress(word_addr)
        self.bin_addr = BinaryAddress(
            word_addr=self.word_addr, num_addr_bits=num_addr_bits)
        self.offset = self.bin_addr.get_offset(num_offset_bits)
        self.index = self.bin_addr.get_index(num_offset_bits, num_index_bits)
        self.tag = self.bin_addr.get_tag(num_tag_bits)

    def __repr__(self):
        return repr(self.__dict__)


# Retrieves a list of address references for use by simulator
def get_addr_refs(word_addrs, num_addr_bits,
                  num_offset_bits, num_index_bits, num_tag_bits):

    refs = []
    for word_addr in word_addrs:

        ref = Reference(
            word_addr, num_addr_bits, num_offset_bits,
            num_index_bits, num_tag_bits)
        refs.append(ref)

    return refs


# Simulate the cache by reading the given address references into it
def read_refs_into_cache(num_sets, num_blocks_per_set, num_index_bits,
                         num_words_per_block, replacement_policy, refs):

    cache = Cache(
        num_sets=num_sets,
        num_index_bits=num_index_bits)

    recently_used_addrs = []
    ref_statuses = []

    for ref in refs:

        # The index and tag (not the offset) uniquely identify each address
        addr_id = (ref.index, ref.tag)
        # Add every retrieved address to the list of recently-used addresses
        if addr_id in recently_used_addrs:
            recently_used_addrs.remove(addr_id)
        recently_used_addrs.append(addr_id)

        # Determine the Hit/Miss value for this address to display in the table
        if cache.is_hit(ref.index, ref.tag):
            # Give emphasis to hits in contrast to misses
            ref_status = RefStatus.hit
        else:
            ref_status = RefStatus.miss
            # Create entry dictionary containing tag and data for this address
            entry = {
                'tag': ref.tag,
                'data': ref.word_addr.get_consecutive_words(
                    num_words_per_block)
            }
            cache.set_block(
                recently_used_addrs=recently_used_addrs,
                replacement_policy=replacement_policy,
                num_blocks_per_set=num_blocks_per_set,
                addr_index=ref.index,
                new_entry=entry)

        ref_statuses.append(ref_status)

    return cache, ref_statuses


# Displays details for each address reference, including its hit/miss status
def display_addr_refs(refs, ref_statuses, table_width):

    table = Table(
        num_cols=len(REF_COL_NAMES), width=table_width, alignment='right')
    table.header[:] = REF_COL_NAMES

    for ref, ref_status in zip(refs, ref_statuses):

        if ref.tag is not None:
            ref_tag = ref.tag
        else:
            ref_tag = 'n/a'

        if ref.index is not None:
            ref_index = ref.index
        else:
            ref_index = 'n/a'

        if ref.offset is not None:
            ref_offset = ref.offset
        else:
            ref_offset = 'n/a'

        # Display data for each address as a row in the table
        table.rows.append((
            ref.word_addr,
            BinaryAddress.prettify(ref.bin_addr, MIN_BITS_PER_GROUP),
            BinaryAddress.prettify(ref_tag, MIN_BITS_PER_GROUP),
            BinaryAddress.prettify(ref_index, MIN_BITS_PER_GROUP),
            BinaryAddress.prettify(ref_offset, MIN_BITS_PER_GROUP),
            ref_status))

    print(table)


# Displays the contents of the given cache as nicely-formatted table
def display_cache(cache, table_width):

    table = Table(
        num_cols=len(cache), width=table_width, alignment='center')
    table.title = 'Cache'

    cache_set_names = sorted(cache.keys())
    # A cache containing only one set is considered a fully associative cache
    if len(cache) != 1:
        # Display set names in table header if cache is not fully associative
        table.header[:] = cache_set_names

    # Add to table the cache entries for each block
    table.rows.append([])
    for index in cache_set_names:
        blocks = cache[index]
        table.rows[0].append(
            ' '.join(','.join(map(str, entry['data'])) for entry in blocks))

    print(table)


# Run the entire cache simulation
def run_simulation(num_blocks_per_set, num_words_per_block, cache_size,
                   replacement_policy, num_addr_bits, word_addrs):

    num_blocks = cache_size // num_words_per_block
    num_sets = num_blocks // num_blocks_per_set

    # Ensure that the number of bits used to represent each address is always
    # large enough to represent the largest address
    num_addr_bits = max(num_addr_bits, int(math.log2(max(word_addrs))) + 1)

    num_offset_bits = int(math.log2(num_words_per_block))
    num_index_bits = int(math.log2(num_sets))
    num_tag_bits = num_addr_bits - num_index_bits - num_offset_bits

    refs = get_addr_refs(
        word_addrs, num_addr_bits,
        num_offset_bits, num_index_bits, num_tag_bits)

    cache, ref_statuses = read_refs_into_cache(
        num_sets, num_blocks_per_set, num_index_bits,
        num_words_per_block, replacement_policy, refs)

    # The character-width of all displayed tables
    # Attempt to fit table to terminal width, otherwise use default of 80
    table_width = max((shutil.get_terminal_size(
        (DEFAULT_TABLE_WIDTH, 20)).columns, DEFAULT_TABLE_WIDTH))

    print()
    display_addr_refs(refs, ref_statuses, table_width)
    print()
    display_cache(cache, table_width)
    print()


# Parse command-line arguments passed to the program
def parse_cli_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--cache-size',
        type=int,
        required=True,
        help='the size of the cache in words')

    parser.add_argument(
        '--num-blocks-per-set',
        type=int,
        default=1,
        help='the number of blocks per set')

    parser.add_argument(
        '--num-words-per-block',
        type=int,
        default=1,
        help='the number of words per block')

    parser.add_argument(
        '--word-addrs',
        nargs='+',
        type=int,
        required=True,
        help='one or more base-10 word addresses')

    parser.add_argument(
        '--num-addr-bits',
        type=int,
        default=1,
        help='the number of bits in each given word address')

    parser.add_argument(
        '--replacement-policy',
        choices=('lru', 'mru'),
        default='lru',
        help='the cache replacement policy (LRU or MRU)')

    return parser.parse_args()


def main():

    cli_args = parse_cli_args()
    run_simulation(
        num_blocks_per_set=cli_args.num_blocks_per_set,
        num_words_per_block=cli_args.num_words_per_block,
        cache_size=cli_args.cache_size,
        replacement_policy=cli_args.replacement_policy,
        num_addr_bits=cli_args.num_addr_bits,
        word_addrs=cli_args.word_addrs)


if __name__ == '__main__':
    main()
