#!/usr/bin/env python3

import contextlib
import io
import re
import shlex
from collections import namedtuple
from pathlib import Path
from unittest.mock import patch

import pytest

import cachesimulator.__main__ as main


def create_example(command, output_lines):
    args = shlex.split(command)
    if args and args[0] == "cache-simulator":
        args = args[1:]
    return {"args": args, "output": "\n".join(output_lines).rstrip()}


def get_examples():
    examples = []
    lines = Path("examples.sh").read_text().splitlines(keepends=True)

    current_command = None
    output_lines = []

    for raw_line in lines:
        line = raw_line.rstrip("\n")

        if line.startswith("cache-simulator "):
            if current_command and output_lines:
                examples.append(create_example(current_command, output_lines))
            current_command = line
            output_lines = []
            continue

        if current_command is None:
            continue

        if not line:
            if current_command and output_lines:
                examples.append(create_example(current_command, output_lines))
                current_command = None
                output_lines = []
            continue

        if line.startswith("#"):
            comment = line[1:]
            if comment.startswith(" "):
                comment = comment[1:]
            output_lines.append(comment)
            continue

        # Non-comment content signals the end of the current example block.
        if current_command and output_lines:
            examples.append(create_example(current_command, output_lines))
        current_command = None
        output_lines = []
    if current_command and output_lines:
        examples.append(create_example(current_command, output_lines))
    return examples


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
            return_value=TerminalSize(columns=78, lines=20),
        ),
        contextlib.redirect_stdout(out),
    ):
        main.main()
    main_output = out.getvalue()
    assert normalize_output(main_output) == normalize_output(example["output"])
