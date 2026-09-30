# Fix Report: Lexer & Transpiler

**Status:** All issues resolved ✅
**Files changed:** `lexer.py`, `transpiler.py`
**Tests run:** 43/43 passed

──────

## Issues Found & Fixed

### 1. ✅ Comments Tokenized as Code (Critical)

**Problem:**
`_TOKEN_RE` had no rule for comments. The `#` character was matched by the
catch-all `[^\s]` alternation as a single character, while the rest of the
comment line was tokenized normally as code. This caused two bugs:
- Keywords inside comments (e.g. `# kung totoo`) were being transpiled into
  Python (`# if True`), corrupting the output.
- Symbols not in `_SYMBOLS` inside comments (e.g. `# 100% complete` or
  `# a@b.com`) caused fatal crashes: `[Lexer Error] Line X: Unknown token '%'`.

**Fix:**
Added `#[^\n]*` as the **first** alternation in `_TOKEN_RE`, before `[^\s]`.
This greedily consumes the entire comment line as a single `COMMENT` token.
The classifier's existing `word.startswith('#')` branch handles it correctly.

```python
# Before
_TOKEN_RE = re.compile(
    r'[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]+)?|"[^"]*"|\'[^\']*\'|\s+|[^\s]'
)

# After
_TOKEN_RE = re.compile(
    r'#[^\n]*|[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]+)?|"[^"]*"|\'[^\']*\'|\s+|[^\s]'
)
```

──────

### 2. ✅ Stray Quote Misclassified as STRING (High)

**Problem:**
`_classify()` checked `word.startswith('"') and word.endswith('"')` without
verifying `len(word) >= 2`. A single stray `"` satisfies both conditions
(a one-character string starts and ends with itself), so it was silently
classified as a valid empty `STRING` instead of raising a `LexerError`.

**Fix:**
Added a `len(word) >= 2` guard to the STRING check so a lone quote character
falls through to the unknown-token path and produces a proper error.

```python
# Before
if (word.startswith('"') and word.endswith('"')) or \
   (word.startswith("'") and word.endswith("'")):
    return "STRING"

# After
if len(word) >= 2 and (
    (word.startswith('"') and word.endswith('"')) or
    (word.startswith("'") and word.endswith("'"))
):
    return "STRING"
```

Also removed bare `"` and `'` from `_SYMBOLS` — they were included previously,
which meant a stray quote was classified as `SYMBOL` instead of triggering an
error even after the guard above was added.

──────

### 3. ✅ Missing Math & Bitwise Operators (High)

**Problem:**
`_SYMBOLS` was missing `%`, `&`, `|`, `^`, `~`, and `;`. Any expression using
these operators (e.g. `x = 10 % 3`, `a & b`, `~x`) caused an immediate
`LexerError` on the unrecognised character.

**Fix:**
Added all missing operators to `_SYMBOLS`.

```python
# Before
_SYMBOLS = set('+-*/=<>!:(),.[]{}"\'')

# After
_SYMBOLS = set('+-*/=<>!:(),.[]{};%^&|~')
```

Note: `"` and `'` were also removed from `_SYMBOLS` as part of fix #2.

──────

### 4. ✅ Transpiler Line Map Desynchronization (Critical)

**Problem:**
In `transpiler.py`, `out_line` was only incremented inside the
`token.type == "WHITESPACE"` branch. Any other token that contained a newline
(e.g. a multiline string `"hello\nworld"`) would not advance `out_line`.
Every token after that would be mapped to the wrong output line, causing the
executor to report incorrect traceback line numbers. Additionally, multi-line
whitespace chunks jumped `out_line` without filling the intermediate entries,
leaving gaps in `line_map`.

**Fix:**
Moved the newline-counting logic outside all token-type branches so it runs
for **every** token. Intermediate empty lines are now pre-seeded in `line_map`
so there are never any gaps.

```python
# Before — only WHITESPACE advanced out_line
elif token.type == "WHITESPACE":
    output_parts.append(token.value)
    newlines = token.value.count('\n')
    if newlines:
        out_line += newlines
        line_map[out_line] = token.line

# After — every token advances out_line if it contains newlines
output_parts.append(...)          # append for all token types
line_map[out_line] = token.line   # record before advancing

newlines = token.value.count('\n')
if newlines:
    for i in range(1, newlines + 1):
        line_map[out_line + i] = token.line   # pre-seed intermediate lines
    out_line += newlines
```

──────

## Test Coverage

43 tests written and verified across 4 classes before the test file was removed:

| Class | Tests | What it covers |
|---|---|---|
| `TestCommentFix` | 8 | Full comment capture, keyword passthrough, bad symbols in comments |
| `TestStrayQuoteFix` | 6 | Stray `"` / `'` error, valid empty strings still work |
| `TestMissingOperatorsFix` | 11 | Each new operator, expressions, `@`/`$` still unknown |
| `TestLineMapDesyncFix` | 9 | 2–5 line maps, empty lines, gaps, intermediate seeding |
| `TestRegression` | 9 | All 19 keywords, full snippets, `print`, `%` expressions |

All 43 tests passed. ✅
