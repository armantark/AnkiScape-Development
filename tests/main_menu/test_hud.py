from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _find_named_widget, _make_player_data
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QMainWindow, QPushButton, QStackedWidget, QTreeWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_review_context_strip_is_compact_interactive_and_hides_when_empty(self) -> None:
        parent = QMainWindow()
        parent.resize(900, 620)
        parent.show()
        strip = self._ui.ReviewContextActionStrip(parent)
        calls = []
        strip.set_data(
            {
                "active": {
                    "family_id": "pit_reward",
                    "label": "Pit reward",
                    "detail": "320 Agility XP",
                    "options": (
                        {"id": "take_xp", "label": "Take XP"},
                        {"id": "gamble", "label": "Gamble"},
                    ),
                    "default_option": "take_xp",
                    "remembered_option": None,
                },
                "queued_count": 2,
            },
            lambda family_id, option_id: calls.append((family_id, option_id)),
        )
        QApplication.processEvents()

        self.assertTrue(strip.isVisible())
        self.assertLessEqual(
            len(strip.findChildren(QPushButton)),
            3,
        )
        take = strip.findChild(
            QPushButton, "reviewContextAction::pit_reward::take_xp"
        )
        gamble = strip.findChild(
            QPushButton, "reviewContextAction::pit_reward::gamble"
        )
        self.assertIsNotNone(take)
        self.assertIsNotNone(gamble)
        self.assertIn("Pit reward", take.accessibleName())
        self.assertIn("automatic on next answer", take.accessibleName())
        self.assertTrue(take.property("safeOption"))
        self.assertFalse(bool(gamble.property("safeOption")))
        self.assertNotEqual(take.focusPolicy(), Qt.FocusPolicy.NoFocus)
        self.assertIn("next card", take.toolTip())
        self.assertIn("2x, 1x, or 0.5x", gamble.toolTip())
        queue_badge = strip.findChild(QLabel, "reviewContextQueueBadge")
        self.assertTrue(queue_badge.isVisible())
        self.assertEqual(queue_badge.text(), "+2")
        self.assertEqual(
            queue_badge.accessibleName(),
            "Queued reviewer decisions",
        )
        gamble.click()
        QApplication.processEvents()
        self.assertEqual(calls, [("pit_reward", "gamble")])
        self.assertGreaterEqual(strip.x(), 8)
        self.assertGreaterEqual(strip.y(), 8)

        strip.set_data({"active": None, "queued_count": 0})
        QApplication.processEvents()
        self.assertFalse(strip.isVisible())
        strip.deleteLater()
        parent.deleteLater()

    def test_hud_recognizes_fletching_as_active_skill(self) -> None:
        hud = self._ui.ReviewHUD(None)
        self.assertTrue(
            hud.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        )
        hud.set_data(_make_player_data(), "Fletching")
        self.assertTrue(
            hud.title_lbl.text().startswith("Fletching"),
            f"HUD did not recognize Fletching; shows {hud.title_lbl.text()!r}",
        )
        self.assertFalse(hud.icon_lbl.pixmap().isNull(), "HUD has no Fletching icon")

    def test_hud_recognizes_targeted_skills(self) -> None:
        cases = (
            ("Firemaking", "current_firemaking", "logs", "Logs"),
            ("Fishing", "current_fishing", "catch_crayfish", "Catch crayfish"),
            ("Cooking", "current_cooking", "cook_shrimps", "Cook raw shrimps"),
        )
        for skill, target_key, target_id, target_label in cases:
            with self.subTest(skill):
                pd = _make_player_data()
                pd[target_key] = target_id
                hud = self._ui.ReviewHUD(None)
                hud.set_data(pd, skill)
                self.assertTrue(
                    hud.title_lbl.text().startswith(skill),
                    f"HUD did not recognize {skill}; shows {hud.title_lbl.text()!r}",
                )
                self.assertEqual(hud.target_lbl.text(), target_label)
                self.assertFalse(hud.icon_lbl.pixmap().isNull(), f"HUD has no {skill} icon")

    def test_review_hud_omits_evil_tree_world_notices(self) -> None:
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "evil_tree",
                "shop_market_clock": {"answered_cards": 20},
                "evil_tree": default_evil_tree_state_pure(),
            }
        )
        active, _ = advance_evil_tree_world_clock_pure(pd)
        active["evil_tree"]["blessing_ticks_remaining"] = 12  # two speed-1 cards
        active["evil_tree"]["blessing_tier"] = "normal"
        hud = self._ui.ReviewHUD(None)

        hud.set_data(active, "Utility / Activities")

        notice = hud.findChild(QLabel, "reviewWorldNotice")
        self.assertFalse(notice.isVisible())
        self.assertNotIn("evil tree", notice.text())
        self.assertNotIn("Evil Tree blessing", notice.text())
        # The projection itself must survive: the subtitle branch reads it.
        self.assertIn("Nurture phase", hud.sub_lbl.text())

        active["evil_tree"]["active_event"] = {}
        active["evil_tree"]["session"] = {}
        hud.set_data(active, "Utility / Activities")
        self.assertIn("awaiting an active tree", hud.sub_lbl.text())

    def test_review_hud_omits_shooting_star_world_notices(self) -> None:
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "shooting_stars",
                "mining_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "shooting_star": default_shooting_star_state_pure(),
            }
        )
        active, _ = advance_shooting_star_world_clock_pure(pd)
        hud = self._ui.ReviewHUD(None)
        hud.set_data(active, "Activities")
        notice = hud.findChild(QLabel, "reviewWorldNotice")
        self.assertFalse(notice.isVisible())
        self.assertNotIn("Shooting Star size", notice.text())
        # The projection itself must survive: the subtitle branch reads it.
        self.assertIn("stardust", hud.sub_lbl.text())

        event = active["shooting_star"]["active_event"]
        event.update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_card": 22,
            }
        )
        hud.set_data(active, "Activities")
        self.assertNotIn("Star sprite", notice.text())
        self.assertIn("ready for exchange", hud.sub_lbl.text())

    def test_review_hud_surfaces_active_fist_of_guthix_match(self) -> None:
        from ankiscape.logic.fist_of_guthix_logic import (
            default_fist_of_guthix_state_pure,
            start_fist_of_guthix_match_pure,
        )

        pd = _make_player_data()
        pd["current_utility"] = "fist_of_guthix"
        pd["fist_of_guthix"] = default_fist_of_guthix_state_pure()
        pd["fist_of_guthix"]["tutorial_complete"] = True
        active, ok, _ = start_fist_of_guthix_match_pure(
            pd, iter((0.3, 0.5, 0.2, 0.8, 0.1)).__next__
        )
        self.assertTrue(ok)
        match = active["fist_of_guthix"]["active_match"]
        match["player_charges"] = 1_240
        match["opponent_charges"] = 760
        hud = self._ui.ReviewHUD(None)

        hud.set_data(active, "Activities")

        notice = hud.findChild(QLabel, "reviewWorldNotice")
        self.assertTrue(notice.isVisible())
        self.assertIn("Fist of Guthix round 1/2", notice.text())
        self.assertIn("1,240–760 charges", notice.text())
        self.assertIn("Round 1/2", hud.sub_lbl.text())

    def test_review_hud_omits_big_chinchompa_world_notice(self) -> None:
        from ankiscape.logic.big_chinchompa_logic import (
            advance_big_chinchompa_world_clock_pure,
            default_big_chinchompa_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "big_chinchompa",
                "shop_market_clock": {"answered_cards": 60},
                "big_chinchompa": default_big_chinchompa_state_pure(),
            }
        )
        active, _ = advance_big_chinchompa_world_clock_pure(pd)
        hud = self._ui.ReviewHUD(None)

        hud.set_data(active, "Utility / Activities")

        # The reviewer overlay keeps in-progress session counters only; the
        # world event now reads on the D&D badge and the Activities strip.
        notice = hud.findChild(QLabel, "reviewWorldNotice")
        self.assertFalse(notice.isVisible())
        self.assertNotIn("Big Chinchompa", notice.text())
        # The projection itself must survive: the subtitle branch reads it.
        self.assertIn("soporith moth", hud.sub_lbl.text())
        rows = self._ui._world_event_rows(active)
        self.assertTrue(
            any(
                activity_id == "big_chinchompa" and "world min left" in text
                for activity_id, text in rows
            ),
            rows,
        )

    def test_distraction_badge_route_opens_the_named_activity_card(self) -> None:
        # The reviewer D&D badge calls this ctx entry; without it the badge
        # click would land the player on the Skills tab with no card open.
        from ankiscape.logic.big_chinchompa_logic import (
            advance_big_chinchompa_world_clock_pure,
            default_big_chinchompa_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "shop_market_clock": {"answered_cards": 60},
                "big_chinchompa": default_big_chinchompa_state_pure(),
            }
        )
        active, _ = advance_big_chinchompa_world_clock_pure(pd)
        pd.update(active)
        dialog = self._open(pd)

        navigate = self._ui._MAIN_MENU_CTX.get("open_activity")
        self.assertTrue(callable(navigate))
        navigate("big_chinchompa")
        QApplication.processEvents()

        selection = _find_named_widget(dialog, "skillListWidget")
        self.assertEqual(
            selection.currentItem().text(),
            "Distractions and Diversions",
        )
        panel = _find_named_widget(dialog, "bigChinchompaPanel")
        stack = _find_named_widget(dialog, "utilityActivityDetailsStack")
        self.assertFalse(stack.isHidden())
        self.assertIs(stack.currentWidget(), panel)
        strip = _find_named_widget(dialog, "activityWorldEventsStrip")
        # The open card already shows this event in full, so the strip drops it.
        self.assertTrue(strip.isHidden())

        activities_button = next(
            button
            for button in dialog.findChildren(QPushButton)
            if button.text() == "Activities"
        )
        activities_button.click()
        QApplication.processEvents()
        self.assertEqual(selection.currentItem().text(), "Activities")
        self.assertTrue(stack.isHidden())
        self.assertTrue(
            any(
                not tree.isHidden()
                for tree in dialog.findChildren(QTreeWidget)
                if tree.objectName() == "utilityActivityTree"
            )
        )

        # No id means "show me the list", where the strip is at the top. The
        # panel is rebuilt, so every live detail stack must be hidden.
        navigate(None)
        QApplication.processEvents()
        self.assertEqual(
            [
                w for w in dialog.findChildren(QStackedWidget)
                if w.objectName() == "utilityActivityDetailsStack" and not w.isHidden()
            ],
            [],
        )
        self.assertTrue(
            any(
                "Big Chinchompa" in lbl.text()
                for lbl in dialog.findChildren(QLabel)
                if lbl.objectName() == "activityWorldEventsBody"
            ),
            "the hub list must keep the event on its world-events strip",
        )

    def test_hud_labels_legacy_no_xp_selection_with_its_real_surface(self) -> None:
        hud = self._ui.ReviewHUD(None)
        pd = _make_player_data()
        pd["current_utility"] = "gather_flax"
        hud.set_data(pd, "Utility / Activities")
        # The title carries the surface, so a "(no XP)" tail only restated it.
        self.assertEqual(hud.title_lbl.text(), "Utilities")
        self.assertEqual(hud.sub_lbl.text(), "Gather flax")

        pd["current_utility"] = "livid_farm"
        hud.set_data(pd, "Utility / Activities")
        self.assertEqual(hud.title_lbl.text(), "Activities")

        # Bankstanding keeps its qualifier: "deliberately not training" is not
        # implied by the title.
        pd["current_utility"] = "bankstanding"
        hud.set_data(pd, "Utility / Activities")
        self.assertEqual(hud.sub_lbl.text(), "Bankstanding • idle at the Bank")

    def test_hud_names_the_landmark_it_is_bound_to(self) -> None:
        # Landmarks live outside UTILITY_ACTIVITY_DATA, so the spec lookup is
        # empty and the subtitle used to read the literal "Material prep" — the
        # owner screenshotted exactly that while running Stronghold of Security.
        # Step-counter landmarks also carry their progress, which is the other
        # half of the same report ("no indication as to what I'm actually
        # doing"); the attunement has no counter, so it carries none.
        hud = self._ui.ReviewHUD(None)
        pd = _make_player_data()
        for activity_key, expected, wants_bar in (
            ("stronghold_of_security", "Stronghold of Security • 0/4", True),
            ("knight_waves", "Knight Waves Training Ground • 0/8", True),
            ("mage_arena", "Mage Arena • 0/5", True),
            ("mage_arena_attune:saradomin", "Mage Arena attunement", False),
        ):
            with self.subTest(activity=activity_key):
                pd["current_utility"] = activity_key
                hud.set_data(pd, "Utility / Activities")
                self.assertEqual(hud.sub_lbl.text(), expected)
                self.assertNotIn("Material prep", hud.sub_lbl.text())
                self.assertEqual(hud.progress.isVisible(), wants_bar)

    def test_hud_carries_no_grand_exchange_notice(self) -> None:
        # The collect reminder now lives on the Grand Exchange tab as a
        # collapsible fill log; the HUD line was removed with it.
        hud = self._ui.ReviewHUD(None)
        pd = _make_player_data()
        pd["ge_player_orders"] = [{"collectible_coins": 0, "collectible_items": 1}]

        hud.set_data(pd, "Mining")

        self.assertIsNone(hud.findChild(QLabel, "geOfferNotice"))

    def test_resume_shows_only_at_bankstanding_and_wraps_the_longest_quest_name(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        parent = QMainWindow()
        parent.resize(900, 560)
        parent.show()
        hud = self._ui.ReviewHUD(parent)
        resume = hud.findChild(QPushButton, "reviewResumeButton")
        clicks = []
        resume.set_action(lambda: clicks.append("resume"))
        pd = _make_player_data()
        quest_id = "recipe_for_disaster_defeating_the_culinaromancer"
        pd["quests"] = {quest_id: {"started": True, "progress": 1, "completed": False}}
        pd["last_action"] = {"kind": "quest", "quest_id": quest_id}
        pd["current_utility"] = "bankstanding"

        hud.set_data(pd, "Utilities")
        for _ in range(5):
            QApplication.processEvents()

        self.assertTrue(resume.isVisible())
        self.assertEqual(
            resume.accessibleName(),
            "Resume Recipe for Disaster: Defeating the Culinaromancer",
        )
        self.assertEqual(text_fit_defects(hud), [])
        resume.click()
        self.assertEqual(clicks, ["resume"])

        pd["quests"][quest_id]["completed"] = True
        hud.set_data(pd, "Utilities")
        self.assertFalse(resume.isVisible())
        pd["quests"][quest_id]["completed"] = False
        pd["current_utility"] = "gather_flax"
        hud.set_data(pd, "Utilities")
        self.assertFalse(resume.isVisible())
        parent.deleteLater()
