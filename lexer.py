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
#   1. Identifiers / keywords:  [a-zA-Z_]\w*
#   2. Numbers (int or float):  [0-9]+(?:\.[0-9]+)?
#   3. Double-quoted strings:   "[^"]*"
#   4. Single-quoted strings:   '[^']*'
#   5. Whitespace (incl. \n):   \s+
#   6. Any other single char:   [^\s]   (symbols, operators, unknown)
_TOKEN_RE = re.compile(
    r'[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]+)?|"[^"]*"|\'[^\']*\'|\s+|[^\s]'
)

# Characters that are valid single-character symbols / operators in PussyCat.
# Only include characters that appear in valid PussyCat/Python syntax.
# Unknown characters like @, $, `, ~ etc. are intentionally excluded so the
# lexer can report them as errors.
_SYMBOLS = set('+-*/=<>!:(),.[]{}"\'')


def _classify(word: str) -> str:
    """Return the token type for a matched word.

    Returns None to signal an unknown / invalid token.
    """
    if word in KEYWORD_MAP:
        return "KEYWORD"
    if re.fullmatch(r'[a-zA-Z_]\w*', word):
        return "IDENT"
    if re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', word):
        return "NUMBER"
    if (word.startswith('"') and word.endswith('"')) or \
       (word.startswith("'") and word.endswith("'")):
        return "STRING"
    if word.startswith('#'):
        return "COMMENT"
    if word.strip() == '':          # pure whitespace / newlines
        return "WHITESPACE"
    if len(word) == 1 and word in _SYMBOLS:
        return "SYMBOL"
    return None                     # unknown token


def tokenize(source: str) -> LexerResult:
    """Tokenize PussyCat source code into a list of tokens.

    Scans left-to-right using the master regex.  Each match is classified
    and appended to the token list.  If an unrecognised token is found the
    function returns immediately with a LexerError — no partial stream is
    passed downstream.

    Never raises an exception; all error paths return a LexerResult with
    the error field set.
    """
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
