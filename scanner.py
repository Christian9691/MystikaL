from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from spellbook import SPELLBOOK

SIGNS = frozenset("+-*/=<>!:(),.[]{};%^&|~")


class Kind(Enum):
    SPELL = auto()    # a magic word from the spellbook
    NAME = auto()     # an ordinary identifier
    NUMBER = auto()
    TEXT = auto()     # string literal
    SIGN = auto()     # operator / punctuation
    NOTE = auto()     # comment
    GAP = auto()      # whitespace (kept so indentation survives)


@dataclass(frozen=True)
class Rune:
    kind: Kind
    text: str
    line: int
    col: int


@dataclass
class ScanOutcome:
    runes: Optional[list[Rune]]
    problem: Optional[str]


class ScanError(Exception):
    def __init__(self, line: int, col: int, message: str):
        super().__init__(message)
        self.line, self.col, self.message = line, col, message


class _Cursor:
    def __init__(self, source: str):
        self.src = source
        self.pos = 0
        self.line = 1
        self.col = 1

    def peek(self, ahead: int = 0) -> str:
        i = self.pos + ahead
        return self.src[i] if i < len(self.src) else ""

    def take(self) -> str:
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def take_while(self, test) -> str:
        start = self.pos
        while self.peek() and test(self.peek()):
            self.take()
        return self.src[start:self.pos]

    def at_end(self) -> bool:
        return self.pos >= len(self.src)


def _read_text(cur: _Cursor) -> str:
    """Read a quoted string (single, double or triple-quoted)."""
    start_line, start_col = cur.line, cur.col
    quote = cur.peek()
    begin = cur.pos
    triple = cur.src.startswith(quote * 3, cur.pos)

    if triple:
        for _ in range(3):
            cur.take()
        while True:
            if cur.at_end():
                raise ScanError(start_line, start_col, "Triple-quoted text was never closed")
            if cur.peek() == "\\":
                cur.take()
                if not cur.at_end():
                    cur.take()
            elif cur.src.startswith(quote * 3, cur.pos):
                for _ in range(3):
                    cur.take()
                break
            else:
                cur.take()
    else:
        cur.take()
        while True:
            ch = cur.peek()
            if ch == "" or ch == "\n":
                raise ScanError(start_line, start_col, "Text was never closed")
            if ch == "\\":
                cur.take()
                if cur.peek() == "" :
                    raise ScanError(start_line, start_col, "Text was never closed")
                cur.take()
            elif ch == quote:
                cur.take()
                break
            else:
                cur.take()
    return cur.src[begin:cur.pos]


def _read_number(cur: _Cursor) -> str:
    begin = cur.pos
    cur.take_while(str.isdigit)
    if cur.peek() == "." and cur.peek(1).isdigit():
        cur.take()
        cur.take_while(str.isdigit)
    return cur.src[begin:cur.pos]


def scan(source: str) -> ScanOutcome:
    """Turn source text into runes. Never raises; problems come back as text."""
    if not isinstance(source, str):
        return ScanOutcome(None, "[Scanner] Source must be text")

    cur = _Cursor(source)
    runes: list[Rune] = []

    try:
        while not cur.at_end():
            line, col = cur.line, cur.col
            ch = cur.peek()

            if ch.isspace():
                runes.append(Rune(Kind.GAP, cur.take_while(str.isspace), line, col))
            elif ch == "#":
                runes.append(Rune(Kind.NOTE, cur.take_while(lambda c: c != "\n"), line, col))
            elif ch.isalpha() or ch == "_":
                word = cur.take_while(lambda c: c.isalnum() or c == "_")
                kind = Kind.SPELL if word in SPELLBOOK else Kind.NAME
                runes.append(Rune(kind, word, line, col))
            elif ch.isdigit():
                runes.append(Rune(Kind.NUMBER, _read_number(cur), line, col))
            elif ch in "\"'":
                runes.append(Rune(Kind.TEXT, _read_text(cur), line, col))
            elif ch in SIGNS:
                runes.append(Rune(Kind.SIGN, cur.take(), line, col))
            else:
                raise ScanError(line, col, f"Unknown rune {ch!r}")
    except ScanError as err:
        return ScanOutcome(None, f"[Scanner] Line {err.line}, column {err.col}: {err.message}")

    return ScanOutcome(runes, None)