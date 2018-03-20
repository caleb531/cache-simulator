#!/usr/bin/env python3


class BinaryAddress(str):

    # Retrieves the binary address of a certain length for a base-10 word
    # address; we must define __new__ instead of __init__ because the class we
    # are inheriting from (str) is an immutable data type
    def __new__(cls, bin_addr=None, word_addr=None, num_addr_bits=0):

        if word_addr is not None:
            return super().__new__(
                cls, bin(word_addr)[2:].zfill(num_addr_bits))
        else:
            return super().__new__(cls, bin_addr)

    @classmethod
    def prettify(cls, bin_addr, min_bits_per_group):

        mid = len(bin_addr) // 2

        if mid < min_bits_per_group:
            # Return binary string immediately if bisecting the binary string
            # produces a substring which is too short
            return bin_addr
        else:
            # Otherwise, bisect binary string and separate halves with a space
            left = cls.prettify(bin_addr[:mid], min_bits_per_group)
            right = cls.prettify(bin_addr[mid:], min_bits_per_group)
            return ' '.join((left, right))

    # Retrieves the tag used to distinguish cache entries with the same index
    def get_tag(self, num_tag_bits):

        end = num_tag_bits
        tag = self[:end]
        if len(tag) != 0:
            return tag
        else:
            return None

    # Retrieves the index used to group blocks in the cache
    def get_index(self, num_offset_bits, num_index_bits):

        start = len(self) - num_offset_bits - num_index_bits
        end = len(self) - num_offset_bits
        index = self[start:end]
        if len(index) != 0:
            return index
        else:
            return None

    # Retrieves the word offset used to select a word in the data pointed to by
    # the given binary address
    def get_offset(self, num_offset_bits):

        start = len(self) - num_offset_bits
        offset = self[start:]
        if len(offset) != 0:
            return offset
        else:
            return None
