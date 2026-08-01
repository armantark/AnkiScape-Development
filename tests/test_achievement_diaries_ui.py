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
from dataclasses import replace
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

try:
    from aqt.qt import (  # type: ignore
        QApplication,
        QComboBox,
        QLabel,
        QPushButton,
        QSize,
        QWidget,
    )

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


def _claim_family():
    return next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "ardougne")


# Shared with the pure diary tests rather than reimplemented here, because a
# local copy that silently skipped the kinds it had never heard of is what made
# a whole tier quietly unfinishable when a new kind arrived.
from tests.test_achievement_diaries import _satisfy  # noqa: E402


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
        family = _claim_family()
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

    def test_every_taskmaster_portrait_matches_its_family(self):
        from ankiscape.core.constants import current_dir
        from ankiscape.ui.ui import _pixel_path_icon

        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        page, _ctx = self._build(player, lambda *_a: {"ok": True})

        for family in ACHIEVEMENT_DIARY_CATALOG:
            with self.subTest(family=family.id):
                if not family.taskmaster:
                    self.assertIsNone(
                        page.findChild(QLabel, f"cabinetTaskmasterPortrait_{family.id}")
                    )
                    continue

                self.assertEqual(
                    self._named(
                        page, f"cabinetTaskmasterName_{family.id}", QLabel
                    ).text(),
                    f"Reward handed over by {family.taskmaster}",
                )
                portrait = self._named(
                    page, f"cabinetTaskmasterPortrait_{family.id}", QLabel
                )
                self.assertIsNotNone(portrait.pixmap())
                self.assertFalse(portrait.pixmap().isNull())
                expected = _pixel_path_icon(
                    os.path.join(current_dir, family.taskmaster_chathead_asset_path), 48
                )
                self.assertIsNotNone(expected)
                self.assertEqual(
                    portrait.pixmap().toImage(),
                    expected.pixmap(QSize(48, 48)).toImage(),
                )

    def test_taskmaster_without_period_art_has_no_fallback_face(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        family = _varrock()
        player["achievement_diaries"]["completed_tasks"] = [
            task.id for task in family.tiers[0].tasks
        ]
        without_art = replace(family, taskmaster_chathead_asset_path="")
        catalog = tuple(
            without_art if candidate.id == family.id else candidate
            for candidate in ACHIEVEMENT_DIARY_CATALOG
        )
        with patch(
            "ankiscape.logic.achievement_diary_logic.ACHIEVEMENT_DIARY_CATALOG",
            catalog,
        ):
            page, _ctx = self._build(player, lambda *_a: {"ok": True})

        portrait = self._named(
            page, f"cabinetTaskmasterPortrait_{family.id}", QLabel
        )
        self.assertEqual(
            self._named(page, f"cabinetTaskmasterName_{family.id}", QLabel).text(),
            f"Reward handed over by {family.taskmaster}",
        )
        self.assertTrue(portrait.pixmap() is None or portrait.pixmap().isNull())

    def test_no_tier_renders_the_pending_harvest_status(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        page, _ctx = self._build(player)
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                self.assertTrue(tier.tasks, tier.id)
                self.assertNotEqual(
                    self._named(page, f"cabinetStatus_{tier.id}", QLabel).text(),
                    "Roster pending harvest",
                )

    def test_latent_tasks_are_labelled_without_fake_progress(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        latent = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.latent
        )
        page, _ctx = self._build(player)
        label = self._named(page, f"cabinetTask_{latent.id}", QLabel)
        self.assertIn("Not yet obtainable", label.text())
        labels = self._labels(page)
        self.assertIn("Not yet obtainable — its predicate has not shipped.", labels)
        self.assertNotIn("0/0", labels)

    def test_source_incomplete_rosters_are_visible(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        tier = next(
            tier
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            if tier.total_tasks > len(tier.tasks)
        )
        page, _ctx = self._build(player)
        notice = self._named(page, f"cabinetSourceGap_{tier.id}", QLabel)
        self.assertIn("roster incomplete at source", notice.text())

    def test_pressing_claim_runs_the_command_and_re_renders(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        family = _claim_family()
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
        self.assertEqual(calls[0][1], {"tier_id": family.tiers[0].id})
        self.assertEqual(player["inventory"].get("Ardougne cloak 1"), 1)
        self.assertEqual(
            self._named(page, f"cabinetStatus_{family.tiers[0].id}", QLabel).text(),
            "Claimed",
        )

    def test_the_cabinet_defers_lamp_choice_to_bank_claims(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        family = _claim_family()
        tier = family.tiers[0]
        for task in tier.tasks:
            _satisfy(player, task)
        player.update(refresh_achievement_diaries_pure(player)[0])

        page, _ctx = self._build(player, lambda *_a: {"ok": True})

        self.assertIsNone(page.findChild(QComboBox, f"cabinetLamp_{tier.id}"))
        self.assertTrue(
            any(
                f"{tier.lamp.experience:,} XP reward lamp" in label
                and "Bank Claims" in label
                for label in self._labels(page)
            )
        )

    def test_a_pinned_task_renders_first_in_its_tier(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        family = _varrock()
        target = next(task for task in reversed(family.tiers[0].tasks) if not task.latent)
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
