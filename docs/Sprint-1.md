# Sprint 1: Core Infrastructure - Lexer, Transpiler, Executor, and GUI Foundation

**Status:** 0/14 tasks completed

## Tasks

- [ ] #1. Create project structure with lexer.py, transpiler.py, executor.py, gui.py, main.py
- [ ] #2. Implement KEYWORD_MAP constant in a shared module (lexer.py or new constants.py)
- [ ] #3. Implement lexer.py tokenize() function per SPEC Section 5.1
- [ ] #4. Implement transpiler.py transpile() function per SPEC Section 5.2
- [ ] #5. Implement executor.py execute() function per SPEC Section 5.3
- [ ] #6. Implement gui.py base layout: split panel, editor, line numbers, output, keyword bar, status bar
- [ ] #7. Implement line number sync between editor and line_numbers widget
- [ ] #8. Implement Tab key binding to insert 4 spaces
- [ ] #9. Implement Ctrl+Enter run pipeline trigger
- [ ] #10. Wire run pipeline: tokenize → transpile → execute with status updates
- [ ] #11. Test: verify lexer catches unknown token and displays error
- [ ] #12. Test: verify transpiler outputs correct Python for kung/kundi/habang
- [ ] #13. Test: verify executor runs Python and captures stdout
- [ ] #14. Test: verify error remapping works for runtime errors
