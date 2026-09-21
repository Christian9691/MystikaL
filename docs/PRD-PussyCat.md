# PRD — PussyCat IDE
> Status: Draft | Date: 2026-09-21 | Owner: Rem

## 1. Problem Statement

CS students building a custom programming language need a dedicated desktop tool to write,
transpile, and run code in their language. Today there is no dedicated tool — students either
run transpiler scripts manually via CLI or paste code into separate editors, breaking the
feedback loop. A tkinter desktop IDE ships as a single Python file with zero extra
dependencies, making it ideal for a coursework demo.

## 2. Goals

- Students can write PussyCat code and see the generated Python output side-by-side in under 1 second (local execution, no network).
- Runtime errors are displayed with line numbers that map back to the PussyCat source, not the generated Python.
- The tool runs as a standalone Python desktop app — no browser, no API, no installation beyond Python itself.

## 3. Non-Goals (Out of Scope for v1)

- Persistent file saving or project management.
- Multi-file support.
- Syntax highlighting / tokenization coloring in the editor.
- User accounts or authentication.
- Custom keyword configuration via UI (KEYWORD_MAP is hardcoded).
- Web or mobile version.
- Packaging as a standalone executable (.exe / .app).

## 4. Target Users

**Primary** — CS students (3rd year, CCS course) writing and demoing a custom language transpiler as a group project.  
**Secondary** — Course instructor evaluating the transpiler's correctness and error reporting.

## 5. User Stories

- As a student, I want to type PussyCat code in an editor and see the Python equivalent immediately, so I can verify my transpiler's output without using a CLI.
- As a student, I want errors to point to the line in my PussyCat source, so I can fix mistakes without mentally mapping back from generated Python.
- As a student, I want a keyword reference visible while coding, so I don't have to memorize every custom keyword.
- As an instructor, I want to see both the source and generated Python at once, so I can assess whether the transpiler is working correctly.

## 6. Functional Requirements

| ID    | Requirement                                                                                                        | Priority |
|-------|--------------------------------------------------------------------------------------------------------------------|----------|
| FR-1  | Editor accepts PussyCat source code with tab support (4 spaces) and line numbers synced to editor scroll           | P0       |
| FR-2  | Lexer tokenizes source and raises a `LexerError` with line number for unknown tokens before any execution          | P0       |
| FR-3  | Transpiler maps custom keywords to Python equivalents and outputs valid Python                                      | P0       |
| FR-4  | Generated Python is displayed in the right panel's output area before execution result                             | P0       |
| FR-5  | Code executes via `subprocess` calling the local Python interpreter; stdout is captured and displayed              | P0       |
| FR-6  | Runtime errors display with the line number remapped to the PussyCat source line                                   | P0       |
| FR-7  | Lexer errors, syntax errors, and runtime errors are visually distinct (color-coded) in the output panel            | P0       |
| FR-8  | Keyword reference bar shows all custom keywords and their Python equivalents                                        | P1       |
| FR-9  | `Ctrl+Enter` triggers run                                                                                          | P1       |
| FR-10 | Clear button resets editor and output panel                                                                        | P1       |
| FR-11 | Status bar shows current state: ready / running / ok / error                                                       | P1       |
| FR-12 | Cat-themed UI using tkinter color configuration — decorative elements must not obstruct editor or output            | P2       |

## 7. Non-Functional Requirements

**Execution latency** — Transpilation (lexer + code gen) must complete in <100ms for files under 200 lines. Subprocess execution should return within the natural runtime of the user's code plus <200ms overhead.

**Error safety** — Lexer must never pass malformed token streams to the transpiler. Subprocess errors must be caught and rendered; they must never crash the IDE.

**Execution timeout** — Subprocess execution must be killed after 10 seconds to prevent infinite loops from hanging the UI.

**Platform** — Must run on Windows, macOS, and Linux where Python 3.10+ is installed. No external pip packages required beyond the stdlib.

## 8. Success Metrics

- Transpiler correctly maps all keywords in `KEYWORD_MAP` with zero substitution errors on a 50-line test file.
- Error messages reference PussyCat line numbers, not generated Python line numbers, in 100% of tested error cases.
- A new student can write and run their first PussyCat program without reading documentation (validated by a 5-minute observation during demo).
- App launches in under 3 seconds on a standard student laptop.

## 9. Assumptions & Open Questions

- **Assumed**: Python 3.10+ is available on the student's machine — tkinter ships with it by default.
- **Assumed**: Execution uses `subprocess` calling `python` or `python3` to run a temp file; no sandboxing beyond the timeout.
- **Assumed**: `KEYWORD_MAP` is fixed for v1 — no UI for adding custom keywords.
- **Open**: Does the course require the transpiler to support multi-line expressions (e.g. line continuations with `\`)? If yes, the lexer needs adjustment.
- **Open**: Is there a submission deadline that affects which P1/P2 features are cut?

## 10. Risks

- **Subprocess hanging** — A student's infinite loop will block the UI thread if not handled. Mitigation: run subprocess with `timeout=10`; kill process and show timeout error.
- **Temp file cleanup** — Execution writes a `.py` temp file to disk. Mitigation: use `tempfile` module with `delete=True` to auto-clean after execution.
- **Keyword collision** — Short keywords like `o` (→ `or`) could match inside identifiers if the lexer regex is too loose. Mitigation: regex uses word-boundary matching; test with identifiers that contain keyword substrings.
- **tkinter unavailability** — Some Linux distros ship Python without tkinter. Mitigation: document `sudo apt install python3-tk` as the only setup step.

## 11. Technical Stack

| Layer         | Choice                    | Reason                                          |
|---------------|---------------------------|-------------------------------------------------|
| GUI framework | tkinter                   | stdlib, zero install, cross-platform            |
| Execution     | subprocess + tempfile     | local Python, no API dependency                 |
| Transpiler    | custom lexer + code gen   | pure Python, already prototyped                 |
| Packaging     | single `main.py`          | simplest delivery for coursework submission     |
