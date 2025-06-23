#!/usr/bin/env python3

import contextlib
import io
import unittest
from unittest.mock import patch

import cachesimulator.__main__ as main


class TestSimulatorMain(unittest.TestCase):
    @patch(
        "sys.argv",
        [
            main.__file__,
            "--cache-size",
            "4",
            "--num-blocks-per-set",
            "1",
            "--num-words-per-block",
            "1",
            "--word-addrs",
            "0",
            "8",
            "0",
            "6",
            "8",
        ],
    )
    def test_main(self):
        """main function should produce some output"""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main.main()
        main_output = out.getvalue()
        self.assertRegex(main_output, r"\bWordAddr\b")
        self.assertRegex(main_output, r"\b0110\b")
        self.assertRegex(main_output, r"\bCache")
        self.assertRegex(main_output, r"\b01\b")
        self.assertRegex(main_output, r"\b8\s*6\b")
