"""Transpiler for PussyCat custom language.

Converts a validated token stream (from lexer.tokenize) into Python source
code, and builds a line map so runtime errors can be remapped back to the
original PussyCat source line numbers.
"""

from dataclasses import dataclass
from constants import KEYWORD_MAP
from lexer import Token


@dataclass
class TranspileResult:
    """Result of transpilation operation.

    Attributes:
        python:   Generated Python source code.
        line_map: Maps each generated Python line number (1-indexed) to the
                  PussyCat source line number it was produced from.
    """
    python: str
    line_map: dict[int, int]


def transpile(tokens: list[Token]) -> TranspileResult:
    """Transpile a PussyCat token stream into Python source code.

    Iterates over every token produced by tokenize():

      - KEYWORD tokens     → substituted with their Python equivalent from
                             KEYWORD_MAP (e.g. "kung" → "if").
      - WHITESPACE tokens  → appended verbatim; newlines advance the internal
                             output-line counter so the line_map stays in sync.
      - All other tokens   → appended verbatim (value unchanged).

    line_map records, for each output Python line, the PussyCat source line
    that produced the content on that line.  Executor uses this to rewrite
    Python traceback line numbers back to PussyCat source lines.

    Precondition: `tokens` is a valid stream from tokenize() with no unknown
    tokens.  transpile() never calls tokenize() itself.
    """
    output_parts: list[str] = []
    line_map: dict[int, int] = {}

    out_line: int = 1   # 1-indexed current output (Python) line

    for token in tokens:
        if token.type == "KEYWORD":
            # Replace PussyCat keyword with its Python equivalent
            output_parts.append(KEYWORD_MAP[token.value])
        else:
            # WHITESPACE, IDENT, NUMBER, STRING, SYMBOL, COMMENT — verbatim
            output_parts.append(token.value)

        # Record the mapping before advancing the line counter so the token
        # is attributed to the line it *starts* on.
        line_map[out_line] = token.line

        # Advance out_line for every newline inside ANY token (multiline
        # strings, whitespace chunks, comments that end in \n, etc.).
        newlines = token.value.count('\n')
        if newlines:
            for i in range(1, newlines + 1):
                # Pre-seed each newly opened output line with the correct
                # source line — token.line + i keeps it in sync with the
                # actual source line each newline corresponds to.
                line_map[out_line + i] = token.line + i
            out_line += newlines

    python_code = "".join(output_parts)
    return TranspileResult(python=python_code, line_map=line_map)
