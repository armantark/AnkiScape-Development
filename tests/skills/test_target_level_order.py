"""Every skill's target list renders in level order, flat and per tree group.

Owner note 2026-08-30: Herblore's targets were alphabetical inside each
group because its rows carried no sort key, and flat skills rendered rows
in data-file insertion order. Ruling 8: target lists sort by level in
every skill.
"""

import re
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    DEFAULT_MINING_TARGET,
    FLETCHED_ITEM_IMAGES,
    FLETCHING_DATA,
    GEM_IMAGES,
    HERBLORE_DATA,
    HERBLORE_ITEM_IMAGES,
    MINING_PICKAXE_DATA,
    ORE_DATA,
    ORE_IMAGES,
)
from ankiscape.core.target_metadata import (
    fletching_target_rows,
    herblore_target_rows,
    mining_target_rows,
    thieving_target_rows,
)
from ankiscape.data.thieving_data import (
    DEFAULT_THIEVING_TARGET,
    THIEVING_ITEM_IMAGES,
    THIEVING_TARGETS,
)


_LEVEL_PATTERN = re.compile(r"\(Lvl (\d+)\)")


def _levels(rows, group=None):
    """Read each row's level the way a player sees it: the rendered label.

    Sorting by sort_key first would make `levels == sorted(levels)` true by
    construction, so the level must come from the label's "(Lvl N)" tag.
    """
    members = [row for row in rows if group is None or row.group == group]
    ordered = sorted(members, key=lambda row: row.sort_key)
    return [int(_LEVEL_PATTERN.search(row.label).group(1)) for row in ordered]


class TargetLevelOrderTest(unittest.TestCase):
    def test_herblore_groups_render_in_level_order(self):
        rows = herblore_target_rows(
            {"herblore_level": 99, "inventory": {}},
            HERBLORE_DATA,
            HERBLORE_ITEM_IMAGES,
        )
        for group in ("clean", "unf", "finished"):
            levels = _levels(rows, group)
            self.assertEqual(levels, sorted(levels))
        clean_keys = [
            row.sort_key
            for row in sorted(
                (row for row in rows if row.group == "clean"),
                key=lambda row: row.sort_key,
            )
        ][:4]
        self.assertEqual(
            clean_keys,
            [
                (1, "Clean guam"),
                (3, "Clean ardrigal"),
                (3, "Clean rogue's purse"),
                (3, "Clean sito foil"),
            ],
        )

    def test_mining_flat_list_renders_in_level_order(self):
        rows = mining_target_rows(
            {
                "mining_level": 99,
                "inventory": {},
                "toolbelt": {"mining": ["dragon_pickaxe"]},
            },
            ORE_DATA,
            ORE_IMAGES,
            GEM_IMAGES,
            MINING_PICKAXE_DATA,
            DEFAULT_MINING_TARGET,
        )
        self.assertEqual(rows[0].sort_key, (1, "Rune essence"))
        levels = _levels(rows)
        self.assertEqual(levels, sorted(levels))

    def test_fletching_groups_render_in_level_order(self):
        rows = fletching_target_rows(
            {"fletching_level": 99, "inventory": {}},
            FLETCHING_DATA,
            FLETCHED_ITEM_IMAGES,
        )
        for group in {row.group for row in rows}:
            levels = _levels(rows, group)
            self.assertEqual(levels, sorted(levels))

    def test_thieving_flat_render_is_level_ordered_across_groups(self):
        # Thieving has enough rows for the flat renderer but its old key led
        # with a group index, so level order had to survive grouping.
        rows = thieving_target_rows(
            {"thieving_level": 99, "inventory": {}},
            THIEVING_TARGETS,
            THIEVING_ITEM_IMAGES,
            DEFAULT_THIEVING_TARGET,
        )
        self.assertGreater(len({row.group for row in rows}), 1)
        levels = _levels(rows)
        self.assertEqual(levels, sorted(levels))


try:
    from tests.test_main_menu_widget import (  # noqa: E402  (sets up Qt)
        MainMenuWidgetTest,
        _find_list_with_user_role,
        _find_tree_with_user_role,
        _make_player_data,
    )
    from aqt.qt import Qt

    _QT_READY = True
except Exception:  # pragma: no cover - environment without aqt installed
    _QT_READY = False


def _level_of(text: str) -> int:
    # First "(Lvl N)" is the row's own requirement; a later "at Lvl 30+"
    # describes an alternate output, not the sort level.
    return int(_LEVEL_PATTERN.search(text).group(1))


@unittest.skipUnless(_QT_READY, "aqt/PyQt6 not installed (use .venv-qt)")
class TargetLevelOrderWidgetTest(MainMenuWidgetTest, unittest.TestCase):
    """The renderers must apply sort_key: flat list and tree groups alike."""

    def test_mining_flat_list_renders_level_ordered(self):
        pd = _make_player_data()
        pd["mining_level"] = 99
        dialog = self._open(pd, current_skill="Mining")
        dialog.show()
        QApplication_processEvents()
        ore_list = _find_list_with_user_role(dialog, "copper")
        texts = [ore_list.item(i).text() for i in range(ore_list.count())]
        pairs = [
            (_level_of(text), text.removeprefix("✓ "))
            for text in texts
        ]
        self.assertEqual(pairs, sorted(pairs))
        levels = [level for level, _name in pairs]
        self.assertEqual(levels, sorted(levels))
        dialog.deleteLater()

    def test_herblore_tree_groups_render_level_ordered(self):
        pd = _make_player_data()
        pd["herblore_level"] = 99
        dialog = self._open(pd, current_skill="Herblore")
        dialog.show()
        QApplication_processEvents()
        tree = _find_tree_with_user_role(dialog, "clean_guam")
        roles = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertEqual(
            roles,
            [
                "__herblore_group__:clean",
                "__herblore_group__:unf",
                "__herblore_group__:finished",
            ],
        )
        clean = tree.topLevelItem(0)
        levels = [_level_of(clean.child(i).text(0)) for i in range(clean.childCount())]
        self.assertEqual(levels, sorted(levels))
        dialog.deleteLater()


def QApplication_processEvents():
    from aqt.qt import QApplication

    QApplication.processEvents()
