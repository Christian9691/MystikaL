"""Lexer for PussyCat custom language.

Tokenizes source code into a stream of tokens for the transpiler.
"""

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


def tokenize(source: str) -> LexerResult:
    """Tokenize source code into a list of tokens."""
    return LexerResult(tokens=[], error=None)
