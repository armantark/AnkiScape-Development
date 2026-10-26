from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _load_addon_as_package,
    copy,
    sys,
    types,
)
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_prayer_composite_selection_persists_once_and_rejection_has_no_side_effects(self):
        addon = _load_addon_as_package("ankiscape_prayer_selection_integration")
        calls = {"save": 0, "hud": 0}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon._state.current_skill = "Prayer"
        target_id = "gilded_altar_dragon_bones"
        addon._state.player_data = {
            "prayer_level": 99,
            "current_prayer": target_id,
            "prayer_gilded_mode": "owned",
            "prayer_gilded_house_search": {"target_id": target_id, "reviews_remaining": 2},
            "prayer_owned_altar_stint": {"target_id": target_id, "burners_lit": 1},
            "house_owned": True,
            "house_rooms_bought": {"chapel": True},
            "house_built_flags": {"guilded_altar": True, "marble_burner": True},
            "inventory": {"Dragon bones": 2},
        }

        self.assertTrue(addon.set_prayer_selection("dragon_bones", "gilded_owned"))
        self.assertEqual(calls, {"save": 1, "hud": 1})
        self.assertEqual(
            addon._state.player_data["prayer_owned_altar_stint"],
            {"target_id": target_id, "burners_lit": 1},
        )
        self.assertEqual(addon._state.player_data["prayer_gilded_house_search"]["reviews_remaining"], 2)

        self.assertTrue(addon.set_prayer_selection("dragon_bones", "gilded_hosted"))
        self.assertEqual(calls, {"save": 2, "hud": 2})
        self.assertEqual(addon._state.player_data["prayer_gilded_mode"], "hosted")
        self.assertEqual(addon._state.player_data["prayer_owned_altar_stint"], {})
        self.assertEqual(addon._state.player_data["prayer_gilded_house_search"], {})

        rejected_state = {"prayer_level": 99, "inventory": {"Dragon bones": 1}}
        addon._state.player_data = copy.deepcopy(rejected_state)
        self.assertFalse(addon.set_prayer_selection("dragon_bones", "gilded_owned"))
        self.assertEqual(addon._state.player_data, rejected_state)
        self.assertEqual(calls, {"save": 2, "hud": 2})

    def test_direct_urn_teleports_use_shared_lifo_undo(self):
        addon = _load_addon_as_package("ankiscape_direct_urn_undo_integration")
        from ankiscape.data.urn_data import URN_TIERS_BY_ID

        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        col = _DummyCol()
        mw = _DummyMW(col)
        addon.mw = mw
        calls = {"save": 0, "hud": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon._state.current_skill = "Mining"
        initial = {
            "inventory": {tier.item_full: 2},
            "carried_inventory": {"copper": {tier.item_full: 2}},
            "current_ore": "copper",
            "mining_level": 1,
            "mining_exp": 0.0,
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.review_undo_stack.append({"sentinel": True})

        self.assertTrue(addon.teleport_training_urn(tier.id))
        self.assertTrue(addon.teleport_training_urn(tier.id))
        self.assertEqual(
            col.custom_undo_entries,
            ["AnkiScape direct action", "AnkiScape direct action"],
        )
        self.assertEqual(mw.undo_updates, 2)
        self.assertEqual(addon._state.player_data["inventory"][tier.item_full], 0)
        self.assertNotIn("copper", addon._state.player_data["carried_inventory"])
        self.assertEqual(addon._state.player_data["mining_exp"], tier.teleport_xp * 2)
        telemetry = addon._state.player_data["action_telemetry"]["actions"][f"mining:teleport_{tier.id}"]
        self.assertEqual((telemetry["attempts"], telemetry["successes"]), (2, 2))
        self.assertEqual(len(addon._state.direct_action_undo_stack), 2)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        undo = types.SimpleNamespace(operation="AnkiScape direct action")
        addon._on_state_did_undo(undo)
        self.assertEqual(addon._state.player_data["inventory"][tier.item_full], 1)
        self.assertEqual(addon._state.player_data["carried_inventory"]["copper"][tier.item_full], 1)
        self.assertEqual(addon._state.player_data["mining_exp"], tier.teleport_xp)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(undo)
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)
        self.assertEqual(calls["xp"], [tier.teleport_xp, tier.teleport_xp])
        self.assertEqual(calls["save"], 4)

    def test_bank_kebab_uses_runtime_rng_and_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_consumable_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Combat"
        initial = {
            "inventory": {"Kebab": 1},
            "constitution_level": 50,
            "combat_lifepoints": 100,
        }
        addon._state.player_data = copy.deepcopy(initial)
        original_random = addon.random.random
        addon.random.random = lambda: 0.5
        self.addCleanup(setattr, addon.random, "random", original_random)

        result = addon.on_consume_item("Kebab")

        self.assertEqual(result["healed"], 50)
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 150)
        self.assertNotIn("Kebab", addon._state.player_data["inventory"])
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_bank_pack_open_all_uses_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_pack_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Herblore"
        initial = {"inventory": {"Vial pack": 2, "Vial": 1}}
        addon._state.player_data = copy.deepcopy(initial)

        result = addon.on_open_item_pack("Vial pack", True)

        self.assertEqual(result["packs_opened"], 2)
        self.assertEqual(addon._state.player_data["inventory"], {"Vial": 101})
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)

    def test_bank_impling_jar_loot_uses_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_impling_jar_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Hunter"
        initial = {
            "inventory": {
                "Butterfly net": 1,
                "Impling jar": 1,
                "Dragon impling jar": 1,
            },
            "hunter_level": 83,
            "quests": {"troll_romance": {"completed": True}},
            "music_log": {"version": 1, "unlocked_tracks": []},
        }
        addon._state.player_data = copy.deepcopy(initial)
        rolls = iter((2_700_000 / 6_700_000, 0.0))
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls)
        self.addCleanup(setattr, addon.random, "random", original_random)

        result = addon.on_open_impling_jar("Dragon impling jar")

        self.assertEqual(result["reward_item"], "Dragon dart tip")
        self.assertEqual(result["reward_quantity"], 105)
        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Butterfly net": 1, "Impling jar": 1, "Dragon dart tip": 105},
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        # The completed quest is pending before the jar opens, so this proves the
        # application path ran the shared music-log refresh during its commit.
        self.assertIn(4, addon._state.player_data["music_log"]["unlocked_tracks"])

        addon._state.current_skill = "Cooking"
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.current_skill, "Hunter")
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_impling_jar_loot_restores_rng_when_undo_registration_fails(self):
        addon = _load_addon_as_package("ankiscape_impling_jar_rng_rollback_integration")

        def _reject_undo(*_args):
            raise RuntimeError

        addon.mw = _DummyMW(types.SimpleNamespace(add_custom_undo_entry=_reject_undo))
        addon._state.player_data = {"inventory": {"Dragon impling jar": 1}}
        before = addon.random.getstate()

        self.assertIsNone(addon.on_open_impling_jar("Dragon impling jar"))
        self.assertEqual(addon._state.player_data, {"inventory": {"Dragon impling jar": 1}})
        self.assertEqual(addon.random.getstate(), before)

    def test_bank_discard_x_preserves_remainder_and_uses_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_discard_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Cooking"
        initial = {"inventory": {"Shrimps": 5}}
        addon._state.player_data = copy.deepcopy(initial)

        self.assertTrue(addon.on_discard_item("Shrimps", 2))
        self.assertEqual(addon._state.player_data["inventory"]["Shrimps"], 3)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_ranging_guild_entry_is_one_direct_action_and_undoes_atomically(self):
        addon = _load_addon_as_package(
            "ankiscape_ranging_guild_direct_action_integration"
        )
        ranging = sys.modules[
            f"{addon.__name__}.logic.ranging_guild_logic"
        ]
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Coins": 200, "Bronze arrows": 0},
            "equipment": {
                "weapon": "Shortbow",
                "ammunition": "Bronze arrows",
            },
            "ranged_level": 40,
            "combat_current_levels": {},
            "ranging_guild": ranging.default_ranging_guild_state_pure(),
            "activity_session": {"active_id": ""},
        }
        addon._state.player_data = copy.deepcopy(initial)

        def enter(current):
            updated, ok, _info = ranging.enter_ranging_guild_pure(current)
            return updated, ok

        self.assertTrue(addon.commit_direct_action(enter))
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Bronze arrows"], 10)
        self.assertEqual(
            addon._state.player_data["activity_session"]["active_id"],
            "ranging_guild",
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_family_gauntlet_conversion_is_one_direct_action_and_undoes_atomically(self):
        addon = _load_addon_as_package(
            "ankiscape_cooking_gauntlets_direct_action_integration"
        )
        gauntlets = sys.modules[
            f"{addon.__name__}.logic.cooking_gauntlets_logic"
        ]
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Cooking"
        initial = {
            "inventory": {
                "Goldsmith gauntlets": 1,
                "Cooking gauntlets": 0,
                "Coins": 25_000,
            },
            "equipment": {},
            "quests": {
                "family_crest": {
                    "started": True,
                    "progress": 16,
                    "completed": True,
                }
            },
        }
        addon._state.player_data = copy.deepcopy(initial)

        def convert(current):
            updated, ok, _message = gauntlets.apply_family_gauntlet_conversion_pure(
                current, "Goldsmith gauntlets"
            )
            return updated, ok

        self.assertTrue(addon.commit_direct_action(convert))
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Cooking gauntlets"], 1)
        self.assertEqual(
            addon._state.player_data["family_gauntlet_enchantment"], "cooking"
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_cooking_gauntlet_equip_and_unequip_are_direct_action_undo_safe(self):
        addon = _load_addon_as_package(
            "ankiscape_cooking_gauntlets_equipment_undo_integration"
        )
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Cooking gauntlets": 1},
            "equipment": {},
        }
        addon._state.player_data = copy.deepcopy(initial)

        self.assertTrue(addon.on_equip_item("Cooking gauntlets"))
        self.assertEqual(
            addon._state.player_data["equipment"], {"hands": "Cooking gauntlets"}
        )
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)

        equipped = {
            "inventory": {"Cooking gauntlets": 0},
            "equipment": {"hands": "Cooking gauntlets"},
        }
        addon._state.player_data = copy.deepcopy(equipped)
        self.assertTrue(addon.on_unequip_slot("hands"))
        self.assertEqual(addon._state.player_data["inventory"]["Cooking gauntlets"], 1)
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, equipped)

    def test_bank_discard_x_removes_and_undoes_exact_degradable_instance(self):
        addon = _load_addon_as_package("ankiscape_condition_discard_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Combat"
        initial = {
            "inventory": {"Combat hood 100": 2},
            "equipment": {},
            "equipment_instances": {
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 89_000,
                    "location": "bank",
                },
                "equipment-2": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 80_000,
                    "location": "bank",
                },
            },
            "equipment_instance_next_id": 3,
        }
        addon._state.player_data = copy.deepcopy(initial)

        self.assertTrue(addon.on_discard_item("Combat hood 100", 1))
        self.assertEqual(addon._state.player_data["inventory"]["Combat hood 100"], 1)
        self.assertNotIn("equipment-2", addon._state.player_data["equipment_instances"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
