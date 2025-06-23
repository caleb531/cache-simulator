#!/usr/bin/env python3

import contextlib
import io
import re
import unittest
from collections import namedtuple
from unittest.mock import patch

import cachesimulator.__main__ as main


class TestSimulatorExamples(unittest.TestCase):
    maxDiff = 10000

    def get_examples(self):
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

    def normalize_output(self, output):
        # Strip off leading and trailing whitespace from the beginning and end
        # of the output string
        output = output.strip()
        # Strip off trailing whitespace from each line in the output string
        output = re.sub(r" +\n", "\n", output)
        return output

    def test_examples(self):
        """output should be correct for all examples in examples.txt"""

        TerminalSize = namedtuple("TerminalSize", ("columns", "lines"))

        for example in self.get_examples():
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
            yield (
                self.assertEqual,
                self.normalize_output(main_output),
                self.normalize_output(example["output"]),
            )
