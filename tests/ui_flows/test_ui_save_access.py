"""UI files draw what the logic layer decides; they do not read the save.

STANDING-SLICE-CONTRACT failure mode 4: a `*_view_pure` function owns every
enable and visibility decision, and the panel only draws its result. In
Pass 16, review found three moved panels deciding rules again, which the
implementers had missed. This test catches the mechanical part at commit: a
UI file may hand `player_data` to logic, but may not index it, call its
methods, test membership in it, loop over it or pass it to a built-in such
as `len`. A bare truth test stays free: UI code uses it to check that a save
is loaded at all.
"""

import ast
import builtins
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


def _reads_save(node: ast.AST) -> bool:
    if isinstance(node, (ast.Subscript, ast.Attribute)):
        return _is_save(node.value)
    if isinstance(node, (ast.For, ast.comprehension)):
        return _is_save(node.iter)
    if isinstance(node, ast.Compare):
        membership = any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops)
        return membership and any(map(_is_save, node.comparators))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and hasattr(builtins, node.func.id):
        return any(map(_is_save, node.args))
    return False


def _save_reads(source: str) -> int:
    return sum(map(_reads_save, ast.walk(ast.parse(source))))


class UiSaveAccessTest(unittest.TestCase):
    def test_reads_are_told_apart_from_handing_the_save_to_logic(self) -> None:
        for source, reads in (
            ('player_data["gold"]', 1),
            ('self.player_data.get("gold", 0)', 1),
            ('"gold" in player_data', 1),
            ("[key for key in player_data]", 1),
            ("len(player_data)", 1),
            ("prayer_view_pure(player_data)", 0),
            ("self.player_data = player_data", 0),
            ("if not player_data:\n    pass", 0),
        ):
            with self.subTest(source=source):
                self.assertEqual(_save_reads(source), reads)

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
