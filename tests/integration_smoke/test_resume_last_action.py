"""Resume: the switch to Bankstanding saves what it stopped, and one click restarts it.

The owner's case: Black Knights' Fortress stopped for a missing Iron chainbody;
after buying one he had to dig the quest out of the Quests tab again.
"""

from tests.integration_smoke import fixtures

_BKF = "black_knights_fortress"


class TestIntegrationSmoke(fixtures.ReviewedProfile):
    def _resume_view(self, addon):
        from ankiscape.core.last_action import resume_button_view_pure

        return resume_button_view_pure(addon._state.player_data, addon._state.current_skill)

    def test_black_knights_fortress_resumes_at_its_step_once_the_chainbody_arrives(self):
        addon = self._addon("ankiscape_resume_black_knights_fortress")
        self._new_save(
            addon,
            quest_points=13,
            current_quest=_BKF,
            quests={_BKF: {"started": True, "progress": 0, "completed": False}},
        )
        addon._state.player_data["inventory"]["Bronze med helm"] = 1
        addon._state.current_skill = "Quests"

        self._answer(addon)

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(len(self.errors), 1)
        blocked = self.errors[0]
        self.assertEqual(blocked[0], "Quest blocked")
        self.assertIn("Needs Iron chainbody", blocked[1])

        addon.load_player_data()
        self.assertEqual(
            addon._state.player_data["last_action"],
            {"kind": "quest", "quest_id": _BKF, "reason": "Needs Iron chainbody"},
        )
        view = self._resume_view(addon)
        self.assertTrue(view["visible"])
        self.assertEqual(view["text"], "Resume Black Knights' Fortress")
        self.assertEqual(view["bank_status"], "stopped: Needs Iron chainbody")

        self.assertFalse(addon.on_resume_last_action())
        self.assertEqual(self.errors, [blocked, blocked])
        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")

        addon._state.player_data["inventory"]["Iron chainbody"] = 1
        self.assertTrue(addon.on_resume_last_action())
        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(self._resume_view(addon)["visible"])
        self.assertEqual(addon._state.player_data["quests"][_BKF]["progress"], 0)

        self._answer(addon)

        # An unblocked first review enters the fortress in disguise: step 0 to 2.
        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertEqual(addon._state.player_data["quests"][_BKF]["progress"], 2)
        self.assertEqual(self.errors, [blocked, blocked])

    def test_every_switch_to_bankstanding_saves_what_it_stopped_for_resume(self):
        def run_dry_crafting(addon):
            self._answer(addon)

        def stop_from_the_menu(addon):
            captured = {}
            addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
            addon._on_main_menu()
            self.assertTrue(captured["on_stop_training"]())

        def run_out_of_food(addon):
            addon._runtime_action_context().switch_to_bankstanding("No food left.")
            addon.save_player_data()

        cases = (
            (
                "a skill stopped by its review",
                "Crafting",
                {"crafting_level": 50, "current_craft": "fire_empty_pot"},
                run_dry_crafting,
                {
                    "kind": "skill",
                    "skill": "Crafting",
                    "target": "fire_empty_pot",
                    "reason": "You need 1 Pot (unfired) to craft Empty pot.",
                },
                "Resume Crafting",
            ),
            (
                "a utility stopped from the menu",
                "Utilities",
                {"current_utility": "gather_flax"},
                stop_from_the_menu,
                {"kind": "utility", "utility_id": "gather_flax", "reason": "Training was stopped manually."},
                "Resume Gather flax",
            ),
            (
                "a fight",
                "Combat",
                {"current_combat_target": "chicken", "combat_action": "attack"},
                run_out_of_food,
                {"kind": "combat", "target": "chicken", "combat_action": "attack", "reason": "No food left."},
                "Resume Combat",
            ),
        )
        for label, skill, fields, stop, record, button_text in cases:
            with self.subTest(label):
                addon = self._addon(f"ankiscape_resume_{skill.lower()}")
                self._new_save(addon, **fields)
                addon._state.current_skill = skill

                stop(addon)

                self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
                addon.load_player_data()
                self.assertEqual(addon._state.player_data["last_action"], record)
                self.assertEqual(self._resume_view(addon)["text"], button_text)

                self.assertTrue(addon.on_resume_last_action())
                self.assertEqual(addon._state.current_skill, skill)
                self.assertFalse(self._resume_view(addon)["visible"])
