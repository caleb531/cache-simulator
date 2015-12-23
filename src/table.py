#!/usr/bin/env python3


# A class for displaying ASCII tables
class Table(object):

    # Map alignment keywords to their respective string format specifiers
    alignment_symbols = {
        'left': '<',
        'center': '^',
        'right': '>'
    }

    def __init__(self, num_cols, width, alignment='left', title=None):

        self.title = title
        self.width = width
        self.num_cols = num_cols
        self.alignment = alignment
        self.header = []
        self.rows = []

    # Retrieves a separator used to separate rows
    def get_separator(self):

        return '-' * self.width

    def __str__(self):

        table_strs = []

        if self.title:
            table_strs.append(self.title.center(self.width))
            table_strs.append(self.get_separator())

        # Format string used to align columns
        cell_format_str = ''.join('{{:{}{}}}'.format(
            Table.alignment_symbols[self.alignment],
            self.width // self.num_cols) for i in range(self.num_cols))

        if self.header:
            table_strs.append(cell_format_str.format(*self.header))
            table_strs.append(self.get_separator())

        for row in self.rows:
            table_strs.append(cell_format_str.format(*row))

        return '\n'.join(table_strs)
