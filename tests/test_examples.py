"""Tests that every sample program in examples/ runs as documented (Sprint-3 #39)."""

import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from executor import execute
from lexer import tokenize
from transpiler import transpile

EXAMPLES = os.path.join(ROOT, "examples")


def run_example(name: str):
    with open(os.path.join(EXAMPLES, name), encoding="utf-8") as fh:
        lexed = tokenize(fh.read())
    assert lexed.error is None, lexed.error
    tr = transpile(lexed.tokens)
    return execute(tr.python, tr.line_map)


class TestExamples(unittest.TestCase):
    def test_hello(self):
        ex = run_example("hello.cat")
        self.assertIsNone(ex.error)
        self.assertEqual(ex.stdout.splitlines(), ["Hello, world! 🐱", "purr purr"])

    def test_loops(self):
        ex = run_example("loops.cat")
        self.assertIsNone(ex.error)
        self.assertEqual(
            ex.stdout.splitlines(),
            ["odd or four: 1", "even: 2", "odd or four: 3", "odd or four: 4",
             "odd or four: 5", "countdown 3", "countdown 2", "countdown 1"],
        )

    def test_tricks(self):
        ex = run_example("tricks.cat")
        self.assertIsNone(ex.error)
        self.assertEqual(
            ex.stdout.splitlines(),
            ["Meow, Rem", "purr", "caught a division by zero", "always runs"],
        )

    def test_error_demo_reports_pussycat_line(self):
        ex = run_example("error_demo.cat")
        self.assertNotEqual(ex.returncode, 0)
        self.assertIn("ZeroDivisionError", ex.error)
        self.assertIn("line 4", ex.error)

    def test_every_example_is_covered(self):
        self.assertEqual(
            sorted(os.listdir(EXAMPLES)),
            ["error_demo.cat", "hello.cat", "loops.cat", "tricks.cat"],
        )


if __name__ == "__main__":
    unittest.main()
