# SPEC — PussyCat IDE
> Status: Draft | Version: 1.0 | Date: 2026-09-21  
> Source of truth for implementation. Any behavior not covered here is an open question, not a green light to assume.  
> Reference: PRD-PussyCat.md

---

## 1. Scope

This spec covers the full implementation of the PussyCat IDE — a single-file tkinter desktop
application that lets students write code in the PussyCat custom language, transpile it to
Python, execute it locally via subprocess, and see output and errors remapped to PussyCat
source lines. It covers the lexer, transpiler, executor, and GUI contracts.

---

## 2. Non-Goals

- No file I/O (open/save dialogs).
- No syntax highlighting in the editor.
- No custom keyword editor in the UI.
- No packaging to `.exe` / `.app`.
- No network requests of any kind.
- No multi-file or import resolution across PussyCat files.

---

## 3. Requirements (EARS)

| ID    | Requirement |
|-------|-------------|
| FR-1  | THE SYSTEM SHALL render a split-panel GUI with a left editor pane and a right output pane separated by a draggable sash. |
| FR-2  | THE SYSTEM SHALL display a line number column in the left pane that stays in sync with the editor's vertical scroll position. |
| FR-3  | WHEN the user presses `Tab` in the editor THE SYSTEM SHALL insert 4 spaces instead of a tab character. |
| FR-4  | WHEN the user presses `Ctrl+Enter` THE SYSTEM SHALL trigger the run pipeline. |
| FR-5  | WHEN run is triggered THE SYSTEM SHALL pass the editor contents through the lexer before any other step. |
| FR-6  | WHEN the lexer encounters an unrecognized token THE SYSTEM SHALL abort and display a `LexerError` with the source line number in the output pane; no execution shall occur. |
| FR-7  | WHEN lexing succeeds THE SYSTEM SHALL pass the token stream to the transpiler and display the generated Python in the output pane. |
| FR-8  | WHEN transpilation succeeds THE SYSTEM SHALL write the generated Python to a temporary file and execute it via `subprocess.run` with `timeout=10`. |
| FR-9  | WHEN subprocess stdout is non-empty THE SYSTEM SHALL display it in the output pane under a clearly labeled section. |
| FR-10 | WHEN subprocess exits with a non-zero return code THE SYSTEM SHALL parse stderr, remap any line numbers to PussyCat source lines using the line map, and display the error in the output pane. |
| FR-11 | WHEN subprocess execution exceeds 10 seconds THE SYSTEM SHALL terminate the process and display a timeout error. |
| FR-12 | THE SYSTEM SHALL delete the temporary `.py` file after execution completes, regardless of success or failure. |
| FR-13 | THE SYSTEM SHALL display a keyword reference bar above the editor showing every entry in `KEYWORD_MAP` as `custom → python`. |
| FR-14 | THE SYSTEM SHALL show a status bar at the bottom with the current state: `ready`, `running`, `ok`, or `error`. |
| FR-15 | WHEN the Clear button is clicked THE SYSTEM SHALL reset the editor to empty and clear the output pane. |
| FR-16 | IF any unhandled exception occurs in the run pipeline THEN THE SYSTEM SHALL catch it, display a generic error in the output pane, and return the IDE to `ready` state without crashing. |

---

## 4. Data Models

### 4.1 Token

```
Token
  type  : str   — one of: KEYWORD | IDENT | NUMBER | STRING | SYMBOL | WHITESPACE | COMMENT
  value : str   — the raw matched text
  line  : int   — 1-indexed source line number where the token starts
```

### 4.2 LexerResult

```
LexerResult
  tokens : list[Token] | None   — None if lexing failed
  error  : str | None           — error message if lexing failed, None on success
```

### 4.3 TranspileResult

```
TranspileResult
  python   : str            — generated Python source code
  line_map : dict[int, int] — maps generated Python line number → PussyCat source line number
```

### 4.4 ExecutionResult

