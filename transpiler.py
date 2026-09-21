"""Transpiler for PussyCat custom language.

Converts token stream to Python code.
"""

from dataclasses import dataclass
from typing import Optional
from constants import KEYWORD_MAP
from lexer import Token, LexerResult


@dataclass
class TranspileResult:
    """Result of transpilation operation."""
    python: str
    line_map: dict[int, int]


def transpile(tokens: list[Token]) -> TranspileResult:
    """Transpile token stream to Python code."""
    return TranspileResult(python="", line_map={})
