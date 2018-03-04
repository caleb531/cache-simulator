#!/usr/bin/env python3

import copy

from cachesimulator.bin_addr import BinaryAddress
from cachesimulator.word_addr import WordAddress


class Cache(object):

    # Initializes the reference cache with a fixed number of sets
    def __init__(self, cache=None, num_sets=None, num_index_bits=None):

        if cache is not None:
            self.map = cache
        else:
            self.map = {}
            for i in range(num_sets):
                index = BinaryAddress(
                    word_addr=WordAddress(i), num_addr_bits=num_index_bits)
                self.map[index] = []

    def __eq__(self, other):
        return self.map == other

    def __len__(self):
        return len(self.map)

    def __getitem__(self, key):
        return self.map[key]

    def __contains__(self, value):
        return value in self.map

    def __deepcopy__(self, memodict={}):
        return copy.deepcopy(self.map)

    def keys(self):
        return self.map.keys()

    # Returns True if a block at the given index and tag exists in the cache,
    # indicating a hit; returns False otherwise, indicating a miss
    def is_hit(self, addr_index, addr_tag):

        # Ensure that indexless fully associative caches are accessed correctly
        if addr_index is None:
            blocks = self['0']
        elif addr_index in self:
            blocks = self[addr_index]
        else:
            return False

        for block in blocks:
            if block['tag'] == addr_tag:
                return True

        return False

    # Adds the given entry to the cache at the given index
    def set_block(self, recently_used_addrs, replacement_policy,
                  num_blocks_per_set, addr_index, new_entry):

        # Place all cache entries in a single set if cache is fully associative
        if addr_index is None:
            blocks = self['0']
        else:
            blocks = self[addr_index]
        # Replace MRU or LRU entry if number of blocks in set exceeds the limit
        if len(blocks) == num_blocks_per_set:
            # Iterate through the recently-used entries in reverse order for
            # MRU
            if replacement_policy == 'mru':
                recently_used_addrs = reversed(recently_used_addrs)
            # Replace the first matching entry with the entry to add
            for recent_index, recent_tag in recently_used_addrs:
                for i, block in enumerate(blocks):
                    if (recent_index == addr_index and
                            block['tag'] == recent_tag):
                        blocks[i] = new_entry
                        return
        else:
            blocks.append(new_entry)
