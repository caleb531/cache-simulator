#!/usr/bin/env python3

import math
import shutil

from cachesimulator.bin_addr import BinaryAddress
from cachesimulator.cache import Cache
from cachesimulator.reference import Reference, ReferenceCacheStatus
from cachesimulator.table import Table

# The names of all reference table columns
REF_COL_NAMES = ('WordAddr', 'BinAddr', 'Tag', 'Index', 'Offset', 'Hit/Miss')
# The minimum number of bits required per group in a prettified binary string
MIN_BITS_PER_GROUP = 3
# The default column width of the displayed results table
DEFAULT_TABLE_WIDTH = 80


class Simulator(object):

    def __init__(self):

        # A list of recently ordered addresses, ordered from least-recently
        # used to most
        self.recently_used_addrs = []

    # Retrieves a list of address references for use by simulator
    def get_addr_refs(self, word_addrs, num_addr_bits,
                      num_offset_bits, num_index_bits, num_tag_bits):

        return [Reference(
                word_addr, num_addr_bits, num_offset_bits,
                num_index_bits, num_tag_bits) for word_addr in word_addrs]

    # Every time we see an address, place it at the top of the
    # list of recently-seen addresses
    def mark_ref_as_last_seen(self, ref):

        # The index and tag (not the offset) uniquely identify each address
        addr_id = (ref.index, ref.tag)
        if addr_id in self.recently_used_addrs:
            self.recently_used_addrs.remove(addr_id)
        self.recently_used_addrs.append(addr_id)

    # Simulate the cache by reading the given address references into it
    def read_refs_into_cache(self, num_sets, num_blocks_per_set,
                             num_index_bits, num_words_per_block,
                             replacement_policy, refs):

        cache = Cache(
            num_sets=num_sets,
            num_index_bits=num_index_bits)
        ref_statuses = []

        for ref in refs:
            self.mark_ref_as_last_seen(ref)

            # Record if the reference is already in the cache or not
            if cache.is_hit(ref.index, ref.tag):
                # Give emphasis to hits in contrast to misses
                ref_status = ReferenceCacheStatus.hit
            else:
                ref_status = ReferenceCacheStatus.miss
                cache.set_block(
                    recently_used_addrs=self.recently_used_addrs,
                    replacement_policy=replacement_policy,
                    num_blocks_per_set=num_blocks_per_set,
                    addr_index=ref.index,
                    new_entry=ref.get_cache_entry(num_words_per_block))

            ref_statuses.append(ref_status)

        return cache, ref_statuses

    # Displays details for each address reference, including its hit/miss
    # status
    def display_addr_refs(self, refs, ref_statuses, table_width):

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
    def display_cache(self, cache, table_width):

        table = Table(
            num_cols=len(cache), width=table_width, alignment='center')
        table.title = 'Cache'

        cache_set_names = sorted(cache.keys())
        # A cache containing only one set is considered a fully associative
        # cache
        if len(cache) != 1:
            # Display set names in table header if cache is not fully
            # associative
            table.header[:] = cache_set_names

        # Add to table the cache entries for each block
        table.rows.append([])
        for index in cache_set_names:
            blocks = cache[index]
            table.rows[0].append(' '.join(
                ','.join(map(str, entry['data'])) for entry in blocks))

        print(table)

    # Run the entire cache simulation
    def run_simulation(self, num_blocks_per_set, num_words_per_block,
                       cache_size, replacement_policy, num_addr_bits,
                       word_addrs):

        num_blocks = cache_size // num_words_per_block
        num_sets = num_blocks // num_blocks_per_set

        # Ensure that the number of bits used to represent each address is
        # always large enough to represent the largest address
        num_addr_bits = max(num_addr_bits, int(math.log2(max(word_addrs))) + 1)

        num_offset_bits = int(math.log2(num_words_per_block))
        num_index_bits = int(math.log2(num_sets))
        num_tag_bits = num_addr_bits - num_index_bits - num_offset_bits

        refs = self.get_addr_refs(
            word_addrs, num_addr_bits,
            num_offset_bits, num_index_bits, num_tag_bits)

        cache, ref_statuses = self.read_refs_into_cache(
            num_sets, num_blocks_per_set, num_index_bits,
            num_words_per_block, replacement_policy, refs)

        # The character-width of all displayed tables
        # Attempt to fit table to terminal width, otherwise use default of 80
        table_width = max((shutil.get_terminal_size(
            (DEFAULT_TABLE_WIDTH, 20)).columns, DEFAULT_TABLE_WIDTH))

        print()
        self.display_addr_refs(refs, ref_statuses, table_width)
        print()
        self.display_cache(cache, table_width)
        print()
