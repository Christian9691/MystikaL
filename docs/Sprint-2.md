# Sprint 2: Transpiler Pipeline Implementation

**Status:** 0/11 tasks completed

## Tasks

### Lexer
- [ ] #15. Implement regex pattern: `r'[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]+)?|"[^"]*"|\'[^\']*\'|[^\s]|\s+'`
- [ ] #16. Implement line tracking by counting `\n` in each match
- [ ] #17. Implement token classification (KEYWORD, IDENT, NUMBER, STRING, SYMBOL, WHITESPACE, COMMENT)
- [ ] #18. Handle unknown tokens with `LexerError` including line number
- [ ] #19. Unit tests for tokenize() with edge cases

### Transpiler
- [ ] #20. Implement token iteration and Python code building
- [ ] #21. Implement line_map generation (Python line → PussyCat source line)
- [ ] #22. Handle KEYWORD_MAP substitution for all 19 keywords

### Executor
- [ ] #23. Write Python code to tempfile, subprocess.run with 10s timeout, capture output
- [ ] #24. Implement stderr line number remapping to PussyCat source
- [ ] #25. Unit tests for execute() with success/error/timeout cases
