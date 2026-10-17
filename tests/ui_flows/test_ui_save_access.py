"""UI files draw what the logic layer decides; they do not read the save.

STANDING-SLICE-CONTRACT failure mode 4: a `*_view_pure` function owns every
enable and visibility decision, and the panel only draws its result. In
Pass 16, review found three moved panels deciding rules again, which the
implementers had missed. This test catches the mechanical part at commit: a
UI file may hand `player_data` to logic, but may not index it, call its
methods or test membership in it.
"""

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Direct save reads per UI file on 2026-10-16. The allowance only shrinks.
ALLOWED_SAVE_READS = {
    "ui/dominion_tower_panel.py": 1,
    "ui/ui.py": 178,
    "ui/ui_bank_menu.py": 8,
    "ui/ui_tab_quests.py": 3,
    "ui/ui_tab_shop.py": 5,
    "ui/ui_utility_activity_list.py": 7,
}


def _is_save(node: ast.AST) -> bool:
    return (isinstance(node, ast.Name) and node.id == "player_data") or (
        isinstance(node, ast.Attribute) and node.attr in {"player_data", "_player_data"}
    )


def _save_reads(source: str) -> int:
    reads = 0
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Subscript, ast.Attribute)):
            reads += _is_save(node.value)
        elif isinstance(node, ast.Compare):
            membership = any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops)
            reads += membership and any(map(_is_save, node.comparators))
    return reads


class UiSaveAccessTest(unittest.TestCase):
    def test_ui_files_read_the_save_only_where_already_allowed(self) -> None:
        reads = {
            path.relative_to(ROOT).as_posix(): count
            for path in sorted((ROOT / "ui").rglob("*.py"))
            if (count := _save_reads(path.read_text(encoding="utf-8")))
        }
        self.assertEqual(
            reads,
            ALLOWED_SAVE_READS,
            "A UI file above its allowance must ask a *_view_pure function for the rule"
            " and draw the result; a file below it must lower its allowance.",
        )


if __name__ == "__main__":
    unittest.main()
