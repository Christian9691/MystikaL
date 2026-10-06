# All Sprints — PussyCat IDE

## Overview

3-sprint plan for a complete, functional PussyCat IDE (single-file tkinter transpiler demo).

---

## Sprint 1: Core Infrastructure ✓
**Goal:** Project foundation and blank GUI

- Project structure (6 modules: constants, lexer, transpiler, executor, gui, main)
- Module stubs with dataclass contracts
- Blank tkinter GUI with all required widgets
- PRD, SPEC, DESIGN, ASSETS documentation

**Deliverable:** Runnable app with blank functionality (stubs return empty results)

---

## Sprint 2: Transpiler Pipeline ✓
**Goal:** Complete the core lexer → transpiler → executor logic

### Lexer (tokenize)
- Regex-based tokenization with line tracking
- Token classification (KEYWORD, IDENT, NUMBER, STRING, SYMBOL, WHITESPACE, COMMENT)
- LexerError with line numbers for unknown tokens
- Unit tests

### Transpiler (transpile)
- Token-to-Python conversion
- Line map generation for error remapping
- KEYWORD_MAP substitution for all 19 keywords
- Unit tests

### Executor (execute)
- Temp file creation + subprocess.run with 10s timeout
- Stdout/stderr capture
- Stderr line number remapping to PussyCat source
- Windows fallback (python3 → python)
- Unit tests (success, error, timeout)

**Deliverable:** Full pipeline works; students can transpile & run PussyCat code

---

## Sprint 3: GUI Integration & Polish ✓
**Goal:** Wire GUI to pipeline, add cat theme, ship v1

### GUI Wiring
- Connect run_pipeline to tokenize → transpile → execute
- Line number synchronization (KeyRelease + Modified)
- Tab binding (4 spaces), Ctrl+Enter trigger
- Color-coded output (python/output/error sections)
- Status bar states (ready/running/ok/error)

### Cat Theme & UX
- Startup splash screen (2-second cat video loop or emoji)
- Success animation (hearts, green pulse)
- Error animation (shake, red pulse)
- Keyword bar with all 19 mappings

### Polish & Testing
- End-to-end pipeline tests
- Edge cases (empty, timeout, missing python3)
- README with usage, requirements, demo
- Sample PussyCat programs

**Deliverable:** Complete, themed v1 app ready for classroom demo
