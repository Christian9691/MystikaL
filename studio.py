import re
import threading
import tkinter as tk
from tkinter import ttk

from spellbook import GRIMOIRE, SPELLBOOK
from scanner import scan
from weaver import weave
from caster import cast

THEME = {
    "night":   "#14101f",
    "panel":   "#1c1630",
    "panel2":  "#261d42",
    "gutter":  "#171128",
    "ink":     "#ece6ff",
    "dim":     "#8b7fb0",
    "gold":    "#f2c14e",
    "rose":    "#ff7aa8",
    "mint":    "#6ee7b7",
    "sky":     "#7cc4ff",
    "danger":  "#ff5d73",
    "select":  "#43326e",
}

MONO = ("Consolas", 12)
MONO_SM = ("Consolas", 10)
MONO_B = ("Consolas", 11, "bold")

SAMPLE = '''# Abisala! Isang maliit na spell sa Mystika
brilyante sumpa(hanggang):
    kabuuan = 0
    sapiro n hathoria range(1, hanggang + 1):
        abisala n % 2 == 0:
            kabuuan = kabuuan + n
        ashti:
            tahimik
    bumalik kabuuan

hayag("Abisala, eshma!")
hayag("Kabuuan ng even hanggang 10:", sumpa(10))
'''

SPLASH_LINES = [
    "✦  Abisala, eshma!  ✦",
    "Binubuksan ang Spellbook…",
    "Ginigising ang mga Brilyante…",
    "Handa na ang mahika  ✦",
]

_WORD = re.compile(r"[^\W\d]\w*")
_TEXT = re.compile(r"\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'")
_NOTE = re.compile(r"#[^\n]*")
_NUMBER = re.compile(r"\b\d+(?:\.\d+)?\b")


