"""Tests for the keyword lookup popup. Skipped automatically when no display is available."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tkinter as tk

from constants import KEYWORD_MAP
from gui import PussyCatIDE


def _display_available() -> bool:
    try:
        tk.Tk().destroy()
        return True
    except tk.TclError:
        return False


@unittest.skipUnless(_display_available(), "no display available for tkinter")
class TestKeywordPopup(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = PussyCatIDE(self.root)
        self.root.update()  # keep root mapped: a transient popup of a withdrawn root is never shown

    def tearDown(self):
        for after_id in self.root.tk.splitlist(self.root.tk.call("after", "info")):
            self.root.after_cancel(after_id)
        self.root.destroy()

    def rows(self):
        t = self.app.keyword_table
        return [tuple(t.item(i, "values")) for i in t.get_children()]

    def test_no_popup_until_button_clicked(self):
        self.assertIsNone(getattr(self.app, "_keyword_popup", None))

    def test_button_opens_popup_with_every_mapping(self):
        self.app.keywords_btn.invoke()
        self.assertTrue(self.app._keyword_popup.winfo_exists())
        self.assertEqual(self.rows(), list(KEYWORD_MAP.items()))
        self.assertEqual(len(self.rows()), len(KEYWORD_MAP))

    def test_spot_check_known_equivalents(self):
        self.app.keywords_btn.invoke()
        rows = dict(self.rows())
        self.assertEqual(rows["meow"], "if")
        self.assertEqual(rows["nyan"], "print")
        self.assertEqual(rows["pounce"], "try")

    def test_clicking_again_reuses_same_window(self):
        self.app.keywords_btn.invoke()
        first = self.app._keyword_popup
        self.app.keywords_btn.invoke()
        self.assertIs(self.app._keyword_popup, first)
        toplevels = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]
        self.assertEqual(sum(1 for w in toplevels if w is first), 1)

    def test_popup_can_be_reopened_after_close(self):
        self.app.keywords_btn.invoke()
        first = self.app._keyword_popup
        first.destroy()
        self.app.keywords_btn.invoke()
        self.assertIsNot(self.app._keyword_popup, first)
        self.assertTrue(self.app._keyword_popup.winfo_exists())

    def test_escape_closes_popup(self):
        self.app.keywords_btn.invoke()
        popup = self.app._keyword_popup
        popup.update()
        popup.focus_force()
        popup.update()
        popup.event_generate("<Escape>")
        self.root.update()
        self.assertFalse(popup.winfo_exists())

    def test_row_activate_inserts_pussycat_keyword(self):
        self.app.keywords_btn.invoke()
        self.root.update()
        t = self.app.keyword_table
        first = t.get_children()[0]
        x, y, w, h = t.bbox(first)

        class E:  # minimal event stand-in
            pass
        e = E()
        e.y = y + h // 2
        self.app._on_keyword_row_activate(e)
        self.assertEqual(self.app.editor.get("1.0", "end-1c"), "meow ")


if __name__ == "__main__":
    unittest.main()
