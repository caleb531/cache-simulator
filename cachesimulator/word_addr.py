#!/usr/bin/env python3


class WordAddress(int):

    # Retrieves all consecutive words for the given word address (including
    # itself)
    def get_consecutive_words(self, num_words_per_block):

        offset = self % num_words_per_block
        return [(self - offset + i) for i in range(num_words_per_block)]