class MystikaStudio:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._gutter_lines = 0
        self._refresh_job = None
        self._hints = {w: h for es in GRIMOIRE.values() for w, _p, h in es}

        root.withdraw()
        root.title("✦ Mystika Studio ✦")
        root.geometry("1280x780")
        root.minsize(980, 560)
        root.configure(bg=THEME["night"])

        self._configure_ttk()
        self._build_header()
        self._build_footer()
        self._build_body()
        self._bind_keys()

        self.editor.insert("1.0", SAMPLE)
        self._refresh_editor_visuals()
        self.editor.edit_modified(False)
        self._show_splash()

    # ── styling ──────────────────────────────────────────────────────────────
    def _configure_ttk(self):
        t = THEME
        s = ttk.Style(self.root)
        s.theme_use("clam")
        s.configure("Spell.Treeview", background=t["panel"], fieldbackground=t["panel"],
                    foreground=t["ink"], rowheight=24, borderwidth=0, font=MONO_SM)
        s.layout("Spell.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        s.map("Spell.Treeview", background=[("selected", t["select"])],
              foreground=[("selected", t["gold"])])
        s.configure("TNotebook", background=t["night"], borderwidth=0)
        s.configure("TNotebook.Tab", background=t["panel"], foreground=t["dim"],
                    padding=(16, 6), font=MONO_SM, borderwidth=0)
        s.map("TNotebook.Tab", background=[("selected", t["panel2"])],
              foreground=[("selected", t["gold"])])
        s.configure("Vertical.TScrollbar", background=t["panel2"], troughcolor=t["panel"],
                    bordercolor=t["panel"], arrowcolor=t["dim"])

    def _button(self, parent, text, command, primary=False):
        t = THEME
        return tk.Button(
            parent, text=text, command=command, relief=tk.FLAT, bd=0, cursor="hand2",
            font=MONO_B, padx=14, pady=4,
            bg=t["gold"] if primary else t["panel"],
            fg=t["night"] if primary else t["gold"],
            activebackground=t["rose"], activeforeground=t["night"],
        )

    # ── layout ───────────────────────────────────────────────────────────────
    def _build_header(self):
        t = THEME
        bar = tk.Frame(self.root, bg=t["night"])
        bar.pack(side=tk.TOP, fill=tk.X, pady=(8, 4))
        tk.Label(bar, text="✦  M Y S T I K A  ✦", bg=t["night"], fg=t["gold"],
                 font=("Georgia", 20, "bold")).pack()
        tk.Label(bar, text="isang wikang pang-mahika  ·  isulat ang spell, ihayag ang resulta",
                 bg=t["night"], fg=t["dim"], font=MONO_SM).pack()

    def _build_footer(self):
        t = THEME
        bar = tk.Frame(self.root, bg=t["panel2"], height=44)
        bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.cast_btn = self._button(bar, "✦  Cast Spell", self.cast_spell, primary=True)
        self.cast_btn.pack(side=tk.LEFT, padx=10, pady=6)
        self._button(bar, "📜  Sample", self.load_sample).pack(side=tk.LEFT, padx=(0, 8), pady=6)
        self._button(bar, "🗑  Clear", self.clear_all).pack(side=tk.LEFT, padx=(0, 8), pady=6)
        tk.Label(bar, text="Ctrl+Enter = cast  ·  Tab = 4 spaces  ·  double-click a spell to insert",
                 bg=t["panel2"], fg=t["dim"], font=MONO_SM).pack(side=tk.LEFT, padx=8)

        self.status = tk.Label(bar, text="✦ ready", bg=t["panel2"], fg=t["dim"], font=MONO_B)
        self.status.pack(side=tk.RIGHT, padx=12)

    def _build_body(self):
        t = THEME
        panes = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5,
                               bg=t["night"], bd=0, sashrelief=tk.FLAT)
        panes.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        panes.add(self._build_spell_panel(panes), minsize=210, width=250)
        panes.add(self._build_editor_panel(panes), minsize=380, width=560)
        panes.add(self._build_output_panel(panes), minsize=320)

    def _build_spell_panel(self, parent):
        t = THEME
        frame = tk.Frame(parent, bg=t["panel"])
        tk.Label(frame, text="📜 SPELLBOOK", bg=t["panel"], fg=t["rose"],
                 font=MONO_B).pack(anchor="w", padx=10, pady=(8, 4))

        self.spell_tree = ttk.Treeview(frame, show="tree", style="Spell.Treeview",
                                       selectmode="browse")
        for category, entries in GRIMOIRE.items():
            parent_row = self.spell_tree.insert("", "end", text=category, open=True)
            for word, py, _hint in entries:
                self.spell_tree.insert(parent_row, "end", text=f"{word}  →  {py}", values=(word,))
        self.spell_tree.pack(fill=tk.BOTH, expand=True, padx=6)
        self.spell_tree.bind("<Double-1>", self._on_spell_pick)
        self.spell_tree.bind("<<TreeviewSelect>>", self._on_spell_select)

        self.hint = tk.Label(frame, text="Pumili ng spell para makita ang kahulugan.",
                             bg=t["panel"], fg=t["dim"], font=MONO_SM,
                             wraplength=220, justify="left", anchor="w")
        self.hint.pack(fill=tk.X, padx=10, pady=8)
        return frame

    def _build_editor_panel(self, parent):
        t = THEME
        frame = tk.Frame(parent, bg=t["panel"])
        tk.Label(frame, text="✎ GRIMOIRE PAGE", bg=t["panel"], fg=t["rose"],
                 font=MONO_B).pack(anchor="w", padx=10, pady=(8, 4))

        body = tk.Frame(frame, bg=t["panel"])
        body.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        self.gutter = tk.Text(body, width=4, state="disabled", takefocus=0, bd=0,
                              highlightthickness=0, bg=t["gutter"], fg=t["dim"], font=MONO)
        self.gutter.tag_configure("num", justify="right")
        self.gutter.pack(side=tk.LEFT, fill=tk.Y)

        self.scrollbar = ttk.Scrollbar(body, orient="vertical", command=self._scroll_both)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.editor = tk.Text(
            body, undo=True, wrap=tk.NONE, bd=0, font=MONO, bg=t["night"], fg=t["ink"],
            insertbackground=t["gold"], selectbackground=t["select"], selectforeground=t["ink"],
            highlightthickness=1, highlightcolor=t["rose"], highlightbackground=t["panel"],
            yscrollcommand=self._on_editor_yview, padx=6, pady=4,
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.editor.tag_configure("spell", foreground=t["gold"], font=("Consolas", 12, "bold"))
        self.editor.tag_configure("number", foreground=t["sky"])
        self.editor.tag_configure("text", foreground=t["mint"])
        self.editor.tag_configure("note", foreground=t["dim"], font=("Consolas", 12, "italic"))
        return frame

    def _build_output_panel(self, parent):
        t = THEME
        book = ttk.Notebook(parent)
        self.result = self._readonly_text(book)
        self.pyview = self._readonly_text(book)
        book.add(self.result[0], text="✨ Result")
        book.add(self.pyview[0], text="🐍 Python Form")

        for widget in (self.result[1], self.pyview[1]):
            widget.tag_configure("title_ok", foreground=t["mint"], font=MONO_B)
            widget.tag_configure("title_bad", foreground=t["danger"], font=MONO_B)
            widget.tag_configure("body", foreground=t["ink"])
            widget.tag_configure("body_bad", foreground=t["danger"])
            widget.tag_configure("py", foreground=t["sky"])
        return book

    def _readonly_text(self, parent):
        t = THEME
        frame = tk.Frame(parent, bg=t["panel"])
        text = tk.Text(frame, state="disabled", wrap=tk.WORD, bd=0, highlightthickness=0,
                       font=MONO, bg=t["night"], fg=t["ink"], padx=10, pady=8,
                       selectbackground=t["select"])
        bar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=bar.set)
        bar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True, padx=(6, 0), pady=6)
        return frame, text

    # ── editor behaviour ─────────────────────────────────────────────────────
    def _bind_keys(self):
        self.editor.bind("<Tab>", self._on_tab)
        self.editor.bind("<Shift-Tab>", self._on_shift_tab)
        self.editor.bind("<Return>", self._on_return)
        self.editor.bind("<Control-Return>", lambda e: (self.cast_spell(), "break")[1])
        self.editor.bind("<<Modified>>", self._on_modified)

    def _scroll_both(self, *args):
        self.editor.yview(*args)
        self.gutter.yview(*args)

    def _on_editor_yview(self, first, last):
        self.scrollbar.set(first, last)
        self.gutter.yview_moveto(first)

    def _on_modified(self, _event):
        if self.editor.edit_modified():
            self._schedule_refresh()
            self.editor.edit_modified(False)

    def _schedule_refresh(self):
        if self._refresh_job is not None:
            self.root.after_cancel(self._refresh_job)
        self._refresh_job = self.root.after(120, self._refresh_editor_visuals)

    def _refresh_editor_visuals(self):
        self._refresh_job = None
        self._refresh_gutter()
        self._highlight()

    def _refresh_gutter(self):
        total = int(self.editor.index("end-1c").split(".")[0])
        if total != self._gutter_lines:
            self._gutter_lines = total
            self.gutter.config(state="normal")
            self.gutter.delete("1.0", tk.END)
            self.gutter.insert("1.0", "\n".join(str(n) for n in range(1, total + 1)), "num")
            self.gutter.config(state="disabled")
        self.gutter.yview_moveto(self.editor.yview()[0])

    def _highlight(self):
        text = self.editor.get("1.0", "end-1c")
        for tag in ("spell", "number", "text", "note"):
            self.editor.tag_remove(tag, "1.0", tk.END)

        def mark(tag, match):
            self.editor.tag_add(tag, f"1.0+{match.start()}c", f"1.0+{match.end()}c")

        for m in _WORD.finditer(text):
            if m.group() in SPELLBOOK:
                mark("spell", m)
        for m in _NUMBER.finditer(text):
            mark("number", m)
        for m in _TEXT.finditer(text):
            mark("text", m)
        for m in _NOTE.finditer(text):
            mark("note", m)
        self.editor.tag_raise("text")
        self.editor.tag_raise("note")

    def _on_tab(self, _event):
        self.editor.insert(tk.INSERT, "    ")
        return "break"

    def _on_shift_tab(self, _event):
        line_start = self.editor.index("insert linestart")
        head = self.editor.get(line_start, f"{line_start}+4c")
        remove = len(head) - len(head.lstrip(" "))
        if remove:
            self.editor.delete(line_start, f"{line_start}+{remove}c")
        return "break"

    def _on_return(self, _event):
        before = self.editor.get("insert linestart", "insert")
        indent = re.match(r"[ \t]*", before).group()
        if before.rstrip().endswith(":"):
            indent += "    "
        self.editor.insert(tk.INSERT, "\n" + indent)
        self.editor.see(tk.INSERT)
        return "break"

    # ── spellbook panel ──────────────────────────────────────────────────────
    def _on_spell_select(self, _event):
        row = self.spell_tree.focus()
        values = self.spell_tree.item(row, "values") if row else ()
        if values:
            word = str(values[0])
            self.hint.config(text=f"{word}: {self._hints.get(word, '')}", fg=THEME["gold"])

    def _on_spell_pick(self, event):
        row = self.spell_tree.identify_row(event.y)
        values = self.spell_tree.item(row, "values") if row else ()
        if values:
            self.editor.insert(tk.INSERT, str(values[0]) + " ")
            self.editor.focus_set()

    # ── casting ──────────────────────────────────────────────────────────────
    def cast_spell(self):
        if str(self.cast_btn["state"]) == "disabled":
            return
        self._wipe(self.result[1])
        self._wipe(self.pyview[1])
        self._set_status("casting")

        outcome = scan(self.editor.get("1.0", "end-1c"))
        if outcome.problem:
            self._write(self.result[1], "🙀 Scanner Problem", outcome.problem, bad=True)
            self._finish(ok=False)
            return

        weaving = weave(outcome.runes)
        self._write(self.pyview[1], "🐍 Isinalin na Python", weaving.python, body_tag="py")

        self.cast_btn.config(state="disabled", text="⏳ Casting…")
        holder = {}

        def work():
            holder["report"] = cast(weaving.python, weaving.line_map)

        worker = threading.Thread(target=work, daemon=True)
        worker.start()
        self._wait_for(worker, holder)

    def _wait_for(self, worker, holder):
        if worker.is_alive():
            self.root.after(60, lambda: self._wait_for(worker, holder))
            return
        report = holder["report"]
        self.cast_btn.config(state="normal", text="✦  Cast Spell")

        if report.stdout:
            self._write(self.result[1], "✨ Resulta", report.stdout)
        if report.problem:
            self._write(self.result[1], "🙀 Pumalya ang Spell", report.problem, bad=True)
        self._finish(ok=report.problem is None)

    def _finish(self, ok: bool):
        self._set_status("ok" if ok else "error")
        self._flash(self.result[1], "#12301f" if ok else "#3a1420")

    # ── output helpers ───────────────────────────────────────────────────────
    def _wipe(self, widget):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.config(state="disabled")

    def _write(self, widget, title, body, bad=False, body_tag=None):
        widget.config(state="normal")
        widget.insert(tk.END, f"── {title} ──\n", "title_bad" if bad else "title_ok")
        widget.insert(tk.END, body + "\n\n", body_tag or ("body_bad" if bad else "body"))
        widget.see(tk.END)
        widget.config(state="disabled")

    def _set_status(self, kind):
        t = THEME
        text, color = {
            "ready":   ("✦ ready", t["dim"]),
            "casting": ("⚡ casting…", t["gold"]),
            "ok":      ("✔ nagtagumpay ang spell", t["mint"]),
            "error":   ("✖ pumalya ang spell", t["danger"]),
        }[kind]
        self.status.config(text=text, fg=color)

    def _flash(self, widget, tint, times=3, interval=110):
        colors = [tint, THEME["night"]] * times

        def step(i=0):
            if i < len(colors):
                widget.config(bg=colors[i])
                self.root.after(interval, lambda: step(i + 1))
        step()

    # ── misc actions ─────────────────────────────────────────────────────────
    def load_sample(self):
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", SAMPLE)
        self._refresh_editor_visuals()

    def clear_all(self):
        self.editor.delete("1.0", tk.END)
        self._wipe(self.result[1])
        self._wipe(self.pyview[1])
        self._refresh_editor_visuals()
        self._set_status("ready")

    # ── splash ───────────────────────────────────────────────────────────────
    def _show_splash(self):
        t = THEME
        self._splash = tk.Toplevel(self.root)
        sp = self._splash
        sp.overrideredirect(True)
        sp.attributes("-topmost", True)
        sp.configure(bg=t["gold"])
        w, h = 460, 200
        sp.geometry(f"{w}x{h}+{(sp.winfo_screenwidth() - w) // 2}+{(sp.winfo_screenheight() - h) // 2}")

        inner = tk.Frame(sp, bg=t["night"])
        inner.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        self._splash_label = tk.Label(inner, text="", bg=t["night"], fg=t["gold"],
                                      font=("Georgia", 18, "bold"))
        self._splash_label.place(relx=0.5, rely=0.45, anchor="center")
        tk.Label(inner, text="Mystika Studio", bg=t["night"], fg=t["dim"],
                 font=MONO_SM).place(relx=0.5, rely=0.78, anchor="center")

        step = 450
        for i, line in enumerate(SPLASH_LINES):
            self.root.after(i * step, lambda s=line: self._splash_say(s))
        self.root.after(len(SPLASH_LINES) * step + 200, self._end_splash)

    def _splash_say(self, text):
        if self._splash.winfo_exists():
            self._splash_label.config(text=text)

    def _end_splash(self):
        if self._splash.winfo_exists():
            self._splash.destroy()
        self.root.deiconify()
        self.root.lift()
        self.editor.focus_set()


def launch():
    root = tk.Tk()
    MystikaStudio(root)
    root.mainloop()


if __name__ == "__main__":
    launch()