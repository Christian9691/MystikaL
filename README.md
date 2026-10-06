# PussyCat 🐱

A cat-themed programming language and a single-window desktop IDE for it. PussyCat
source is tokenized, transpiled to Python, and executed in a subprocess. Runtime
errors are reported against **your PussyCat line numbers**, not the generated Python's.

## Requirements

- Python 3.10+ (developed on 3.14)
- `tkinter` (bundled with most Python installs; on Debian/Ubuntu: `sudo apt install python3-tk`)
- No third-party packages

## Run

```bash
python3 main.py
```

## Usage

| Action | How |
|--------|-----|
| Run the program | `▶ Run` button or `Ctrl+Enter` |
| Indent | `Tab` inserts 4 spaces |
| Reset editor and output | `🗑 Clear` button |
| Insert a keyword | Click it in the keyword bar (hover shows its Python equivalent) |

The right panel shows the generated Python first, then program output, or an error section
(lexer error, syntax error, or traceback). The status bar shows `ready / running / ok / error`.

## Keywords

| PussyCat | Python | | PussyCat | Python |
|----------|--------|-|----------|--------|
| `meow` | `if` | | `trick` | `def` |
| `mew` | `else` | | `furball` | `return` |
| `chase` | `while` | | `breed` | `class` |
| `paws` | `for` | | `pounce` | `try` |
| `purr` | `True` | | `miss` | `except` |
| `hiss` | `False` | | `nap` | `finally` |
| `box` | `None` | | `adopt` | `import` |
| `whiskers` | `and` | | `shelter` | `from` |
| `tail` | `or` | | `nyan` | `print` |
| `scratch` | `not` | | | |

Everything else is plain Python syntax.

## Example

```
trick greet(name):
    furball "Meow, " + name

nyan(greet("Rem"))
```

More programs are in [`examples/`](examples/): `hello.cat`, `loops.cat`, `tricks.cat`
and `error_demo.cat` (shows error line remapping). Paste one into the editor to try it.

## Known limitations

- Keywords are reserved everywhere outside strings and comments. A variable named `meow` or
  `tail` is treated as the keyword and transpiled to `if` / `or`.
- Scripts are killed after 10 seconds and reported as a timeout error.
- Keywords are hardcoded in `constants.py`; there is no file save/open or multi-file support (PRD non-goals).
- The IDE runs your code with your Python interpreter and user permissions. Only run code you trust.

## Tests

```bash
python3 -m unittest discover tests
```

GUI tests need a display and are skipped automatically when none is available
(on a headless machine use `xvfb-run python3 -m unittest discover tests`).

## Project layout

| File | Role |
|------|------|
| `constants.py` | `KEYWORD_MAP` |
| `lexer.py` | `tokenize()` → tokens or lexer error with line number |
| `transpiler.py` | `transpile()` → Python source + line map |
| `executor.py` | `execute()` → subprocess run, timeout, traceback remapping |
| `gui.py` | tkinter IDE |
| `main.py` | entry point |