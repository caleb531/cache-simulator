#!/usr/bin/env python3

import argparse
import collections
import math
import shutil


# The character-width of all displayed tables
# Attempt to fit table to size of terminal window, otherwise use default of 80
TABLE_WIDTH = shutil.get_terminal_size((80, 20)).columns
# The names of all columns for a displayed address table
ADDR_COL_NAMES = ('WordAddr', 'BinAddr', 'Tag', 'Index', 'Offset', 'Hit/Miss')
# The number of columns for a displayed address table
NUM_ADDR_COLS = len(ADDR_COL_NAMES)
# Build the format string used to space columns evenly in the address table
ADDR_ROW_FORMAT_STR = ''.join('{{:>{}}}'.format(
    TABLE_WIDTH // NUM_ADDR_COLS) for i in range(NUM_ADDR_COLS))
# The minimum number of bits required per group in a prettified binary string
MIN_BITS_PER_GROUP = 3


# Retrieves the binary address of a certain length for a base-10 word address
def get_bin_addr(word_addr, num_addr_bits):

    # Strip the '0b' prefix included in the binary string returned by bin()
    bin_num = bin(word_addr)[2:]
    # Pad binary address with zeroes if too short
    bin_addr = ('0' * (num_addr_bits - len(bin_num))) + bin_num
    return bin_addr


# Formats the given binary address by inserting spaces to improve readability
# e.g. 0101010101010101 => 0101 0101 0101 0101
#      010101010101     => 010 101 010 101
#      010101010101010  => 010 1010 1010 1010
#      01010            => 01010
def prettify_bin_addr(bin_addr, min_bits_per_group):

    mid = len(bin_addr) // 2

    if mid < min_bits_per_group:
        # Return binary string immediately if bisecting the binary string
        # produces a binary string which is too short
        return bin_addr
    else:
        # Otherwise, bisect binary string and separate halves with a space
        first = prettify_bin_addr(bin_addr[:mid], min_bits_per_group)
        last = prettify_bin_addr(bin_addr[mid:], min_bits_per_group)
        return ' '.join((first, last))


# Retrieves the tag used to distinguish cache entries with the same index
def get_tag(bin_addr, num_tag_bits):

    end = num_tag_bits
    return bin_addr[:end]


# Retrieves the index used to group blocks in the cache
def get_index(bin_addr, num_offset_bits, num_index_bits):

    start = len(bin_addr) - num_offset_bits - num_index_bits
    end = len(bin_addr) - num_offset_bits
    index = bin_addr[start:end]
    # Ensure that the index is at least one bit (in case it needs to be used);
    # this allows entries to be indexed correctly for fully associative caches
    if len(index) == 0:
        return '0'
    else:
        return index


# Retrieves the word offset used to select a word in the data pointed to by the
# given binary address
def get_offset(bin_addr, num_offset_bits):

    start = len(bin_addr) - num_offset_bits
    offset = bin_addr[start:]
    # Ensure that the offset has at least one bit (in case it needs to be used)
    if len(offset) == 0:
        return '0'
    else:
        return offset


# Get all consecutive words for the given word address (including itself)
def get_consecutive_words(word_addr, num_words_per_block):

    offset = word_addr % num_words_per_block
    return [(word_addr - offset + i) for i in range(num_words_per_block)]


# Returns True if a block at the given index and tag exists in the cache,
# indicating a hit; returns False otherwise, indicating a miss
def is_hit(cache, addr_index, addr_tag):

    if addr_index in cache:
        blocks = cache[addr_index]
        for block in blocks:
            if block['tag'] == addr_tag:
                return True

    return False


# Adds the given entry to the cache at the given index
def set_block(cache, recently_used, replacement,
              num_blocks_per_set, addr_index, new_entry):

    blocks = cache[addr_index]
    # Replace MRU or LRU entry if number of blocks in set exceeds the limit
    if len(blocks) == num_blocks_per_set:
        # Iterate through the recently-used entries in reverse order for MRU
        if replacement == 'mru':
            recently_used = reversed(recently_used)
        # Replace the first matching entry with the entry to add
        for tag in recently_used:
            for i, block in enumerate(blocks):
                if block['tag'] == tag:
                    blocks[i] = new_entry
                    return
    else:
        blocks.append(new_entry)


# Prints a separator used to separate table headers/rows
def print_table_separator():

    print('-' * TABLE_WIDTH)


# Displays the contents of the given cache as nicely-formatted table
def display_cache(cache):

    # Parameters for how table columns are formatted
    num_cache_cols = len(cache)
    # Build the format string used to space columns evenly in the cache table
    cache_row_format_str = ''.join('{{:^{}}}'.format(
        TABLE_WIDTH // num_cache_cols) for i in range(num_cache_cols))

    # Display table header (each column name is a cache index)
    print('Cache'.center(TABLE_WIDTH))
    print_table_separator()
    # A cache containing only one set is considered a fully associative cache
    if len(cache) != 1:
        # Display set names in table header if cache is not fully associative
        print(cache_row_format_str.format(*cache.keys()))
        print_table_separator()

    # Build list of strings, each representing a list of entries in a block
    block_list_strs = []
    for index, blocks in cache.items():
        block_list_strs.append(
            ' '.join(','.join(map(str, entry['data'])) for entry in blocks))
    print(cache_row_format_str.format(*block_list_strs))


# Runs the cache simulation by displaying address data as they are read and
# displaying the final cache contents
def run_simulation(num_blocks_per_set, num_words_per_block, cache_size,
                   replacement, num_addr_bits, word_addrs):

    num_blocks = cache_size // num_words_per_block
    num_sets = num_blocks // num_blocks_per_set

    # Ensure that the number of bits used to represent each address is always
    # large enough to represent the largest address
    num_addr_bits = max(num_addr_bits, int(math.log2(max(word_addrs))) + 1)

    num_offset_bits = int(math.log2(num_words_per_block))
    num_index_bits = int(math.log2(num_sets))
    num_tag_bits = num_addr_bits - num_index_bits - num_offset_bits

    # Initialize cache with the maximum number of sets
    cache = collections.OrderedDict()
    for i in range(num_sets):
        index = get_bin_addr(i, num_index_bits)
        cache[index] = []
    # Store recently-used address entries
    recently_used = []

    # Display table header for the table of address addresss
    print()
    print(ADDR_ROW_FORMAT_STR.format(*ADDR_COL_NAMES))
    print_table_separator()

    for word_addr in word_addrs:

        # Compute additional ddress data
        bin_addr = get_bin_addr(word_addr, num_addr_bits)
        addr_index = get_index(bin_addr, num_offset_bits, num_index_bits)
        addr_offset = get_offset(bin_addr, num_offset_bits)
        addr_tag = get_tag(bin_addr, num_tag_bits)

        # Add every retrieved address to the list of recently-used addresses
        if addr_tag in recently_used:
            recently_used.remove(addr_tag)
        recently_used.append(addr_tag)

        # Determine the Hit/Miss value for this address to display in the table
        if is_hit(cache, addr_index, addr_tag):
            # Give emphasis to hits in contrast to misses
            addr_hm = 'HIT'
        else:
            addr_hm = 'miss'
            # Create entry dictionary containing tag and data for this address
            entry = {
                'tag': addr_tag,
                'data': get_consecutive_words(
                    word_addr, num_words_per_block)
            }
            set_block(
                cache=cache,
                recently_used=recently_used,
                replacement=replacement,
                num_blocks_per_set=num_blocks_per_set,
                addr_index=addr_index,
                new_entry=entry)

        # Replace bottom values for offset/index with human-readable values for
        # display in address table
        if num_offset_bits == 0:
            addr_offset = 'n/a'
        if num_index_bits == 0:
            addr_index = 'n/a'

        # Display data for each address as a row in the table
        print(ADDR_ROW_FORMAT_STR.format(
            word_addr,
            prettify_bin_addr(bin_addr, MIN_BITS_PER_GROUP),
            prettify_bin_addr(addr_tag, MIN_BITS_PER_GROUP),
            prettify_bin_addr(addr_index, MIN_BITS_PER_GROUP),
            prettify_bin_addr(addr_offset, MIN_BITS_PER_GROUP),
            addr_hm))

    # Print newline before/after displaying cache table for better readability
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
        default=4,
        help='the number of bits in each given word address')

    parser.add_argument(
        '--replacement',
        choices=('lru', 'mru'),
        default='lru',
        help='the cache replacement scheme (LRU or MRU)')

    return parser.parse_args()


def main():

    cli_args = parse_cli_args()
    run_simulation(
        num_blocks_per_set=cli_args.num_blocks_per_set,
        num_words_per_block=cli_args.num_words_per_block,
        cache_size=cli_args.cache_size,
        replacement=cli_args.replacement,
        num_addr_bits=cli_args.num_addr_bits,
        word_addrs=cli_args.word_addrs)


if __name__ == '__main__':
    main()