```
ExecutionResult
  stdout     : str        — captured standard output (empty string if none)
  stderr     : str        — raw stderr from subprocess
  error      : str | None — human-readable error message remapped to PussyCat lines, or None
  timed_out  : bool       — True if the process was killed due to timeout
  returncode : int        — subprocess return code
```

### 4.5 KEYWORD_MAP

```python
KEYWORD_MAP: dict[str, str] = {
    "kung":     "if",
    "kundi":    "else",
    "habang":   "while",
    "para":     "for",
    "ibalik":   "return",
    "totoo":    "True",
    "mali":     "False",
    "wala":     "None",
    "ipakita":  "print",
    "at":       "and",
    "o":        "or",
    "hindi":    "not",
    "klase":    "class",
    "gawain":   "def",
    "subukan":  "try",
    "maliban":  "except",
    "wakas":    "finally",
    "itaas":    "import",
    "mula":     "from",
}
```

`KEYWORD_MAP` is a module-level constant. It is not modified at runtime.

---

## 5. Module Contracts

### 5.1 `lexer.py`

```python
def tokenize(source: str) -> LexerResult
```

- Scans `source` left-to-right using the regex pattern:
  `r'[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]+)?|"[^"]*"|\'[^\']*\'|[^\s]|\s+'`
- Tracks `line` by counting `\n` characters in each match.
- For each match, classifies as:
  - `KEYWORD` — if `word in KEYWORD_MAP`
  - `IDENT` — if matches `[a-zA-Z_]\w*` and not a keyword
  - `NUMBER` — if matches `[0-9]+(\.[0-9]+)?`
  - `STRING` — if starts with `"` or `'`
  - `WHITESPACE` — if `word.strip() == ""`
  - `COMMENT` — if starts with `#`
  - `SYMBOL` — if matches `[+\-*/=<>!:(),.\[\]{}'"]`
  - Otherwise → return `LexerResult(tokens=None, error=f"[Lexer Error] Line {line}: Unknown token '{word}'")`
- On success → return `LexerResult(tokens=[...], error=None)`

**Constraint**: `tokenize` must never raise an exception. All error paths return a `LexerResult` with `error` set.

---

### 5.2 `transpiler.py`

```python
def transpile(tokens: list[Token]) -> TranspileResult
```

- Iterates over tokens, building `output: str` and `line_map: dict[int, int]`.
- For each token:
  - `KEYWORD` → append `KEYWORD_MAP[token.value]` to output; record `line_map[current_output_line] = token.line`
  - `WHITESPACE` containing `\n` → append as-is; increment `current_output_line` per newline; record mapping
  - All other types → append `token.value` as-is
- Returns `TranspileResult(python=output, line_map=line_map)`

**Constraint**: `transpile` receives only valid token streams from `tokenize`. It must never call `tokenize` itself.

---

### 5.3 `executor.py`

```python
def execute(python_code: str, line_map: dict[int, int]) -> ExecutionResult
```

- Writes `python_code` to a temp file using `tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w")`.
- Calls `subprocess.run(["python3", tmp_path], capture_output=True, text=True, timeout=10)`.
  - On Windows, falls back to `["python", tmp_path]` if `python3` is not found.
- Deletes the temp file in a `finally` block regardless of outcome.
- On `subprocess.TimeoutExpired`: kills the process, returns `ExecutionResult(timed_out=True, error="[Timeout] Execution exceeded 10 seconds.", ...)`.
- On success (returncode == 0): returns `ExecutionResult(stdout=result.stdout, stderr="", error=None, timed_out=False, returncode=0)`.
- On failure (returncode != 0): parses `result.stderr` to extract line number, remaps via `line_map`, returns `ExecutionResult(error=remapped_error, ...)`.

**Line number remapping**:
```python
# Extract Python line number from stderr traceback
match = re.search(r'line (\d+)', stderr)
if match:
    py_line = int(match.group(1))
    source_line = line_map.get(py_line, py_line)
    error = stderr.replace(f"line {py_line}", f"line {source_line} (PussyCat source)")
```

---

### 5.4 `gui.py`

#### Layout

