#!/usr/bin/env python3


class WordAddress(int):

    def __init__(self, value):
        self.value = value

    # Retrieves all consecutive words for the given word address (including
    # itself)
    def get_consecutive_words(self, num_words_per_block):

        offset = self.value % num_words_per_block
        return [(self.value - offset + i) for i in range(num_words_per_block)]
