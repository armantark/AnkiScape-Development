"""A target above the player's level stops at Bankstanding once, like a missing material.

The owner's Pass 11 ruling: "I think everything should just become
bankstanding." A level refusal that only showed a pop-up left the action
selected, so every card repeated the pop-up and a queued or resumed entry
above the player's level stalled the queue.
"""

from tests.integration_smoke import fixtures

# (skill, target, save fields, the reason the player reads)
_LEVEL_REFUSALS = (
    ("Mining", "iron", {}, "You need level 15 Mining to mine Iron."),
    ("Woodcutting", "oak", {}, "You need level 15 Woodcutting to chop Oak."),
    ("Fishing", "catch_mackerel_cod_bass", {}, "You need level 16 Fishing to catch mackerel/cod/bass."),
    (
        "Fishing",
        "catch_leaping_fish",
        {"fishing_level": 48, "inventory": {"Feather": 10}},
        "You need level 15 Strength and 15 Agility to catch leaping fish.",
    ),
    ("Hunter", "catch_cerulean_twitch", {"inventory": {"Bird snare": 1}}, "You need level 11 Hunter to catch cerulean twitch."),
    ("Crafting", "spin_sinew_to_crossbow_string", {"inventory": {"Sinew": 5}}, "You need level 10 Crafting to make Crossbow string."),
    ("Fletching", "longbow_u", {"inventory": {"Logs": 5}}, "You need level 10 Fletching to make Longbow (u)."),
    ("Herblore", "clean_tarromin", {}, "You need level 11 Herblore to make Clean tarromin."),
    ("Smithing", "forge_bronze_battleaxe", {}, "You need level 10 Smithing to make Bronze battleaxe."),
    ("Firemaking", "oak_logs", {}, "You need level 15 Firemaking to burn Oak logs."),
    ("Cooking", "cook_mackerel", {}, "You need level 10 Cooking to cook raw mackerel."),
    ("Runecrafting", "craft_earth_runes", {}, "You need level 9 Runecrafting for Earth runes."),
    ("Summoning", "infuse_spiritspider", {}, "You need Summoning level 10 for Infuse Spirit spider pouch."),
)


class TestIntegrationSmoke(fixtures.ReviewedProfile):
    def test_each_level_refusal_switches_to_bankstanding_once_and_keeps_its_reason(self):
        from ankiscape.core.last_action import resume_button_view_pure
        from ankiscape.core.skill_registry import get_skill

        for skill, target, fields, reason in _LEVEL_REFUSALS:
            with self.subTest(f"{skill}: {target}"):
                addon = self._addon(f"ankiscape_level_refusal_{target}")
                self._new_save(addon, **fields)
                addon._state.player_data[get_skill(skill).current_target_key] = target
                addon._state.current_skill = skill

                self._answer(addon)
                self._answer(addon)

                self.assertEqual(addon._state.current_skill, "Utilities")
                self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
                self.assertEqual(self.errors, [])
                self.assertEqual(self.bankstanding_dialogs, [reason])
                addon.load_player_data()
                self.assertEqual(
                    addon._state.player_data["last_action"],
                    {"kind": "skill", "skill": skill, "target": target, "reason": reason},
                )
                view = resume_button_view_pure(addon._state.player_data, addon._state.current_skill)
                self.assertEqual(view["bank_status"], f"stopped: {reason}")