```
root (Tk)
├── keyword_bar (Frame)        — top, fixed height, scrollable if needed
├── main_pane (PanedWindow)    — horizontal, fills remaining space
│   ├── left_frame (Frame)
│   │   ├── panel_label       — "YOUR CODE"
│   │   └── editor_frame (Frame)
│   │       ├── line_numbers (Text, read-only, width=4)
│   │       └── editor (Text)  — main input widget
│   └── right_frame (Frame)
│       ├── panel_label       — "OUTPUT"
│       └── output (Text, read-only)
└── status_bar (Frame)         — bottom, fixed height
    └── status_label (Label)
```

#### Widget specifications

**editor (Text)**
- `bg="#1E1E2E"`, `fg="#E8D5B7"`, `insertbackground="#F4A261"`
- `font=("Courier New", 11)` or `("JetBrains Mono", 11)` with fallback
- `undo=True`, `wrap=tk.NONE`
- Bound: `<Tab>` → insert 4 spaces, `return "break"` to suppress default
- Bound: `<Control-Return>` → trigger run pipeline
- Bound: `<KeyRelease>` → update line numbers

**line_numbers (Text)**
- `width=4`, `state="disabled"`, same `bg` and `font` as editor
- `fg="#7a7a9a"`, `takefocus=0`
- Updated on every `<KeyRelease>` and `<<Modified>>` event in editor
- Scroll synced to editor via `yscrollcommand`

**output (Text)**
- `state="disabled"` at all times except during write operations
- Uses named tags for color coding:
  - `tag_config("python_header", foreground="#6BCB77")`
  - `tag_config("python_code",   foreground="#E8D5B7")`
  - `tag_config("output_header", foreground="#F4A261")`
  - `tag_config("output_text",   foreground="#C9B99A")`
  - `tag_config("error_header",  foreground="#FF6B6B")`
  - `tag_config("error_text",    foreground="#FF6B6B")`

**status_label**
- States and colors:
  - `ready`   → `fg="#7a7a9a"`, text: `● ready`
  - `running` → `fg="#F4A261"`, text: `● running...`
  - `ok`      → `fg="#6BCB77"`, text: `● ok`
  - `error`   → `fg="#FF6B6B"`, text: `● error`

#### Run pipeline (triggered by `Ctrl+Enter` or Run button)

```
1. Set status → "running"
2. Get source = editor.get("1.0", tk.END).strip()
3. result = tokenize(source)          # lexer.py
4. IF result.error:
     display_error(result.error)
     set status → "error"
     return
5. transpile_result = transpile(result.tokens)   # transpiler.py
6. display_python(transpile_result.python)
7. exec_result = execute(transpile_result.python, transpile_result.line_map)  # executor.py
8. IF exec_result.stdout:
     display_output(exec_result.stdout)
9. IF exec_result.error:
     display_error(exec_result.error)
     set status → "error"
   ELSE:
     set status → "ok"
```

**Constraint**: Steps 3–9 must run in the main thread for v1 (subprocess call is blocking but short-lived due to timeout). If UI freezes become an issue, wrap in `threading.Thread` — but that is out of scope for v1.

---

## 6. Edge Cases & Error Handling

| Case | Defined Behavior |
|------|-----------------|
| Empty editor on run | Lexer receives empty string; returns empty token list; transpiler outputs empty string; subprocess runs empty file and exits 0 with no output. Display "no output." |
| Unknown token mid-source | Lexer returns immediately with `LexerError` at the offending line. No partial transpilation. |
| Valid PussyCat that produces invalid Python | Subprocess returns non-zero. stderr is parsed and remapped. Displayed as runtime error. |
| Infinite loop in user code | Subprocess killed at 10s. `ExecutionResult.timed_out = True`. Display timeout message. |
| `python3` not found on Windows | `executor.py` catches `FileNotFoundError` and retries with `python`. If both fail, display: `[Executor Error] Python interpreter not found. Ensure Python 3.10+ is installed.` |
| Temp file write fails | Catch `OSError`, display: `[Executor Error] Could not write temp file: {e}`. Do not attempt execution. |
| Keyword used as identifier (e.g. variable named `kung`) | Lexer classifies it as `KEYWORD` and transpiler replaces it with `if`. This is a known limitation — document in README, not handled in code. |
| `o` keyword inside identifier (e.g. `foo`) | Regex `[a-zA-Z_]\w*` matches `foo` as a single `IDENT` token, never as `f` + `o` + `o`. No collision. |

