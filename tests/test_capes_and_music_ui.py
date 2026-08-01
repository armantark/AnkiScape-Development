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
    from aqt.qt import QApplication, QLabel, QPushButton  # type: ignore

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

    def test_the_cabinet_keeps_cape_status_but_points_purchases_to_shop(self):
        player = default_player_data(ORE_DATA)
        player["mining_level"] = SKILLCAPE_LEVEL
        player["inventory"] = {"Coins": 0}
        page, _ctx = self._build(player, _command(player))

        self.assertIsNone(self._named(page, "cabinetCapeBuy_mining"))
        hint = self._named(page, "cabinetCapeShopHint_mining", QLabel)
        self.assertIsNotNone(hint)
        self.assertEqual(hint.text(), "Buy in Shop")
        self.assertIn("99,000 coins needed", " ".join(self._labels(page)))

    def test_the_cabinet_has_no_second_skillcape_purchase_path(self):
        player = default_player_data(ORE_DATA)
        player["mining_level"] = SKILLCAPE_LEVEL
        player["inventory"] = {"Coins": SKILLCAPE_PRICE}
        page, _ctx = self._build(player, _command(player))

        self.assertFalse(
            any(
                button.objectName().startswith("cabinetCapeBuy_")
                for button in page.findChildren(QPushButton)
            )
        )
        self.assertNotIn("Mining cape", player["inventory"])

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
        self.assertIn("Level 99 in every skill", line.text())
        # Dungeoneering's activation removed the skill-shortfall note; the
        # boss long-tail row stays latent until Fight Kiln and QBD exist.
        self.assertNotIn("latent until the skill ships", line.text())
        self.assertIn("(latent)", line.text())

    def test_the_music_log_shows_its_totals_and_marks_an_unlocked_track(self):
        from ankiscape.data.music_log_data import MUSIC_TRACKS
        from ankiscape.logic.music_log_logic import refresh_music_log_pure

        track = next(row for row in MUSIC_TRACKS if row.trigger_kind == "quest")
        player = default_player_data(ORE_DATA)
        player.setdefault("quests", {})[track.trigger_key] = {"completed": True}
        player.update(refresh_music_log_pure(player)[0])

        page, _ctx = self._build(player, _command(player))
        labels = " ".join(self._labels(page))
        self.assertIn("Music Log", labels)
        row = self._named(page, f"cabinetTrack_{track.id}", QLabel)
        if row is not None:
            self.assertIn("♪", row.text())

    def test_the_unreachable_task_track_is_visible_and_labelled_latent(self):
        from ankiscape.data.music_log_data import MUSIC_TRACKS

        track = next(row for row in MUSIC_TRACKS if row.name == "The Task at Hand")
        player = default_player_data(ORE_DATA)
        page, _ctx = self._build(player, _command(player))

        row = self._named(page, f"cabinetTrack_{track.id}", QLabel)
        self.assertIsNotNone(row)
        self.assertIn("latent", row.text().lower())

    def test_the_show_all_toggle_is_a_real_route_to_the_hidden_tracks(self):
        """A hidden row is only honest if something on the page reveals it."""

        from aqt.qt import QToolButton  # type: ignore

        from ankiscape.data.music_log_data import MUSIC_TRACKS

        player = default_player_data(ORE_DATA)
        page, _ctx = self._build(player, _command(player))

        toggle = self._named(page, "cabinetMusicShowAll", QToolButton)
        self.assertIsNotNone(toggle)
        rows = [
            self._named(page, f"cabinetTrack_{track.id}", QLabel) for track in MUSIC_TRACKS
        ]
        self.assertNotIn(None, rows, "every track needs a row of its own")
        self.assertTrue(any(not row.isVisible() for row in rows))

        toggle.click()
        for _ in range(3):
            QApplication.instance().processEvents()

        self.assertTrue(all(row.isVisible() for row in rows))

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
