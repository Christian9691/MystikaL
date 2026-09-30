"""Lexer for PussyCat custom language.

Tokenizes source code into a stream of tokens for the transpiler.
"""

import re
from dataclasses import dataclass
from typing import Optional
from constants import KEYWORD_MAP


@dataclass
class Token:
    """Represents a single token in the source code."""
    type: str
    value: str
    line: int


@dataclass
class LexerResult:
    """Result of lexing operation."""
    tokens: Optional[list[Token]]
    error: Optional[str]


# Master regex pattern — order of alternations matters:
#   1. Comments:                #[^\n]*            (full line, must precede [^\s])
#   2. Identifiers / keywords:  [a-zA-Z_]\w*
#   3. Numbers (int or float):  [0-9]+(?:\.[0-9]+)?
#   4. Double-quoted strings:   "(?:\\.|[^"\\\n])*"
#                               (?:\\.)      matches any backslash-escaped char
#                               [^"\\\n]     matches normal chars (no quote/backslash/newline)
#                               Together: supports \"  \\  \n escape sequences inside strings
#                               while still stopping at an unescaped newline (no bleed).
#   5. Single-quoted strings:   '(?:\\.|[^'\\\n])*'  (same logic)
#   6. Whitespace (incl. \n):   \s+
#   7. Any other single char:   [^\s]              (symbols, operators, unknown)
_TOKEN_RE = re.compile(
    r'#[^\n]*|[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]+)?|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'|\s+|[^\s]'
)

# Characters that are valid single-character symbols / operators in PussyCat.
# Includes arithmetic, comparison, bitwise, and punctuation operators.
# Quote characters (" and ') are intentionally excluded — a stray lone quote
# is not a valid symbol; it should produce a LexerError.
# Unknown characters like @, $, ` are also excluded so the lexer reports them.
_SYMBOLS = set('+-*/=<>!:(),.[]{};%^&|~')


def _classify(word: str) -> Optional[str]:
    """Return the token type for a matched word.

    Returns None to signal an unknown / invalid token.

    Uses simple character-level checks rather than re.fullmatch() to avoid
    redundant regex overhead — _TOKEN_RE has already guaranteed the shape of
    every match before _classify() is called.
    """
    # KEYWORD — exact lookup in the map
    if word in KEYWORD_MAP:
        return "KEYWORD"

    # COMMENT — starts with #
    if word[0] == '#':
        return "COMMENT"

    # WHITESPACE — all characters are whitespace
    if word[0] in ' \t\r\n\f\v':
        return "WHITESPACE"

    # IDENT — starts with a letter or underscore
    if word[0].isalpha() or word[0] == '_':
        return "IDENT"

    # NUMBER — starts with a digit
    if word[0].isdigit():
        return "NUMBER"

    # STRING — at least 2 chars, wrapped in matching quotes, no newlines
    # (newlines already excluded by _TOKEN_RE, but guard len >= 2 for safety)
    if len(word) >= 2 and word[0] == word[-1] and word[0] in ('"', "'"):
        return "STRING"

    # SYMBOL — single valid operator / punctuation character
    if len(word) == 1 and word in _SYMBOLS:
        return "SYMBOL"

    return None     # unknown token


def tokenize(source: str) -> LexerResult:
    """Tokenize PussyCat source code into a list of tokens.

    Scans left-to-right using the master regex.  Each match is classified
    and appended to the token list.  If an unrecognised token is found the
    function returns immediately with a LexerError — no partial stream is
    passed downstream.

    Never raises an exception; all error paths return a LexerResult with
    the error field set.
    """
    # Enforce non-throwing invariant: reject non-string input immediately
    # instead of letting _TOKEN_RE.finditer() raise a TypeError.
    if not isinstance(source, str):
        return LexerResult(
            tokens=None,
            error="[Lexer Error] Source must be a string"
        )

    tokens: list[Token] = []
    line: int = 1                   # 1-indexed current line

    for match in _TOKEN_RE.finditer(source):
        word = match.group()

        token_type = _classify(word)

        if token_type is None:
            # Unknown token — abort immediately with a descriptive error
            return LexerResult(
                tokens=None,
                error=f"[Lexer Error] Line {line}: Unknown token '{word}'"
            )

        tokens.append(Token(type=token_type, value=word, line=line))

        # Advance line counter for every newline inside this match
        line += word.count('\n')

    return LexerResult(tokens=tokens, error=None)
