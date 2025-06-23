#!/usr/bin/env python3

import unittest

from cachesimulator.table import Table


class TestTable(unittest.TestCase):
    def test_init_default(self):
        """
        should initialize table with required parameters and default values
        """
        table = Table(num_cols=5, width=78)
        self.assertEqual(table.num_cols, 5)
        self.assertEqual(table.width, 78)
        self.assertEqual(table.alignment, "left")
        self.assertEqual(table.title, None)
        self.assertEqual(table.header, [])
        self.assertEqual(table.rows, [])

    def test_init_optional(self):
        """should initialize table with optional parameters if supplied"""
        table = Table(num_cols=5, width=78, alignment="right", title="Cache")
        self.assertEqual(table.num_cols, 5)
        self.assertEqual(table.width, 78)
        self.assertEqual(table.alignment, "right")
        self.assertEqual(table.title, "Cache")

    def test_get_separator(self):
        """should return the correct ASCII separator string"""
        table = Table(num_cols=5, width=78)
        self.assertEqual(table.get_separator(), "-" * 78)

    def test_str_title(self):
        """should correctly display title"""
        table = Table(num_cols=5, width=12, title="Cache")
        self.assertRegex("".join(("Cache".center(12), "\n", ("-" * 12))), str(table))

    def test_str_no_title(self):
        """should not display title if not originally supplied"""
        table = Table(num_cols=5, width=12)
        self.assertEqual(str(table).strip(), "")

    def _test_str_align(self, alignment, just):
        table_width = 16
        num_cols = 2
        col_width = table_width // num_cols
        table = Table(num_cols=num_cols, width=table_width, alignment=alignment)
        table.header = ["First", "Last"]
        table.rows.append(["Bob", "Smith"])
        table.rows.append(["John", "Earl"])
        self.assertEqual(
            str(table),
            "{}{}\n{}\n{}{}\n{}{}".format(
                just("First", col_width),
                just("Last", col_width),
                "-" * table_width,
                just("Bob", col_width),
                just("Smith", col_width),
                just("John", col_width),
                just("Earl", col_width),
            ),
        )

    def test_str_align_left(self):
        """should correctly display table when left-aligned"""
        self._test_str_align(alignment="left", just=str.ljust)

    def test_str_align_center(self):
        """should correctly display table when center-aligned"""
        self._test_str_align(alignment="center", just=str.center)

    def test_str_align_right(self):
        """should correctly display table when right-aligned"""
        self._test_str_align(alignment="right", just=str.rjust)