---

## 7. Acceptance Criteria

**FR-1 / FR-2 — Split panel + line numbers**
- Given the app is launched
- When the window renders
- Then two panes are visible side-by-side with a draggable sash
- And the left pane shows line numbers starting at `1`
- And typing in the editor increments line numbers correctly

**FR-3 — Tab inserts spaces**
- Given focus is in the editor
- When the user presses `Tab`
- Then 4 spaces are inserted at the cursor position
- And no tab character (`\t`) appears in the editor content

**FR-4 / FR-5 — Ctrl+Enter triggers run**
- Given source code is in the editor
- When the user presses `Ctrl+Enter`
- Then the run pipeline executes
- And status changes to `running` then to `ok` or `error`

**FR-6 — LexerError on unknown token**
- Given the editor contains `@ x = 5`
- When run is triggered
- Then the output pane shows `[Lexer Error] Line 1: Unknown token '@'`
- And no Python code is displayed
- And no subprocess is spawned

**FR-7 — Generated Python displayed**
- Given the editor contains `kung x > 5:`
- When run is triggered and lexing succeeds
- Then the output pane shows `if x > 5:` under a "generated python" header

**FR-8 — Subprocess execution and stdout capture**
- Given the editor contains `ipakita("hello")`
- When run is triggered
- Then the output pane shows `hello` under an "output" header

**FR-9 — Runtime error remapped to PussyCat line**
- Given a 3-line PussyCat source where line 2 causes a `NameError`
- When run is triggered
- Then the error message references line 2 (PussyCat source), not the generated Python line number

**FR-10 — Timeout**
- Given the editor contains `habang totoo: ipakita("x")`
- When run is triggered
- Then after 10 seconds the output pane shows a timeout error
- And the IDE returns to a usable state

**FR-12 — Temp file deleted**
- Given any run completes (success or failure)
- When execution finishes
- Then no `.py` temp file remains on disk

**FR-13 — Keyword bar**
- Given the app is launched
- Then every key in `KEYWORD_MAP` is visible in the keyword bar with its Python equivalent

**FR-14 — Status bar states**
- `ready` on launch and after clear
- `running` during subprocess execution
- `ok` after successful run with no errors
- `error` after any lexer, transpiler, or runtime error

---

## 8. Assumptions

- Python 3.10+ is installed on the target machine and available as `python3` (Unix) or `python` (Windows).
- tkinter is available — it ships with the standard CPython distribution. Linux users may need `sudo apt install python3-tk`.
- `KEYWORD_MAP` is the single source of truth for keyword definitions. The lexer, transpiler, and keyword bar all read from the same dict — no duplication.
- The IDE runs entirely on the main thread for v1. Blocking on subprocess for up to 10s is accepted.
- Source files are UTF-8 encoded.

---

## 9. Open Questions

- 🚧 Does the course spec require specific PussyCat keywords beyond what's in `KEYWORD_MAP`? If yes, update the map before implementation.
- 🚧 Should multi-line expressions (`\` continuation) be supported? Current lexer handles each line independently.
- 🚧 Is there a required app window title or icon specified by the course instructor?
- 🚧 Should the keyword bar support clicking to insert at cursor, or is display-only sufficient for v1?

---

## 10. File Structure

```
pussycat/
├── main.py          — entry point, calls gui.py
├── lexer.py         — tokenize()
├── transpiler.py    — transpile()
├── executor.py      — execute()
├── gui.py           — PussyCatIDE class (tkinter)
├── PRD-PussyCat.md
└── SPEC-PussyCat.md
```

---

## 11. Changelog

- 2026-09-21 — v1.0 initial spec drafted from PRD-PussyCat.md
