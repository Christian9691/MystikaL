from dataclasses import dataclass

from scanner import Kind, Rune
from spellbook import SPELLBOOK


@dataclass
class Weaving:
    python: str
    line_map: dict[int, int]   # python line -> mystika line


def _is_attribute_access(previous_sign: str) -> bool:
    return previous_sign == "."


def weave(runes: list[Rune]) -> Weaving:
    pieces: list[str] = []
    line_map: dict[int, int] = {}
    py_line = 1
    last_meaningful = ""   # text of the last non-gap, non-note rune

    for rune in runes:
        if rune.kind is Kind.SPELL and not _is_attribute_access(last_meaningful):
            # a spell used after a dot (obj.hati) is just a normal attribute name
            output = SPELLBOOK[rune.text]
        else:
            output = rune.text
        pieces.append(output)

        line_map.setdefault(py_line, rune.line)
        extra_lines = output.count("\n")
        for step in range(1, extra_lines + 1):
            line_map[py_line + step] = rune.line + step
        py_line += extra_lines

        if rune.kind not in (Kind.GAP, Kind.NOTE):
            last_meaningful = rune.text

    return Weaving("".join(pieces), line_map)