"""End-to-end and edge-case tests (Sprint-3 tasks #37, #38).

Exercises tokenize -> transpile -> execute together, without the GUI.

Run with:  python -m unittest discover tests
"""

import os
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import executor
from executor import execute
from lexer import tokenize
from transpiler import transpile


def run_pussycat(source: str):
    """Full pipeline. Returns (lexer_error, TranspileResult | None, ExecutionResult | None)."""
    lexed = tokenize(source)
    if lexed.error:
        return lexed.error, None, None
    transpiled = transpile(lexed.tokens)
    return None, transpiled, execute(transpiled.python, transpiled.line_map)


class TestEndToEnd(unittest.TestCase):
    """#37"""

    def test_hello_world(self):
        err, tr, ex = run_pussycat('nyan("Hello, cat!")')
        self.assertIsNone(err)
        self.assertEqual(tr.python, 'print("Hello, cat!")')
        self.assertEqual(ex.stdout, "Hello, cat!")
        self.assertIsNone(ex.error)
        self.assertEqual(ex.returncode, 0)

    def test_control_flow_and_loops(self):
        src = (
            "total = 0\n"
            "paws i in range(4):\n"
            "    meow i % 2 == 0:\n"
            "        total = total + i\n"
            "    mew:\n"
            "        total = total + 10\n"
            "nyan(total)\n"
        )
        err, _, ex = run_pussycat(src)
        self.assertIsNone(err)
        self.assertEqual(ex.stdout, "22")

    def test_functions_and_logic_keywords(self):
        src = (
            "trick check(a, b):\n"
            "    furball a whiskers scratch b\n"
            "nyan(check(purr, hiss))\n"
            "nyan(box)\n"
        )
        _, _, ex = run_pussycat(src)
        self.assertEqual(ex.stdout.splitlines(), ["True", "None"])

    def test_class_and_try_except_finally(self):
        src = (
            "breed Cat:\n"
            "    trick speak(self):\n"
            '        furball "meow"\n'
            "pounce:\n"
            "    nyan(Cat().speak())\n"
            "    nyan(1 / 0)\n"
            "miss ZeroDivisionError:\n"
            '    nyan("caught")\n'
            "nap:\n"
            '    nyan("done")\n'
        )
        _, _, ex = run_pussycat(src)
        self.assertIsNone(ex.error)
        self.assertEqual(ex.stdout.splitlines(), ["meow", "caught", "done"])

    def test_imports(self):
        src = "adopt math\nshelter math adopt sqrt\nnyan(sqrt(16))\n"
        _, _, ex = run_pussycat(src)
        self.assertEqual(ex.stdout, "4.0")

    def test_comments_and_blank_lines_survive(self):
        src = '# a comment\n\nnyan("x")  # trailing\n'
        err, _, ex = run_pussycat(src)
        self.assertIsNone(err)
        self.assertEqual(ex.stdout, "x")

    def test_keyword_inside_string_is_not_substituted(self):
        _, _, ex = run_pussycat('nyan("meow purr")')
        self.assertEqual(ex.stdout, "meow purr")

    def test_lexer_error_stops_pipeline_before_execution(self):
        with patch("subprocess.run") as run:
            err, tr, ex = run_pussycat('nyan("ok")\nx = 1 $ 2')
        self.assertIn("Line 2", err)
        self.assertIsNone(tr)
        self.assertIsNone(ex)
        run.assert_not_called()

    def test_runtime_error_line_is_remapped_to_pussycat_source(self):
        src = "x = 1\n\n\nnyan(x / 0)\n"
        _, tr, ex = run_pussycat(src)
        self.assertNotEqual(ex.returncode, 0)
        self.assertIn("ZeroDivisionError", ex.error)
        self.assertIn("line 4", ex.error)

    def test_runtime_error_in_multiline_function_is_remapped(self):
        src = "trick boom():\n    furball 1 / 0\n\n\nboom()\n"
        _, _, ex = run_pussycat(src)
        self.assertIn("line 2", ex.error)  # inside boom
        self.assertIn("line 5", ex.error)  # call site

    def test_python_syntax_error_is_reported_not_raised(self):
        _, _, ex = run_pussycat("meow purr\n    nyan(1)\n")
        self.assertIsNotNone(ex.error)
        self.assertIn("SyntaxError", ex.error)
        self.assertNotEqual(ex.returncode, 0)

    def test_stderr_never_leaks_temp_path(self):
        _, _, ex = run_pussycat("nyan(1/0)")
        self.assertNotIn(".py\"", ex.stderr.replace("<pussycat>", ""))
        self.assertIn("<pussycat>", ex.stderr)


class TestEdgeCases(unittest.TestCase):
    """#38"""

    def test_empty_input(self):
        err, tr, ex = run_pussycat("")
        self.assertIsNone(err)
        self.assertEqual(tr.python, "")
        self.assertEqual(ex.stdout, "")
        self.assertIsNone(ex.error)
        self.assertFalse(ex.timed_out)

    def test_whitespace_and_comment_only_input(self):
        for src in ("   \n\n  ", "# nothing here"):
            err, _, ex = run_pussycat(src)
            self.assertIsNone(err, src)
            self.assertIsNone(ex.error, src)

    def test_infinite_loop_times_out_and_is_killed(self):
        with patch.object(executor, "EXECUTION_TIMEOUT", 1):
            _, _, ex = run_pussycat("chase purr:\n    pass\n")
        self.assertTrue(ex.timed_out)
        self.assertIn("timed out", ex.error)
        self.assertEqual(ex.returncode, -1)

    def test_temp_file_removed_after_timeout(self):
        created = []
        real = executor.tempfile.NamedTemporaryFile

        def spy(*a, **kw):
            f = real(*a, **kw)
            created.append(f.name)
            return f

        with patch.object(executor.tempfile, "NamedTemporaryFile", spy), \
                patch.object(executor, "EXECUTION_TIMEOUT", 1):
            execute("while True:\n    pass\n", {})
        self.assertEqual(len(created), 1)
        self.assertFalse(os.path.exists(created[0]))

    def test_interpreter_not_found_returns_error_instead_of_raising(self):
        with patch("subprocess.run", side_effect=FileNotFoundError("python3")):
            ex = execute("print(1)", {1: 1})
        self.assertIsNotNone(ex.error)
        self.assertIn("Executor Error", ex.error)
        self.assertEqual(ex.returncode, -1)
        self.assertFalse(ex.timed_out)

    def test_uses_the_running_interpreter(self):
        with patch("subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, "", "")
            execute("print(1)", {1: 1})
        self.assertEqual(run.call_args.args[0][0], sys.executable)

    def test_unicode_output_round_trips(self):
        _, _, ex = run_pussycat('nyan("😺 purr")')
        self.assertEqual(ex.stdout, "😺 purr")

    def test_large_input_transpiles_quickly(self):
        import time
        src = "\n".join(f"x{i} = {i}" for i in range(200))
        start = time.perf_counter()
        tokens = tokenize(src).tokens
        transpile(tokens)
        self.assertLess(time.perf_counter() - start, 0.1)  # PRD NFR: <100ms for 200 lines

    def test_unterminated_string_is_a_lexer_error(self):
        err, tr, ex = run_pussycat('nyan("abc')
        self.assertIn("Lexer Error", err)
        self.assertIsNone(ex)


if __name__ == "__main__":
    unittest.main()
