#!/usr/bin/env python3

import contextlib
import io
import re
from collections import namedtuple
from unittest.mock import patch

import pytest

import cachesimulator.__main__ as main


def get_examples():
    with open("examples.txt", "r") as examples_file:
        examples_str = examples_file.read()
    matches = re.findall(
        r"(?<=cache-simulator )([^\n]+)\n([^#$]+)(?=\n#|\n$)", examples_str
    )
    return [
        {
            "args": args_str.split(" "),
            "output": output,
        }
        for args_str, output in matches
    ]


def normalize_output(output):
    # Strip off leading and trailing whitespace from the beginning and end
    # of the output string
    output = output.strip()
    # Strip off trailing whitespace from each line in the output string
    output = re.sub(r" +\n", "\n", output)
    return output


@pytest.mark.parametrize("example", get_examples())
def test_examples(example):
    """output should be correct for all examples in examples.txt"""

    TerminalSize = namedtuple("TerminalSize", ("columns", "lines"))

    out = io.StringIO()
    with (
        patch("sys.argv", [main.__file__, *example["args"]]),
        patch(
            "shutil.get_terminal_size",
            return_value=TerminalSize(columns=80, lines=20),
        ),
        contextlib.redirect_stdout(out),
    ):
        main.main()
    main_output = out.getvalue()
    assert normalize_output(main_output) == normalize_output(example["output"])
