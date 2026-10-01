"""A quest boss fight drives the review HUD's ordinary Combat card through real
quest reviews, and the Quests card returns once the boss falls."""

import itertools
import random
import re
import unittest

import pkg_alias  # noqa: F401
from tests import test_review_strip as _review_strip
from tests.test_runtime_actions import _context

if _review_strip.HAS_AQT:
    from aqt.qt import QApplication


_PARENT_SIZES = ((1000, 700), (900, 560))


@unittest.skipUnless(
    _review_strip.HAS_AQT,
    "aqt/PyQt6 not installed (use .venv-qt)",
)
class QuestFightCombatCardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _review_strip.ReviewStripTest.setUpClass()

    def setUp(self) -> None:
        self.strip = _review_strip.ReviewStripTest(methodName="runTest")
        self.strip.setUp()
        self.ui = self.strip.ui

    def tearDown(self) -> None:
        self.strip.tearDown()

    def _fighter(self, quest_id, stage, level):
        """A player at a quest's fight stage, mid Slayer task, with an ordinary
        combat target and kill count the quest fight must not show."""
        player = self.strip._state()
        for skill in ("attack", "strength", "defense", "constitution", "ranged", "magic"):
            player[f"{skill}_level"] = level
        player.update(
            {
                "combat_lifepoints": level * 10,
                "current_quest": quest_id,
                "current_combat_target": "chicken",
                "combat_kill_counts": {"chicken": 40},
                "slayer_assignment": {
                    "master_id": "turael_spria",
                    "family_id": "bears",
                    "initial_count": 17,
                    "remaining": 4,
                },
            }
        )
        player["quests"][quest_id] = {"started": True, "progress": stage, "completed": False}
        return player

    def _show(self, player, skill="Quests"):
        from ankiscape.core.action_registry import review_action_handler_key

        self.ui.update_review_hud(player, skill)
        self.ui.update_review_bank_run_button(player, review_action_handler_key(skill), lambda: None)
        hud = self.ui._REVIEW_HUD
        hud.show()
        for _ in range(4):
            QApplication.processEvents()
        return hud

    def _assert_fits(self, hud):
        from tests.ui_flows.qt_text_fit import text_fit_defects

        self.assertEqual(text_fit_defects(hud), [])

    def _fight(self, player, label, seed):
        """Answer quest reviews until the Combat card gives way, and return each
        review's (boss bar, player LP text) as the card showed it."""
        from ankiscape.runtime.runtime_actions_production import handle_quest_answer

        rolls = random.Random(seed)
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        ctx = _context(player, calls, random_values=[rolls.random() for _ in range(20_000)])
        ctx.cadence_live_enabled = True
        frames = []
        hud = self._show(player)
        while hud.title_lbl.text().startswith("Combat"):
            self.assertLess(len(frames), 200, "the quest fight never ended")
            self.assertEqual(hud.target_lbl.text(), label)
            self.assertTrue(hud.enemy_progress.isVisible())
            self.assertTrue(hud.combat_resources.isVisible())
            self.assertEqual(hud.chips_lbl.toolTip(), "Trains Attack • Constitution")
            self.assertFalse(hud.slayer_lbl.isVisible())
            self._assert_fits(hud)
            frames.append(
                (
                    hud.enemy_progress.value(),
                    hud.combat_resource_labels["lifepoints"].text(),
                )
            )
            self.assertTrue(handle_quest_answer(ctx))
            hud = self._show(player)
        self.assertEqual(calls["errors"], [])
        return frames, calls["activity"], hud

    def _assert_quests_card_after_the_kill(self, hud, quest_name, stage_text):
        self.assertEqual(hud.title_lbl.text(), "Quests")
        self.assertEqual(hud.target_lbl.text(), quest_name)
        self.assertEqual(hud.sub_lbl.text(), stage_text)
        for combat_only in (hud.enemy_progress, hud.combat_resources, hud.chips_lbl, hud.slayer_lbl):
            self.assertFalse(combat_only.isVisible())
        self._assert_fits(hud)

    def _assert_ordinary_combat_card_is_untouched(self, player):
        hud = self._show(player, "Combat")
        self.assertEqual(hud.target_lbl.text(), "Chicken")
        self.assertEqual(hud.chips_lbl.toolTip(), "Kills: 40 · Trains Attack • Constitution")
        self.assertEqual(hud.slayer_lbl.text(), "Slayer: 4 of 17 left")
        self._assert_fits(hud)

    def test_the_card_draws_the_wielded_weapons_trained_skills_as_icons_beside_bank_run(self):
        """Silverlight's controlled lunge trains Attack, Strength and Defence;
        bare fists have no controlled style, which is what the card read before
        it was given the equipment. The quest label, the ordinary target and the
        Slayer line all keep the icons and Bank run on one row."""
        player = self._fighter("demon_slayer", 7, 30)
        player["equipment"]["weapon"] = "Silverlight"
        cases = (
            ("controlled", "stab", ("attack", "strength", "defense", "constitution"), "Attack • Strength • Defence • Constitution"),
            ("aggressive", "slash", ("strength", "constitution"), "Strength • Constitution"),
        )
        for (style, style_type, icons, trains), skill, parent_size in itertools.product(cases, ("Quests", "Combat"), _PARENT_SIZES):
            with self.subTest(style=style, skill=skill, parent_size=parent_size):
                player.update({"combat_attack_style": style, "combat_attack_style_type": style_type})
                self.strip.parent.resize(*parent_size)
                hud = self._show(player, skill)
                lead = "Trains " if skill == "Quests" else "Kills: 40 · Trains "
                self.assertEqual(hud.chips_lbl.toolTip(), lead + trains)
                self.assertTrue(hud.chips_lbl.text().startswith(lead))
                self.assertEqual(re.findall(r"icon/(\w+)_icon\.png", hud.chips_lbl.text()), list(icons))
                self.assertEqual(hud.slayer_lbl.isVisible(), skill == "Combat")
                self.assertTrue(self.ui._BANK_RUN_BUTTON.isVisible())
                self._assert_fits(hud)

    def test_delrith_fills_the_combat_card_only_with_silverlight_and_his_bar_falls_to_the_kill(self):
        player = self._fighter("demon_slayer", 7, 30)
        hud = self._show(player)
        # Delrith takes no damage from any other weapon, so without Silverlight
        # there is no fight to show.
        self.assertEqual(hud.title_lbl.text(), "Quests")
        self.assertEqual(hud.target_lbl.text(), "Demon Slayer")
        self.assertFalse(hud.enemy_progress.isVisible())

        player["equipment"]["weapon"] = "Silverlight"
        for parent_size in _PARENT_SIZES:
            with self.subTest(parent_size=parent_size):
                self.strip.parent.resize(*parent_size)
                hud = self._show(player)
                self.assertEqual(hud.title_lbl.text(), f"Combat — Lv {self.ui.player_combat_level_pure(player)}")
                self.assertEqual(hud.target_lbl.text(), "Demon Slayer · Delrith")
                self.assertEqual(hud.enemy_progress.value(), 100)
                self.assertEqual(hud.combat_resource_labels["lifepoints"].text(), "300/300")
                self._assert_fits(hud)

        frames, activity, hud = self._fight(player, "Demon Slayer · Delrith", seed=4)
        bars = [bar for bar, _lp in frames]
        self.assertEqual(bars, sorted(bars, reverse=True))
        self.assertEqual(bars[0], 100)
        self.assertTrue(any(0 < bar < 100 for bar in bars), bars)
        self.assertEqual(activity[-1], "Defeated Delrith")
        self._assert_quests_card_after_the_kill(hud, "Demon Slayer", "Stage 7/9")
        self._assert_ordinary_combat_card_is_untouched(player)

    def test_count_draynor_resets_to_full_after_a_death_and_the_card_follows_the_retry(self):
        player = self._fighter("vampyre_slayer", 3, 30)
        player["inventory"].update({"Stake": 1, "Stake hammer": 1})

        frames, activity, hud = self._fight(player, "Vampyre Slayer · Count Draynor", seed=4)
        deaths = [index for index, line in enumerate(activity) if line.startswith("☠ YOU DIED")]
        self.assertTrue(deaths, activity)
        # Each attempt opens at full on both bars and Draynor's bar only falls
        # within it; a death sends both back to full for the retry.
        attempts, current = [], []
        for bar, lifepoints in frames:
            if bar == 100 and current and current[-1][0] < 100:
                attempts.append(current)
                current = []
            current.append((bar, lifepoints))
        attempts.append(current)
        self.assertEqual(len(attempts), len(deaths) + 1)
        for attempt in attempts:
            self.assertEqual(attempt[0], (100, "300/300"))
            attempt_bars = [bar for bar, _lp in attempt]
            self.assertEqual(attempt_bars, sorted(attempt_bars, reverse=True))
        self.assertTrue(any(lp != "300/300" for _bar, lp in frames))
        self.assertEqual(activity[-1], "Defeated Count Draynor")
        self._assert_quests_card_after_the_kill(hud, "Vampyre Slayer", "Stage 3/5")
        self._assert_ordinary_combat_card_is_untouched(player)

    def _stage_ready_player(self, quest_id, requirement, encounters):
        """A level-99 player holding everything the fight stage asks for, and
        poisoned, which lengthens the label with the longest status it carries."""
        from ankiscape.logic_pure.logic_pure_quest import _quest_stage_item_option_groups

        player = self._fighter(quest_id, requirement["stage"], 99)
        player["combat_status_effects"] = {"poison": {"ticks_left": 90, "tick_progress": 0}}
        player["inventory"].update(requirement.get("required_inventory") or {})
        player["inventory"].update(requirement.get("required_tools") or {})
        for group in _quest_stage_item_option_groups(requirement, "required_inventory_options"):
            player["inventory"][group[0][0]] = group[0][1]
        player["quest_action_proofs"] = list(requirement.get("required_actions") or ())
        player["quest_route_states"] = {quest_id: list(requirement.get("required_routes") or ())}
        weapons = [encounter["npc_configs"].get("required_weapon") for encounter in encounters]
        player["equipment"]["weapon"] = next((weapon for weapon in weapons if weapon), None)
        return player

    def _wrapped_fight_labels(self, player, quest, encounter):
        """Check the encounter's Combat card at both strip sizes and return the
        labels that took a second line."""
        wrapped = []
        for parent_size in _PARENT_SIZES:
            with self.subTest(quest=quest["id"], encounter=encounter["encounter_id"], parent_size=parent_size):
                self.strip.parent.resize(*parent_size)
                hud = self._show(player)
                if not hud.title_lbl.text().startswith("Combat"):
                    continue
                self.assertTrue(hud.target_lbl.text().startswith(f"{quest['display_name']} · "))
                self.assertTrue(hud.enemy_progress.isVisible())
                self.assertFalse(hud.slayer_lbl.isVisible())
                self.assertTrue(hud.chips_lbl.toolTip().startswith("Trains "))
                if int(encounter.get("quantity", 1) or 1) > 1:
                    self.assertRegex(hud.target_lbl.text(), r" x\d+ • Poisoned")
                self._assert_fits(hud)
                if hud.target_lbl.height() > 1.5 * hud.target_lbl.fontMetrics().lineSpacing():
                    wrapped.append(hud.target_lbl.text())
        return wrapped

    def test_every_resolvable_quest_fight_shows_its_quest_and_boss_whole_on_the_combat_card(self):
        """Walks each statted quest fight stage encounter by encounter, as the
        stage's kills land, at both strip sizes, with the label at its longest."""
        from ankiscape.core.constants import QUEST_DATA
        from ankiscape.logic_pure.logic_pure_quest import quest_combat_encounter_has_stats_pure

        wrapped = []
        stages = (
            (quest, requirement)
            for quest in QUEST_DATA.values()
            for requirement in quest.get("stage_requirements", ())
        )
        for quest, requirement in stages:
            encounters = [
                encounter
                for encounter in requirement.get("combat_encounters", ()) or ()
                if quest_combat_encounter_has_stats_pure(encounter)
            ]
            if not encounters:
                continue
            player = self._stage_ready_player(quest["id"], requirement, encounters)
            for encounter in encounters:
                wrapped += self._wrapped_fight_labels(player, quest, encounter)
                player.setdefault("quest_combat_encounters", {}).setdefault(quest["id"], []).append(
                    encounter["encounter_id"]
                )
        # The longest labels (the Recipe for Disaster subquests) take the
        # second line; the sweep must have reached them.
        self.assertTrue(any(label.startswith("Recipe for Disaster") for label in wrapped), wrapped)


if __name__ == "__main__":
    unittest.main()
