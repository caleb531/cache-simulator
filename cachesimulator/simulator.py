#!/usr/bin/env python3

import argparse
import math
import shutil
from enum import Enum
from cachesimulator.table import Table


# The character-width of all displayed tables
# Attempt to fit table to size of terminal window, otherwise use default of 80
TABLE_WIDTH = shutil.get_terminal_size((80, 20)).columns
# The names of all reference table columns
REF_COL_NAMES = ('WordAddr', 'BinAddr', 'Tag', 'Index', 'Offset', 'Hit/Miss')
# The minimum number of bits required per group in a prettified binary string
MIN_BITS_PER_GROUP = 3


# Retrieves the binary address of a certain length for a base-10 word address
def get_bin_addr(word_addr, num_addr_bits=None):

    # Strip the '0b' prefix included in the binary string returned by bin()
    bin_addr = bin(word_addr)[2:]
    if num_addr_bits is None:
        return bin_addr
    else:
        # Pad binary address with zeroes if too short
        bin_addr = bin_addr.zfill(num_addr_bits)
        return bin_addr


# Formats the given binary address by inserting spaces to improve readability
def prettify_bin_addr(bin_addr, min_bits_per_group):

    mid = len(bin_addr) // 2

    if mid < min_bits_per_group:
        # Return binary string immediately if bisecting the binary string
        # produces a substring which is too short
        return bin_addr
    else:
        # Otherwise, bisect binary string and separate halves with a space
        left = prettify_bin_addr(bin_addr[:mid], min_bits_per_group)
        right = prettify_bin_addr(bin_addr[mid:], min_bits_per_group)
        return ' '.join((left, right))


# Retrieves the tag used to distinguish cache entries with the same index
def get_tag(bin_addr, num_tag_bits):

    end = num_tag_bits
    tag = bin_addr[:end]
    if len(tag) != 0:
        return tag
    else:
        return None


# Retrieves the index used to group blocks in the cache
def get_index(bin_addr, num_offset_bits, num_index_bits):

    start = len(bin_addr) - num_offset_bits - num_index_bits
    end = len(bin_addr) - num_offset_bits
    index = bin_addr[start:end]
    if len(index) != 0:
        return index
    else:
        return None


# Retrieves the word offset used to select a word in the data pointed to by the
# given binary address
def get_offset(bin_addr, num_offset_bits):

    start = len(bin_addr) - num_offset_bits
    offset = bin_addr[start:]
    if len(offset) != 0:
        return offset
    else:
        return None


# Retrieves all consecutive words for the given word address (including itself)
def get_consecutive_words(word_addr, num_words_per_block):

    offset = word_addr % num_words_per_block
    return [(word_addr - offset + i) for i in range(num_words_per_block)]


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
        self.word_addr = word_addr
        self.bin_addr = get_bin_addr(self.word_addr, num_addr_bits)
        self.offset = get_offset(self.bin_addr, num_offset_bits)
        self.index = get_index(self.bin_addr, num_offset_bits, num_index_bits)
        self.tag = get_tag(self.bin_addr, num_tag_bits)


# Returns True if a block at the given index and tag exists in the cache,
# indicating a hit; returns False otherwise, indicating a miss
def is_hit(cache, addr_index, addr_tag):

    # Ensure that indexless fully associative caches are accessed correctly
    if addr_index is None:
        blocks = cache['0']
    elif addr_index in cache:
        blocks = cache[addr_index]
    else:
        return False

    for block in blocks:
        if block['tag'] == addr_tag:
            return True

    return False


# Adds the given entry to the cache at the given index
def set_block(cache, recently_used_addrs, replacement_policy,
              num_blocks_per_set, addr_index, new_entry):

    # Place all cache entries in a single set if cache is fully associative
    if addr_index is None:
        blocks = cache['0']
    else:
        blocks = cache[addr_index]
    # Replace MRU or LRU entry if number of blocks in set exceeds the limit
    if len(blocks) == num_blocks_per_set:
        # Iterate through the recently-used entries in reverse order for MRU
        if replacement_policy == 'mru':
            recently_used_addrs = reversed(recently_used_addrs)
        # Replace the first matching entry with the entry to add
        for recent_index, recent_tag in recently_used_addrs:
            for i, block in enumerate(blocks):
                if recent_index == addr_index and block['tag'] == recent_tag:
                    blocks[i] = new_entry
                    return
    else:
        blocks.append(new_entry)


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


# Initializes the reference cache with a fixed number of sets
def create_cache(num_sets, num_index_bits):

    cache = {}
    for i in range(num_sets):
        index = get_bin_addr(i, num_index_bits)
        cache[index] = []
    return cache


# Simulate the cache by reading the given address references into it
def read_refs_into_cache(num_sets, num_blocks_per_set, num_index_bits,
                         num_words_per_block, replacement_policy, refs):

    cache = create_cache(num_sets, num_index_bits)

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
        if is_hit(cache, ref.index, ref.tag):
            # Give emphasis to hits in contrast to misses
            ref_status = RefStatus.hit
        else:
            ref_status = RefStatus.miss
            # Create entry dictionary containing tag and data for this address
            entry = {
                'tag': ref.tag,
                'data': get_consecutive_words(
                    ref.word_addr, num_words_per_block)
            }
            set_block(
                cache=cache,
                recently_used_addrs=recently_used_addrs,
                replacement_policy=replacement_policy,
                num_blocks_per_set=num_blocks_per_set,
                addr_index=ref.index,
                new_entry=entry)

        ref_statuses.append(ref_status)

    return cache, ref_statuses


# Displays details for each address reference, including its hit/miss status
def display_addr_refs(refs, ref_statuses):

    table = Table(
        num_cols=len(REF_COL_NAMES), width=TABLE_WIDTH, alignment='right')
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
            prettify_bin_addr(ref.bin_addr, MIN_BITS_PER_GROUP),
            prettify_bin_addr(ref_tag, MIN_BITS_PER_GROUP),
            prettify_bin_addr(ref_index, MIN_BITS_PER_GROUP),
            prettify_bin_addr(ref_offset, MIN_BITS_PER_GROUP),
            ref_status))

    print(table)


# Displays the contents of the given cache as nicely-formatted table
def display_cache(cache):

    table = Table(
        num_cols=len(cache), width=TABLE_WIDTH, alignment='center')
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

    print()
    display_addr_refs(refs, ref_statuses)
    print()
    display_cache(cache)
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
