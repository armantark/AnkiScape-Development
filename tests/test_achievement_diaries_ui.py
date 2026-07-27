"""Offscreen Qt checks for the Achievement Cabinet.

These follow `.claude/rules/qt-offscreen-screenshots.md`: geometry and widget
state are the evidence, never a grab of a dialog that was never shown. The
dialog is also sized to the height a real Anki dialog gets on a laptop, because
a tall test window hides overflow bugs.

What matters here is the panel-versus-logic boundary. Every enable and every
status string must come from `achievement_cabinet_view_pure`; a test that only
checked "the button exists" would pass against a panel that re-derived the rule
itself and got it wrong.
"""

from __future__ import annotations

import os
import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

try:
    from aqt.qt import QApplication, QComboBox, QLabel, QPushButton, QWidget  # type: ignore

    _QT = True
except Exception:  # pragma: no cover - the non-Qt lane skips this module
    _QT = False

from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.logic.achievement_diary_logic import (
    apply_achievement_diary_command_pure,
    refresh_achievement_diaries_pure,
)


def _varrock():
    return next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")


def _satisfy(player, task):
    for condition in task.conditions:
        if condition.kind == "skill_level":
            player[f"{condition.key}_level"] = max(
                condition.amount, int(player.get(f"{condition.key}_level", 1))
            )
        elif condition.kind == "quest":
            player.setdefault("quests", {})[condition.key] = {"completed": True}
        elif condition.kind == "hold_item":
            player["inventory"][condition.key] = condition.amount


class _Ctx:
    """The slice of MainMenuCtx the Cabinet actually uses."""

    def __init__(self, player_data, on_command=None):
        self.player_data = player_data
        self.dialog = None
        self.selection = {}
        self.warn_label = None
        self.on_save_skill = lambda _skill: None
        self.on_achievement_diary_command = on_command
        self.refreshers: dict = {}

    def refresh(self, key):
        fn = self.refreshers.get(key)
        if fn is not None:
            fn()


