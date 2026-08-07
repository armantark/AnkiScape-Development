"""Offscreen Qt checks for the cape, Music Log and Taskmaster surfaces.

Follows `.claude/rules/qt-offscreen-screenshots.md`: widget state and geometry
are the evidence, and the page is shown before it is sized so the layout has
actually settled. The dialog is sized to the height a real Anki dialog gets on
a laptop, because a tall test window hides overflow.

The boundary under test is the same one the Cabinet already defends: every
enable, every price and every status string comes from the view, so a panel that
re-derived a rule and got it wrong would fail here rather than ship.
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
    from aqt.qt import QApplication, QLabel, QPushButton, QTreeWidget  # type: ignore

    _QT = True
except Exception:  # pragma: no cover - the non-Qt lane skips this module
    _QT = False

from ankiscape.core.constants import ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.achievement_cape_data import SKILLCAPE_LEVEL, SKILLCAPE_PRICE
from ankiscape.logic.achievement_diary_logic import apply_achievement_diary_command_pure


class _Ctx:
    """The slice of MainMenuCtx these panels actually use."""

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


def _command(player):
    """A real dispatcher over a real save: no fake agreeing with itself."""

    def run(action_id, payload):
        updated, ok, info = apply_achievement_diary_command_pure(player, action_id, payload)
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, **info}

    return run


@unittest.skipUnless(_QT, "offscreen Qt lane only")
class CabinetCapeAndMusicUITest(unittest.TestCase):
    app = None

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _build(self, player, on_command=None):
        from ankiscape.ui.ui_tab_achievements import build_achievements_tab

        ctx = _Ctx(player, on_command)
        page = build_achievements_tab(ctx)
        page.show()
        page.resize(900, 560)
        for _ in range(3):
            QApplication.instance().processEvents()
        return page, ctx

    def _named(self, page, name, kind=None):
        # Resolved here rather than as a default argument: the non-Qt lane
        # imports this module to skip it, and a Qt class in a signature would
        # fail at class-definition time.
        widget_class = QPushButton if kind is None else kind
        return next(
            (w for w in page.findChildren(widget_class) if w.objectName() == name), None
        )

    def _labels(self, page):
        return [label.text() for label in page.findChildren(QLabel)]

    def test_capes_are_display_only_in_the_cabinet(self):
        player = default_player_data(ORE_DATA)
        player["mining_level"] = SKILLCAPE_LEVEL
        player["inventory"] = {"Coins": SKILLCAPE_PRICE}
        page, _ctx = self._build(player, _command(player))

        purchase_buttons = [
            button
            for button in page.findChildren(QPushButton)
            if button.objectName().startswith("cabinetCapeBuy_")
        ]
        self.assertEqual(purchase_buttons, [])
        labels = " ".join(self._labels(page))
        self.assertIn("Mining cape", labels)
        self.assertIn("99,000 coins", labels)

    def test_the_keepsake_line_names_the_first_99(self):
        player = default_player_data(ORE_DATA)
        player["capes"] = {"version": 1, "keepsake_skill": "mining"}
        page, _ctx = self._build(player, _command(player))

        keepsake = self._named(page, "cabinetKeepsake", QLabel)
        self.assertIsNotNone(keepsake)
        self.assertIn("Mining cape", keepsake.text())

    def test_the_completionist_line_lists_what_is_outstanding(self):
        player = default_player_data(ORE_DATA)
        page, _ctx = self._build(player, _command(player))

        line = self._named(page, "cabinetCompletionistRequirements", QLabel)
        self.assertIsNotNone(line)
        self.assertIn("Maximum level in every skill", line.text())
        self.assertNotIn("latent until the skill ships", line.text())
        self.assertIn("Fight Kiln completed (latent)", line.text())
        self.assertIn("Queen Black Dragon", line.text())

        trim = self._named(page, "cabinetTrimmedCompletionistRequirements", QLabel)
        self.assertIsNotNone(trim)
        self.assertIn("5,000 Castle Wars games", trim.text())
        self.assertNotIn("5,000 Castle Wars games (latent)", trim.text())

    def test_the_cabinet_keeps_only_a_compact_music_summary(self):
        player = default_player_data(ORE_DATA)
        page, _ctx = self._build(player, _command(player))

        summary = self._named(page, "cabinetMusicSummary", QLabel)
        self.assertIsNotNone(summary)
        self.assertIn("Collections", summary.text())
        self.assertFalse(
            any(label.objectName().startswith("cabinetTrack_") for label in page.findChildren(QLabel))
        )

    def test_collections_keeps_player_facing_music_text_without_source_or_state(self):
        from ankiscape.data.music_log_data import MUSIC_TRACKS
        from ankiscape.logic.music_log_logic import refresh_music_log_pure
        from ankiscape.ui.ui_tab_collections import build_collections_tab

        track = next(row for row in MUSIC_TRACKS if row.trigger_kind == "quest")
        player = default_player_data(ORE_DATA)
        player.setdefault("quests", {})[track.trigger_key] = {"completed": True}
        player.update(refresh_music_log_pure(player)[0])
        ctx = _Ctx(player, _command(player))
        page = build_collections_tab(ctx)
        page.show()
        page.resize(900, 560)
        for _ in range(3):
            QApplication.instance().processEvents()

        tree = self._named(page, "collectionsMusicTracks", QTreeWidget)
        self.assertIsNotNone(tree)
        self.assertEqual(tree.topLevelItemCount(), len(MUSIC_TRACKS))
        item = next(
            tree.topLevelItem(index)
            for index in range(tree.topLevelItemCount())
            if tree.topLevelItem(index).text(0) == track.name
        )
        self.assertEqual(item.text(0), track.name)
        rendered = " ".join(
            tree.topLevelItem(index).text(0)
            for index in range(tree.topLevelItemCount())
        )
        self.assertNotIn(track.source, rendered)
        self.assertNotIn("oldid", rendered.lower())
        self.assertNotIn("trace", rendered.lower())
        self.assertNotIn("Unlocked", rendered)
        self.assertNotIn("Locked", rendered)
        self.assertNotIn("Latent", rendered)

    def test_collections_labels_the_task_track_locked_until_350_tasks(self):
        from ankiscape.data.music_log_data import MUSIC_TRACKS
        from ankiscape.ui.ui_tab_collections import build_collections_tab

        ctx = _Ctx(default_player_data(ORE_DATA))
        page = build_collections_tab(ctx)
        page.show()
        page.resize(900, 560)
        for _ in range(3):
            QApplication.instance().processEvents()

        tree = self._named(page, "collectionsMusicTracks", QTreeWidget)
        track = next(row for row in MUSIC_TRACKS if row.name == "The Task at Hand")
        item = next(
            tree.topLevelItem(index)
            for index in range(tree.topLevelItemCount())
            if tree.topLevelItem(index).text(0) == track.hint
        )
        self.assertEqual(item.text(0), "by completing 350 Tasks.")
        self.assertFalse(
            any(
                tree.topLevelItem(index).text(0) == "The Task at Hand"
                for index in range(tree.topLevelItemCount())
            )
        )

    def test_collections_drop_log_conceals_then_reveals_and_dims_rows(self):
        from ankiscape.ui.ui_tab_collections import build_collections_tab

        def build(player):
            ctx = _Ctx(player)
            page = build_collections_tab(ctx)
            page.show()
            page.resize(900, 560)
            for _ in range(3):
                QApplication.instance().processEvents()
            return page

        hidden_player = default_player_data(ORE_DATA)
        hidden_page = build(hidden_player)
        hidden_nav = self._named(hidden_page, "collectionsFamilyTree", QTreeWidget)
        self.assertEqual(hidden_nav.width(), 244)
        hidden_drop_family = hidden_nav.topLevelItem(1)
        hidden_chicken = next(
            hidden_drop_family.child(index)
            for index in range(hidden_drop_family.childCount())
            if hidden_drop_family.child(index).text(0) == "Chicken"
        )
        hidden_nav.setCurrentItem(hidden_chicken)
        QApplication.instance().processEvents()
        hidden_names = [
            label.text()
            for label in hidden_page.findChildren(QLabel)
            if label.objectName().startswith("collectionsDropName::chicken::")
        ]
        self.assertEqual(hidden_names, ["???", "???", "???"])

        player = default_player_data(ORE_DATA)
        player["combat_kill_counts"] = {"chicken": 1}
        player["combat_observed_drops"] = {
            "chicken": {
                "Bones": {"times_seen": 1, "quantity_seen": 1},
            }
        }
        page = build(player)
        nav = self._named(page, "collectionsFamilyTree", QTreeWidget)
        drop_family = nav.topLevelItem(1)
        chicken = next(
            drop_family.child(index)
            for index in range(drop_family.childCount())
            if drop_family.child(index).text(0) == "Chicken"
        )
        nav.setCurrentItem(chicken)
        QApplication.instance().processEvents()

        names = {
            label.text(): label.parentWidget()
            for label in page.findChildren(QLabel)
            if label.objectName().startswith("collectionsDropName::chicken::")
        }
        self.assertEqual(set(names), {"Bones", "Raw chicken", "Feather"})
        self.assertIsNone(names["Bones"].graphicsEffect())
        self.assertAlmostEqual(names["Feather"].graphicsEffect().opacity(), 0.58)
        self.assertEqual(chicken.text(1), "1/3")
        family_counts = [
            tuple(
                int(value)
                for value in nav.topLevelItem(index).text(1).split("/", 1)
            )
            for index in range(2)
        ]
        self.assertEqual(
            self._named(page, "collectionsGlobalTotals", QLabel).text(),
            "Collected "
            f"{sum(count[0] for count in family_counts)} / "
            f"{sum(count[1] for count in family_counts)} overall",
        )
        rendered = [label.text() for label in page.findChildren(QLabel)]
        for tree in page.findChildren(QTreeWidget):
            pending = [
                tree.topLevelItem(index)
                for index in range(tree.topLevelItemCount())
            ]
            while pending:
                item = pending.pop()
                rendered.extend(
                    item.text(column) for column in range(tree.columnCount())
                )
                pending.extend(
                    item.child(index) for index in range(item.childCount())
                )
        surface_text = " ".join(rendered).lower()
        for forbidden in (
            "/users/",
            "oldid",
            "trace",
            "source_status",
            "encounter_only",
            "target_id",
        ):
            self.assertNotIn(forbidden, surface_text)

    def test_the_taskmaster_presentation_appears_once_and_the_button_clears_it(self):
        player = default_player_data(ORE_DATA)
        diaries = dict(player["achievement_diaries"])
        diaries["taskmaster"] = True
        player["achievement_diaries"] = diaries

        page, _ctx = self._build(player, _command(player))
        button = self._named(page, "cabinetTaskmasterAcknowledge")
        self.assertIsNotNone(button)
        button.click()
        for _ in range(3):
            QApplication.instance().processEvents()

        self.assertTrue(player["achievement_diaries"]["taskmaster_presented"])
        self.assertIsNone(self._named(page, "cabinetTaskmasterAcknowledge"))

    def test_nothing_is_presented_before_taskmaster_is_earned(self):
        page, _ctx = self._build(default_player_data(ORE_DATA))
        self.assertIsNone(self._named(page, "cabinetTaskmasterAcknowledge"))

    def test_the_page_never_scrolls_sideways_at_the_real_dialog_size(self):
        """620 points wide is what a laptop Anki dialog actually gets."""

        player = default_player_data(ORE_DATA)
        player["mining_level"] = SKILLCAPE_LEVEL
        page, _ctx = self._build(player, _command(player))
        page.resize(620, 560)
        for _ in range(3):
            QApplication.instance().processEvents()

        from aqt.qt import QScrollArea  # type: ignore

        for scroll in page.findChildren(QScrollArea):
            self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)


@unittest.skipUnless(_QT, "offscreen Qt lane only")
class ShopSkillcapeSectionUITest(unittest.TestCase):
    """The shop's Skillcapes subsection, extended from the Agility row."""

    app = None

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_a_level_one_player_sees_a_hint_rather_than_dead_master_buttons(self):
        from ankiscape.logic.cape_logic import cape_view_pure

        view = cape_view_pure(default_player_data(ORE_DATA))
        self.assertFalse(any(row["show_in_shop"] for row in view["skillcapes"]))

    def test_reaching_99_puts_exactly_that_master_s_row_in_the_shop(self):
        from ankiscape.logic.cape_logic import cape_view_pure

        player = default_player_data(ORE_DATA)
        player["mining_level"] = SKILLCAPE_LEVEL
        view = cape_view_pure(player)
        shown = [row for row in view["skillcapes"] if row["show_in_shop"]]
        self.assertEqual([row["cape_id"] for row in shown], ["mining"])
        self.assertEqual(shown[0]["master"], "Dwarf")
        self.assertEqual(shown[0]["price"], SKILLCAPE_PRICE)


if __name__ == "__main__":
    unittest.main()
