#!/usr/bin/env python3

import contextlib
import io
import unittest

from cachesimulator.simulator import Simulator

WORD_ADDRS = [43, 14, 253, 186]
TABLE_WIDTH = 80


class TestSimulatorDisplay(unittest.TestCase):
    def apply_cache_statuses_to_refs(self, cache_statuses, refs):
        for cache_status, ref in zip(cache_statuses, refs):
            ref.cache_status = cache_status

    def test_display_addr_refs(self):
        """should display table of address references"""
        sim = Simulator()
        refs = sim.get_addr_refs(
            word_addrs=WORD_ADDRS,
            num_addr_bits=8,
            num_tag_bits=5,
            num_index_bits=2,
            num_offset_bits=1,
        )
        self.apply_cache_statuses_to_refs(["miss", "miss", "HIT", "miss"], refs)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_addr_refs(refs, table_width=TABLE_WIDTH)
        table_output = out.getvalue()
        num_cols = 6
        col_width = TABLE_WIDTH // num_cols
        self.assertRegex(
            table_output,
            r"{}\s*{}\s*{}\s*{}\s*{}\s*{}\n{}".format(
                "WordAddr".rjust(col_width),
                "BinAddr".rjust(col_width),
                "Tag".rjust(col_width),
                "Index".rjust(col_width),
                "Offset".rjust(col_width),
                "Hit/Miss".rjust(col_width),
                ("-" * TABLE_WIDTH),
            ),
        )
        self.assertRegex(
            table_output,
            r"{}\s*{}\s*{}\s*{}\s*{}\s*{}".format(
                "253".rjust(col_width),
                "1111 1101".rjust(col_width),
                "11111".rjust(col_width),
                "10".rjust(col_width),
                "1".rjust(col_width),
                "HIT".rjust(col_width),
            ),
        )

    def test_display_addr_refs_no_tag(self):
        """should display n/a for tag when there are no tag bits"""
        sim = Simulator()
        refs = sim.get_addr_refs(
            word_addrs=WORD_ADDRS,
            num_addr_bits=2,
            num_tag_bits=0,
            num_index_bits=1,
            num_offset_bits=1,
        )
        self.apply_cache_statuses_to_refs(["miss", "miss", "miss", "miss"], refs)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_addr_refs(refs, table_width=TABLE_WIDTH)
        table_output = out.getvalue()
        self.assertRegex(
            table_output, r"\s*{}\s*{}\s*{}".format(r"\d\d", r"n/a", r"\d")
        )

    def test_display_addr_refs_no_index(self):
        """should display n/a for index when there are no index bits"""
        sim = Simulator()
        refs = sim.get_addr_refs(
            word_addrs=WORD_ADDRS,
            num_addr_bits=8,
            num_tag_bits=7,
            num_index_bits=0,
            num_offset_bits=1,
        )
        self.apply_cache_statuses_to_refs(["miss", "miss", "miss", "miss"], refs)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_addr_refs(refs, table_width=TABLE_WIDTH)
        table_output = out.getvalue()
        self.assertRegex(table_output, r"\s*{}\s*{}\s*{}".format(r"n/a", r"\d", "miss"))

    def test_display_addr_refs_no_offset(self):
        """should display n/a for offset when there are no offset bits"""
        sim = Simulator()
        refs = sim.get_addr_refs(
            word_addrs=WORD_ADDRS,
            num_addr_bits=8,
            num_tag_bits=4,
            num_index_bits=4,
            num_offset_bits=0,
        )
        self.apply_cache_statuses_to_refs(["miss"] * 12, refs)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_addr_refs(refs, table_width=TABLE_WIDTH)
        table_output = out.getvalue()
        self.assertRegex(
            table_output, r"\s*{}\s*{}\s*{}".format(r"\d\d", r"n/a", "miss")
        )

    def test_display_cache(self):
        """should display table for direct-mapped/set associative cache"""
        sim = Simulator()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_cache(
                {
                    "000": [{"tag": "0101", "data": [88, 89]}],
                    "001": [
                        {"tag": "0000", "data": [2, 3]},
                        {"tag": "0010", "data": [42, 43]},
                    ],
                },
                table_width=TABLE_WIDTH,
            )
        table_output = out.getvalue()
        num_cols = 2
        col_width = TABLE_WIDTH // num_cols
        self.assertRegex(
            table_output,
            "{}\n{}".format("Cache".center(TABLE_WIDTH), ("-" * TABLE_WIDTH)),
        )
        self.assertEqual(table_output.count("-"), TABLE_WIDTH * 2)
        self.assertRegex(
            table_output,
            r"{}{}".format("000".center(col_width), "001".center(col_width)),
        )
        self.assertRegex(
            table_output,
            r"{}{}".format("88,89".center(col_width), "2,3 42,43".center(col_width)),
        )

    def test_display_cache_fully_assoc(self):
        """should correctly display table for fully associative cache"""
        sim = Simulator()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sim.display_cache(
                {
                    "0": [
                        {"tag": "0000001", "data": [2, 3]},
                        {"tag": "1111110", "data": [252, 253]},
                    ]
                },
                table_width=TABLE_WIDTH,
            )
        table_output = out.getvalue()
        self.assertRegex(
            table_output,
            "{}\n{}".format("Cache".center(TABLE_WIDTH), ("-" * TABLE_WIDTH)),
        )
        self.assertEqual(table_output.count("-"), TABLE_WIDTH)
        self.assertRegex(table_output, "2,3 252,253".center(TABLE_WIDTH))
