"""GUI tests for PussyCat IDE (Sprint-3 tasks #26-#36, FR-10).

Run with:  python -m unittest discover tests

Requires a display (tkinter). Tests are skipped when none is available.
"""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tkinter as tk

from constants import KEYWORD_MAP
from executor import ExecutionResult
import gui
from gui import PussyCatIDE, CAT


def _display_available() -> bool:
    try:
        root = tk.Tk()
        root.destroy()
        return True
    except tk.TclError:
        return False


@unittest.skipUnless(_display_available(), "no display available for tkinter")
class GuiTestCase(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = PussyCatIDE(self.root)
        self.root.update()

    def tearDown(self):
        for after_id in self.root.tk.splitlist(self.root.tk.call("after", "info")):
            self.root.after_cancel(after_id)
        self.root.destroy()

    # helpers
    def set_source(self, text: str):
        self.app.editor.delete("1.0", tk.END)
        self.app.editor.insert("1.0", text)

    def output_text(self) -> str:
        return self.app.output.get("1.0", tk.END)

    def status_text(self) -> str:
        return self.app.status_label.cget("text").lower()


class TestWiringAndBindings(GuiTestCase):
    """#27, #28, #29"""

    def test_tab_inserts_four_spaces_and_breaks(self):
        result = self.app._on_tab(None)
        self.assertEqual(result, "break")
        self.assertEqual(self.app.editor.get("1.0", "end-1c"), "    ")

    def test_ctrl_enter_binding_exists_and_runs_pipeline(self):
        self.assertTrue(self.app.editor.bind("<Control-Return>"))
        with patch.object(self.app, "run_pipeline") as run:
            self.assertEqual(self.app._on_ctrl_enter(None), "break")
            run.assert_called_once()

    def test_tab_binding_registered(self):
        self.assertTrue(self.app.editor.bind("<Tab>"))

    def test_line_numbers_follow_editor(self):
        self.set_source("a\nb\nc")
        self.app._update_line_numbers()
        self.assertEqual(self.app.line_numbers.get("1.0", "end-1c"), "1\n2\n3")

    def test_line_numbers_state_stays_disabled(self):
        self.app._update_line_numbers()
        self.assertEqual(str(self.app.line_numbers.cget("state")), "disabled")

    def test_key_release_refreshes_line_numbers(self):
        self.set_source("x\ny")
        self.app._on_key_release(None)
        self.assertEqual(self.app.line_numbers.get("1.0", "end-1c"), "1\n2")

    def test_modified_event_refreshes_and_resets_flag(self):
        self.set_source("x\ny\nz\nw")
        self.app.editor.edit_modified(True)
        self.app._on_modified(None)
        self.assertEqual(self.app.line_numbers.get("1.0", "end-1c"), "1\n2\n3\n4")
        self.assertFalse(self.app.editor.edit_modified())


class TestKeywordBar(GuiTestCase):
    """#32"""

    def test_bar_has_all_keywords(self):
        labels = [w.cget("text").split(" ")[0] for w in self.app.keyword_bar.winfo_children()]
        self.assertEqual(len(KEYWORD_MAP), 19)
        self.assertEqual(sorted(labels), sorted(KEYWORD_MAP))

    def test_insert_keyword_adds_to_editor(self):
        self.app._insert_keyword("meow")
        self.assertEqual(self.app.editor.get("1.0", "end-1c"), "meow ")


class TestDisplayAndStatus(GuiTestCase):
    """#30, #31"""

    def test_display_sections_have_headers_and_tags(self):
        self.app.display_python("x = 1")
        self.app.display_output("hi")
        self.app.display_error("boom")
        text = self.output_text()
        for needle in ("Generated Python", "x = 1", "Output", "hi", "Error", "boom"):
            self.assertIn(needle, text)
        tag_names = set(self.app.output.tag_names())
        for tag in ("python_header", "output_header", "error_header",
                    "python_body", "output_body", "error_body"):
            self.assertIn(tag, tag_names)

    def test_error_body_is_red_and_distinct(self):
        self.app.display_error("boom")
        idx = self.app.output.search("boom", "1.0")
        self.assertIn("error_body", self.app.output.tag_names(idx))
        self.assertEqual(self.app.output.tag_cget("error_body", "foreground"), CAT["error_hdr"])
        self.assertNotEqual(
            self.app.output.tag_cget("error_body", "foreground"),
            self.app.output.tag_cget("python_body", "foreground"),
        )

    def test_output_pane_read_only_after_display(self):
        self.app.display_output("hi")
        self.assertEqual(str(self.app.output.cget("state")), "disabled")

    def test_status_states_and_colors(self):
        expected = {
            "ready": ("ready", CAT["fg_dim"]),
            "running": ("running", CAT["accent2"]),
            "ok": ("ok", CAT["success"]),
            "error": ("error", CAT["error"]),
        }
        for state, (word, color) in expected.items():
            self.app.update_status(state)
            self.assertIn(word, self.status_text())
            self.assertEqual(str(self.app.status_label.cget("fg")), color)

    def test_initial_status_ready(self):
        self.assertIn("ready", self.status_text())


class TestThemeAndSplash(GuiTestCase):
    """#33, #34"""

    def test_window_title_has_cat_emoji(self):
        self.assertIn("🐱", self.root.title())

    def test_splash_created_then_closed(self):
        self.assertTrue(self.app._splash.winfo_exists())
        self.app._close_splash()
        self.assertFalse(self.app._splash.winfo_exists())

    def test_main_window_hidden_while_splash_is_showing(self):
        self.assertEqual(self.root.state(), "withdrawn")
        self.assertTrue(self.app._splash.winfo_exists())

    def test_main_window_shown_when_splash_finishes(self):
        self.app._close_splash()
        self.root.update()
        self.assertEqual(self.root.state(), "normal")

    def test_timer_closes_splash_and_shows_main_window(self):
        self.root.update()
        end = gui.SPLASH_TOTAL_MS + 300
        self.root.after(end, self.root.quit)
        self.root.mainloop()
        self.assertFalse(self.app._splash.winfo_exists())
        self.assertEqual(self.root.state(), "normal")

    def test_splash_total_is_about_two_seconds(self):
        self.assertTrue(2000 <= gui.SPLASH_TOTAL_MS <= 2500)


class TestRunPipeline(GuiTestCase):
    """#26, #31"""

    def test_success_run_shows_python_and_output(self):
        self.set_source('nyan("hello cat")')
        self.app.run_pipeline()
        text = self.output_text()
        self.assertIn('print("hello cat")', text)
        self.assertIn("hello cat", text)
        self.assertNotIn("Error", text)
        self.assertIn("ok", self.status_text())

    def test_lexer_error_shown_and_no_python_displayed(self):
        self.set_source("x = 1 $ 2")
        self.app.run_pipeline()
        text = self.output_text()
        self.assertIn("Lexer Error", text)
        self.assertIn("Line 1", text)
        self.assertNotIn("Generated Python", text)
        self.assertIn("error", self.status_text())

    def test_runtime_error_is_remapped_to_pussycat_line(self):
        self.set_source('x = 1\n\nnyan(1 / 0)')
        self.app.run_pipeline()
        text = self.output_text()
        self.assertIn("ZeroDivisionError", text)
        self.assertIn("line 3", text)
        self.assertIn("error", self.status_text())

    def test_timeout_reported_as_error(self):
        timed_out = ExecutionResult(
            stdout="", stderr="", error="[Executor Error] Script timed out after 10s",
            timed_out=True, returncode=-1,
        )
        self.set_source("chase purr:\n    pass")
        with patch("gui.execute", return_value=timed_out):
            self.app.run_pipeline()
        self.assertIn("timed out", self.output_text())
        self.assertIn("error", self.status_text())

    def test_empty_source_does_not_crash(self):
        self.set_source("")
        self.app.run_pipeline()
        self.assertNotIn("Error", self.output_text())

    def test_run_button_reenabled_after_run(self):
        for src in ('nyan("a")', "x = 1 $ 2", "nyan(1/0)"):
            self.set_source(src)
            self.app.run_pipeline()
            self.assertEqual(str(self.app.run_btn.cget("state")), "normal", src)

    def test_output_cleared_between_runs(self):
        self.set_source('nyan("first")')
        self.app.run_pipeline()
        self.set_source('nyan("second")')
        self.app.run_pipeline()
        text = self.output_text()
        self.assertIn("second", text)
        self.assertNotIn("first", text)

    def test_animations_do_not_raise_on_success_and_error(self):
        self.app._animate_success()
        self.app._animate_error()
        self.root.update()


class TestClear(GuiTestCase):
    """FR-10 / FR-15"""

    def test_clear_button_exists_and_wired(self):
        self.assertEqual(self.app.clear_btn.cget("text").strip()[-5:], "Clear")
        self.set_source('nyan("x")')
        self.app.run_pipeline()
        self.app.clear_btn.invoke()
        self.assertEqual(self.app.editor.get("1.0", "end-1c"), "")
        self.assertEqual(self.output_text().strip(), "")
        self.assertIn("ready", self.status_text())
        self.assertEqual(self.app.line_numbers.get("1.0", "end-1c"), "1")


if __name__ == "__main__":
    unittest.main()
