#!/usr/bin/env python3

import contextlib
import io
import re
from unittest.mock import patch

import cachesimulator.__main__ as main


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
def test_main():
    """main function should produce some output"""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        main.main()
    main_output = out.getvalue()
    assert re.search(r"\bWordAddr\b", main_output)
    assert re.search(r"\b0110\b", main_output)
    assert re.search(r"\bCache", main_output)
    assert re.search(r"\b01\b", main_output)
    assert re.search(r"\b8\s*6\b", main_output)