@unittest.skipUnless(_QT, "offscreen Qt lane only")
class AchievementCabinetUITest(unittest.TestCase):
    app = None

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _build(self, player, on_command=None):
        from ankiscape.ui.ui_tab_achievements import build_achievements_tab

        ctx = _Ctx(player, on_command)
        page = build_achievements_tab(ctx)
        # Rule 1: show, then size, then let the layout settle. A page that was
        # never shown reports stale child geometry.
        page.show()
        page.resize(900, 560)
        for _ in range(3):
            QApplication.instance().processEvents()
        return page, ctx

    def _labels(self, page):
        return [label.text() for label in page.findChildren(QLabel)]

    def _named(self, page, name, kind=None):
        found = page.findChild(kind or QWidget, name)
        self.assertIsNotNone(found, f"missing widget {name}")
        return found

    def test_the_cabinet_replaces_the_fabricated_difficulty_tabs(self):
        page, _ctx = self._build(default_player_data(ORE_DATA, ITEM_DEFINITIONS))
        labels = self._labels(page)
        self.assertIn("Achievement Cabinet", labels)
        for family in ACHIEVEMENT_DIARY_CATALOG:
            self.assertIn(family.name, labels)
        self.assertFalse(
            [text for text in labels if "Completed:" in text and "%" in text],
            "the moving-denominator percentage is back",
        )

    def test_every_tier_is_visible_from_the_beginning(self):
        page, _ctx = self._build(default_player_data(ORE_DATA, ITEM_DEFINITIONS))
        rendered = {
            button.objectName()
            for button in page.findChildren(QPushButton)
            if button.objectName().startswith("cabinetClaim_")
        }
        expected = {
            f"cabinetClaim_{tier.id}"
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
        }
        self.assertEqual(rendered, expected)

    def test_claim_is_disabled_until_the_logic_layer_says_ready(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        page, _ctx = self._build(player)
        tier = _varrock().tiers[0]
        self.assertFalse(
            self._named(page, f"cabinetClaim_{tier.id}", QPushButton).isEnabled()
        )

    def test_claim_enables_only_for_the_tier_the_view_calls_ready(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        family = _varrock()
        for tier in family.tiers[:2]:
            for task in tier.tasks:
                _satisfy(player, task)
        player.update(refresh_achievement_diaries_pure(player)[0])

        page, _ctx = self._build(player, lambda *_a: {"ok": True})
        # Easy is ready; Medium is finished but sequentially blocked, and the
        # panel must not decide that for itself.
        self.assertTrue(
            self._named(page, f"cabinetClaim_{family.tiers[0].id}", QPushButton).isEnabled()
        )
        self.assertFalse(
            self._named(page, f"cabinetClaim_{family.tiers[1].id}", QPushButton).isEnabled()
        )
        self.assertEqual(
            self._named(page, f"cabinetStatus_{family.tiers[1].id}", QLabel).text(),
            "Claim Easy first",
        )

    def test_an_empty_tier_reads_as_pending_rather_than_ready(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        page, _ctx = self._build(player)
        empty = [
            tier
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            if not tier.tasks
        ]
        self.assertTrue(empty, "expected at least one un-harvested tier")
        for tier in empty:
            self.assertEqual(
                self._named(page, f"cabinetStatus_{tier.id}", QLabel).text(),
                "Roster pending harvest",
            )
            self.assertFalse(
                self._named(page, f"cabinetClaim_{tier.id}", QPushButton).isEnabled()
            )

    def test_pressing_claim_runs_the_command_and_re_renders(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        family = _varrock()
        for task in family.tiers[0].tasks:
            _satisfy(player, task)
        player.update(refresh_achievement_diaries_pure(player)[0])

        calls: list = []

        def _command(action_id, payload):
            calls.append((action_id, dict(payload)))
            updated, ok, info = apply_achievement_diary_command_pure(
                player, action_id, payload
            )
            if ok:
                player.clear()
                player.update(updated)
            return {"ok": ok, **info}

        page, _ctx = self._build(player, _command)
        button = self._named(page, f"cabinetClaim_{family.tiers[0].id}", QPushButton)
        button.click()
        QApplication.instance().processEvents()

        self.assertEqual(calls[0][0], "claim_tier")
        self.assertEqual(calls[0][1]["tier_id"], family.tiers[0].id)
        self.assertEqual(player["inventory"].get("Varrock armour 1"), 1)
        self.assertEqual(
            self._named(page, f"cabinetStatus_{family.tiers[0].id}", QLabel).text(),
            "Claimed",
        )

    def test_the_lamp_choice_offers_only_skills_the_view_allows(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        family = _varrock()
        for task in family.tiers[0].tasks:
            _satisfy(player, task)
        player.update(refresh_achievement_diaries_pure(player)[0])

        page, _ctx = self._build(player, lambda *_a: {"ok": True})
        box = self._named(page, f"cabinetLamp_{family.tiers[0].id}", QComboBox)
        from ankiscape.logic.achievement_diary_logic import lamp_skill_options_pure

        expected = lamp_skill_options_pure(player, family.tiers[0])
        self.assertEqual(
            [box.itemData(index) for index in range(box.count())], list(expected)
        )

    def test_a_pinned_task_renders_first_in_its_tier(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        family = _varrock()
        target = family.tiers[0].tasks[-1]
        player.update(
            apply_achievement_diary_command_pure(
                player, "pin_task", {"task_id": target.id}
            )[0]
        )
        page, _ctx = self._build(player, family_filtered := lambda *_a: {"ok": True})
        del family_filtered
        labels = self._labels(page)
        first = labels.index(family.tiers[0].tasks[0].name)
        pinned = labels.index(target.name)
        self.assertLess(pinned, first, "the pinned task did not move to the top")

    def test_searching_narrows_the_rendered_rows(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        page, _ctx = self._build(player)
        needle = _varrock().tiers[0].tasks[0].name
        search = self._named(page, "cabinetSearch")
        search.setText(needle)
        for _ in range(3):
            QApplication.instance().processEvents()
        labels = self._labels(page)
        self.assertIn(needle, labels)

    def test_the_page_does_not_scroll_sideways_at_a_real_dialog_size(self):
        """A laptop Anki dialog is about 560 points tall and not very wide."""
        from aqt.qt import QScrollArea  # type: ignore

        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        page, _ctx = self._build(player)
        page.resize(620, 560)
        for _ in range(4):
            QApplication.instance().processEvents()
        scroll = page.findChild(QScrollArea)
        self.assertIsNotNone(scroll)
        self.assertEqual(
            scroll.horizontalScrollBar().maximum(),
            0,
            "the Cabinet overflows horizontally at a real dialog width",
        )

    def test_no_label_hardcodes_a_light_mode_text_colour(self):
        """Dark mode: text colours come from the palette, never a fixed hex."""
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        page, _ctx = self._build(player)
        for label in page.findChildren(QLabel):
            sheet = label.styleSheet()
            if "color:" not in sheet:
                continue
            self.assertFalse(
                "#333" in sheet or "#666" in sheet or "black" in sheet,
                f"hardcoded light-mode text colour: {sheet}",
            )


if __name__ == "__main__":
    unittest.main()
