"""Placeholders must be findable, and the register must not drift from the code.

The breadth phase allows a placeholder to stand in for a value that would need an
intense source dig, so the mechanic around it can ship complete. The danger is
that a placeholder quietly becomes canon — which happened twice on the day this
rule was written, with an invented Daily Challenges reroll and an invented Fish
Flingers weight. Both survived review because nothing distinguished them from
settled values.

This test is that distinction. Every `PLACEHOLDER(<id>)` marker in the code must
appear in `memory-bank/placeholder-values.md`, and every id in the register must
still exist in the code. Drift in either direction fails, so the register cannot
rot into a list of things that were fixed years ago, and a placeholder cannot hide
by simply not being written down.
"""

from __future__ import annotations

import os
import re
import unittest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_THIS_DIR)
_REGISTER = os.path.join(_ROOT, "memory-bank", "placeholder-values.md")

_MARKER = re.compile(r"PLACEHOLDER\(([A-Za-z0-9_.-]+)\)")
_SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv-qt",
    "memory-bank",
    "tools",
    "tests",
}


def _markers_in_code() -> dict[str, list[str]]:
    """Every PLACEHOLDER id in the shipped add-on, with where it appears."""
    found: dict[str, list[str]] = {}
    for dirpath, dirnames, filenames in os.walk(_ROOT):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            path = os.path.join(dirpath, filename)
            relative = os.path.relpath(path, _ROOT)
            with open(path, encoding="utf-8", errors="ignore") as handle:
                for number, line in enumerate(handle, 1):
                    for marker in _MARKER.finditer(line):
                        found.setdefault(marker.group(1), []).append(
                            f"{relative}:{number}"
                        )
    return found


def _ids_in_register() -> set[str]:
    if not os.path.isfile(_REGISTER):
        return set()
    ids: set[str] = set()
    with open(_REGISTER, encoding="utf-8") as handle:
        for line in handle:
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if not cells or cells[0] in {"id", "---"} or set(cells[0]) <= {"-"}:
                continue
            ids.add(cells[0].strip("`"))
    return ids


class PlaceholderRegisterTest(unittest.TestCase):
    def test_every_placeholder_in_code_is_registered(self):
        code = _markers_in_code()
        unregistered = sorted(set(code) - _ids_in_register())

        self.assertEqual(
            unregistered,
            [],
            "these placeholders are in the code but not in "
            "memory-bank/placeholder-values.md, so nobody can find them later: "
            + "; ".join(f"{i} at {', '.join(code[i])}" for i in unregistered),
        )

    def test_the_register_names_no_placeholder_that_is_gone(self):
        """A register that outlives its placeholders becomes noise."""
        stale = sorted(_ids_in_register() - set(_markers_in_code()))

        self.assertEqual(
            stale,
            [],
            "these ids are registered but no longer appear in the code; delete "
            "their rows: " + ", ".join(stale),
        )

    def test_the_marker_pattern_actually_matches_the_documented_form(self):
        """Guard the guard: the scanner must recognise the form we tell people to write."""
        sample = '    RATE = 0.25  # PLACEHOLDER(fish_flingers.big_fish): needs the period roll'
        self.assertEqual(
            _MARKER.findall(sample), ["fish_flingers.big_fish"]
        )
        self.assertEqual(_MARKER.findall("# placeholder(lowercase): ignored"), [])


if __name__ == "__main__":
    unittest.main()
