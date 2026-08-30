import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.combat_data import (
    COMBAT_ANTIPOISON_POTION_DATA,
    COMBAT_ALLOTMENT_SEED_DROP_TABLE,
    COMBAT_ENEMY_DATA,
    COMBAT_FOOD_DATA,
    COMBAT_GEM_DROP_TABLE,
    CHAOS_DWARF_DROPS,
    COMBAT_MEGA_RARE_DROP_TABLE,
    COMBAT_MINOR_HERB_DROP_TABLE,
    COMBAT_UNCOMMON_SEED_DROP_TABLE,
    COMBAT_MAGIC_SPELL_DATA,
    COMBAT_MAGIC_STAFF_DATA,
    COMBAT_RANGED_AMMO_DATA,
    COMBAT_RANGED_WEAPON_DATA,
    DARKAN_GEM_DROP_TABLE,
    DARKAN_HERB_DROP_TABLE,
    DARKAN_MEGA_RARE_DROP_TABLE,
    DARKAN_ABERRANT_RARE_SEED_DROP_TABLE,
    DARKAN_VARIABLE_ALLOTMENT_DROP_TABLE,
    HAAKON_DROPS,
    HAM_GUARD_DROPS,
    HILL_GIANT_DROPS,
    ICE_GIANT_DROPS,
    IMP_DROPS,
    MOSS_GIANT_DROPS,
    MAGIC_FORMULA_SOURCE_PATH,
    MAGIC_STRATEGY_SOURCE_PATH,
    OUTLAW_DROPS,
    RANGED_FORMULA_SOURCE_PATH,
    RANGED_STRATEGY_SOURCE_PATH,
    SKELETON_HIGH_DROPS,
    SKELETON_LOW_DROPS,
    TZHAAR_KET_DROPS,
    WHITE_KNIGHT_LEVEL_36_DROPS,
    WHITE_KNIGHT_LEVEL_38_DROPS,
    WHITE_KNIGHT_LEVEL_39_DROPS,
    WHITE_KNIGHT_LEVEL_42_DROPS,
    ZOMBIE_DROPS,
    ZOMBIE_LEVEL_25_DROPS,
)
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import migrate_loaded_data
from ankiscape.data.livid_farm_data import ARCANE_CAPACITOR_CHARGED
from ankiscape.logic_pure.logic_pure import (
    _combat_apply_pvm_death,
    _combat_apply_wilderness_ambush,
    _combat_auto_drink_potions,
    _combat_attack_bonus_from_totals,
    _combat_defence_bonus_from_totals,
    combat_melee_attack_type_pure,
    combat_weapon_attack_style_slots_pure,
    combat_weapon_style_options_pure,
    _combat_roll_drops,
    _combat_apply_triple_charm_reward,
    _combat_try_pack_yak_winter_storage,
    _combat_refill_context_supplies,
    _combat_enemy_attack_class,
    _combat_enemy_bonuses,
    _combat_enemy_max_hit_old_hp,
    _combat_enemy_protection_class,
    advance_combat_grave_review_pure,
    apply_combat_burst_pure,
    apply_combat_finisher_pure,
    apply_combat_poison_effect_pure,
    apply_safe_combat_recovery_pure,
    combat_death_office_reclaim_cost_pure,
    combat_death_office_summary_pure,
    combat_dragonfire_protection_pure,
    combat_enemy_drop_item_names_pure,
    combat_observed_drop_item_names_pure,
    combat_poison_damage_for_ticks_pure,
    combat_poison_immunity_ticks_pure,
    combat_poison_ticks_for_initial_damage_pure,
    combat_status_summary_pure,
    combat_supply_loadout_summary_pure,
    refill_combat_supply_loadout_pure,
    combat_target_locked_reasons_pure,
    combat_target_preview_pure,
    combat_wilderness_equipment_risk_pure,
    apply_consumable_pure,
    derive_casual_combat_magic_pure,
    reclaim_death_office_items_pure,
    reconcile_combat_method_pure,
    request_combat_bank_run_now_pure,
    set_combat_auto_eat_food_pure,
    set_combat_auto_eat_threshold_pure,
    set_combat_pack_mode_pure,
    start_combat_grave_walk_pure,
    unload_combat_supply_loadout_pure,
)
from ankiscape.core.storage_pure import migrate_loaded_data


def _rng(values):
    iterator = iter(values)

    def _next():
        try:
            return next(iterator)
        except StopIteration:
            return 0.999999

    return _next


def _player(**overrides):
    data = {
        "inventory": {},
        "equipment": {},
        "attack_level": 99,
        "strength_level": 99,
        "defense_level": 99,
        "ranged_level": 99,
        "magic_level": 99,
        "constitution_level": 10,
        "attack_exp": 0.0,
        "strength_exp": 0.0,
        "defense_exp": 0.0,
        "ranged_exp": 0.0,
        "magic_exp": 0.0,
        "constitution_exp": 0.0,
        "current_combat_target": "chicken",
        "combat_attack_style": "accurate",
        "current_combat_spell": "wind_strike",
        "combat_lifepoints": 100,
        "combat_auto_eat_threshold_percent": 40,
        "combat_auto_eat_food": ["Shrimps"],
        "combat_supply_loadout": {},
        "combat_special_attack_energy": 100,
        "combat_current_levels": {},
        "combat_status_effects": {},
        "combat_recovery_progress": {},
        "combat_encounter": {},
        "combat_kill_counts": {},
    }
    data.update(overrides)
    return data


_KILLER_ENEMY_DATA = {
    "killer": {
        "display_name": "Killer",
        "level": 999,
        "group": "Test",
        "stats": {
            "attack": 99,
            "strength": 99,
            "defence": 99,
            "hitpoints": 1000,
        },
        "bonuses": {},
        "attack_speed": 1,
        "drops": {"guaranteed": (), "tables": ()},
        "source": "test",
    }
}


class CombatStatPotionAutoDrinkTest(unittest.TestCase):
    def test_familiarisation_triples_all_eligible_period_charm_drops(self):
        data = {
            "summoning_state": {"triple_charm_reviews_remaining": 2}
        }
        self.assertEqual(
            _combat_apply_triple_charm_reward(
                data,
                {
                    "Gold charm": 1,
                    "Obsidian charm": 2,
                    "Abyssal charm": 1,
                    "Talon beast charm": 1,
                    "Bones": 1,
                },
            ),
            {
                "Gold charm": 3,
                "Obsidian charm": 6,
                "Abyssal charm": 3,
                "Talon beast charm": 1,
                "Bones": 1,
            },
        )

    def test_pack_yak_winter_storage_only_commits_when_it_avoids_bank_run(self):
        loot = {f"Loot {index}": 1 for index in range(26)}
        carried = {
            **loot,
            "Bones": 1,
            "Winter storage scroll": 1,
        }
        player = {
            "inventory": dict(carried),
            "summoning_exp": 0.0,
            "summoning_state": {
                "active_follower": {
                    "kind": "familiar",
                    "entity_id": "packyak",
                },
                "special_move_points_current": 60,
                "target_policies": {
                    "chicken": {"winter_storage_priority": ["Bones"]}
                },
            },
            "carried_inventory": {"chicken": dict(carried)},
            "current_combat_target": "chicken",
            "combat_supply_loadout": {},
        }

        used = _combat_try_pack_yak_winter_storage(
            player, "chicken", "melee", {}, {}, {}, COMBAT_ENEMY_DATA
        )

        self.assertTrue(used)
        self.assertNotIn("Bones", player["carried_inventory"]["chicken"])
        self.assertNotIn(
            "Winter storage scroll", player["carried_inventory"]["chicken"]
        )
        self.assertEqual(player["inventory"]["Bones"], 1)
        self.assertEqual(player["inventory"]["Winter storage scroll"], 0)
        self.assertEqual(
            player["summoning_state"]["special_move_points_current"], 48
        )
        self.assertEqual(player["summoning_exp"], 4.8)

    def test_combat_bank_boundary_restores_prayer_and_summoning_together(self):
        player = {
            "inventory": {},
            "prayer_level": 70,
            "summoning_level": 52,
            "combat_prayer_points": 1,
            "summoning_state": {"summoning_points_current": 0},
        }

        _combat_refill_context_supplies(
            player, "chicken", "melee", {}, {}, {}, COMBAT_ENEMY_DATA
        )

        self.assertEqual(player["combat_prayer_points"], 700)
        self.assertEqual(
            player["summoning_state"]["summoning_points_current"], 52
        )

    def _melee(self, **overrides):
        base = dict(
            current_combat_target="chicken",
            combat_attack_style="aggressive",
            attack_level=50,
            strength_level=50,
            defense_level=50,
            constitution_level=20,
            combat_lifepoints=200,
            combat_auto_eat_food=["Shrimps"],
        )
        base.update(overrides)
        return _player(**base)

    def test_melee_drinks_strength_potion_boosts_and_consumes_a_dose(self):
        player = self._melee(combat_supply_loadout={"stat_potions": {"Super strength (4)": 1}})
        out, ok, result = apply_combat_burst_pure(player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0]))
        self.assertTrue(ok)
        # Super strength on base 50 = 50 + floor(15*50/100)+5 = 62.
        self.assertEqual(out["combat_current_levels"]["strength"], 62)
        # The (4) flask dropped to a (3).
        self.assertEqual(out["combat_supply_loadout"]["stat_potions"], {"Super strength (3)": 1})
        self.assertIn({"item": "Super strength (4)", "skills": ("strength",)}, result["potions_used"])

    def test_no_potion_means_no_boost(self):
        out, ok, _ = apply_combat_burst_pure(self._melee(), COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0]))
        self.assertNotIn("strength", out.get("combat_current_levels", {}))

    def test_does_not_redrink_while_the_boost_is_still_active(self):
        # Start already boosted (as if drunk last burst); the flask must not be sipped again.
        player = self._melee(
            combat_current_levels={"strength": 62},
            combat_supply_loadout={"stat_potions": {"Super strength (4)": 1}},
        )
        out, ok, _ = apply_combat_burst_pure(player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0]))
        self.assertEqual(out["combat_supply_loadout"]["stat_potions"], {"Super strength (4)": 1})

    def test_combat_potion_boosts_both_attack_and_strength_from_one_dose(self):
        player = self._melee(combat_supply_loadout={"stat_potions": {"Combat potion (4)": 1}})
        out, ok, _ = apply_combat_burst_pure(player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0]))
        # Regular boost on base 50 = 50 + floor(50/10)+3 = 58, on both stats, one dose spent.
        self.assertEqual(out["combat_current_levels"]["strength"], 58)
        self.assertEqual(out["combat_current_levels"]["attack"], 58)
        self.assertEqual(out["combat_supply_loadout"]["stat_potions"], {"Combat potion (3)": 1})

    def test_refill_loads_stat_potions_from_the_bank(self):
        player = self._melee(inventory={"Shrimps": 5, "Super strength (4)": 3}, combat_pack_mode="max_output")
        refilled, ok, reason = refill_combat_supply_loadout_pure(player, EQUIPMENT_DATA)
        self.assertTrue(ok, reason)
        self.assertEqual(refilled["combat_supply_loadout"]["stat_potions"], {"Super strength (4)": 3})
        self.assertEqual(refilled["inventory"]["Super strength (4)"], 0)

    def test_six_dose_flask_is_registered_drinkable_and_auto_drunk(self):
        from ankiscape.data.potion_data import potion_items_as_dict, potion_consumables_as_dict

        items = potion_items_as_dict()
        consumables = potion_consumables_as_dict()
        # Flask (6) is a real registered, drinkable item that walks down to (5).
        self.assertIn("Super strength flask (6)", items)
        self.assertEqual(items["Super strength flask (6)"]["item_id"], 23279)
        self.assertEqual(consumables["Super strength flask (6)"]["leaves"], "Super strength flask (5)")
        # A drained flask leaves an empty Potion flask, not a Vial.
        self.assertEqual(consumables["Super strength flask (1)"]["leaves"], "Potion flask")

        # Combat auto-drinks a flask and it lasts 6 doses (vs a vial's 4).
        player = self._melee(combat_supply_loadout={"stat_potions": {"Super strength flask (6)": 1}})
        out, ok, _ = apply_combat_burst_pure(player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0]))
        self.assertEqual(out["combat_current_levels"]["strength"], 62)
        self.assertEqual(out["combat_supply_loadout"]["stat_potions"], {"Super strength flask (5)": 1})

    def test_antifire_potions_are_registered_and_manually_drinkable(self):
        from ankiscape.data.potion_data import potion_items_as_dict, potion_consumables_as_dict

        items = potion_items_as_dict()
        consumables = potion_consumables_as_dict()
        self.assertEqual(items["Antifire (4)"]["item_id"], 2452)
        self.assertEqual(items["Super antifire flask (6)"]["item_id"], 23489)
        self.assertEqual(consumables["Antifire (4)"]["duration_ticks"], 600)
        self.assertEqual(
            consumables["Super antifire (3)"]["protection_level"], 2
        )

        regular, regular_result = apply_consumable_pure(
            {"inventory": {"Antifire (4)": 1}},
            "Antifire (4)",
        )
        supered, super_result = apply_consumable_pure(
            {"inventory": {"Super antifire (3)": 1}},
            "Super antifire (3)",
        )

        self.assertTrue(regular_result["allowed"])
        self.assertEqual(regular["combat_antifire_ticks_remaining"], 600)
        self.assertEqual(regular["inventory"], {"Antifire (3)": 1})
        self.assertTrue(super_result["allowed"])
        self.assertEqual(
            supered["combat_super_antifire_ticks_remaining"], 600
        )
        self.assertEqual(supered["inventory"], {"Super antifire (2)": 1})

    def test_full_flask_is_preferred_over_a_vial(self):
        # Carrying both, the fuller flask (6 doses) is drunk before the vial (4).
        player = self._melee(
            combat_supply_loadout={"stat_potions": {"Super strength (4)": 1, "Super strength flask (6)": 1}},
        )
        out, ok, _ = apply_combat_burst_pure(player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0]))
        self.assertIn("Super strength (4)", out["combat_supply_loadout"]["stat_potions"])  # vial untouched
        self.assertEqual(out["combat_supply_loadout"]["stat_potions"]["Super strength flask (5)"], 1)  # flask sipped

    def test_super_prayer_auto_drink_outranks_regular_and_restores_prayer_points(self):
        player = self._melee(
            prayer_level=80,
            combat_prayer_points=100,
            combat_prayer_book="standard",
            combat_selected_prayers=["protect_item"],
            combat_prayer_uptime="100",
            combat_prayers_enabled=True,
            combat_supply_loadout={
                "stat_potions": {
                    "Prayer potion (4)": 1,
                    "Super prayer (4)": 1,
                }
            },
        )
        events = _combat_auto_drink_potions(player, "melee")
        self.assertIn({"item": "Super prayer (4)", "skills": ("prayer",)}, events)
        self.assertEqual(player["combat_prayer_points"], 450)
        self.assertNotIn("prayer", player.get("combat_current_levels", {}))
        self.assertEqual(
            player["combat_supply_loadout"]["stat_potions"],
            {"Prayer potion (4)": 1, "Super prayer (3)": 1},
        )

    def test_style_relevant_potions_load_and_off_style_ones_do_not(self):
        # Melee: strength/attack potions load (supers first, covering both stats);
        # a magic potion is off-style and never loaded.
        player = self._melee(
            inventory={"Shark": 5, "Super strength (4)": 5, "Magic potion (4)": 5},
            combat_auto_eat_food=["Shark"],
            combat_pack_mode="max_output",
        )
        lo = refill_combat_supply_loadout_pure(player, EQUIPMENT_DATA)[0]["combat_supply_loadout"]
        self.assertIn("Super strength (4)", lo["stat_potions"])
        self.assertNotIn("Magic potion (4)", lo["stat_potions"])

    def test_antipoison_refill_is_capped_and_cannot_softlock_combat(self):
        # Regression: the antipoison refill loaded the player's ENTIRE stock. Each
        # unstackable dose costs a slot, so 50 potions pushed supplies to 70 slots,
        # making `supply + loot >= 28` permanently true — every answer became a bank
        # run and the player could never fight a poisonous enemy.
        from ankiscape.logic_pure.logic_pure import _combat_supply_slots_used, CARRIED_CAPACITY

        player = {
            "inventory": {"Shark": 100, "Antipoison (4)": 50}, "equipment": {},
            "attack_level": 99, "strength_level": 99, "defense_level": 99,
            "constitution_level": 99, "current_combat_target": "poison_scorpion",
            "combat_attack_style": "aggressive", "combat_lifepoints": 990,
            "combat_auto_eat_food": ["Shark"], "combat_pack_mode": "max_safety",
        }
        fights = 0
        for _ in range(6):
            player, _ok, result = apply_combat_burst_pure(
                player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=5, rng=_rng([0.5] * 40))
            if result.get("reason") != "combat_bank_run":
                fights += 1
        self.assertGreater(fights, 0, "combat softlocked into a permanent bank-run loop")
        self.assertLessEqual(_combat_supply_slots_used(player), CARRIED_CAPACITY)
        # Only a couple of doses are carried; the rest stay banked.
        self.assertEqual(sum(player["combat_supply_loadout"]["potions"].values()), 2)
        self.assertEqual(player["inventory"]["Antipoison (4)"], 48)

    def test_a_stale_carried_view_cannot_duplicate_items_through_the_grave(self):
        # The view is a view over the bank, but the bank can shrink underneath it:
        # discard the looted bones, sell them, or eat looted food. Graving what the
        # view *claims* rather than what the bank *holds* would mint the difference
        # when the grave is reclaimed. Loot 10 bones, discard 8, die -> grave 2.
        player = {
            "inventory": {"Bones": 2}, "equipment": {}, "constitution_level": 10,
            "current_combat_target": "chicken",
            "carried_inventory": {"chicken": {"Bones": 10}},  # view outlived the items
            "carried_churn": {}, "skilling_bank_run": {},
        }
        _combat_apply_pvm_death(player, 100)
        self.assertEqual(player["combat_grave"]["items"].count("Bones"), 2)
        self.assertEqual(player["inventory"]["Bones"], 0)

    def test_pvm_death_applies_pet_loss_without_putting_pet_in_grave(self):
        from ankiscape.logic.pet_logic import acquire_pet_pure, let_out_pet_pure
        from ankiscape.logic.summoning_logic import default_summoning_state_pure

        player = {
            "inventory": {},
            "equipment": {},
            "summoning_level": 99,
            "summoning_state": default_summoning_state_pure(),
            "current_combat_target": "chicken",
        }
        player, _, instance_id = acquire_pet_pure(player, "bulldog")
        player, _, _ = let_out_pet_pure(player, instance_id)

        _combat_apply_pvm_death(player, 100)

        self.assertNotIn(
            instance_id, player["summoning_state"]["pet_instances"]
        )
        self.assertEqual(player["summoning_state"]["active_follower"], {})
        self.assertEqual(player["combat_grave"], {})

    def test_master_off_prevents_protect_item_from_saving_pvm_death_gear(self):
        disabled = _player(
            equipment={"weapon": "Iron sword", "shield": "Iron kiteshield"},
            prayer_level=99,
            combat_prayer_points=990,
            combat_prayer_uptime="100",
            combat_selected_prayers=["protect_item"],
            combat_prayers_enabled=False,
        )
        _combat_apply_pvm_death(disabled, 100)
        self.assertEqual(disabled["equipment"], {})
        self.assertCountEqual(disabled["combat_grave"]["items"], ["Iron sword", "Iron kiteshield"])
        self.assertEqual(disabled["combat_selected_prayers"], ["protect_item"])
        self.assertEqual(disabled["combat_prayer_uptime"], "100")

        enabled = _player(
            equipment={"weapon": "Rune scimitar", "ammunition": "Bronze arrows"},
            prayer_level=99,
            combat_prayer_points=990,
            combat_prayer_uptime="100",
            combat_selected_prayers=["protect_item"],
            combat_prayers_enabled=True,
        )
        _combat_apply_pvm_death(enabled, 100)
        self.assertEqual(enabled["equipment"], {"weapon": "Rune scimitar"})
        self.assertEqual(enabled["combat_grave"]["items"], ["Bronze arrows"])

    def test_a_stale_carried_view_does_not_occupy_phantom_loot_slots(self):
        # 20 food + a view claiming 8 trophies the bank no longer has must not fire a
        # bank run: those slots are not really occupied, and banking has nothing to
        # deposit.
        player = self._melee(
            combat_supply_loadout={"food": {"Shark": 20}},
            current_combat_target="chicken",
            inventory={},  # the trophies were sold/discarded
            carried_inventory={"chicken": {f"Trophy {i}": 1 for i in range(8)}},
        )
        _out, _ok, result = apply_combat_burst_pure(
            player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0]))
        self.assertNotEqual(result.get("reason"), "combat_bank_run")

    def test_a_full_supply_loadout_with_no_loot_never_forces_a_bank_run(self):
        # Banking only deposits loot, so with nothing to deposit a "full" inventory
        # cannot be relieved by banking — it must not trigger one.
        player = self._melee(
            combat_supply_loadout={"food": {"Shark": 28}},  # supplies alone fill it
            current_combat_target="chicken",
            carried_inventory={},  # no loot to deposit
        )
        _out, _ok, result = apply_combat_burst_pure(
            player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0]))
        self.assertNotEqual(result.get("reason"), "combat_bank_run")

    def test_supplies_and_loot_share_one_28_slot_budget(self):
        # 20 slots of supplies + 7 loot = 27 (room left, fights on); + 8 loot = 28,
        # so supplies+loot fill the one inventory and a bank run is forced. Before
        # this fix loot had its own separate 28-slot budget.
        base = self._melee(
            combat_supply_loadout={"food": {"Shark": 20}},
            current_combat_target="chicken",
        )

        # Kept loot lives in the bank too (the view is a view over it), so the
        # fixture must back every carried trophy with a real banked item.
        def _with_loot(n):
            trophies = {f"Trophy {i}": 1 for i in range(n)}
            return dict(
                base,
                inventory=dict(base.get("inventory", {}) or {}, **trophies),
                carried_inventory={"chicken": trophies},
            )
        _out, ok, result = apply_combat_burst_pure(_with_loot(7), COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0]))
        self.assertNotEqual(result.get("reason"), "combat_bank_run")

        _out2, ok2, result2 = apply_combat_burst_pure(_with_loot(8), COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0]))
        self.assertEqual(result2.get("reason"), "combat_bank_run")  # 20 + 8 = 28 -> bank

    def test_pack_mode_allocates_the_food_and_potion_budget(self):
        def loaded(mode):
            player = self._melee(
                inventory={"Shark": 100, "Super strength (4)": 20},
                combat_auto_eat_food=["Shark"],
                combat_pack_mode=mode,
            )
            lo = refill_combat_supply_loadout_pure(player, EQUIPMENT_DATA)[0]["combat_supply_loadout"]
            return sum(lo["food"].values()), sum(lo["stat_potions"].values())

        # Food + a small style-relevant potion set; the rest of the 28 is loot room.
        self.assertEqual(loaded("max_safety"), (20, 2))
        self.assertEqual(loaded("balanced"), (14, 4))
        self.assertEqual(loaded("max_output"), (8, 6))

    def test_manual_combat_bank_run_request_starts_the_existing_two_review_route(self):
        requested, ok, reason = request_combat_bank_run_now_pure(
            self._melee(combat_encounter={})
        )
        self.assertTrue(ok, reason)
        self.assertEqual(
            requested["combat_bank_run"],
            {"reviews_remaining": 2, "target_id": "chicken"},
        )

    def test_repeated_bank_request_does_not_restart_active_route(self):
        player = self._melee(
            combat_encounter={},
            combat_bank_run={"reviews_remaining": 1, "target_id": "chicken"},
        )

        requested, ok, reason = request_combat_bank_run_now_pure(player)

        self.assertTrue(ok, reason)
        self.assertEqual(
            requested["combat_bank_run"],
            {"reviews_remaining": 1, "target_id": "chicken"},
        )

    def test_switching_pack_mode_immediately_rebalances_a_stale_loadout(self):
        player = self._melee(
            inventory={"Sardine": 60, "Super strength (4)": 20},
            combat_auto_eat_food=["Sardine"],
            combat_supply_loadout={"food": {"Sardine": 1}},
        )

        expected = {
            "max_safety": (20, 2),
            "balanced": (14, 4),
            "max_output": (8, 6),
        }
        for mode, allocation in expected.items():
            with self.subTest(mode=mode):
                switched, ok, reason = set_combat_pack_mode_pure(
                    player, mode, EQUIPMENT_DATA
                )
                self.assertTrue(ok, reason)
                loadout = switched["combat_supply_loadout"]
                self.assertEqual(
                    (sum(loadout["food"].values()), sum(loadout["stat_potions"].values())),
                    allocation,
                )
                self.assertEqual(
                    loadout["food"], {"Sardine": allocation[0]}
                )

    def test_pack_mode_repairs_invalid_dream_fight_but_rejects_a_real_fight(self):
        reported = self._melee(
            magic_level=1,
            quests={"dream_mentor": {"completed": False}},
            combat_dream_thrift=True,
            combat_encounter={"target_id": "citizen", "enemy_lifepoints": 67},
            inventory={"Shrimps": 89},
            combat_auto_eat_food=["Shrimps"],
            combat_supply_loadout={"food": {"Shrimps": 1}},
        )

        repaired, ok, reason = set_combat_pack_mode_pure(
            reported, "max_safety", EQUIPMENT_DATA
        )
        self.assertTrue(ok, reason)
        self.assertFalse(repaired["combat_dream_thrift"])
        self.assertEqual(repaired["combat_encounter"], {})
        self.assertEqual(repaired["combat_supply_loadout"]["food"], {"Shrimps": 20})

        active = dict(repaired)
        active["combat_encounter"] = {"target_id": "chicken", "enemy_lifepoints": 3}
        refused, ok, reason = set_combat_pack_mode_pure(
            active, "max_output", EQUIPMENT_DATA
        )
        self.assertFalse(ok)
        self.assertEqual(
            reason, "Finish the active fight before changing supply mode."
        )
        self.assertEqual(refused["combat_pack_mode"], "max_safety")
        self.assertEqual(refused["combat_supply_loadout"]["food"], {"Shrimps": 20})


class CombatEnemyAttackStyleTest(unittest.TestCase):
    """The enemy attacks with ITS style: its accuracy comes off the matching attack
    stat/bonus, and the player resists with the matching defence bonus."""

    @staticmethod
    def _enemy(style, strength=80, ranged=80, magic=80, **extra):
        enemy = dict(
            display_name="X", level=50, group="T", attack_style=style, attack_speed=4,
            respawn_delay=10, slayer_xp=0.0,
            stats={"hitpoints": 500, "attack": 80, "strength": strength, "defence": 1,
                   "magic": magic, "ranged": ranged},
            bonuses={k: 0 for k in (
                "attack_stab", "attack_slash", "attack_crush", "defence_stab", "defence_slash",
                "defence_crush", "defence_magic", "defence_ranged", "melee_strength")},
            drops={"guaranteed": [], "tables": []}, source="synthetic",
        )
        enemy.update(extra)
        return {"x": enemy}

    @staticmethod
    def _magic_robe_setup():
        from ankiscape.data.equipment_data import EquipmentItem, EquipmentBonuses

        robe = EquipmentItem(
            item_name="Robe", slot="body", combat_skill="defense", required_level=1,
            two_handed=False, equipment_type="body",
            # +300 magic defence, zero melee defence
            bonuses=EquipmentBonuses(0, 0, 0, 0, 0, 0, 0, 0, 300, 0, 0, 0, 0, 0),
            attack_speed=4, source_item_id=0, source="t", source_status="t", skill_requirements={},
        )
        player = {
            "inventory": {}, "equipment": {"body": "Robe"}, "attack_level": 50, "strength_level": 50,
            "defense_level": 50, "magic_level": 50, "ranged_level": 50, "constitution_level": 50,
            "combat_lifepoints": 500, "current_combat_target": "x",
            "combat_attack_style": "aggressive", "combat_auto_eat_food": [],
        }
        return player, {"Robe": robe}

    def test_magic_defence_resists_a_magic_enemy_but_not_a_melee_one(self):
        player, equipment_data = self._magic_robe_setup()
        _o, _ok, melee_result = apply_combat_burst_pure(
            dict(player), self._enemy("melee"), equipment_data, ticks=1, rng=lambda: 0.5)
        _o2, _ok2, magic_result = apply_combat_burst_pure(
            dict(player), self._enemy("magic"), equipment_data, ticks=1, rng=lambda: 0.5)
        # +300 magic defence barely helps against a melee attacker, but heavily
        # blunts the mage. Before this change both used melee defence (0) equally.
        self.assertGreater(melee_result["enemy_accuracy"], 0.5)
        self.assertLess(magic_result["enemy_accuracy"], 0.2)

    def test_magic_melee_uses_attack_against_magic_defence_and_melee_prayer(self):
        player, equipment_data = self._magic_robe_setup()
        magic_melee = self._enemy("magic_melee", magic=1, max_hit=40)
        ordinary_magic = self._enemy("magic", magic=1, max_hit=40)

        _out, ok, magic_melee_result = apply_combat_burst_pure(
            dict(player),
            magic_melee,
            equipment_data,
            ticks=1,
            rng=lambda: 0.5,
        )
        _out2, ok2, ordinary_magic_result = apply_combat_burst_pure(
            dict(player),
            ordinary_magic,
            equipment_data,
            ticks=1,
            rng=lambda: 0.5,
        )

        self.assertTrue(ok)
        self.assertTrue(ok2)
        self.assertGreater(
            magic_melee_result["enemy_accuracy"],
            ordinary_magic_result["enemy_accuracy"],
        )
        self.assertLess(magic_melee_result["enemy_accuracy"], 0.2)
        self.assertEqual(_combat_enemy_attack_class(magic_melee["x"]), "magic")
        self.assertEqual(_combat_enemy_protection_class(magic_melee["x"]), "melee")

        def fought_with(prayer_id):
            prepared = {
                **player,
                "prayer_level": 99,
                "combat_prayer_points": 990,
                "combat_prayer_uptime": "100",
                "combat_selected_prayers": [prayer_id],
                "combat_auto_flee": False,
            }
            return apply_combat_burst_pure(
                prepared,
                magic_melee,
                equipment_data,
                ticks=5,
                rng=_rng([0.999, 0.0, 0.999, 0.0, 0.999, 0.0, 0.999]),
            )[2]

        self.assertEqual(fought_with("protect_from_melee")["enemy_damage"], 0)
        self.assertGreater(fought_with("protect_from_magic")["enemy_damage"], 0)

    def test_casual_max_safety_selects_melee_prayer_for_pyrefiend(self):
        prepared = derive_casual_combat_magic_pure(
            _player(
                current_combat_target="pyrefiend",
                combat_pack_mode="max_safety",
                prayer_level=99,
                combat_prayers_enabled=True,
            )
        )

        self.assertEqual(
            prepared["combat_selected_prayers"],
            ["protect_from_melee"],
        )

    def test_casual_max_safety_tracks_killerwatt_distance_style(self):
        for attack_style, expected_prayer in (
            ("melee_accurate", "protect_from_melee"),
            ("ranged_accurate", "protect_from_missiles"),
            ("magic_standard", "protect_from_missiles"),
        ):
            with self.subTest(attack_style=attack_style):
                prepared = derive_casual_combat_magic_pure(
                    _player(
                        current_combat_target="killerwatt",
                        combat_attack_style=attack_style,
                        combat_pack_mode="max_safety",
                        prayer_level=99,
                        combat_prayers_enabled=True,
                    )
                )
                self.assertEqual(
                    prepared["combat_selected_prayers"],
                    [expected_prayer],
                )

    def test_ranged_enemy_max_hit_uses_its_ranged_stat_not_melee_strength(self):
        weak_melee_strong_bow = self._enemy("ranged", strength=1, ranged=99)["x"]
        same_but_melee = self._enemy("melee", strength=1, ranged=99)["x"]
        totals = _combat_enemy_bonuses(weak_melee_strong_bow)
        ranged_hit = _combat_enemy_max_hit_old_hp(weak_melee_strong_bow, 1 + 8, 0, totals)
        melee_hit = _combat_enemy_max_hit_old_hp(same_but_melee, 1 + 8, 0, totals)
        self.assertGreater(ranged_hit, 10.0)  # scales off ranged 99
        self.assertLess(melee_hit, 2.0)       # scales off strength 1

    def test_explicit_max_hit_wins_and_unknown_style_falls_back_to_melee(self):
        # Magic NPC hits are spell-defined in the source, so they declare max_hit.
        mage = {"attack_style": "magic", "max_hit": 120, "stats": {"strength": 1, "ranged": 1}}
        totals = _combat_enemy_bonuses(mage)
        self.assertEqual(_combat_enemy_max_hit_old_hp(mage, 9, 0, totals), 12.0)
        self.assertEqual(_combat_enemy_attack_class({"attack_style": "nonsense"}), "melee")
        self.assertEqual(_combat_enemy_attack_class({}), "melee")

    def test_every_shipped_enemy_is_melee_or_declares_a_max_hit(self):
        # Data guard: a non-melee enemy without an explicit max_hit would silently
        # fall back to the melee-strength derivation, which is wrong for a caster.
        for name, enemy in COMBAT_ENEMY_DATA.items():
            if enemy.get("attack_style") in {"magic", "magic_melee"}:
                with self.subTest(enemy=name):
                    self.assertTrue(enemy.get("max_hit") or enemy.get("max_hit_old_hp"))


class CombatPeriodXpTest(unittest.TestCase):
    def test_death_spawn_never_grants_slayer_xp(self):
        death_spawn = COMBAT_ENEMY_DATA["death_spawn"]

        self.assertEqual(death_spawn["slayer_xp"], 0.0)
        self.assertIn("Death spawn oldid 6327456", death_spawn["source"])

    def test_level_8_crawling_hand_uses_period_slayer_xp(self):
        crawling_hand = COMBAT_ENEMY_DATA["crawling_hand"]

        self.assertEqual(crawling_hand["level"], 8)
        self.assertEqual(crawling_hand["stats"]["hitpoints"], 160)
        self.assertEqual(crawling_hand["slayer_xp"], 16.0)
        self.assertIn("Crawling hand oldid 6530506", crawling_hand["source"])

    def test_stronghold_shade_applies_period_reduced_combat_and_slayer_xp(self):
        shade = COMBAT_ENEMY_DATA["shade"]
        ordinary_shade = dict(shade)
        ordinary_shade.pop("xp_multiplier")
        player = _player(current_combat_target="shade")

        _reduced, ok, reduced_result = apply_combat_burst_pure(
            player,
            {"shade": shade},
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.5]),
        )
        _ordinary, ordinary_ok, ordinary_result = apply_combat_burst_pure(
            player,
            {"shade": ordinary_shade},
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.5]),
        )

        self.assertTrue(ok)
        self.assertTrue(ordinary_ok)
        self.assertEqual(shade["slayer_xp"], 3.5)
        self.assertAlmostEqual(
            reduced_result["xp_rewards"]["attack_exp"],
            ordinary_result["xp_rewards"]["attack_exp"] * 0.25,
        )
        self.assertAlmostEqual(
            reduced_result["xp_rewards"]["constitution_exp"],
            ordinary_result["xp_rewards"]["constitution_exp"] * 0.25,
        )


class CombatDropItemNamesTest(unittest.TestCase):
    def test_flattens_guaranteed_and_nested_table_items_in_order(self):
        enemy = {
            "drops": {
                "guaranteed": [["Bones", 1], ["Raw beef", 1]],
                "tables": [
                    {"slots": [
                        {"item": "Cowhide"},
                        {"slots": 1},  # empty slot -> nothing
                        {"table": {"slots": [{"item": "Rare gem"}]}},
                    ]},
                ],
            }
        }
        self.assertEqual(
            combat_enemy_drop_item_names_pure(enemy),
            ("Bones", "Raw beef", "Cowhide", "Rare gem"),
        )

    def test_handles_missing_or_malformed_drops(self):
        self.assertEqual(combat_enemy_drop_item_names_pure({}), ())
        self.assertEqual(combat_enemy_drop_item_names_pure({"drops": None}), ())
        self.assertEqual(combat_enemy_drop_item_names_pure(None), ())

    def test_observed_drop_names_include_only_the_selected_targets_log(self):
        player = {
            "combat_observed_drops": {
                "chicken": {
                    "Bones": {"times_seen": 2, "quantity_seen": 2},
                    "Feather": {"times_seen": 1, "quantity_seen": 5},
                },
                "cow": {
                    "Cowhide": {"times_seen": 1, "quantity_seen": 1}
                },
            }
        }

        self.assertEqual(
            combat_observed_drop_item_names_pure(player, "chicken"),
            ("Bones", "Feather"),
        )
        self.assertEqual(combat_observed_drop_item_names_pure(player, "cow"), ("Cowhide",))
        self.assertEqual(combat_observed_drop_item_names_pure(player, "giant_rat"), ())


class CombatLogicTest(unittest.TestCase):
    def test_standard_bow_and_arrow_rows_match_2011scape_source(self):
        expected_bows = {
            "Shortbow": ("shortbow", ("Bronze arrows", "Iron arrows")),
            "Longbow": ("longbow", ("Bronze arrows", "Iron arrows")),
            "Oak shortbow": ("oak_shortbow", ("Bronze arrows", "Iron arrows", "Steel arrows")),
            "Oak longbow": ("oak_longbow", ("Bronze arrows", "Iron arrows", "Steel arrows")),
            "Willow shortbow": ("willow_shortbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows")),
            "Willow longbow": ("willow_longbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows")),
            "Maple shortbow": ("maple_shortbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows")),
            "Maple longbow": ("maple_longbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows")),
            "Yew shortbow": ("yew_shortbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows")),
            "Yew longbow": ("yew_longbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows")),
            "Magic shortbow": ("magic_shortbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows", "Broad arrows")),
            "Magic longbow": ("magic_longbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows", "Broad arrows")),
        }

        for bow_name, (equipment_type, ammo) in expected_bows.items():
            with self.subTest(bow_name=bow_name):
                spec = COMBAT_RANGED_WEAPON_DATA[bow_name]
                self.assertEqual(spec["equipment_type"], equipment_type)
                self.assertEqual(spec["compatible_ammo"], ammo)

        expected_ammo = {
            "Bronze arrows": (882, "Bronze arrow", 7),
            "Iron arrows": (884, "Iron arrow", 10),
            "Steel arrows": (886, "Steel arrow", 16),
            "Mithril arrows": (888, "Mithril arrow", 22),
            "Adamant arrows": (890, "Adamant arrow", 31),
            "Rune arrows": (892, "Rune arrow", 49),
            "Broad arrows": (4160, "Broad arrow", 28),
        }
        for ammo_name, (source_item_id, source_item_name, ranged_strength) in expected_ammo.items():
            with self.subTest(ammo_name=ammo_name):
                spec = COMBAT_RANGED_AMMO_DATA[ammo_name]
                self.assertEqual(spec["source_item_id"], source_item_id)
                self.assertEqual(spec["source_item_name"], source_item_name)
                self.assertEqual(spec["ranged_strength"], ranged_strength)

    def test_standard_arrow_drops_use_equippable_stack_identities(self):
        drop_names = {
            item_name
            for enemy in COMBAT_ENEMY_DATA.values()
            for item_name in combat_enemy_drop_item_names_pure(enemy)
        }
        standard_drop_ammo = {
            "Bronze arrows",
            "Iron arrows",
            "Steel arrows",
            "Mithril arrows",
            "Adamant arrows",
            "Rune arrows",
        }
        source_names = {
            COMBAT_RANGED_AMMO_DATA[item_name]["source_item_name"]
            for item_name in standard_drop_ammo
        }
        self.assertTrue(standard_drop_ammo.issubset(drop_names))
        self.assertTrue(source_names.isdisjoint(drop_names))

    def test_standard_strike_spell_rows_match_2011scape_source(self):
        self.assertEqual(
            COMBAT_MAGIC_SPELL_DATA["water_strike"]["rune_cost"],
            {"Air rune": 1, "Mind rune": 1, "Water rune": 1},
        )
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["water_strike"]["required_magic_level"], 5)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["water_strike"]["max_hit_old_hp"], 4)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["water_strike"]["base_magic_xp"], 7.5)

        self.assertEqual(
            COMBAT_MAGIC_SPELL_DATA["earth_strike"]["rune_cost"],
            {"Air rune": 1, "Mind rune": 1, "Earth rune": 2},
        )
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["earth_strike"]["required_magic_level"], 9)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["earth_strike"]["max_hit_old_hp"], 6)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["earth_strike"]["base_magic_xp"], 9.5)

        self.assertEqual(
            COMBAT_MAGIC_SPELL_DATA["fire_strike"]["rune_cost"],
            {"Air rune": 1, "Mind rune": 1, "Fire rune": 3},
        )
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["fire_strike"]["required_magic_level"], 13)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["fire_strike"]["max_hit_old_hp"], 8)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["fire_strike"]["base_magic_xp"], 11.5)
        self.assertEqual(COMBAT_MAGIC_STAFF_DATA["Staff of air"]["covered_runes"], ("Air rune",))
        self.assertEqual(COMBAT_MAGIC_STAFF_DATA["Staff of fire"]["covered_runes"], ("Fire rune",))

    def test_standard_bolt_blast_wave_spell_rows_match_2011scape_source(self):
        expected = {
            "wind_bolt": ("Wind Bolt", 17, {"Air rune": 2, "Chaos rune": 1}, 9, 13.5, 73, 34, 11),
            "water_bolt": ("Water Bolt", 23, {"Air rune": 2, "Water rune": 2, "Chaos rune": 1}, 10, 16.5, 76, 39, 13),
            "earth_bolt": ("Earth Bolt", 29, {"Air rune": 2, "Earth rune": 3, "Chaos rune": 1}, 11, 19.5, 79, 42, 15),
            "fire_bolt": ("Fire Bolt", 35, {"Air rune": 3, "Fire rune": 4, "Chaos rune": 1}, 12, 22.5, 82, 45, 17),
            "wind_blast": ("Wind Blast", 41, {"Air rune": 3, "Death rune": 1}, 13, 25.5, 85, 49, 19),
            "water_blast": ("Water Blast", 47, {"Air rune": 3, "Water rune": 3, "Death rune": 1}, 14, 28.5, 88, 52, 21),
            "earth_blast": ("Earth Blast", 53, {"Air rune": 3, "Earth rune": 4, "Death rune": 1}, 15, 31.5, 90, 58, 23),
            "fire_blast": ("Fire Blast", 59, {"Air rune": 4, "Fire rune": 5, "Death rune": 1}, 16, 34.5, 95, 63, 25),
            "wind_wave": ("Wind Wave", 62, {"Air rune": 5, "Blood rune": 1}, 17, 36.0, 96, 70, 27),
            "water_wave": ("Water Wave", 65, {"Air rune": 5, "Water rune": 7, "Blood rune": 1}, 18, 37.5, 98, 73, 29),
            "earth_wave": ("Earth Wave", 70, {"Air rune": 5, "Earth rune": 7, "Blood rune": 1}, 19, 40.0, 101, 77, 31),
            "fire_wave": ("Fire Wave", 75, {"Air rune": 5, "Fire rune": 7, "Blood rune": 1}, 20, 42.5, 102, 80, 33),
        }

        for spell_id, (display, level, runes, max_hit, base_xp, unique_id, component_id, autocast_id) in expected.items():
            with self.subTest(spell_id=spell_id):
                spell = COMBAT_MAGIC_SPELL_DATA[spell_id]
                self.assertEqual(spell["display_name"], display)
                self.assertEqual(spell["spellbook"], "standard")
                self.assertEqual(spell["required_magic_level"], level)
                self.assertEqual(spell["rune_cost"], runes)
                self.assertEqual(spell["max_hit_old_hp"], max_hit)
                self.assertEqual(spell["base_magic_xp"], base_xp)
                self.assertEqual(spell["attack_speed"], 5)
                self.assertEqual(spell["unique_id"], unique_id)
                self.assertEqual(spell["component_id"], component_id)
                self.assertEqual(spell["autocast_id"], autocast_id)
                self.assertIn(spell_id.upper(), spell["source"])

    def test_antipoison_potions_match_2011scape_source(self):
        self.assertEqual(COMBAT_ANTIPOISON_POTION_DATA["Antipoison (4)"]["replacement"], "Antipoison (3)")
        self.assertEqual(COMBAT_ANTIPOISON_POTION_DATA["Antipoison (1)"]["replacement"], "Vial")
        self.assertEqual(COMBAT_ANTIPOISON_POTION_DATA["Antipoison (4)"]["immunity_ticks"], 1500)
        self.assertEqual(COMBAT_ANTIPOISON_POTION_DATA["Super antipoison (4)"]["replacement"], "Super antipoison (3)")
        self.assertEqual(COMBAT_ANTIPOISON_POTION_DATA["Super antipoison (1)"]["replacement"], "Vial")
        self.assertEqual(COMBAT_ANTIPOISON_POTION_DATA["Super antipoison (4)"]["immunity_ticks"], 6000)
        self.assertIn("Potion.kt", COMBAT_ANTIPOISON_POTION_DATA["Antipoison (4)"]["source"])
        self.assertIn("PotionType.kt", COMBAT_ANTIPOISON_POTION_DATA["Super antipoison (4)"]["source"])

    def test_simple_enemy_import_rows_match_source(self):
        cow_calf = COMBAT_ENEMY_DATA["cow_calf"]
        ram = COMBAT_ENEMY_DATA["ram"]
        seagull = COMBAT_ENEMY_DATA["seagull"]

        self.assertEqual(cow_calf["stats"]["hitpoints"], 60)
        self.assertEqual(cow_calf["drops"]["guaranteed"], (("Bones", 1), ("Raw beef", 1), ("Cowhide", 1)))
        self.assertEqual(cow_calf["drops"]["tables"], ())
        self.assertTrue(cow_calf["source"].endswith("cow_calf_level_2.plugin.kts"))
        self.assertEqual(ram["stats"]["hitpoints"], 80)
        self.assertEqual(ram["drops"]["guaranteed"], (("Bones", 1),))
        self.assertTrue(ram["source"].endswith("ram_level_2.plugin.kts"))
        self.assertEqual(seagull["group"], "Coastal")
        self.assertEqual(seagull["slayer_xp"], 5.0)
        self.assertTrue(seagull["source"].endswith("seagull_level_2.plugin.kts"))

    def test_giant_rat_and_unicorn_variants_match_source(self):
        rat6 = COMBAT_ENEMY_DATA["giant_rat_level_6"]
        rat26 = COMBAT_ENEMY_DATA["giant_rat_level_26"]
        unicorn = COMBAT_ENEMY_DATA["unicorn"]
        black_unicorn = COMBAT_ENEMY_DATA["black_unicorn"]
        black_bear = COMBAT_ENEMY_DATA["black_bear"]

        self.assertEqual(rat6["display_name"], "Giant rat")
        self.assertEqual(rat6["level"], 6)
        self.assertEqual(rat6["attack_speed"], 4)
        self.assertEqual(rat6["respawn_delay"], 30)
        self.assertEqual(rat6["stats"]["hitpoints"], 100)
        self.assertEqual(rat6["stats"]["attack"], 6)
        self.assertEqual(rat6["stats"]["strength"], 5)
        self.assertEqual(rat6["stats"]["defence"], 2)
        self.assertIs(rat6["drops"], COMBAT_ENEMY_DATA["giant_rat"]["drops"])
        self.assertIn("giant_rat_level_6.plugin.kts", rat6["source"])
        self.assertIn("GIANT_RAT_2091", rat6["source"])

        self.assertEqual(rat26["level"], 26)
        self.assertEqual(rat26["stats"]["hitpoints"], 250)
        self.assertEqual(rat26["stats"]["attack"], 22)
        self.assertEqual(rat26["stats"]["strength"], 23)
        self.assertEqual(rat26["stats"]["defence"], 22)
        self.assertIs(rat26["drops"], COMBAT_ENEMY_DATA["giant_rat"]["drops"])
        self.assertIn("giant_rat_level_26.plugin.kts", rat26["source"])
        self.assertIn("GIANT_RAT_4945", rat26["source"])

        self.assertEqual(unicorn["display_name"], "Unicorn")
        self.assertEqual(unicorn["level"], 15)
        self.assertEqual(unicorn["group"], "Animals")
        self.assertEqual(unicorn["respawn_delay"], 90)
        self.assertEqual(unicorn["stats"]["hitpoints"], 190)
        self.assertEqual(unicorn["stats"]["attack"], 11)
        self.assertEqual(unicorn["stats"]["strength"], 13)
        self.assertEqual(unicorn["stats"]["defence"], 13)
        self.assertEqual(unicorn["drops"]["guaranteed"], (("Bones", 1), ("Unicorn horn", 1)))
        self.assertEqual(unicorn["drops"]["tables"][0]["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 130})
        self.assertIn("unicorn_level_15.plugin.kts", unicorn["source"])
        self.assertIn("Npcs.UNICORN", unicorn["source"])

        self.assertEqual(black_unicorn["display_name"], "Black unicorn")
        self.assertEqual(black_unicorn["level"], 27)
        self.assertEqual(black_unicorn["stats"]["hitpoints"], 290)
        self.assertEqual(black_unicorn["stats"]["attack"], 21)
        self.assertEqual(black_unicorn["stats"]["strength"], 21)
        self.assertEqual(black_unicorn["stats"]["defence"], 23)
        self.assertIs(black_unicorn["drops"], unicorn["drops"])
        self.assertIn("black_unicorn_level_27.plugin.kts", black_unicorn["source"])
        self.assertIn("Npcs.BLACK_UNICORN", black_unicorn["source"])

        (bear_charms,) = black_bear["drops"]["tables"]
        self.assertEqual(black_bear["display_name"], "Black bear")
        self.assertEqual(black_bear["level"], 19)
        self.assertEqual(black_bear["group"], "Animals")
        self.assertEqual(black_bear["attack_speed"], 4)
        self.assertEqual(black_bear["respawn_delay"], 50)
        self.assertEqual(black_bear["slayer_xp"], 25.0)
        self.assertEqual(black_bear["stats"]["hitpoints"], 250)
        self.assertEqual(black_bear["stats"]["attack"], 15)
        self.assertEqual(black_bear["stats"]["strength"], 16)
        self.assertEqual(black_bear["stats"]["defence"], 13)
        self.assertEqual(black_bear["drops"]["guaranteed"], (("Bones", 1), ("Bear fur", 1), ("Raw bear meat", 1)))
        self.assertEqual(bear_charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in bear_charms["slots"]), 1000)
        self.assertEqual(bear_charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 180})
        self.assertEqual(bear_charms["slots"][1], {"item": "Green charm", "quantity": 1, "slots": 8})
        self.assertEqual(bear_charms["slots"][-1], {"slots": 796})
        self.assertIn("black_bear_level_19.plugin.kts", black_bear["source"])
        self.assertIn("SlayerAssignment.BEAR", black_bear["source"])

    def test_wolf_rows_match_source_and_charm_tables(self):
        wolf = COMBAT_ENEMY_DATA["wolf"]
        white_25 = COMBAT_ENEMY_DATA["white_wolf_level_25"]
        white_38 = COMBAT_ENEMY_DATA["white_wolf_level_38"]
        big_wolf = COMBAT_ENEMY_DATA["big_wolf"]

        (wolf_main,) = wolf["drops"]["tables"]
        self.assertEqual(wolf["display_name"], "Wolf")
        self.assertEqual(wolf["level"], 11)
        self.assertEqual(wolf["group"], "Animals")
        self.assertEqual(wolf["attack_speed"], 4)
        self.assertEqual(wolf["respawn_delay"], 90)
        self.assertEqual(wolf["slayer_xp"], 10.0)
        self.assertEqual(wolf["stats"]["hitpoints"], 100)
        self.assertEqual(wolf["stats"]["attack"], 10)
        self.assertEqual(wolf["stats"]["strength"], 10)
        self.assertEqual(wolf["stats"]["defence"], 10)
        self.assertEqual(wolf["drops"]["guaranteed"], (("Wolf bones", 1), ("Bones", 1)))
        self.assertEqual(wolf_main["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in wolf_main["slots"]), 1000)
        self.assertEqual(wolf_main["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 20})
        self.assertEqual(wolf_main["slots"][1], {"item": "Green charm", "quantity": 1, "slots": 30})
        self.assertEqual(wolf_main["slots"][2], {"item": "Crimson charm", "quantity": 1, "slots": 50})
        self.assertEqual(wolf_main["slots"][3], {"item": "Blue charm", "quantity": 1, "slots": 10})
        self.assertEqual(wolf_main["slots"][-1], {"slots": 890})
        self.assertIn("wolf_lvl_11.plugin.kts", wolf["source"])
        self.assertIn("attackStyle STAB", wolf["source"])

        (white_main,) = white_25["drops"]["tables"]
        self.assertEqual(white_25["display_name"], "White wolf")
        self.assertEqual(white_25["level"], 25)
        self.assertEqual(white_25["slayer_xp"], 34.0)
        self.assertEqual(white_25["stats"]["hitpoints"], 340)
        self.assertEqual(white_25["stats"]["attack"], 20)
        self.assertEqual(white_25["stats"]["strength"], 16)
        self.assertEqual(white_25["stats"]["defence"], 22)
        self.assertEqual(white_25["drops"]["guaranteed"], (("Wolf bones", 1),))
        self.assertEqual(white_main["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in white_main["slots"]), 1000)
        self.assertEqual(white_main["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 110})
        self.assertEqual(white_main["slots"][1], {"item": "Green charm", "quantity": 1, "slots": 50})
        self.assertEqual(white_main["slots"][2], {"item": "Crimson charm", "quantity": 1, "slots": 140})
        self.assertEqual(white_main["slots"][3], {"item": "Blue charm", "quantity": 1, "slots": 80})
        self.assertEqual(white_main["slots"][-1], {"slots": 620})
        self.assertIn("white_wolf_lvl_25.plugin.kts", white_25["source"])

        self.assertEqual(white_38["level"], 38)
        self.assertEqual(white_38["slayer_xp"], 44.0)
        self.assertEqual(white_38["stats"]["hitpoints"], 440)
        self.assertEqual(white_38["stats"]["attack"], 30)
        self.assertEqual(white_38["stats"]["strength"], 31)
        self.assertEqual(white_38["stats"]["defence"], 32)
        self.assertIs(white_38["drops"], white_25["drops"])
        self.assertIn("white_wolf_lvl_38.plugin.kts", white_38["source"])

        self.assertEqual(big_wolf["display_name"], "Big wolf")
        self.assertEqual(big_wolf["level"], 73)
        self.assertEqual(big_wolf["slayer_xp"], 74.0)
        self.assertEqual(big_wolf["stats"]["hitpoints"], 740)
        self.assertEqual(big_wolf["stats"]["attack"], 60)
        self.assertEqual(big_wolf["stats"]["strength"], 61)
        self.assertEqual(big_wolf["stats"]["defence"], 62)
        self.assertIs(big_wolf["drops"], white_25["drops"])
        self.assertIn("big_wolf_lvl_73.plugin.kts", big_wolf["source"])
        for enemy in (wolf, white_25, white_38, big_wolf):
            self.assertEqual(enemy["group"], "Animals")
            self.assertIn("SlayerAssignment.WOLF", enemy["source"])

    def test_giant_bat_row_matches_source(self):
        giant_bat = COMBAT_ENEMY_DATA["giant_bat"]

        self.assertEqual(giant_bat["display_name"], "Giant bat")
        self.assertEqual(giant_bat["level"], 27)
        self.assertEqual(giant_bat["group"], "Bats")
        self.assertEqual(giant_bat["attack_speed"], 4)
        self.assertEqual(giant_bat["respawn_delay"], 35)
        self.assertEqual(giant_bat["slayer_xp"], 32.0)
        self.assertEqual(giant_bat["stats"]["hitpoints"], 320)
        self.assertEqual(giant_bat["stats"]["attack"], 22)
        self.assertEqual(giant_bat["stats"]["strength"], 22)
        self.assertEqual(giant_bat["stats"]["defence"], 22)
        self.assertEqual(giant_bat["bonuses"]["defence_stab"], 10)
        self.assertEqual(giant_bat["bonuses"]["defence_slash"], 10)
        self.assertEqual(giant_bat["bonuses"]["defence_crush"], 12)
        self.assertEqual(giant_bat["bonuses"]["defence_magic"], 10)
        self.assertEqual(giant_bat["bonuses"]["defence_ranged"], 8)
        self.assertEqual(giant_bat["drops"]["guaranteed"], (("Bat bones", 1),))
        self.assertEqual(giant_bat["drops"]["tables"], ())
        self.assertIn("giant_bat_level_27.plugin.kts", giant_bat["source"])
        self.assertIn("SlayerAssignment.BAT", giant_bat["source"])

    def test_giant_rows_match_source_and_drop_tables(self):
        expected = {
            "hill_giant": (28, 350, 18, 22, 26, 6, 35.0, HILL_GIANT_DROPS, "hill_giant_lvl_28.plugin.kts"),
            "moss_giant": (42, 600, 30, 30, 30, 6, 60.0, MOSS_GIANT_DROPS, "moss_giant_level_42.plugin.kts"),
            "ice_giant": (53, 700, 40, 40, 40, 5, 70.0, ICE_GIANT_DROPS, "ice_giant_level_53.plugin.kts"),
        }

        for key, (level, hitpoints, attack, strength, defence, attack_speed, slayer_xp, drops, source_file) in expected.items():
            with self.subTest(key=key):
                giant = COMBAT_ENEMY_DATA[key]
                self.assertEqual(giant["group"], "Giants")
                self.assertEqual(giant["attack_speed"], attack_speed)
                self.assertEqual(giant["respawn_delay"], 30)
                self.assertEqual(giant["level"], level)
                self.assertEqual(giant["slayer_xp"], slayer_xp)
                self.assertEqual(giant["stats"]["hitpoints"], hitpoints)
                self.assertEqual(giant["stats"]["attack"], attack)
                self.assertEqual(giant["stats"]["strength"], strength)
                self.assertEqual(giant["stats"]["defence"], defence)
                self.assertIs(giant["drops"], drops)
                self.assertIn(source_file, giant["source"])
                self.assertIn("aggro radius", giant["source"])

        hill_main, hill_charms = COMBAT_ENEMY_DATA["hill_giant"]["drops"]["tables"]
        moss_main, moss_charms = COMBAT_ENEMY_DATA["moss_giant"]["drops"]["tables"]
        ice_main, ice_tertiary = COMBAT_ENEMY_DATA["ice_giant"]["drops"]["tables"]
        self.assertEqual(COMBAT_ENEMY_DATA["hill_giant"]["bonuses"]["attack_stab"], 18)
        self.assertEqual(COMBAT_ENEMY_DATA["hill_giant"]["bonuses"]["attack_crush"], 16)
        self.assertEqual(COMBAT_ENEMY_DATA["moss_giant"]["bonuses"]["attack_stab"], 33)
        self.assertEqual(COMBAT_ENEMY_DATA["moss_giant"]["bonuses"]["attack_crush"], 31)
        self.assertEqual(COMBAT_ENEMY_DATA["ice_giant"]["bonuses"]["attack_slash"], 29)
        self.assertEqual(COMBAT_ENEMY_DATA["ice_giant"]["bonuses"]["melee_strength"], 31)
        self.assertEqual(COMBAT_ENEMY_DATA["ice_giant"]["bonuses"]["defence_crush"], 2)
        self.assertEqual(hill_main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in hill_main["slots"]), 128)
        self.assertEqual(hill_main["slots"][14], {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7})
        self.assertEqual(hill_main["slots"][15], {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18})
        self.assertEqual(hill_main["slots"][-1], {"table": COMBAT_GEM_DROP_TABLE, "slots": 3})
        self.assertEqual(hill_charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 150})
        self.assertEqual(hill_charms["slots"][-1], {"slots": 828})
        self.assertEqual(moss_main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in moss_main["slots"]), 128)
        self.assertEqual(moss_main["slots"][23], {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 5})
        self.assertEqual(moss_main["slots"][24], {"table": COMBAT_UNCOMMON_SEED_DROP_TABLE, "slots": 35})
        self.assertEqual(moss_main["slots"][-1], {"table": COMBAT_GEM_DROP_TABLE, "slots": 4})
        self.assertEqual(moss_charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 360})
        self.assertEqual(moss_charms["slots"][-1], {"slots": 573})
        self.assertEqual(ice_main["total"], 1024)
        # Source declares total(1024) but its slots add to 1026; the runtime roll still uses the declared total.
        self.assertEqual(sum(slot["slots"] for slot in ice_main["slots"]), 1026)
        self.assertEqual(ice_main["slots"][16], {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 64})
        self.assertEqual(ice_main["slots"][-1], {"table": COMBAT_GEM_DROP_TABLE, "slots": 32})
        self.assertEqual(ice_tertiary["total"], 100000)
        self.assertEqual(sum(slot["slots"] for slot in ice_tertiary["slots"]), 100000)
        self.assertEqual(ice_tertiary["slots"][2], {"item": "Champion's scroll", "quantity": 1, "slots": 20})

    def test_ghost_row_matches_source_and_has_no_death_drops(self):
        ghost = COMBAT_ENEMY_DATA["ghost"]

        self.assertEqual(ghost["display_name"], "Ghost")
        self.assertEqual(ghost["level"], 19)
        self.assertEqual(ghost["group"], "Undead")
        self.assertEqual(ghost["attack_speed"], 4)
        self.assertEqual(ghost["respawn_delay"], 40)
        self.assertEqual(ghost["slayer_xp"], 25.0)
        self.assertEqual(ghost["stats"]["hitpoints"], 250)
        self.assertEqual(ghost["stats"]["attack"], 13)
        self.assertEqual(ghost["stats"]["strength"], 13)
        self.assertEqual(ghost["stats"]["defence"], 18)
        self.assertEqual(ghost["bonuses"]["defence_stab"], 5)
        self.assertEqual(ghost["bonuses"]["defence_slash"], 5)
        self.assertEqual(ghost["bonuses"]["defence_crush"], 5)
        self.assertEqual(ghost["bonuses"]["defence_magic"], -5)
        self.assertEqual(ghost["bonuses"]["defence_ranged"], 5)
        self.assertEqual(ghost["drops"], {"guaranteed": (), "tables": ()})
        self.assertIn("ghost_level_19.plugin.kts", ghost["source"])
        self.assertIn("SlayerAssignment.GHOST", ghost["source"])
        self.assertIn("no on_npc_death drop callback", ghost["source"])

    def test_zombie_rows_match_source_and_level_25_drop_variant(self):
        expected = {
            "zombie_level_13": (13, 220, 8, 9, 10, 22.0, ZOMBIE_DROPS, "zombie_lvl_13.plugin.kts"),
            "zombie_level_18": (18, 240, 13, 13, 18, 24.0, ZOMBIE_DROPS, "zombie_lvl_18.plugin.kts"),
            "zombie_level_24": (24, 300, 19, 21, 16, 30.0, ZOMBIE_DROPS, "zombie_lvl_24.plugin.kts"),
            "zombie_level_25": (25, 300, 19, 21, 16, 30.0, ZOMBIE_LEVEL_25_DROPS, "zombie_lvl_25.plugin.kts"),
            "zombie_level_30": (30, 300, 25, 29, 20, 30.0, ZOMBIE_DROPS, "zombie_lvl_30.plugin.kts"),
            "zombie_level_44": (44, 400, 35, 40, 40, 30.0, ZOMBIE_DROPS, "zombie_lvl_44.plugin.kts"),
            "zombie_level_53": (53, 500, 55, 40, 48, 50.0, ZOMBIE_DROPS, "zombie_lvl_53.plugin.kts"),
        }

        for key, (level, hitpoints, attack, strength, defence, slayer_xp, drops, source_file) in expected.items():
            with self.subTest(key=key):
                zombie = COMBAT_ENEMY_DATA[key]
                self.assertEqual(zombie["display_name"], "Zombie")
                self.assertEqual(zombie["level"], level)
                self.assertEqual(zombie["group"], "Undead")
                self.assertEqual(zombie["attack_speed"], 5)
                self.assertEqual(zombie["respawn_delay"], 35)
                self.assertEqual(zombie["slayer_xp"], slayer_xp)
                self.assertEqual(zombie["stats"]["hitpoints"], hitpoints)
                self.assertEqual(zombie["stats"]["attack"], attack)
                self.assertEqual(zombie["stats"]["strength"], strength)
                self.assertEqual(zombie["stats"]["defence"], defence)
                self.assertIs(zombie["drops"], drops)
                self.assertIn(source_file, zombie["source"])
                self.assertIn("SlayerAssignment.ZOMBIE", zombie["source"])

        main, charms = COMBAT_ENEMY_DATA["zombie_level_13"]["drops"]["tables"]
        level_25_main = COMBAT_ENEMY_DATA["zombie_level_25"]["drops"]["tables"][0]
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertEqual(main["slots"][0], {"item": "Iron hatchet", "quantity": 1, "slots": 3})
        self.assertEqual(main["slots"][13], {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 25})
        self.assertEqual(main["slots"][-3], {"slots": 8})
        self.assertEqual(main["slots"][-2], {"item": "Fishing bait", "quantity": 5, "slots": 5})
        self.assertEqual(level_25_main["slots"][0], {"item": "Iron hatchet", "quantity": 1, "slots": 5})
        self.assertEqual(level_25_main["slots"][-3], {"slots": 6})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 30})
        self.assertEqual(charms["slots"][-1], {"slots": 937})

        self.assertEqual(COMBAT_ENEMY_DATA["zombie_level_24"]["bonuses"]["attack_crush"], 7)
        self.assertEqual(COMBAT_ENEMY_DATA["zombie_level_24"]["bonuses"]["defence_magic"], 10)
        self.assertEqual(COMBAT_ENEMY_DATA["zombie_level_53"]["bonuses"]["attack_stab"], 19)
        self.assertEqual(COMBAT_ENEMY_DATA["zombie_level_53"]["bonuses"]["defence_ranged"], 21)

    def test_skeleton_rows_match_source_and_share_two_drop_tables(self):
        expected = {
            "skeleton_level_21": (21, 240, 17, 17, 17, 35, 24.0, SKELETON_LOW_DROPS, "skeleton_lvl_21.plugin.kts"),
            "skeleton_level_22": (22, 290, 15, 18, 17, 70, 29.0, SKELETON_LOW_DROPS, "skeleton_lvl_22.plugin.kts"),
            "skeleton_level_25": (25, 170, 24, 24, 24, 60, 17.0, SKELETON_HIGH_DROPS, "skeleton_lvl_25.plugin.kts"),
            "skeleton_level_45": (45, 590, 32, 35, 36, 30, 59.0, SKELETON_HIGH_DROPS, "skeleton_level_45.plugin.kts"),
            "skeleton_level_60": (60, 700, 50, 50, 40, 70, 70.0, SKELETON_HIGH_DROPS, "skeleton_lvl_60.plugin.kts"),
            "skeleton_level_68": (68, 700, 60, 50, 60, 60, 65.0, SKELETON_HIGH_DROPS, "skeleton_lvl_68.plugin.kts"),
            "skeleton_level_85": (85, 770, 74, 74, 74, 60, 65.0, SKELETON_HIGH_DROPS, "skeleton_lvl_85.plugin.kts"),
        }

        for key, (level, hitpoints, attack, strength, defence, respawn, slayer_xp, drops, source_file) in expected.items():
            with self.subTest(key=key):
                skeleton = COMBAT_ENEMY_DATA[key]
                self.assertEqual(skeleton["display_name"], "Skeleton")
                self.assertEqual(skeleton["level"], level)
                self.assertEqual(skeleton["group"], "Undead")
                self.assertEqual(skeleton["attack_speed"], 4)
                self.assertEqual(skeleton["respawn_delay"], respawn)
                self.assertEqual(skeleton["slayer_xp"], slayer_xp)
                self.assertEqual(skeleton["stats"]["hitpoints"], hitpoints)
                self.assertEqual(skeleton["stats"]["attack"], attack)
                self.assertEqual(skeleton["stats"]["strength"], strength)
                self.assertEqual(skeleton["stats"]["defence"], defence)
                self.assertIs(skeleton["drops"], drops)
                self.assertIn(source_file, skeleton["source"])
                self.assertIn("SlayerAssignment.SKELETON", skeleton["source"])

        low_main, low_charms = COMBAT_ENEMY_DATA["skeleton_level_21"]["drops"]["tables"]
        high_main, high_charms = COMBAT_ENEMY_DATA["skeleton_level_25"]["drops"]["tables"]
        self.assertEqual(low_main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in low_main["slots"]), 1024)
        self.assertEqual(low_main["slots"][0], {"item": "Bronze arrows", "quantity": 2, "slots": 56})
        self.assertEqual(low_main["slots"][9], {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 49})
        self.assertEqual(low_main["slots"][-1], {"table": COMBAT_GEM_DROP_TABLE, "slots": 8})
        self.assertEqual(high_main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in high_main["slots"]), 128)
        self.assertEqual(high_main["slots"][0], {"item": "Iron med helm", "quantity": 1, "slots": 6})
        self.assertEqual(high_main["slots"][10], {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 20})
        self.assertEqual(high_main["slots"][-1], {"table": COMBAT_GEM_DROP_TABLE, "slots": 2})
        self.assertEqual(low_charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 50})
        self.assertEqual(high_charms["slots"][-1], {"slots": 894})

        self.assertEqual(COMBAT_ENEMY_DATA["skeleton_level_25"]["bonuses"]["attack_crush"], 14)
        self.assertEqual(COMBAT_ENEMY_DATA["skeleton_level_60"]["bonuses"]["defence_stab"], 35)
        self.assertEqual(COMBAT_ENEMY_DATA["skeleton_level_85"]["bonuses"]["attack_slash"], 14)
        self.assertEqual(COMBAT_ENEMY_DATA["skeleton_level_85"]["bonuses"]["defence_ranged"], 70)

    def test_duck_rows_split_land_and_water_source_drops(self):
        land = COMBAT_ENEMY_DATA["duck_land"]
        water = COMBAT_ENEMY_DATA["duck_water"]

        for duck in (land, water):
            self.assertEqual(duck["level"], 1)
            self.assertEqual(duck["group"], "Birds")
            self.assertEqual(duck["attack_speed"], 4)
            self.assertEqual(duck["respawn_delay"], 25)
            self.assertEqual(duck["slayer_xp"], 3.0)
            self.assertEqual(duck["stats"]["hitpoints"], 30)
            self.assertEqual(duck["stats"]["attack"], 1)
            self.assertEqual(duck["stats"]["strength"], 1)
            self.assertEqual(duck["stats"]["defence"], 1)
            self.assertEqual(duck["bonuses"]["attack_stab"], -47)
            self.assertEqual(duck["bonuses"]["defence_ranged"], -42)
            self.assertIn("duck_level_1.plugin.kts", duck["source"])

        self.assertEqual(land["display_name"], "Duck (land)")
        self.assertEqual(land["drops"], {"guaranteed": (("Bones", 1),), "tables": ()})
        self.assertIn("DUCK_6113", land["source"])
        self.assertIn("Npcs.DRAKE", land["source"])
        self.assertEqual(water["display_name"], "Duck (water)")
        self.assertEqual(water["drops"], {"guaranteed": (), "tables": ()})
        self.assertIn("no death drop callback", water["source"])

    def test_spider_import_rows_match_source_and_quantity_range(self):
        spider = COMBAT_ENEMY_DATA["spider"]
        giant_spider = COMBAT_ENEMY_DATA["giant_spider"]

        self.assertEqual(spider["stats"]["hitpoints"], 20)
        self.assertEqual(spider["respawn_delay"], 35)
        self.assertEqual(spider["drops"]["guaranteed"], ())
        self.assertEqual(spider["drops"]["tables"][0]["total"], 200)
        self.assertEqual(spider["drops"]["tables"][0]["slots"][0]["item"], "Gold charm")
        self.assertTrue(spider["source"].endswith("spider_level_1.plugin.kts"))
        self.assertEqual(giant_spider["stats"]["hitpoints"], 50)
        self.assertEqual(giant_spider["slayer_xp"], 5.0)
        self.assertEqual(giant_spider["drops"]["tables"][0]["slots"][0]["quantity_range"], (4, 6))
        self.assertEqual(giant_spider["drops"]["tables"][1]["slots"][0]["item"], "Bronze med helm")
        self.assertTrue(giant_spider["source"].endswith("giant_spider_level_2.plugin.kts"))

    def test_poison_enemy_rows_match_source_and_no_drop_handler(self):
        scorpion = COMBAT_ENEMY_DATA["poison_scorpion"]
        spider = COMBAT_ENEMY_DATA["poison_spider"]
        spider_64 = COMBAT_ENEMY_DATA["poison_spider_level_64"]

        self.assertEqual(scorpion["level"], 20)
        self.assertEqual(scorpion["group"], "Scorpions")
        self.assertEqual(scorpion["attack_speed"], 4)
        self.assertEqual(scorpion["respawn_delay"], 25)
        self.assertEqual(scorpion["poison_damage"], 3)
        self.assertEqual(scorpion["stats"]["hitpoints"], 230)
        self.assertEqual(scorpion["stats"]["attack"], 16)
        self.assertEqual(scorpion["stats"]["strength"], 17)
        self.assertEqual(scorpion["stats"]["defence"], 15)
        self.assertEqual(scorpion["bonuses"]["defence_slash"], 15)
        self.assertEqual(scorpion["drops"], {"guaranteed": (), "tables": ()})
        self.assertIn("poison_scorpion_lvl_20.plugin.kts", scorpion["source"])
        self.assertIn("no DropTableFactory registration", scorpion["source"])

        self.assertEqual(spider["level"], 31)
        self.assertEqual(spider["group"], "Spiders")
        self.assertEqual(spider["poison_damage"], 3)
        self.assertEqual(spider["stats"]["hitpoints"], 250)
        self.assertEqual(spider["stats"]["attack"], 28)
        self.assertEqual(spider["bonuses"]["defence_stab"], 20)
        self.assertEqual(spider["drops"], {"guaranteed": (), "tables": ()})
        self.assertIn("poison_spider_lvl_31.plugin.kts", spider["source"])

        self.assertEqual(spider_64["level"], 64)
        self.assertEqual(spider_64["group"], "Spiders")
        self.assertEqual(spider_64["poison_damage"], 6)
        self.assertEqual(spider_64["slayer_xp"], 64.0)
        self.assertEqual(spider_64["stats"]["hitpoints"], 640)
        self.assertEqual(spider_64["stats"]["attack"], 50)
        self.assertEqual(spider_64["stats"]["strength"], 58)
        self.assertEqual(spider_64["stats"]["defence"], 52)
        self.assertEqual(spider_64["bonuses"]["defence_magic"], 14)
        self.assertEqual(spider_64["drops"], {"guaranteed": (), "tables": ()})
        self.assertIn("poison_spider_lvl_64.plugin.kts", spider_64["source"])

    def test_scorpion_and_higher_spider_rows_match_source(self):
        scorpion = COMBAT_ENEMY_DATA["scorpion"]
        king = COMBAT_ENEMY_DATA["king_scorpion"]
        pit = COMBAT_ENEMY_DATA["pit_scorpion"]
        scorpion_59 = COMBAT_ENEMY_DATA["scorpion_level_59"]
        spider = COMBAT_ENEMY_DATA["spider_level_24"]
        deadly_red = COMBAT_ENEMY_DATA["deadly_red_spider"]
        giant = COMBAT_ENEMY_DATA["giant_spider_level_50"]

        self.assertEqual(scorpion["level"], 14)
        self.assertEqual(scorpion["group"], "Scorpions")
        self.assertEqual(scorpion["stats"]["hitpoints"], 170)
        self.assertEqual(scorpion["stats"]["strength"], 12)
        self.assertEqual(scorpion["bonuses"]["defence_slash"], 15)
        self.assertEqual(scorpion["drops"]["tables"][0]["total"], 1000)
        self.assertEqual(scorpion["drops"]["tables"][0]["slots"][1], {"item": "Green charm", "quantity": 1, "slots": 70})
        self.assertTrue(scorpion["source"].endswith("scorpion_level_14.plugin.kts"))

        self.assertEqual(king["level"], 32)
        self.assertEqual(king["group"], "Scorpions")
        self.assertEqual(king["stats"]["hitpoints"], 300)
        self.assertEqual(king["stats"]["attack"], 30)
        self.assertEqual(king["stats"]["strength"], 29)
        self.assertEqual(king["stats"]["defence"], 23)
        self.assertEqual(king["bonuses"]["defence_slash"], 15)
        self.assertEqual(king["drops"], {"guaranteed": (), "tables": ()})
        self.assertIn("king_scorpion_level_32.plugin.kts", king["source"])
        self.assertIn("no DropTableFactory registration", king["source"])

        self.assertEqual(pit["display_name"], "Pit scorpion")
        self.assertEqual(pit["level"], 28)
        self.assertEqual(pit["group"], "Scorpions")
        self.assertEqual(pit["attack_speed"], 4)
        self.assertEqual(pit["respawn_delay"], 25)
        self.assertEqual(pit["slayer_xp"], 32.0)
        self.assertEqual(pit["stats"]["hitpoints"], 320)
        self.assertEqual(pit["stats"]["attack"], 20)
        self.assertEqual(pit["stats"]["strength"], 25)
        self.assertEqual(pit["stats"]["defence"], 28)
        self.assertEqual(pit["bonuses"]["defence_slash"], 13)
        self.assertEqual(pit["drops"], {"guaranteed": (), "tables": ()})
        self.assertIn("pit_sorpion_lvl_28.plugin.kts", pit["source"])
        self.assertIn("no DropTableFactory registration", pit["source"])

        self.assertEqual(scorpion_59["level"], 59)
        self.assertEqual(scorpion_59["attack_speed"], 4)
        self.assertEqual(scorpion_59["respawn_delay"], 22)
        self.assertEqual(scorpion_59["slayer_xp"], 55.0)
        self.assertEqual(scorpion_59["stats"]["hitpoints"], 550)
        self.assertEqual(scorpion_59["stats"]["attack"], 50)
        self.assertEqual(scorpion_59["stats"]["strength"], 52)
        self.assertEqual(scorpion_59["stats"]["defence"], 50)
        self.assertEqual(scorpion_59["bonuses"]["defence_ranged"], 55)
        self.assertIs(scorpion_59["drops"], scorpion["drops"])
        self.assertIn("scorpion_level_59.plugin.kts", scorpion_59["source"])

        self.assertEqual(spider["level"], 24)
        self.assertEqual(spider["respawn_delay"], 27)
        self.assertEqual(spider["stats"]["hitpoints"], 220)
        self.assertEqual(spider["bonuses"]["attack_stab"], 53)
        self.assertEqual(spider["drops"]["tables"][0]["total"], 200)
        self.assertTrue(spider["source"].endswith("spider_level_24.plugin.kts"))

        self.assertEqual(deadly_red["level"], 34)
        self.assertEqual(deadly_red["stats"]["hitpoints"], 350)
        self.assertEqual(deadly_red["stats"]["strength"], 25)
        self.assertEqual(deadly_red["drops"]["tables"][0]["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 260})
        self.assertTrue(deadly_red["source"].endswith("deadly_red_spider_level_34.plugin.kts"))

        self.assertEqual(giant["level"], 50)
        self.assertEqual(giant["respawn_delay"], 25)
        self.assertEqual(giant["stats"]["hitpoints"], 500)
        self.assertEqual(giant["stats"]["strength"], 51)
        self.assertEqual(giant["bonuses"]["attack_crush"], 10)
        self.assertEqual(giant["drops"]["tables"][0]["slots"][0]["quantity_range"], (4, 6))
        self.assertEqual(giant["drops"]["tables"][1]["slots"][0]["item"], "Bronze med helm")
        self.assertTrue(giant["source"].endswith("giant_spider_level_50.plugin.kts"))

    def test_highwayman_import_row_matches_source_and_quantity_range(self):
        highwayman = COMBAT_ENEMY_DATA["highwayman"]

        self.assertEqual(highwayman["level"], 5)
        self.assertEqual(highwayman["group"], "Humanoids")
        self.assertEqual(highwayman["respawn_delay"], 60)
        self.assertEqual(highwayman["stats"]["hitpoints"], 130)
        self.assertEqual(highwayman["stats"]["defence"], 4)
        self.assertEqual(highwayman["bonuses"]["attack_stab"], 6)
        self.assertEqual(highwayman["bonuses"]["melee_strength"], 7)
        self.assertEqual(highwayman["drops"]["guaranteed"], (("Bones", 1), ("Cape", 1)))
        self.assertEqual(highwayman["drops"]["tables"][0]["total"], 20)
        self.assertEqual(highwayman["drops"]["tables"][0]["slots"][0]["item"], "Iron bolts")
        self.assertEqual(highwayman["drops"]["tables"][0]["slots"][0]["quantity_range"], (2, 12))
        self.assertTrue(highwayman["source"].endswith("highwayman_level_5.plugin.kts"))

    def test_mugger_import_row_matches_source_and_nested_minor_herbs(self):
        mugger = COMBAT_ENEMY_DATA["mugger"]
        main = mugger["drops"]["tables"][0]
        tertiary = mugger["drops"]["tables"][1]

        self.assertEqual(mugger["level"], 6)
        self.assertEqual(mugger["group"], "Humanoids")
        self.assertEqual(mugger["attack_speed"], 4)
        self.assertEqual(mugger["respawn_delay"], 25)
        self.assertEqual(mugger["stats"]["hitpoints"], 80)
        self.assertEqual(mugger["stats"]["attack"], 5)
        self.assertEqual(mugger["stats"]["strength"], 5)
        self.assertEqual(mugger["stats"]["defence"], 5)
        self.assertEqual(mugger["bonuses"]["melee_strength"], -21)
        self.assertEqual(mugger["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 162})
        self.assertEqual(main["slots"][4], {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 104})
        self.assertEqual(main["slots"][9], {"item": "Rope", "quantity": 1, "slots": 270})
        self.assertEqual(main["slots"][-1], {"item": "Cabbage", "quantity": 1, "slots": 8})
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
        self.assertIn("mugger_level_6.plugin.kts", mugger["source"])
        self.assertIn("MUGGER_7161", mugger["source"])

    def test_thug_import_row_matches_source_minor_herbs_and_charms(self):
        thug = COMBAT_ENEMY_DATA["thug"]
        main, charms, tertiary = thug["drops"]["tables"]

        self.assertEqual(thug["level"], 10)
        self.assertEqual(thug["group"], "Humanoids")
        self.assertEqual(thug["attack_speed"], 4)
        self.assertEqual(thug["respawn_delay"], 50)
        self.assertEqual(thug["stats"]["hitpoints"], 180)
        self.assertEqual(thug["stats"]["attack"], 7)
        self.assertEqual(thug["stats"]["strength"], 5)
        self.assertEqual(thug["stats"]["defence"], 9)
        self.assertEqual(thug["bonuses"]["attack_stab"], 5)
        self.assertEqual(thug["bonuses"]["attack_crush"], 5)
        self.assertEqual(thug["bonuses"]["defence_stab"], 2)
        self.assertEqual(thug["bonuses"]["defence_slash"], 3)
        self.assertEqual(thug["bonuses"]["defence_crush"], 3)
        self.assertEqual(thug["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertEqual(main["slots"][0], {"item": "Iron med helm", "quantity": 1, "slots": 4})
        self.assertEqual(main["slots"][2], {"item": "Steel hatchet", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][15], {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 24})
        self.assertEqual(main["slots"][-1], {"slots": 30})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 120})
        self.assertEqual(charms["slots"][3], {"item": "Blue charm", "quantity": 1, "slots": 5})
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
        self.assertIn("thug_level_10.plugin.kts", thug["source"])
        self.assertIn("THUG_7114", thug["source"])

    def test_thief_import_row_matches_source_and_nested_minor_herbs(self):
        thief = COMBAT_ENEMY_DATA["thief"]
        main, tertiary = thief["drops"]["tables"]

        self.assertEqual(thief["level"], 16)
        self.assertEqual(thief["group"], "Humanoids")
        self.assertEqual(thief["attack_speed"], 4)
        self.assertEqual(thief["respawn_delay"], 25)
        self.assertEqual(thief["stats"]["hitpoints"], 170)
        self.assertEqual(thief["stats"]["attack"], 14)
        self.assertEqual(thief["stats"]["strength"], 13)
        self.assertEqual(thief["stats"]["defence"], 12)
        self.assertEqual(thief["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertEqual(main["slots"][0], {"item": "Bronze med helm", "quantity": 1, "slots": 2})
        self.assertEqual(main["slots"][1], {"item": "Iron dagger", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][2], {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 22})
        self.assertEqual(main["slots"][16], {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 23})
        self.assertEqual(main["slots"][-1], {"slots": 8})
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
        self.assertIn("thief_level_16.plugin.kts", thief["source"])
        self.assertIn("THIEF_5929", thief["source"])

    def test_market_and_jail_guard_rows_match_source(self):
        market = COMBAT_ENEMY_DATA["market_guard"]
        jail = COMBAT_ENEMY_DATA["jail_guard"]

        self.assertEqual(market["display_name"], "Market guard")
        self.assertEqual(market["level"], 20)
        self.assertEqual(market["group"], "Humanoids")
        self.assertEqual(market["attack_speed"], 5)
        self.assertEqual(market["respawn_delay"], 50)
        self.assertEqual(market["stats"]["hitpoints"], 220)
        self.assertEqual(market["stats"]["attack"], 17)
        self.assertEqual(market["stats"]["strength"], 18)
        self.assertEqual(market["stats"]["defence"], 13)
        self.assertEqual(market["bonuses"]["attack_stab"], 9)
        self.assertEqual(market["bonuses"]["attack_crush"], 7)
        self.assertEqual(market["bonuses"]["defence_stab"], 24)
        self.assertEqual(market["bonuses"]["defence_slash"], 14)
        self.assertEqual(market["bonuses"]["defence_crush"], 19)
        self.assertEqual(market["bonuses"]["defence_magic"], 4)
        self.assertEqual(market["bonuses"]["defence_ranged"], 16)
        self.assertEqual(market["drops"], {"guaranteed": (("Bones", 1),), "tables": ()})
        self.assertIn("market_guard_level_20.plugin.kts", market["source"])
        self.assertIn("MARKET_GUARD_2236", market["source"])

        self.assertEqual(jail["display_name"], "Jail guard")
        self.assertEqual(jail["level"], 26)
        self.assertEqual(jail["group"], "Humanoids")
        self.assertEqual(jail["attack_speed"], 5)
        self.assertEqual(jail["respawn_delay"], 30)
        self.assertEqual(jail["stats"]["hitpoints"], 320)
        self.assertEqual(jail["stats"]["attack"], 19)
        self.assertEqual(jail["stats"]["strength"], 23)
        self.assertEqual(jail["stats"]["defence"], 21)
        self.assertEqual(jail["bonuses"]["attack_stab"], 5)
        self.assertEqual(jail["bonuses"]["attack_crush"], 9)
        self.assertEqual(jail["bonuses"]["defence_stab"], 8)
        self.assertEqual(jail["bonuses"]["defence_slash"], 9)
        self.assertEqual(jail["bonuses"]["defence_crush"], 10)
        self.assertEqual(jail["bonuses"]["defence_magic"], 4)
        self.assertEqual(jail["bonuses"]["defence_ranged"], 9)
        self.assertEqual(jail["drops"], {"guaranteed": (("Bones", 1),), "tables": ()})
        self.assertIn("jail_guard_level_26.plugin.kts", jail["source"])
        self.assertIn("JAIL_GUARD_917", jail["source"])
        self.assertIn("aggro radius 4", jail["source"])

    def test_guard_import_rows_match_source_split_variants_and_shared_drops(self):
        varrock = COMBAT_ENEMY_DATA["guard_varrock"]
        sword = COMBAT_ENEMY_DATA["guard_sword"]
        battleaxe = COMBAT_ENEMY_DATA["guard_battleaxe"]

        self.assertEqual(varrock["display_name"], "Guard (Varrock)")
        self.assertEqual(sword["display_name"], "Guard (sword)")
        self.assertEqual(battleaxe["display_name"], "Guard (battleaxe)")
        for guard in (varrock, sword, battleaxe):
            self.assertEqual(guard["level"], 21)
            self.assertEqual(guard["group"], "Humanoids")
            self.assertEqual(guard["attack_speed"], 4)
            self.assertEqual(guard["respawn_delay"], 50)
            self.assertEqual(guard["stats"]["hitpoints"], 220)
            self.assertIs(guard["drops"], varrock["drops"])
            self.assertIn("guard_level_21.plugin.kts", guard["source"])
            self.assertIn("faladorCrossbowId excluded", guard["source"])

        self.assertEqual(varrock["stats"]["attack"], 19)
        self.assertEqual(varrock["stats"]["strength"], 18)
        self.assertEqual(varrock["stats"]["defence"], 14)
        self.assertEqual(varrock["bonuses"]["defence_stab"], 24)
        self.assertEqual(varrock["bonuses"]["defence_slash"], 30)
        self.assertEqual(varrock["bonuses"]["defence_magic"], -9)
        self.assertEqual(sword["stats"]["attack"], 19)
        self.assertEqual(sword["stats"]["strength"], 18)
        self.assertEqual(sword["stats"]["defence"], 14)
        self.assertEqual(sword["bonuses"]["defence_stab"], 18)
        self.assertEqual(sword["bonuses"]["defence_slash"], 25)
        self.assertEqual(sword["bonuses"]["defence_magic"], -4)
        self.assertEqual(battleaxe["stats"]["attack"], 15)
        self.assertEqual(battleaxe["stats"]["strength"], 15)
        self.assertEqual(battleaxe["stats"]["defence"], 16)
        self.assertEqual(battleaxe["bonuses"]["attack_crush"], 10)
        self.assertEqual(battleaxe["bonuses"]["defence_stab"], 5)

        main, tertiary, charms = varrock["drops"]["tables"]
        self.assertEqual(varrock["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 146)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 146)
        self.assertEqual(main["slots"][0], {"item": "Iron bolts", "quantity_range": (2, 12), "slots": 10})
        self.assertEqual(main["slots"][10], {"item": "Steel arrows", "quantity": 5, "slots": 1})
        self.assertEqual(main["slots"][20], {"item": "Body talisman", "quantity": 1, "slots": 2})
        self.assertEqual(main["slots"][21], {"item": "Law talisman", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][22], {"item": "Grain", "quantity": 1, "slots": 1})
        self.assertIs(main["slots"][24]["table"], COMBAT_ALLOTMENT_SEED_DROP_TABLE)
        self.assertEqual(main["slots"][24]["slots"], 18)
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(tertiary["slots"][1], {"item": "Clue scroll (medium)", "quantity": 1, "slots": 1})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 70})

    def test_black_knight_row_matches_source_and_active_slot_total(self):
        black_knight = COMBAT_ENEMY_DATA["black_knight"]
        main, charms = black_knight["drops"]["tables"]

        self.assertEqual(black_knight["display_name"], "Black knight")
        self.assertEqual(black_knight["level"], 33)
        self.assertEqual(black_knight["group"], "Humanoids")
        self.assertEqual(black_knight["attack_speed"], 5)
        self.assertEqual(black_knight["respawn_delay"], 25)
        self.assertEqual(black_knight["stats"]["hitpoints"], 420)
        self.assertEqual(black_knight["stats"]["attack"], 25)
        self.assertEqual(black_knight["stats"]["strength"], 25)
        self.assertEqual(black_knight["stats"]["defence"], 25)
        self.assertEqual(black_knight["bonuses"]["attack_stab"], 18)
        self.assertEqual(black_knight["bonuses"]["attack_crush"], 16)
        self.assertEqual(black_knight["bonuses"]["defence_stab"], 73)
        self.assertEqual(black_knight["bonuses"]["defence_slash"], 76)
        self.assertEqual(black_knight["bonuses"]["defence_crush"], 70)
        self.assertEqual(black_knight["bonuses"]["defence_magic"], -11)
        self.assertEqual(black_knight["bonuses"]["defence_ranged"], 72)
        self.assertEqual(black_knight["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 116)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 116)
        self.assertEqual(main["slots"][0], {"item": "Iron sword", "quantity": 1, "slots": 4})
        self.assertEqual(main["slots"][3], {"item": "Mithril arrows", "quantity": 3, "slots": 4})
        self.assertEqual(main["slots"][11], {"item": "Steel bar", "quantity": 1, "slots": 6})
        self.assertEqual(main["slots"][21], {"item": "Bread", "quantity": 1, "slots": 1})
        self.assertIs(main["slots"][22]["table"], COMBAT_MINOR_HERB_DROP_TABLE)
        self.assertEqual(main["slots"][22]["slots"], 3)
        self.assertIs(main["slots"][23]["table"], COMBAT_ALLOTMENT_SEED_DROP_TABLE)
        self.assertEqual(main["slots"][23]["slots"], 18)
        self.assertIs(main["slots"][24]["table"], COMBAT_GEM_DROP_TABLE)
        self.assertEqual(main["slots"][24]["slots"], 3)
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 30})
        self.assertEqual(charms["slots"][3], {"item": "Blue charm", "quantity": 1, "slots": 8})
        self.assertIn("black_knight_level_33.plugin.kts", black_knight["source"])
        self.assertIn("BLACK_KNIGHT", black_knight["source"])
        self.assertIn("total(128)", black_knight["source"])
        self.assertIn("active source slots sum to 116", black_knight["source"])

    def test_outlaw_row_matches_source_low_xp_and_active_slot_total(self):
        outlaw = COMBAT_ENEMY_DATA["outlaw"]
        main, charms = outlaw["drops"]["tables"]

        self.assertEqual(outlaw["display_name"], "Outlaw")
        self.assertEqual(outlaw["level"], 35)
        self.assertEqual(outlaw["group"], "Humanoids")
        self.assertEqual(outlaw["attack_speed"], 4)
        self.assertEqual(outlaw["respawn_delay"], 2)
        self.assertEqual(outlaw["xp_multiplier"], 0.025)
        self.assertEqual(outlaw["stats"]["hitpoints"], 200)
        self.assertEqual(outlaw["stats"]["attack"], 35)
        self.assertEqual(outlaw["stats"]["strength"], 30)
        self.assertEqual(outlaw["stats"]["defence"], 25)
        self.assertEqual(outlaw["bonuses"]["attack_crush"], -21)
        self.assertEqual(outlaw["drops"], OUTLAW_DROPS)
        self.assertEqual(outlaw["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 127)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 127)
        self.assertEqual(main["slots"][0], {"item": "Bronze med helm", "quantity": 1, "slots": 2})
        self.assertEqual(main["slots"][7], {"item": "Rope", "quantity": 1, "slots": 46})
        self.assertEqual(main["slots"][11], {"item": "Knife", "quantity": 1, "slots": 1})
        self.assertIs(main["slots"][12]["table"], COMBAT_MINOR_HERB_DROP_TABLE)
        self.assertEqual(main["slots"][12]["slots"], 32)
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 360})
        self.assertEqual(charms["slots"][3], {"item": "Blue charm", "quantity": 1, "slots": 7})
        self.assertIn("outlaw_level_35.plugin.kts", outlaw["source"])
        self.assertIn("Npcs.OUTLAW_5851", outlaw["source"])
        self.assertIn("xpMultiplier 0.025", outlaw["source"])
        self.assertIn("total(128)", outlaw["source"])
        self.assertIn("active source slots sum to 127", outlaw["source"])

    def test_chaos_dwarf_row_matches_source_charms_and_muddy_key(self):
        dwarf = COMBAT_ENEMY_DATA["chaos_dwarf"]
        main, charms = dwarf["drops"]["tables"]

        self.assertEqual(dwarf["display_name"], "Chaos dwarf")
        self.assertEqual(dwarf["level"], 48)
        self.assertEqual(dwarf["group"], "Humanoids")
        self.assertEqual(dwarf["attack_speed"], 4)
        self.assertEqual(dwarf["respawn_delay"], 50)
        self.assertEqual(dwarf["slayer_xp"], 61.0)
        self.assertEqual(dwarf["stats"]["hitpoints"], 610)
        self.assertEqual(dwarf["stats"]["attack"], 38)
        self.assertEqual(dwarf["stats"]["strength"], 42)
        self.assertEqual(dwarf["stats"]["defence"], 28)
        self.assertEqual(dwarf["bonuses"]["attack_stab"], 13)
        self.assertEqual(dwarf["bonuses"]["attack_crush"], 9)
        self.assertEqual(dwarf["bonuses"]["defence_stab"], 40)
        self.assertEqual(dwarf["bonuses"]["defence_slash"], 34)
        self.assertEqual(dwarf["bonuses"]["defence_crush"], 25)
        self.assertEqual(dwarf["bonuses"]["defence_magic"], 10)
        self.assertEqual(dwarf["bonuses"]["defence_ranged"], 35)
        self.assertIs(dwarf["drops"], CHAOS_DWARF_DROPS)
        self.assertEqual(dwarf["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertEqual(main["slots"][0], {"item": "Steel full helm", "quantity": 1, "slots": 2})
        self.assertEqual(main["slots"][11], {"item": "Coins", "quantity": 92, "slots": 40})
        self.assertEqual(main["slots"][19], {"item": "Muddy key", "quantity": 1, "slots": 7})
        self.assertEqual(main["slots"][21], {"item": "Mithril bar", "quantity": 1, "slots": 6})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 100})
        self.assertEqual(charms["slots"][3], {"item": "Blue charm", "quantity": 1, "slots": 20})
        self.assertIn("chaos_dwarf_lvl_48.plugin.kts", dwarf["source"])
        self.assertIn("SlayerAssignment.DWARF", dwarf["source"])
        self.assertIn("aggro radius 4", dwarf["source"])

    def test_haakon_the_champion_row_matches_source_and_barbarian_drops(self):
        haakon = COMBAT_ENEMY_DATA["haakon_the_champion"]
        main, tertiary = haakon["drops"]["tables"]

        self.assertEqual(haakon["display_name"], "Haakon the Champion")
        self.assertEqual(haakon["level"], 29)
        self.assertEqual(haakon["group"], "Humanoids")
        self.assertEqual(haakon["attack_speed"], 6)
        self.assertEqual(haakon["respawn_delay"], 50)
        self.assertEqual(haakon["stats"]["hitpoints"], 350)
        self.assertEqual(haakon["stats"]["attack"], 22)
        self.assertEqual(haakon["stats"]["strength"], 22)
        self.assertEqual(haakon["stats"]["defence"], 25)
        self.assertEqual(haakon["bonuses"]["attack_stab"], 8)
        self.assertEqual(haakon["bonuses"]["attack_crush"], 9)
        self.assertEqual(haakon["bonuses"]["defence_stab"], 12)
        self.assertEqual(haakon["bonuses"]["defence_slash"], 14)
        self.assertEqual(haakon["bonuses"]["defence_crush"], 10)
        self.assertEqual(haakon["bonuses"]["defence_magic"], -1)
        self.assertEqual(haakon["bonuses"]["defence_ranged"], 11)
        self.assertIs(haakon["drops"], HAAKON_DROPS)
        self.assertEqual(haakon["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Iron hatchet", "quantity": 1, "slots": 48})
        self.assertEqual(main["slots"][1], {"item": "Bronze battleaxe", "quantity": 1, "slots": 32})
        self.assertEqual(main["slots"][10], {"item": "Coins", "quantity": 8, "slots": 317})
        self.assertEqual(main["slots"][19], {"item": "Ring mould", "quantity": 1, "slots": 8})
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in tertiary["slots"]), 128)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
        self.assertIn("haakon_the_champion_lvl_29.plugin.kts", haakon["source"])
        self.assertIn("Npcs.HAAKON_THE_CHAMPION", haakon["source"])
        self.assertIn("no Charms table", haakon["source"])

    def test_ham_guard_rows_match_source_and_active_slot_total(self):
        expected = {
            "ham_guard_level_12": (12, 150, 8, 12, 8, 5, "Npcs.HAM_GUARD"),
            "ham_guard_level_18": (18, 200, 14, 18, 12, 6, "Npcs.HAM_GUARD_1711"),
            "ham_guard_level_22": (22, 300, 16, 20, 12, 7, "Npcs.HAM_GUARD_1712"),
        }

        for target_id, (level, hitpoints, attack, strength, defence, defence_bonus, npc_id) in expected.items():
            with self.subTest(target_id=target_id):
                guard = COMBAT_ENEMY_DATA[target_id]
                main, tertiary = guard["drops"]["tables"]

                self.assertEqual(guard["display_name"], "H.A.M. guard")
                self.assertEqual(guard["level"], level)
                self.assertEqual(guard["group"], "Humanoids")
                self.assertEqual(guard["attack_speed"], 7)
                self.assertEqual(guard["respawn_delay"], 25)
                self.assertEqual(guard["stats"]["hitpoints"], hitpoints)
                self.assertEqual(guard["stats"]["attack"], attack)
                self.assertEqual(guard["stats"]["strength"], strength)
                self.assertEqual(guard["stats"]["defence"], defence)
                self.assertEqual(guard["bonuses"]["defence_stab"], defence_bonus)
                self.assertEqual(guard["bonuses"]["defence_slash"], defence_bonus)
                self.assertEqual(guard["bonuses"]["defence_ranged"], defence_bonus)
                self.assertIs(guard["drops"], HAM_GUARD_DROPS)
                self.assertEqual(guard["drops"]["guaranteed"], (("Bones", 1),))
                self.assertEqual(main["total"], 648)
                self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 648)
                self.assertEqual(main["slots"][10], {"item": "H.A.M. boots", "quantity": 1, "slots": 12})
                self.assertEqual(main["slots"][12], {"item": "H.A.M. gloves", "quantity": 1, "slots": 15})
                self.assertEqual(main["slots"][17], {"item": "Bronze arrows", "quantity_range": (1, 12), "slots": 16})
                self.assertIs(main["slots"][22]["table"], COMBAT_ALLOTMENT_SEED_DROP_TABLE)
                self.assertEqual(main["slots"][22]["slots"], 57)
                self.assertEqual(main["slots"][31], {"item": "Coins", "quantity_range": (1, 20), "slots": 81})
                self.assertEqual(main["slots"][39], {"item": "Thread", "quantity_range": (1, 10), "slots": 12})
                self.assertEqual(tertiary["total"], 55)
                self.assertEqual(sum(slot["slots"] for slot in tertiary["slots"]), 55)
                self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
                self.assertIn("ham_guard_level_12_18_22.plugin.kts", guard["source"])
                self.assertIn(npc_id, guard["source"])
                self.assertIn("total(660)", guard["source"])
                self.assertIn("active source slots sum to 648", guard["source"])

    def test_imp_row_matches_source_and_imp_catcher_drops(self):
        imp = COMBAT_ENEMY_DATA["imp"]
        (main,) = imp["drops"]["tables"]

        self.assertEqual(imp["display_name"], "Imp")
        self.assertEqual(imp["level"], 2)
        self.assertEqual(imp["group"], "Demons")
        self.assertEqual(imp["attack_speed"], 4)
        self.assertEqual(imp["respawn_delay"], 50)
        self.assertEqual(imp["stats"]["hitpoints"], 80)
        self.assertEqual(imp["stats"]["attack"], 1)
        self.assertEqual(imp["stats"]["strength"], 1)
        self.assertEqual(imp["stats"]["defence"], 1)
        self.assertEqual(imp["bonuses"]["attack_stab"], -42)
        self.assertEqual(imp["bonuses"]["attack_crush"], -37)
        self.assertEqual(imp["bonuses"]["defence_stab"], -42)
        self.assertEqual(imp["bonuses"]["defence_slash"], -42)
        self.assertEqual(imp["bonuses"]["defence_crush"], -42)
        self.assertEqual(imp["bonuses"]["defence_magic"], -42)
        self.assertEqual(imp["bonuses"]["defence_ranged"], -42)
        self.assertIs(imp["drops"], IMP_DROPS)
        self.assertEqual(imp["drops"]["guaranteed"], (("Impious ashes", 1),))
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Black bead", "quantity": 1, "slots": 40})
        self.assertEqual(main["slots"][3], {"item": "Yellow bead", "quantity": 1, "slots": 40})
        self.assertEqual(main["slots"][5], {"item": "Wizard hat", "quantity": 1, "slots": 64})
        self.assertEqual(main["slots"][24], {"item": "Mind talisman", "quantity": 1, "slots": 55})
        self.assertEqual(main["slots"][-1], {"item": "Chef's hat", "quantity": 1, "slots": 16})
        self.assertIn("imp_level_2.plugin.kts", imp["source"])
        self.assertIn("Npcs.IMP_709", imp["source"])
        self.assertIn("teleport timer is spatial movement only", imp["source"])

    def test_white_knight_rows_match_source_and_runtime_drop_totals(self):
        expected = {
            "white_knight_level_36": (
                36,
                27,
                21,
                WHITE_KNIGHT_LEVEL_36_DROPS,
                128,
                "white_knight_level_36.plugin.kts",
                "Npcs.WHITE_KNIGHT",
                None,
            ),
            "white_knight_level_38": (
                38,
                30,
                25,
                WHITE_KNIGHT_LEVEL_38_DROPS,
                130,
                "white_knight_level_38.plugin.kts",
                "Npcs.WHITE_KNIGHT_3348",
                "active source slots sum to 130",
            ),
            "white_knight_level_39": (
                39,
                32,
                27,
                WHITE_KNIGHT_LEVEL_39_DROPS,
                127,
                "white_knight_level_39.plugin.kts",
                "Npcs.WHITE_KNIGHT_3349",
                "active source slots sum to 127",
            ),
            "white_knight_level_42": (
                42,
                32,
                27,
                WHITE_KNIGHT_LEVEL_42_DROPS,
                127,
                "white_knight_level_42.plugin.kts",
                "Npcs.WHITE_KNIGHT_3350",
                "active source slots sum to 127",
            ),
        }

        for target_id, (level, attack, defence, drops, total, source_file, npc_id, mismatch) in expected.items():
            with self.subTest(target_id=target_id):
                knight = COMBAT_ENEMY_DATA[target_id]
                main, tertiary = knight["drops"]["tables"]

                self.assertEqual(knight["display_name"], "White knight")
                self.assertEqual(knight["level"], level)
                self.assertEqual(knight["group"], "Humanoids")
                self.assertEqual(knight["attack_speed"], 7)
                self.assertEqual(knight["respawn_delay"], 50)
                self.assertEqual(knight["stats"]["hitpoints"], 520)
                self.assertEqual(knight["stats"]["attack"], attack)
                self.assertEqual(knight["stats"]["strength"], 29)
                self.assertEqual(knight["stats"]["defence"], defence)
                self.assertEqual(knight["bonuses"]["attack_stab"], 30)
                self.assertEqual(knight["bonuses"]["attack_slash"], 30)
                self.assertEqual(knight["bonuses"]["attack_crush"], 30)
                self.assertEqual(knight["bonuses"]["melee_strength"], 31)
                self.assertEqual(knight["bonuses"]["defence_stab"], 83)
                self.assertEqual(knight["bonuses"]["defence_slash"], 76)
                self.assertEqual(knight["bonuses"]["defence_crush"], 70)
                self.assertEqual(knight["bonuses"]["defence_magic"], -11)
                self.assertEqual(knight["bonuses"]["defence_ranged"], 74)
                self.assertIs(knight["drops"], drops)
                self.assertEqual(knight["drops"]["guaranteed"], (("Bones", 1),))
                self.assertEqual(main["total"], total)
                self.assertEqual(sum(slot["slots"] for slot in main["slots"]), total)
                self.assertEqual(tertiary["total"], 1024)
                self.assertEqual(sum(slot["slots"] for slot in tertiary["slots"]), 1024)
                self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8})
                self.assertIn(source_file, knight["source"])
                self.assertIn(npc_id, knight["source"])
                self.assertIn("attackBonus/strengthBonus", knight["source"])
                if mismatch:
                    self.assertIn("total(128)", knight["source"])
                    self.assertIn(mismatch, knight["source"])

        level36_main = COMBAT_ENEMY_DATA["white_knight_level_36"]["drops"]["tables"][0]
        self.assertEqual(level36_main["slots"][5], {"item": "Body rune", "quantity_range": (9, 13), "slots": 3})
        self.assertEqual(level36_main["slots"][7], {"item": "Water rune", "quantity_range": (25, 30), "slots": 3})
        self.assertEqual(level36_main["slots"][21], {"item": "Half an apple pie", "quantity": 1, "slots": 1})
        self.assertIs(level36_main["slots"][25]["table"], COMBAT_MINOR_HERB_DROP_TABLE)
        self.assertIs(level36_main["slots"][26]["table"], COMBAT_ALLOTMENT_SEED_DROP_TABLE)
        self.assertIs(level36_main["slots"][27]["table"], COMBAT_GEM_DROP_TABLE)

        level42_main = COMBAT_ENEMY_DATA["white_knight_level_42"]["drops"]["tables"][0]
        self.assertEqual(level42_main["slots"][7], {"item": "Water rune", "quantity_range": (40, 47), "slots": 3})
        self.assertEqual(level42_main["slots"][12], {"item": "Coins", "quantity_range": (51, 55), "slots": 13})
        self.assertEqual(level42_main["slots"][25]["slots"], 28)
        self.assertIs(level42_main["slots"][25]["table"], COMBAT_ALLOTMENT_SEED_DROP_TABLE)

    def test_dwarf_import_rows_match_source_and_nested_global_gem_tables(self):
        level10 = COMBAT_ENEMY_DATA["dwarf_level_10"]
        level11 = COMBAT_ENEMY_DATA["dwarf_level_11"]

        self.assertEqual(level10["display_name"], "Dwarf (level 10)")
        self.assertEqual(level11["display_name"], "Dwarf (level 11)")
        self.assertEqual(level10["level"], 10)
        self.assertEqual(level11["level"], 11)
        self.assertEqual(level10["group"], "Humanoids")
        self.assertEqual(level11["group"], "Humanoids")
        self.assertEqual(level10["attack_speed"], 5)
        self.assertEqual(level11["attack_speed"], 4)
        self.assertEqual(level10["respawn_delay"], 50)
        self.assertEqual(level11["respawn_delay"], 50)
        self.assertEqual(level10["slayer_xp"], 16.0)
        self.assertEqual(level11["slayer_xp"], 16.0)
        self.assertEqual(level10["stats"]["hitpoints"], 160)
        self.assertEqual(level10["stats"]["defence"], 6)
        self.assertEqual(level11["stats"]["hitpoints"], 180)
        self.assertEqual(level11["stats"]["defence"], 8)
        self.assertEqual(level10["bonuses"]["attack_stab"], 5)
        self.assertEqual(level10["bonuses"]["attack_crush"], 7)
        self.assertEqual(level10["bonuses"]["defence_magic"], 5)
        self.assertEqual(level11["bonuses"]["defence_ranged"], 10)
        self.assertIs(level10["drops"], level11["drops"])
        self.assertIn("dwarf_level_10_11.plugin.kts", level10["source"])
        self.assertIn("DWARF_3272", level10["source"])
        self.assertIn("DWARF_3270", level11["source"])

        main, charms, tertiary = level10["drops"]["tables"]
        self.assertEqual(level10["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertEqual(main["slots"][0], {"item": "Bronze pickaxe", "quantity": 1, "slots": 13})
        self.assertEqual(main["slots"][4], {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 7})
        self.assertEqual(main["slots"][16], {"item": "Coal", "quantity": 1, "slots": 2})
        self.assertIs(main["slots"][17]["table"], COMBAT_GEM_DROP_TABLE)
        self.assertEqual(main["slots"][17]["slots"], 1)
        self.assertEqual(main["slots"][-1], {"slots": 23})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 40})
        self.assertEqual(charms["slots"][3], {"item": "Blue charm", "quantity": 1, "slots": 7})
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})

        self.assertEqual(COMBAT_GEM_DROP_TABLE["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in COMBAT_GEM_DROP_TABLE["slots"]), 1024)
        self.assertIn("without Ring of Wealth", COMBAT_GEM_DROP_TABLE["source"])
        self.assertEqual(COMBAT_GEM_DROP_TABLE["slots"][0], {"slots": 512})
        self.assertEqual(COMBAT_GEM_DROP_TABLE["slots"][1], {"item": "Uncut sapphire", "quantity": 1, "slots": 240})
        self.assertEqual(COMBAT_GEM_DROP_TABLE["slots"][7], {"item": "Rune javelin", "quantity": 5, "slots": 8})
        self.assertIs(COMBAT_GEM_DROP_TABLE["slots"][-1]["table"], COMBAT_MEGA_RARE_DROP_TABLE)
        self.assertEqual(COMBAT_MEGA_RARE_DROP_TABLE["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in COMBAT_MEGA_RARE_DROP_TABLE["slots"]), 1024)
        self.assertIn("without Ring of Wealth", COMBAT_MEGA_RARE_DROP_TABLE["source"])
        self.assertEqual(COMBAT_MEGA_RARE_DROP_TABLE["slots"][0], {"slots": 904})
        self.assertEqual(COMBAT_MEGA_RARE_DROP_TABLE["slots"][1], {"item": "Rune spear", "quantity": 1, "slots": 64})
        self.assertEqual(COMBAT_MEGA_RARE_DROP_TABLE["slots"][3], {"item": "Dragon spear", "quantity": 1, "slots": 24})

    def test_barbarian_import_row_groups_level_8_and_9_source_twins(self):
        barbarian = COMBAT_ENEMY_DATA["barbarian"]

        self.assertEqual(barbarian["level"], 8)
        self.assertEqual(barbarian["group"], "Humanoids")
        self.assertEqual(barbarian["attack_speed"], 6)
        self.assertEqual(barbarian["respawn_delay"], 25)
        self.assertEqual(barbarian["stats"]["hitpoints"], 140)
        self.assertEqual(barbarian["stats"]["attack"], 6)
        self.assertEqual(barbarian["stats"]["strength"], 5)
        self.assertEqual(barbarian["stats"]["defence"], 5)
        self.assertEqual(barbarian["bonuses"]["attack_stab"], 8)
        self.assertEqual(barbarian["bonuses"]["attack_crush"], 10)
        self.assertEqual(barbarian["bonuses"]["defence_stab"], 1)
        self.assertEqual(barbarian["drops"]["guaranteed"], (("Bones", 1),))

        main, charms, tertiary = barbarian["drops"]["tables"]
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Bronze hatchet", "quantity": 1, "slots": 48})
        self.assertEqual(main["slots"][1], {"item": "Staff", "quantity": 1, "slots": 32})
        self.assertEqual(main["slots"][9], {"item": "Coins", "quantity": 5, "slots": 341})
        self.assertEqual(main["slots"][14], {"item": "Tin ore", "quantity": 1, "slots": 8})
        self.assertEqual(main["slots"][15], {"item": "Bear fur", "quantity": 1, "slots": 8})
        self.assertEqual(main["slots"][18], {"item": "Ring mould", "quantity": 1, "slots": 8})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 50})
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
        self.assertIn("barbarian_lvl_8.plugin.kts", barbarian["source"])
        self.assertIn("barbarian_lvl_9.plugin.kts", barbarian["source"])

    def test_barbarian_level_10_import_row_groups_weapon_source_variants(self):
        barbarian = COMBAT_ENEMY_DATA["barbarian_level_10"]

        self.assertEqual(barbarian["display_name"], "Barbarian")
        self.assertEqual(barbarian["level"], 10)
        self.assertEqual(barbarian["group"], "Humanoids")
        self.assertEqual(barbarian["attack_speed"], 4)
        self.assertEqual(barbarian["respawn_delay"], 50)
        self.assertEqual(barbarian["stats"]["hitpoints"], 180)
        self.assertEqual(barbarian["stats"]["attack"], 8)
        self.assertEqual(barbarian["stats"]["strength"], 7)
        self.assertEqual(barbarian["stats"]["defence"], 3)
        self.assertEqual(barbarian["bonuses"]["attack_stab"], 9)
        self.assertEqual(barbarian["bonuses"]["attack_crush"], 15)
        self.assertEqual(barbarian["bonuses"]["defence_slash"], 3)
        self.assertEqual(barbarian["bonuses"]["defence_magic"], -3)
        self.assertEqual(barbarian["drops"]["guaranteed"], (("Bones", 1),))

        main, charms, tertiary = barbarian["drops"]["tables"]
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][4], {"item": "Bronze arrows", "quantity": 15, "slots": 24})
        self.assertEqual(main["slots"][8], {"item": "Law rune", "quantity": 2, "slots": 8})
        self.assertEqual(main["slots"][18], {"item": "Ring mould", "quantity": 1, "slots": 8})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
        self.assertIn("barbarian_greataxe_lvl_10.plugin.kts", barbarian["source"])
        self.assertIn("barbarian_spear_lvl_10.plugin.kts", barbarian["source"])
        self.assertIn("barbarian_twohand_sword_lvl_10.plugin.kts", barbarian["source"])
        self.assertIn("barbarian_2hsword_lvl_10.plugin.kts", barbarian["source"])

    def test_barbarian_level_17_import_row_groups_weapon_source_variants(self):
        barbarian = COMBAT_ENEMY_DATA["barbarian_level_17"]

        self.assertEqual(barbarian["display_name"], "Barbarian")
        self.assertEqual(barbarian["level"], 17)
        self.assertEqual(barbarian["group"], "Humanoids")
        self.assertEqual(barbarian["attack_speed"], 4)
        self.assertEqual(barbarian["respawn_delay"], 50)
        self.assertEqual(barbarian["stats"]["hitpoints"], 240)
        self.assertEqual(barbarian["stats"]["attack"], 15)
        self.assertEqual(barbarian["stats"]["strength"], 14)
        self.assertEqual(barbarian["stats"]["defence"], 10)
        self.assertEqual(barbarian["bonuses"]["attack_stab"], 9)
        self.assertEqual(barbarian["bonuses"]["attack_crush"], 15)
        self.assertEqual(barbarian["bonuses"]["defence_slash"], 3)
        self.assertEqual(barbarian["bonuses"]["defence_magic"], -3)
        self.assertEqual(barbarian["drops"]["guaranteed"], (("Bones", 1),))

        main, charms, tertiary = barbarian["drops"]["tables"]
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Bronze hatchet", "quantity": 1, "slots": 48})
        self.assertEqual(main["slots"][2], {"item": "Iron mace", "quantity": 1, "slots": 8})
        self.assertEqual(main["slots"][18], {"item": "Ring mould", "quantity": 1, "slots": 8})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][2], {"item": "Crimson charm", "quantity": 1, "slots": 5})
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
        self.assertIn("barbarian_greataxe_lvl_17.plugin.kts", barbarian["source"])
        self.assertIn("BARBARIAN_3248", barbarian["source"])
        self.assertIn("barbarian_spear_lvl_17.plugin.kts", barbarian["source"])
        self.assertIn("BARBARIAN_3260", barbarian["source"])
        self.assertIn("barbarian_twohand_sword_lvl_17.plugin.kts", barbarian["source"])
        self.assertIn("BARBARIAN_3249", barbarian["source"])

    def test_goblin_level_2_import_splits_armed_and_unarmed_source_variants(self):
        unarmed = COMBAT_ENEMY_DATA["goblin_level_2_unarmed"]
        armed = COMBAT_ENEMY_DATA["goblin_level_2_armed"]

        self.assertEqual(unarmed["level"], 2)
        self.assertEqual(unarmed["group"], "Goblins")
        self.assertEqual(unarmed["attack_speed"], 4)
        self.assertEqual(unarmed["respawn_delay"], 35)
        self.assertEqual(unarmed["slayer_xp"], 5.0)
        self.assertEqual(unarmed["stats"]["hitpoints"], 50)
        self.assertEqual(unarmed["stats"]["attack"], 1)
        self.assertEqual(unarmed["stats"]["defence"], 1)
        self.assertEqual(armed["stats"]["attack"], 3)
        self.assertEqual(armed["stats"]["defence"], 4)
        self.assertIs(unarmed["drops"], armed["drops"])

        main, charms, tertiary = unarmed["drops"]["tables"]
        self.assertEqual(unarmed["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Bronze sq shield", "quantity": 1, "slots": 24})
        self.assertEqual(main["slots"][1], {"item": "Bronze spear", "quantity": 1, "slots": 32})
        self.assertEqual(main["slots"][13], {"item": "Hammer", "quantity": 1, "slots": 120})
        self.assertEqual(main["slots"][14], {"item": "Goblin book", "quantity": 1, "slots": 16})
        self.assertEqual(main["slots"][18], {"item": "Brass necklace", "quantity": 1, "slots": 8})
        self.assertEqual(charms["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1024)
        self.assertEqual(tertiary["total"], 1024)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 6})
        self.assertIn("goblin_level_2.plugin.kts", unarmed["source"])
        self.assertIn("unarmed ids", unarmed["source"])
        self.assertIn("armed id", armed["source"])

    def test_higher_goblin_rows_match_source_and_share_minor_herb_table(self):
        expected_rows = {
            "goblin_level_5": (5, 6, 120, 3, 1, 4, 12.0, (12, 0, 12), "goblin_level_5.plugin.kts"),
            "goblin_level_11": (11, 4, 160, 12, 13, 7, 16.0, (4, 6, 8), "goblin_level_11.plugin.kts"),
            "goblin_level_13": (13, 4, 120, 12, 13, 7, 16.0, (4, 6, 8), "goblin_level_13.plugin.kts"),
            "goblin_level_16": (16, 4, 170, 16, 13, 10, 17.0, (4, 6, 8), "goblin_level_16.plugin.kts"),
            "goblin_level_25": (25, 4, 350, 22, 17, 15, 17.0, (4, 6, 8), "goblin_level_25.plugin.kts"),
        }

        shared_drops = COMBAT_ENEMY_DATA["goblin_level_5"]["drops"]
        for target_id, (level, speed, hp, attack, strength, defence, slayer_xp, bonuses, source_file) in expected_rows.items():
            goblin = COMBAT_ENEMY_DATA[target_id]
            self.assertEqual(goblin["display_name"], "Goblin")
            self.assertEqual(goblin["level"], level)
            self.assertEqual(goblin["group"], "Goblins")
            self.assertEqual(goblin["attack_speed"], speed)
            self.assertEqual(goblin["respawn_delay"], 35)
            self.assertEqual(goblin["slayer_xp"], slayer_xp)
            self.assertEqual(goblin["stats"]["hitpoints"], hp)
            self.assertEqual(goblin["stats"]["attack"], attack)
            self.assertEqual(goblin["stats"]["strength"], strength)
            self.assertEqual(goblin["stats"]["defence"], defence)
            self.assertEqual(
                (goblin["bonuses"]["attack_stab"], goblin["bonuses"]["attack_slash"], goblin["bonuses"]["attack_crush"]),
                bonuses,
            )
            self.assertIs(goblin["drops"], shared_drops)
            self.assertIn(source_file, goblin["source"])

        main, charms, tertiary = shared_drops["tables"]
        self.assertEqual(shared_drops["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 127)
        self.assertEqual(main["total"] - sum(slot["slots"] for slot in main["slots"]), 1)
        self.assertEqual(main["slots"][0], {"item": "Bronze spear", "quantity": 1, "slots": 9})
        self.assertEqual(main["slots"][2], {"item": "Bronze scimitar", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][7], {"item": "Bronze javelin", "quantity": 5, "slots": 2})
        self.assertEqual(main["slots"][20]["slots"], 2)
        self.assertEqual(main["slots"][20]["table"]["name"], "Minor herb")
        self.assertEqual(charms["total"], 1024)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 6})

    def test_hobgoblin_rows_match_source_and_runtime_drop_totals(self):
        unarmed = COMBAT_ENEMY_DATA["hobgoblin_unarmed"]
        armed = COMBAT_ENEMY_DATA["hobgoblin_armed"]
        unarmed_main, unarmed_charms = unarmed["drops"]["tables"]
        armed_main, armed_charms = armed["drops"]["tables"]

        self.assertEqual(unarmed["display_name"], "Hobgoblin (unarmed)")
        self.assertEqual(unarmed["level"], 28)
        self.assertEqual(unarmed["group"], "Hobgoblins")
        self.assertEqual(unarmed["slayer_xp"], 29.0)
        self.assertEqual(unarmed["attack_speed"], 4)
        self.assertEqual(unarmed["respawn_delay"], 50)
        self.assertEqual(unarmed["stats"]["hitpoints"], 290)
        self.assertEqual(unarmed["stats"]["attack"], 22)
        self.assertEqual(unarmed["stats"]["strength"], 24)
        self.assertEqual(unarmed["stats"]["defence"], 24)
        self.assertEqual(unarmed_main["total"], 127)
        self.assertEqual(sum(slot["slots"] for slot in unarmed_main["slots"]), 127)
        self.assertEqual(unarmed_main["slots"][3], {"item": "Iron spear", "quantity": 1, "slots": 2})
        self.assertIs(unarmed_main["slots"][21]["table"], COMBAT_MINOR_HERB_DROP_TABLE)
        self.assertIs(unarmed_main["slots"][22]["table"], COMBAT_ALLOTMENT_SEED_DROP_TABLE)
        self.assertIs(unarmed_main["slots"][23]["table"], COMBAT_GEM_DROP_TABLE)
        self.assertEqual(unarmed_charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in unarmed_charms["slots"]), 1000)
        self.assertIn("hobgoblin_unarmed_level_28.plugin.kts", unarmed["source"])
        self.assertIn("total(128)", unarmed["source"])
        self.assertIn("active source slots sum to 127", unarmed["source"])
        self.assertIn("total(1024)", unarmed["source"])
        self.assertIn("active source slots sum to 1000", unarmed["source"])
        self.assertIn("Hobgoblin oldid 6448782", unarmed["source"])

        self.assertEqual(armed["display_name"], "Hobgoblin (armed)")
        self.assertEqual(armed["level"], 28)
        self.assertEqual(armed["group"], "Hobgoblins")
        self.assertEqual(armed["slayer_xp"], 49.0)
        self.assertEqual(armed["attack_speed"], 6)
        self.assertEqual(armed["respawn_delay"], 30)
        self.assertEqual(armed["stats"]["hitpoints"], 490)
        self.assertEqual(armed["stats"]["attack"], 33)
        self.assertEqual(armed["stats"]["strength"], 31)
        self.assertEqual(armed["stats"]["defence"], 36)
        self.assertEqual(armed["bonuses"]["attack_stab"], 8)
        self.assertEqual(armed["bonuses"]["attack_crush"], 10)
        self.assertEqual(armed["bonuses"]["defence_stab"], 1)
        self.assertEqual(armed_main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in armed_main["slots"]), 128)
        self.assertEqual(armed_main["slots"][10], {"item": "Iron javelin", "quantity": 5, "slots": 2})
        self.assertIs(armed_main["slots"][11]["table"], COMBAT_MINOR_HERB_DROP_TABLE)
        self.assertIs(armed_main["slots"][12]["table"], COMBAT_UNCOMMON_SEED_DROP_TABLE)
        self.assertIs(armed_main["slots"][22]["table"], COMBAT_GEM_DROP_TABLE)
        self.assertEqual(armed_charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in armed_charms["slots"]), 1000)
        self.assertIn("hobgoblin_armed_lvl_28.plugin.kts", armed["source"])
        self.assertIn("aggro radius 4", armed["source"])
        self.assertIn("Hobgoblin oldid 6448782", armed["source"])

    def test_tzhaar_ket_row_matches_source_and_equipment_drops(self):
        ket = COMBAT_ENEMY_DATA["tzhaar_ket"]
        main, obsidian, charms = ket["drops"]["tables"]

        self.assertEqual(ket["display_name"], "TzHaar-Ket")
        self.assertEqual(ket["level"], 149)
        self.assertEqual(ket["group"], "TzHaar")
        self.assertEqual(ket["attack_speed"], 4)
        self.assertEqual(ket["respawn_delay"], 50)
        self.assertEqual(ket["slayer_xp"], 136.0)
        self.assertEqual(ket["stats"]["hitpoints"], 1400)
        self.assertEqual(ket["stats"]["attack"], 120)
        self.assertEqual(ket["stats"]["strength"], 140)
        self.assertEqual(ket["stats"]["defence"], 120)
        self.assertEqual(ket["stats"]["magic"], 40)
        self.assertIs(ket["drops"], TZHAAR_KET_DROPS)
        self.assertEqual(ket["drops"]["guaranteed"], ())
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertEqual(main["slots"][0], {"item": "Tokkul", "quantity_range": (100, 2000), "slots": 69})
        self.assertEqual(main["slots"][1], {"item": "Fire battlestaff", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][9], {"item": "Chilli potato", "quantity": 1, "slots": 6})
        self.assertEqual(main["slots"][10], {"item": "Pure essence", "quantity_range": (5, 10), "slots": 1})
        self.assertEqual(main["slots"][11], {"item": "Onyx bolt tips", "quantity_range": (1, 4), "slots": 1})
        self.assertEqual(obsidian["total"], 512)
        self.assertEqual(sum(slot["slots"] for slot in obsidian["slots"]), 512)
        self.assertEqual(obsidian["slots"][0], {"item": "Tzhaar-ket-om", "quantity": 1, "slots": 1})
        self.assertEqual(obsidian["slots"][1], {"item": "Toktz-ket-xil", "quantity": 1, "slots": 1})
        self.assertEqual(obsidian["slots"][2], {"item": "Obsidian cape", "quantity": 1, "slots": 1})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][0], {"item": "Obsidian charm", "quantity": 2, "slots": 720})
        self.assertIn("tzhaar_ket_lvl_149.plugin.kts", ket["source"])
        self.assertIn("Npcs.TZHAARKET_2616", ket["source"])
        self.assertIn("no source combat bonuses", ket["source"])

    def test_al_kharid_warrior_row_matches_source_and_nested_minor_herbs(self):
        warrior = COMBAT_ENEMY_DATA["al_kharid_warrior"]

        self.assertEqual(warrior["level"], 9)
        self.assertEqual(warrior["group"], "Humanoids")
        self.assertEqual(warrior["attack_speed"], 4)
        self.assertEqual(warrior["respawn_delay"], 25)
        self.assertEqual(warrior["stats"]["hitpoints"], 190)
        self.assertEqual(warrior["stats"]["attack"], 7)
        self.assertEqual(warrior["stats"]["strength"], 5)
        self.assertEqual(warrior["stats"]["defence"], 4)
        self.assertEqual(warrior["bonuses"]["attack_stab"], 10)
        self.assertEqual(warrior["bonuses"]["attack_slash"], 10)
        self.assertEqual(warrior["bonuses"]["attack_crush"], 10)
        self.assertEqual(warrior["bonuses"]["melee_strength"], 9)

        main, tertiary = warrior["drops"]["tables"]
        self.assertEqual(warrior["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Bronze med helm", "quantity": 1, "slots": 16})
        self.assertEqual(main["slots"][2], {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 146})
        self.assertEqual(main["slots"][8]["slots"], 84)
        minor_herbs = main["slots"][8]["table"]
        self.assertEqual(minor_herbs["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in minor_herbs["slots"]), 1024)
        self.assertEqual(minor_herbs["slots"][0], {"item": "Grimy guam", "quantity": 1, "slots": 249})
        self.assertEqual(minor_herbs["slots"][-1], {"item": "Grimy dwarf weed", "quantity": 1, "slots": 24})
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8})
        self.assertIn("alkharid_warrior_level_9.plugin.kts", warrior["source"])

    def test_farmer_row_matches_source_and_allotment_seed_table(self):
        farmer = COMBAT_ENEMY_DATA["farmer"]

        self.assertEqual(farmer["level"], 7)
        self.assertEqual(farmer["group"], "Humanoids")
        self.assertEqual(farmer["attack_speed"], 6)
        self.assertEqual(farmer["respawn_delay"], 25)
        self.assertEqual(farmer["stats"]["hitpoints"], 120)
        self.assertEqual(farmer["stats"]["attack"], 3)
        self.assertEqual(farmer["stats"]["strength"], 4)
        self.assertEqual(farmer["stats"]["defence"], 8)
        self.assertEqual(farmer["bonuses"]["attack_stab"], 5)
        self.assertEqual(farmer["bonuses"]["attack_slash"], 0)
        self.assertEqual(farmer["bonuses"]["attack_crush"], 6)

        main, tertiary = farmer["drops"]["tables"]
        self.assertEqual(farmer["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertEqual(main["slots"][0], {"item": "Earth rune", "quantity": 4, "slots": 2})
        self.assertEqual(main["slots"][8], {"item": "Fishing bait", "quantity": 1, "slots": 5})
        self.assertEqual(main["slots"][9], {"item": "Rake", "quantity": 1, "slots": 3})
        self.assertEqual(main["slots"][14], {"item": "Watering can (8)", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][4]["slots"], 11)
        self.assertEqual(main["slots"][4]["table"]["name"], "Minor herb")
        self.assertEqual(main["slots"][5]["slots"], 27)
        allotment_seed = main["slots"][5]["table"]
        self.assertEqual(allotment_seed["name"], "Allotment seed")
        self.assertEqual(allotment_seed["total"], 90)
        self.assertEqual(sum(slot["slots"] for slot in allotment_seed["slots"]), 90)
        self.assertEqual(allotment_seed["slots"][0], {"item": "Potato seed", "quantity": 4, "slots": 32})
        self.assertEqual(allotment_seed["slots"][-1], {"item": "Watermelon seed", "quantity": 2, "slots": 1})
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
        self.assertIn("farmer_level_7.plugin.kts", farmer["source"])
        self.assertIn("FARMER_1757", farmer["source"])

    def test_chaos_druid_row_matches_source_and_nested_tables(self):
        druid = COMBAT_ENEMY_DATA["chaos_druid"]
        (main,) = druid["drops"]["tables"]

        self.assertEqual(druid["display_name"], "Chaos druid")
        self.assertEqual(druid["level"], 13)
        self.assertEqual(druid["group"], "Humanoids")
        self.assertEqual(druid["attack_speed"], 4)
        self.assertEqual(druid["respawn_delay"], 25)
        self.assertEqual(druid["stats"]["hitpoints"], 200)
        self.assertEqual(druid["stats"]["attack"], 8)
        self.assertEqual(druid["stats"]["strength"], 8)
        self.assertEqual(druid["stats"]["defence"], 12)
        self.assertEqual(druid["stats"]["magic"], 10)
        self.assertEqual(druid["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertEqual(main["slots"][0], {"item": "Law rune", "quantity": 2, "slots": 7})
        self.assertEqual(main["slots"][1], {"item": "Mithril bolts", "quantity_range": (2, 12), "slots": 5})
        self.assertEqual(main["slots"][7]["slots"], 46)
        self.assertIs(main["slots"][7]["table"], COMBAT_MINOR_HERB_DROP_TABLE)
        self.assertEqual(main["slots"][13], {"item": "Vial of water", "quantity": 1, "slots": 10})
        self.assertEqual(main["slots"][14], {"item": "Bronze longsword", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][15], {"item": "Snape grass", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][12], {"slots": 32})
        self.assertEqual(main["slots"][16], {"item": "Unholy mould", "quantity": 1, "slots": 1})
        self.assertIs(main["slots"][17]["table"], COMBAT_GEM_DROP_TABLE)
        self.assertEqual(main["slots"][17]["slots"], 1)
        self.assertIn("chaos_druid_lvl_13.plugin.kts", druid["source"])
        self.assertIn("CHAOS_DRUID_7105", druid["source"])
        self.assertIn("aggro radius 4", druid["source"])
        self.assertIn("chaos_druid.json: item 1594 at 1/128", druid["source"])
        self.assertIn("Chaos druid oldid 6381798", druid["source"])

    def test_citizen_row_matches_source_and_nested_minor_herbs(self):
        citizen = COMBAT_ENEMY_DATA["citizen"]
        main, tertiary = citizen["drops"]["tables"]

        self.assertEqual(citizen["display_name"], "Man/Woman")
        self.assertEqual(citizen["level"], 2)
        self.assertEqual(citizen["group"], "Humanoids")
        self.assertEqual(citizen["attack_speed"], 4)
        self.assertEqual(citizen["respawn_delay"], 25)
        self.assertEqual(citizen["stats"]["hitpoints"], 70)
        self.assertEqual(citizen["stats"]["attack"], 1)
        self.assertEqual(citizen["stats"]["strength"], 1)
        self.assertEqual(citizen["stats"]["defence"], 1)
        self.assertEqual(citizen["bonuses"]["defence_stab"], -21)
        self.assertEqual(citizen["bonuses"]["defence_slash"], -21)
        self.assertEqual(citizen["bonuses"]["defence_ranged"], -21)
        self.assertEqual(citizen["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Bronze med helm", "quantity": 1, "slots": 16})
        self.assertEqual(main["slots"][1], {"item": "Bronze dagger", "quantity": 1, "slots": 8})
        self.assertEqual(main["slots"][2], {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 138})
        self.assertEqual(main["slots"][9], {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 152})
        self.assertEqual(main["slots"][-1], {"item": "Cabbage", "quantity": 1, "slots": 8})
        self.assertEqual(tertiary["total"], 1024)
        self.assertEqual(tertiary["slots"][1], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8})
        self.assertIn("citizen_level_2.plugin.kts", citizen["source"])
        self.assertIn("WOMAN_BLOND_LONGSKIRT_3226", citizen["source"])

    def test_low_level_humanoid_rows_match_source(self):
        monk = COMBAT_ENEMY_DATA["monk"]
        cuffs = COMBAT_ENEMY_DATA["cuffs"]
        narf_jeff_rusty = COMBAT_ENEMY_DATA["narf_jeff_rusty"]

        self.assertEqual(monk["display_name"], "Monk")
        self.assertEqual(monk["level"], 5)
        self.assertEqual(monk["group"], "Humanoids")
        self.assertEqual(monk["attack_speed"], 4)
        self.assertEqual(monk["respawn_delay"], 25)
        self.assertEqual(monk["stats"]["hitpoints"], 150)
        self.assertEqual(monk["stats"]["attack"], 2)
        self.assertEqual(monk["stats"]["strength"], 2)
        self.assertEqual(monk["stats"]["defence"], 3)
        self.assertEqual(monk["drops"], {"guaranteed": (("Bones", 1),), "tables": ()})
        self.assertIn("monk_level_5.plugin.kts", monk["source"])
        self.assertIn("MONK_7727", monk["source"])

        self.assertEqual(cuffs["display_name"], "Cuffs")
        self.assertEqual(cuffs["level"], 3)
        self.assertEqual(cuffs["stats"]["hitpoints"], 70)
        self.assertEqual(cuffs["stats"]["defence"], 3)
        self.assertEqual(cuffs["bonuses"]["defence_stab"], 5)
        self.assertEqual(cuffs["bonuses"]["defence_ranged"], 5)
        self.assertIs(cuffs["drops"], COMBAT_ENEMY_DATA["citizen"]["drops"])
        self.assertIn("cuffs_level_3.plugin.kts", cuffs["source"])
        self.assertIn("Npcs.CUFFS", cuffs["source"])

        self.assertEqual(narf_jeff_rusty["display_name"], "Narf/Jeff/Rusty")
        self.assertEqual(narf_jeff_rusty["level"], 2)
        self.assertEqual(narf_jeff_rusty["stats"]["hitpoints"], 70)
        self.assertEqual(narf_jeff_rusty["stats"]["defence"], 1)
        self.assertEqual(narf_jeff_rusty["bonuses"]["defence_magic"], 5)
        self.assertIs(narf_jeff_rusty["drops"], COMBAT_ENEMY_DATA["citizen"]["drops"])
        self.assertIn("narf_jeff_rusty_level_2.plugin.kts", narf_jeff_rusty["source"])
        self.assertIn("Npcs.RUSTY", narf_jeff_rusty["source"])

    def test_pirate_row_matches_source_and_nested_gem_table(self):
        pirate = COMBAT_ENEMY_DATA["pirate"]
        (main,) = pirate["drops"]["tables"]

        self.assertEqual(pirate["display_name"], "Pirate")
        self.assertEqual(pirate["level"], 23)
        self.assertEqual(pirate["group"], "Humanoids")
        self.assertEqual(pirate["attack_speed"], 5)
        self.assertEqual(pirate["respawn_delay"], 25)
        self.assertEqual(pirate["stats"]["hitpoints"], 200)
        self.assertEqual(pirate["stats"]["attack"], 21)
        self.assertEqual(pirate["stats"]["strength"], 21)
        self.assertEqual(pirate["stats"]["defence"], 21)
        self.assertEqual(pirate["bonuses"]["attack_stab"], 8)
        self.assertEqual(pirate["bonuses"]["attack_slash"], 8)
        self.assertEqual(pirate["bonuses"]["attack_crush"], 8)
        self.assertEqual(pirate["bonuses"]["defence_stab"], 3)
        self.assertEqual(pirate["bonuses"]["defence_slash"], 2)
        self.assertEqual(pirate["bonuses"]["melee_strength"], 10)
        self.assertEqual(pirate["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Iron dagger", "quantity": 1, "slots": 48})
        self.assertEqual(main["slots"][3], {"item": "Iron bolts", "quantity_range": (2, 12), "slots": 80})
        self.assertEqual(main["slots"][18], {"item": "Eye patch", "quantity": 1, "slots": 96})
        self.assertEqual(main["slots"][19], {"slots": 64})
        self.assertEqual(main["slots"][21], {"item": "Iron bar", "quantity": 1, "slots": 8})
        self.assertEqual(main["slots"][22], {"table": COMBAT_GEM_DROP_TABLE, "slots": 8})
        self.assertIn("pirate_level_23.plugin.kts", pirate["source"])
        self.assertIn("PIRATE_184", pirate["source"])
        self.assertIn("attackBonus/strengthBonus", pirate["source"])

    def test_monk_of_zamorak_level_45_row_matches_source_and_charms(self):
        monk = COMBAT_ENEMY_DATA["monk_of_zamorak_level_45"]
        main, charms = monk["drops"]["tables"]

        self.assertEqual(monk["display_name"], "Monk of Zamorak")
        self.assertEqual(monk["level"], 45)
        self.assertEqual(monk["group"], "Humanoids")
        self.assertEqual(monk["attack_speed"], 4)
        self.assertEqual(monk["respawn_delay"], 250)
        self.assertEqual(monk["stats"]["hitpoints"], 400)
        self.assertEqual(monk["stats"]["attack"], 38)
        self.assertEqual(monk["stats"]["strength"], 38)
        self.assertEqual(monk["stats"]["defence"], 42)
        self.assertEqual(monk["stats"]["magic"], 40)
        self.assertEqual(monk["stats"]["ranged"], 1)
        self.assertEqual(monk["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 20)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 20)
        self.assertEqual(main["slots"][0], {"item": "Zamorak robe top", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][1], {"item": "Zamorak robe bottom", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][2], {"slots": 18})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 10})
        self.assertEqual(charms["slots"][1], {"item": "Green charm", "quantity": 1, "slots": 100})
        self.assertEqual(charms["slots"][-1], {"slots": 860})
        self.assertIn("monk_of_zamorak_lvl_45.plugin.kts", monk["source"])
        self.assertIn("MONK_OF_ZAMORAK_190", monk["source"])
        self.assertIn("ZAMORAK_ROBE_1035", monk["source"])
        self.assertIn("ZAMORAK_ROBE mapped", monk["source"])

    def test_giant_spider_quantity_range_drop_rolls_inclusive_high(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["giant_spider"],
            _rng([0.0, 0.999999, 0.999999, 0.999999, 0.999999]),
        )

        self.assertEqual(drops, {"Air rune": 6})

    def test_abyssal_demon_drop_rolls_source_quantities_and_rare_table(self):
        abyssal_demon = COMBAT_ENEMY_DATA["abyssal_demon"]

        cases = (
            ([210 / 1024, 0.0], {"Infernal ashes": 1, "Blood rune": 7}),
            ([210 / 1024, 0.999999], {"Infernal ashes": 1, "Blood rune": 50}),
            ([298 / 1024, 0.999999], {"Infernal ashes": 1, "Law rune": 45}),
            ([338 / 1024, 0.999999], {"Infernal ashes": 1, "Nature rune": 77}),
            ([428 / 1024, 0.999999], {"Infernal ashes": 1, "Coins": 486}),
            ([829 / 1024, 0.0], {"Infernal ashes": 1, "Nature rune": 67}),
        )
        for rolls, expected in cases:
            with self.subTest(rolls=rolls):
                self.assertEqual(_combat_roll_drops(abyssal_demon, _rng(rolls)), expected)

    def test_generic_abyssal_demon_excludes_kuradal_dungeon_ring(self):
        abyssal_demon = COMBAT_ENEMY_DATA["abyssal_demon"]

        self.assertNotIn("Ferocious ring (5)", combat_enemy_drop_item_names_pure(abyssal_demon))
        self.assertEqual(
            _combat_roll_drops(abyssal_demon, _rng([583 / 1024])),
            {"Infernal ashes": 1},
        )

    def test_highwayman_quantity_range_drop_rolls_with_guaranteed_cape(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["highwayman"],
            _rng([0.0, 0.999999]),
        )

        self.assertEqual(drops, {"Bones": 1, "Cape": 1, "Iron bolts": 12})

    def test_citizen_quantity_range_and_tertiary_drop_rolls(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["citizen"],
            _rng([24 / 1024, 0.999999, 1016 / 1024]),
        )

        self.assertEqual(drops, {"Bones": 1, "Bronze bolts": 12, "Clue scroll (easy)": 1})

    def test_humanoid_drop_tables_reach_nested_minor_herbs(self):
        cases = (
            ("citizen", [258 / 1024, 0.0, 0.0]),
            ("mugger", [218 / 1024, 0.0, 0.999999]),
            ("thug", [75 / 128, 0.0, 0.999999, 0.999999]),
            ("thief", [100 / 128, 0.0, 0.999999]),
            ("goblin_level_11", [118 / 128, 0.0, 0.999999, 0.999999]),
            ("al_kharid_warrior", [250 / 1024, 0.0, 0.999999]),
        )
        for enemy_id, rolls in cases:
            with self.subTest(enemy_id):
                self.assertEqual(
                    _combat_roll_drops(COMBAT_ENEMY_DATA[enemy_id], _rng(rolls)),
                    {"Bones": 1, "Grimy guam": 1},
                )

    def test_low_level_humanoid_drop_rolls(self):
        monk_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["monk"], _rng([]))
        market_guard_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["market_guard"], _rng([]))
        jail_guard_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["jail_guard"], _rng([]))
        cuffs_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["cuffs"],
            _rng([24 / 1024, 0.999999, 1016 / 1024]),
        )
        shared_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["narf_jeff_rusty"],
            _rng([258 / 1024, 0.0, 0.0]),
        )

        self.assertEqual(monk_drops, {"Bones": 1})
        self.assertEqual(market_guard_drops, {"Bones": 1})
        self.assertEqual(jail_guard_drops, {"Bones": 1})
        self.assertEqual(cuffs_drops, {"Bones": 1, "Bronze bolts": 12, "Clue scroll (easy)": 1})
        self.assertEqual(shared_drops, {"Bones": 1, "Grimy guam": 1})

    def test_giant_rat_and_unicorn_drop_rolls(self):
        rat_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["giant_rat_level_26"], _rng([]))
        unicorn_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["unicorn"], _rng([0.129]))
        black_unicorn_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["black_unicorn"], _rng([0.229]))
        black_bear_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["black_bear"], _rng([0.187]))

        self.assertEqual(rat_drops, {"Bones": 1, "Raw rat meat": 1})
        self.assertEqual(unicorn_drops, {"Bones": 1, "Unicorn horn": 1, "Gold charm": 1})
        self.assertEqual(black_unicorn_drops, {"Bones": 1, "Unicorn horn": 1, "Crimson charm": 1})
        self.assertEqual(black_bear_drops, {"Bones": 1, "Bear fur": 1, "Raw bear meat": 1, "Green charm": 1})

    def test_wolf_drop_rolls_use_source_charm_tables(self):
        wolf_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["wolf"], _rng([0.019]))
        white_wolf_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["white_wolf_level_25"], _rng([0.159]))
        big_wolf_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["big_wolf"], _rng([0.299]))

        self.assertEqual(wolf_drops, {"Wolf bones": 1, "Bones": 1, "Gold charm": 1})
        self.assertEqual(white_wolf_drops, {"Wolf bones": 1, "Green charm": 1})
        self.assertEqual(big_wolf_drops, {"Wolf bones": 1, "Crimson charm": 1})

    def test_giant_bat_drop_rolls_guaranteed_bat_bones(self):
        self.assertEqual(_combat_roll_drops(COMBAT_ENEMY_DATA["giant_bat"], _rng([])), {"Bat bones": 1})

    def test_giant_drop_rolls_use_nested_source_tables(self):
        hill_seed_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["hill_giant"],
            _rng([46 / 128, 0.0, 0.999999]),
        )
        moss_seed_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["moss_giant"],
            _rng([89 / 128, 0.0, 0.999999]),
        )
        ice_tertiary_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["ice_giant"],
            _rng([0.0, 270 / 100000]),
        )
        ice_gem_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["ice_giant"],
            _rng([994 / 1024, 512 / 1024, 0.999999]),
        )

        self.assertEqual(hill_seed_drops, {"Big bones": 1, "Potato seed": 4})
        self.assertEqual(moss_seed_drops, {"Big bones": 1, "Limpwurt seed": 1})
        self.assertEqual(ice_tertiary_drops, {"Big bones": 1, "Iron 2h sword": 1, "Champion's scroll": 1})
        self.assertEqual(ice_gem_drops, {"Big bones": 1, "Uncut sapphire": 1})

    def test_ghost_drop_rolls_no_items(self):
        self.assertEqual(_combat_roll_drops(COMBAT_ENEMY_DATA["ghost"], _rng([])), {})

    def test_ogre_drop_rolls_nested_seed_and_independent_bone_tables(self):
        seed_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["ogre"],
            _rng([0.0, 0.0, 0.999999]),
        )
        long_bone_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["ogre"],
            _rng([0.999999, 0.0]),
        )
        curved_bone_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["ogre"],
            _rng([0.999999, 250 / 100000]),
        )

        self.assertEqual(seed_drops, {"Big bones": 1, "Limpwurt seed": 1})
        self.assertEqual(long_bone_drops, {"Big bones": 1, "Long bone": 1})
        self.assertEqual(curved_bone_drops, {"Big bones": 1, "Curved bone": 1})

    def test_jelly_drop_roll_can_reach_its_mithril_boots(self):
        self.assertEqual(
            _combat_roll_drops(
                COMBAT_ENEMY_DATA["jelly"],
                _rng([125 / 128]),
            ),
            {"Mithril boots": 1},
        )

    def test_fire_giant_drop_selectors_are_independent_and_exact(self):
        giant = COMBAT_ENEMY_DATA["fire_giant"]
        ordinary = _combat_roll_drops(
            giant,
            _rng([127 / 128, 0.0, 0.0, 0.999999, 0.999999]),
        )
        charms = _combat_roll_drops(
            giant,
            _rng([0.0, 207 / 404, 0.999999]),
        )
        bones = _combat_roll_drops(
            giant,
            _rng([0.0, 0.999999, 250 / 100000]),
        )

        self.assertEqual(
            ordinary,
            {"Big bones": 1, "Uncut sapphire": 1},
        )
        self.assertEqual(
            charms,
            {"Big bones": 1, "Coins": 60, "Green charm": 1},
        )
        self.assertEqual(
            bones,
            {"Big bones": 1, "Coins": 60, "Curved bone": 1},
        )

    def test_blue_dragon_drops_preserve_nested_rolls_and_summoning_egg_gate(self):
        dragon = COMBAT_ENEMY_DATA["blue_dragon"]
        nested_herb = _combat_roll_drops(
            dragon,
            _rng([54 / 128, 0.0, 0.999999, 0.999999, 0.999999]),
            {"summoning_level": 99},
        )
        egg_ready = _combat_roll_drops(
            dragon,
            _rng([0.0, 0.999999, 0.0, 0.999999]),
            {"summoning_level": 99},
        )
        egg_locked = _combat_roll_drops(
            dragon,
            _rng([0.0, 0.999999, 0.999999]),
            {"summoning_level": 98},
        )

        self.assertEqual(
            nested_herb,
            {"Blue dragonhide": 1, "Dragon bones": 1, "Grimy guam": 1},
        )
        self.assertEqual(
            egg_ready,
            {
                "Blue dragonhide": 1,
                "Dragon bones": 1,
                "Coins": 44,
                "Blue dragon egg": 1,
            },
        )
        self.assertEqual(
            egg_locked,
            {"Blue dragonhide": 1, "Dragon bones": 1, "Coins": 44},
        )
        self.assertEqual(
            _combat_roll_drops(
                COMBAT_ENEMY_DATA["baby_blue_dragon"],
                _rng([]),
            ),
            {"Baby dragon bones": 1},
        )

    def test_combat_kill_forwards_player_levels_to_gated_drop_tables(self):
        gated_enemy_data = {
            "gated_enemy": {
                "display_name": "Gated enemy",
                "level": 1,
                "group": "Test",
                "attack_style": "melee",
                "attack_speed": 6,
                "max_hit": 0,
                "slayer_xp": 1.0,
                "stats": {
                    "hitpoints": 1,
                    "attack": 1,
                    "strength": 1,
                    "defence": 1,
                    "magic": 1,
                    "ranged": 1,
                },
                "bonuses": {},
                "drops": {
                    "guaranteed": (),
                    "tables": (
                        {
                            "name": "Summoning-gated drop",
                            "total": 1,
                            "required_skill_levels": (("summoning", 99),),
                            "slots": (
                                {
                                    "item": "Blue dragon egg",
                                    "quantity": 1,
                                    "slots": 1,
                                },
                            ),
                        },
                    ),
                },
                "source": "test",
            },
        }

        ready, ready_ok, ready_result = apply_combat_burst_pure(
            _player(
                current_combat_target="gated_enemy",
                summoning_level=99,
                combat_encounter={
                    "target_id": "gated_enemy",
                    "enemy_lifepoints": 1,
                },
            ),
            gated_enemy_data,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.0, 0.0]),
        )
        locked, locked_ok, locked_result = apply_combat_burst_pure(
            _player(
                current_combat_target="gated_enemy",
                summoning_level=98,
                combat_encounter={
                    "target_id": "gated_enemy",
                    "enemy_lifepoints": 1,
                },
            ),
            gated_enemy_data,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.0]),
        )

        self.assertTrue(ready_ok, ready_result)
        self.assertTrue(locked_ok, locked_result)
        self.assertTrue(ready_result["killed"])
        self.assertTrue(locked_result["killed"])
        self.assertEqual(ready["inventory"], {"Blue dragon egg": 1})
        self.assertEqual(locked["inventory"], {})

    def test_bronze_dragon_rolls_exact_ordinary_and_independent_tertiaries(self):
        dragon = COMBAT_ENEMY_DATA["bronze_dragon"]
        empty_ordinary = _combat_roll_drops(
            dragon,
            _rng(
                [
                    127 / 128,
                    0.999999,
                    0.999999,
                    0.999999,
                    0.999999,
                    0.999999,
                ]
            ),
        )
        plates_and_clues = _combat_roll_drops(
            dragon,
            _rng([0.0, 0.999999, 0.0, 0.0, 0.0, 0.0]),
        )

        self.assertEqual(
            empty_ordinary,
            {"Dragon bones": 1, "Bronze bar": 5},
        )
        self.assertEqual(
            plates_and_clues,
            {
                "Dragon bones": 1,
                "Bronze bar": 5,
                "Coins": 196,
                "Dragon plateskirt": 1,
                "Dragon platelegs": 1,
                "Clue scroll (hard)": 1,
                "Clue scroll (elite)": 1,
            },
        )

    def test_iron_dragon_rolls_exact_ordinary_and_independent_tertiaries(self):
        dragon = COMBAT_ENEMY_DATA["iron_dragon"]
        empty_ordinary = _combat_roll_drops(
            dragon,
            _rng(
                [
                    127 / 128,
                    0.999999,
                    0.999999,
                    0.999999,
                    0.999999,
                    0.999999,
                ]
            ),
        )
        rares = _combat_roll_drops(
            dragon,
            _rng([0.0, 0.999999, 0.0, 0.0, 0.0, 0.0, 0.0]),
        )

        self.assertEqual(
            empty_ordinary,
            {"Dragon bones": 1, "Iron bar": 5},
        )
        self.assertEqual(
            rares,
            {
                "Dragon bones": 1,
                "Iron bar": 5,
                "Adamant javelin": 4,
                "Dragon plateskirt": 1,
                "Dragon platelegs": 1,
                "Draconic visage": 1,
                "Clue scroll (hard)": 1,
            },
        )

    def test_steel_dragon_rolls_closed_ordinary_and_independent_tertiaries(self):
        dragon = COMBAT_ENEMY_DATA["steel_dragon"]
        coin_closure = _combat_roll_drops(
            dragon,
            _rng(
                [
                    95 / 128,
                    0.999999,
                    0.999999,
                    0.999999,
                    0.999999,
                    0.999999,
                    0.999999,
                ]
            ),
        )
        rares = _combat_roll_drops(
            dragon,
            _rng([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        )

        self.assertEqual(
            coin_closure,
            {
                "Dragon bones": 1,
                "Steel bar": 5,
                "Coins": 650,
            },
        )
        self.assertEqual(
            rares,
            {
                "Dragon bones": 1,
                "Steel bar": 5,
                "Rune javelin": 7,
                "Gold charm": 3,
                "Dragon plateskirt": 1,
                "Dragon platelegs": 1,
                "Draconic visage": 1,
                "Clue scroll (hard)": 1,
                "Clue scroll (elite)": 1,
            },
        )

    def test_steel_dragon_double_clue_roll_reports_the_refused_scroll(self):
        drops, clue_refusal_reason = _combat_roll_drops(
            COMBAT_ENEMY_DATA["steel_dragon"],
            _rng([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            player_data={"inventory": {}},
            include_clue_refusal=True,
        )

        clue_drops = {
            item: amount
            for item, amount in drops.items()
            if item.startswith("Clue scroll")
        }
        self.assertEqual(clue_drops, {"Clue scroll (elite)": 1})
        self.assertEqual(
            clue_refusal_reason,
            "You can only carry one clue scroll at a time.",
        )

    def test_red_dragon_rolls_exact_ordinary_and_independent_tertiaries(self):
        dragon = COMBAT_ENEMY_DATA["red_dragon"]
        empty_ordinary = _combat_roll_drops(
            dragon,
            _rng([0.999999, 0.999999, 0.999999, 0.999999]),
            player_data={"summoning_level": 99},
        )
        rares = _combat_roll_drops(
            dragon,
            _rng([0.0, 0.999999, 0.0, 0.0]),
            player_data={"summoning_level": 99},
        )
        below_egg_level = _combat_roll_drops(
            dragon,
            _rng([0.0, 0.999999, 0.0]),
            player_data={"summoning_level": 98},
        )

        self.assertEqual(
            empty_ordinary,
            {"Dragon bones": 1, "Red dragonhide": 1},
        )
        self.assertEqual(
            rares,
            {
                "Dragon bones": 1,
                "Red dragonhide": 1,
                "Coins": 196,
                "Red dragon egg": 1,
                "Clue scroll (hard)": 1,
            },
        )
        self.assertEqual(
            below_egg_level,
            {
                "Dragon bones": 1,
                "Red dragonhide": 1,
                "Coins": 196,
                "Clue scroll (hard)": 1,
            },
        )

    def test_black_dragon_rolls_exact_ordinary_and_independent_tertiaries(self):
        dragon = COMBAT_ENEMY_DATA["black_dragon"]
        empty_ordinary = _combat_roll_drops(
            dragon,
            _rng(
                [
                    127 / 128,
                    0.999999,
                    0.999999,
                    0.999999,
                    0.999999,
                    0.999999,
                ]
            ),
            player_data={"summoning_level": 99},
        )
        rares = _combat_roll_drops(
            dragon,
            _rng([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            player_data={"summoning_level": 99},
        )
        below_egg_level = _combat_roll_drops(
            dragon,
            _rng([0.0, 0.0, 0.0, 0.0, 0.0]),
            player_data={"summoning_level": 98},
        )

        self.assertEqual(
            empty_ordinary,
            {"Dragon bones": 1, "Black dragonhide": 1},
        )
        # Both tertiary clue rolls hit here, but the period lets a player hold
        # one clue scroll across every tier (design-thread-queue.md 4.5), so the
        # drop filter keeps the higher tier and drops the other. This assertion
        # changed when that rule landed; before it, the payload carried both.
        self.assertEqual(
            rares,
            {
                "Dragon bones": 1,
                "Black dragonhide": 1,
                "Mithril 2h sword": 1,
                "Gold charm": 3,
                "Black dragon egg": 1,
                "Draconic visage": 1,
                "Clue scroll (elite)": 1,
            },
        )
        self.assertEqual(
            _combat_roll_drops(
                dragon,
                _rng([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                player_data={
                    "summoning_level": 99,
                    "inventory": {"Clue scroll (easy)": 1},
                },
            ).get("Clue scroll (elite)"),
            None,
            "a player already holding a clue receives no second one",
        )
        self.assertEqual(
            below_egg_level,
            {
                "Dragon bones": 1,
                "Black dragonhide": 1,
                "Mithril 2h sword": 1,
                "Gold charm": 3,
                "Draconic visage": 1,
                "Clue scroll (elite)": 1,
            },
        )

    def test_cave_horror_rolls_nested_allotments_and_independent_rares(self):
        horror = COMBAT_ENEMY_DATA["cave_horror"]

        self.assertEqual(DARKAN_VARIABLE_ALLOTMENT_DROP_TABLE["total"], 263)
        self.assertEqual(
            sum(
                slot["slots"]
                for slot in DARKAN_VARIABLE_ALLOTMENT_DROP_TABLE["slots"]
            ),
            263,
        )
        nested_and_mask = _combat_roll_drops(
            horror,
            _rng(
                [
                    46 / 128,
                    0.0,
                    0.0,
                    0.999999,
                    0.999999,
                    0.0,
                    0.999999,
                ]
            ),
        )
        charms_and_clue = _combat_roll_drops(
            horror,
            _rng([0.0, 0.0, 0.999999, 0.999999, 0.0]),
        )

        self.assertEqual(
            nested_and_mask,
            {
                "Big bones": 1,
                "Potato seed": 1,
                "Black mask (10)": 1,
            },
        )
        self.assertEqual(
            charms_and_clue,
            {
                "Big bones": 1,
                "Coins": 44,
                "Gold charm": 1,
                "Clue scroll (hard)": 1,
            },
        )

    def test_dagannoth_forms_preserve_period_combat_identities(self):
        ranged = COMBAT_ENEMY_DATA["dagannoth"]
        melee = COMBAT_ENEMY_DATA["dagannoth_level_92"]

        self.assertEqual(
            (
                ranged["level"],
                ranged["stats"]["hitpoints"],
                ranged["attack_style"],
                ranged["attack_speed"],
                ranged["max_hit"],
                ranged["slayer_xp"],
            ),
            (74, 700, "ranged", 6, 80, 70.0),
        )
        self.assertEqual(
            (
                melee["level"],
                melee["stats"]["hitpoints"],
                melee["attack_style"],
                melee["attack_speed"],
                melee["max_hit"],
                melee["slayer_xp"],
            ),
            (92, 1200, "melee", 6, 80, 120.0),
        )
        self.assertEqual(melee["bonuses"]["defence_magic"], 50)
        self.assertEqual(melee["bonuses"]["defence_ranged"], 50)
        self.assertIs(ranged["drops"], melee["drops"])
        self.assertIn("oldid=6548464", ranged["source"])

    def test_dagannoth_drop_selector_preserves_empty_torstol_and_tertiaries(self):
        dagannoth = COMBAT_ENEMY_DATA["dagannoth"]
        ordinary, charms, clue = dagannoth["drops"]["tables"]

        self.assertEqual(ordinary["total"], 1100)
        self.assertEqual(
            sum(slot["slots"] for slot in ordinary["slots"]),
            ordinary["total"],
        )
        self.assertEqual(
            sum(slot["slots"] for slot in charms["slots"]),
            charms["total"],
        )
        self.assertEqual(
            _combat_roll_drops(
                dagannoth,
                _rng((0.999999, 0.999999, 0.999999)),
            ),
            {"Bones": 1},
        )
        self.assertEqual(
            _combat_roll_drops(
                dagannoth,
                _rng((1075 / 1100, 0.999999, 0.999999)),
            ),
            {"Bones": 1, "Torstol seed": 1},
        )
        self.assertEqual(
            _combat_roll_drops(
                dagannoth,
                _rng((0.0, 0.0, 0.0)),
            ),
            {
                "Bones": 1,
                "Pearl bolt tips": 12,
                "Gold charm": 1,
                "Clue scroll (medium)": 1,
            },
        )

    def test_elf_warrior_forms_preserve_period_combat_identities_and_gate(self):
        ranged = COMBAT_ENEMY_DATA["elf_warrior"]
        melee = COMBAT_ENEMY_DATA["elf_warrior_level_108"]

        self.assertEqual(
            (
                ranged["level"],
                ranged["stats"]["hitpoints"],
                ranged["attack_style"],
                ranged["attack_speed"],
                ranged["max_hit"],
                ranged["slayer_xp"],
            ),
            (90, 1050, "ranged", 6, 116, 105.0),
        )
        self.assertEqual(
            (
                melee["level"],
                melee["stats"]["hitpoints"],
                melee["attack_style"],
                melee["attack_speed"],
                melee["max_hit"],
                melee["slayer_xp"],
            ),
            (108, 1060, "melee", 6, 109, 107.5),
        )
        self.assertIs(ranged["drops"], melee["drops"])
        self.assertEqual(
            combat_target_locked_reasons_pure(
                _player(), "elf_warrior", COMBAT_ENEMY_DATA
            ),
            ("Complete Regicide",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                _player(quests={"regicide": {"completed": True}}),
                "elf_warrior_level_108",
                COMBAT_ENEMY_DATA,
            ),
            (),
        )
        crystal_seed = next(
            item
            for item in ITEM_DEFINITIONS
            if item.storage_key == "Crystal teleport seed"
        )
        self.assertEqual(crystal_seed.source_item_id, 6103)
        self.assertFalse(crystal_seed.stackable)
        self.assertFalse(crystal_seed.tradeable)

    def test_elf_warrior_drop_selectors_preserve_empty_seed_and_tertiaries(self):
        elf = COMBAT_ENEMY_DATA["elf_warrior"]
        ordinary, charms, clue = elf["drops"]["tables"]

        self.assertEqual(
            sum(slot["slots"] for slot in ordinary["slots"]),
            ordinary["total"],
        )
        self.assertEqual(
            sum(slot["slots"] for slot in charms["slots"]),
            charms["total"],
        )
        self.assertEqual(
            _combat_roll_drops(
                elf,
                _rng((0.999999, 0.999999, 0.999999)),
            ),
            {"Bones": 1},
        )
        self.assertEqual(
            _combat_roll_drops(
                elf,
                _rng((29 / 128, 0.999999, 0.999999)),
            ),
            {"Bones": 1, "Crystal teleport seed": 1},
        )
        self.assertEqual(
            _combat_roll_drops(
                elf,
                _rng((0.0, 0.0, 0.0)),
            ),
            {
                "Bones": 1,
                "Coins": 44,
                "Gold charm": 1,
                "Clue scroll (hard)": 1,
            },
        )

    def test_bloodveld_drop_roll_can_reach_black_boots(self):
        self.assertEqual(
            _combat_roll_drops(
                COMBAT_ENEMY_DATA["bloodveld"],
                _rng([117 / 128]),
            ),
            {"Bones": 1, "Black boots": 1},
        )

    def test_darkan_ordinary_drop_rows_are_mutually_exclusive(self):
        cases = (
            (
                "infernal_mage",
                53500 / 64000,
                {"Bones": 1, "Mystic boots (dark)": 1},
            ),
            (
                "basilisk",
                63500 / 64000,
                {"Bones": 1, "Mystic hat (light)": 1},
            ),
            (
                "jungle_horror",
                33580 / 100000,
                {"Bones": 1, "Iron warhammer": 1},
            ),
            (
                "shadow_warrior",
                74 / 128,
                {"Adamant spear": 1},
            ),
        )
        for target_id, roll, expected in cases:
            with self.subTest(target_id=target_id):
                self.assertEqual(
                    _combat_roll_drops(
                        COMBAT_ENEMY_DATA[target_id],
                        _rng([roll, 0.999999]),
                    ),
                    expected,
                )

    def test_darkan_rare_rows_remain_reachable_inside_the_main_selector(self):
        cases = (
            ("infernal_mage", 53625 / 64000, "Mystic hat (dark)"),
            ("infernal_mage", 53750 / 64000, "Lava battlestaff"),
            ("basilisk", 63625 / 64000, "Basilisk head"),
        )
        for target_id, roll, rare_item in cases:
            with self.subTest(target_id=target_id, rare_item=rare_item):
                self.assertEqual(
                    _combat_roll_drops(
                        COMBAT_ENEMY_DATA[target_id],
                        _rng([roll]),
                    ),
                    {"Bones": 1, rare_item: 1},
                )

    def test_older_darkan_targets_also_use_one_ordinary_selector(self):
        cases = (
            ("young_grotworm", [0.0], {"Bones": 1, "Coal": 1}),
            ("desert_lizard", [0.0], {"Bones": 1, "Grimy tarromin": 1}),
            ("rockslug", [0.0, 0.999999], {"Copper ore": 1}),
            ("gargoyle", [0.0, 0.999999], {"Coins": 11}),
            (
                "mutated_zygomite_level_74",
                [0.999999, 0.0, 0.0],
                {"Ashes": 1, "Strawberry seed": 1},
            ),
            (
                "cyclops",
                [0.999999, 0.0],
                {"Big bones": 1, "Limpwurt root": 1},
            ),
            (
                "cyclossus",
                [0.0, 0.999999],
                {"Big bones": 1, "Limpwurt root": 5},
            ),
        )
        for target_id, rolls, expected in cases:
            with self.subTest(target_id=target_id):
                self.assertEqual(
                    _combat_roll_drops(
                        COMBAT_ENEMY_DATA[target_id],
                        _rng(rolls),
                    ),
                    expected,
                )

    def test_aberrant_spectre_rolls_exact_main_and_nested_tables(self):
        spectre = COMBAT_ENEMY_DATA["aberrant_spectre"]

        self.assertEqual(DARKAN_HERB_DROP_TABLE["total"], 128)
        self.assertEqual(DARKAN_ABERRANT_RARE_SEED_DROP_TABLE["total"], 125)
        self.assertEqual(DARKAN_GEM_DROP_TABLE["total"], 128)
        self.assertEqual(DARKAN_MEGA_RARE_DROP_TABLE["total"], 256)
        for table in (
            DARKAN_HERB_DROP_TABLE,
            DARKAN_ABERRANT_RARE_SEED_DROP_TABLE,
            DARKAN_GEM_DROP_TABLE,
            DARKAN_MEGA_RARE_DROP_TABLE,
        ):
            self.assertEqual(
                sum(slot["slots"] for slot in table["slots"]), table["total"]
            )

        herb = _combat_roll_drops(spectre, _rng([0.0, 0.0, 0.999999]))
        seed = _combat_roll_drops(
            spectre, _rng([312 / 512, 0.0, 0.999999])
        )
        mystic = _combat_roll_drops(
            spectre, _rng([440 / 512, 0.999999])
        )
        self.assertEqual(herb, {"Grimy guam": 1})
        self.assertEqual(seed, {"Toadflax seed": 1})
        self.assertEqual(mystic, {"Mystic robe bottom (dark)": 1})
        vecna = _combat_roll_drops(
            spectre,
            _rng(
                [
                    388 / 512,
                    64 / 128,
                    30 / 256,
                    0.999999,
                ]
            ),
        )
        self.assertEqual(vecna, {"Vecna skull": 1})

    def test_zombie_drop_rolls_nested_minor_herbs_and_level_25_variant(self):
        herb_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["zombie_level_13"],
            _rng([41 / 128, 0.0, 0.999999]),
        )
        normal_table_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["zombie_level_24"],
            _rng([4 / 128, 0.999999]),
        )
        level_25_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["zombie_level_25"],
            _rng([4 / 128, 0.999999]),
        )

        self.assertEqual(herb_drops, {"Bones": 1, "Grimy guam": 1})
        self.assertEqual(normal_table_drops, {"Bones": 1, "Bronze med helm": 1})
        self.assertEqual(level_25_drops, {"Bones": 1, "Iron hatchet": 1})

    def test_skeleton_drop_rolls_nested_herb_and_gem_tables(self):
        low_gem_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["skeleton_level_21"],
            _rng([1016 / 1024, 512 / 1024, 0.999999]),
        )
        high_herb_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["skeleton_level_25"],
            _rng([27 / 128, 0.0, 0.999999]),
        )

        self.assertEqual(low_gem_drops, {"Bones": 1, "Uncut sapphire": 1})
        self.assertEqual(high_herb_drops, {"Bones": 1, "Grimy guam": 1})

    def test_duck_drop_rolls_follow_land_water_source_split(self):
        self.assertEqual(_combat_roll_drops(COMBAT_ENEMY_DATA["duck_land"], _rng([])), {"Bones": 1})
        self.assertEqual(_combat_roll_drops(COMBAT_ENEMY_DATA["duck_water"], _rng([])), {})

    def test_pirate_drop_rolls_quantity_range_and_nested_gem_table(self):
        bolt_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["pirate"],
            _rng([88 / 1024, 0.999999]),
        )
        gem_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["pirate"],
            _rng([1016 / 1024, 512 / 1024]),
        )

        self.assertEqual(bolt_drops, {"Bones": 1, "Iron bolts": 12})
        self.assertEqual(gem_drops, {"Bones": 1, "Uncut sapphire": 1})

    def test_monk_of_zamorak_level_45_drop_rolls_main_and_charms(self):
        top_and_charm = _combat_roll_drops(
            COMBAT_ENEMY_DATA["monk_of_zamorak_level_45"],
            _rng([0.0, 10 / 1000]),
        )
        bottom_only = _combat_roll_drops(
            COMBAT_ENEMY_DATA["monk_of_zamorak_level_45"],
            _rng([1 / 20, 140 / 1000]),
        )

        self.assertEqual(top_and_charm, {"Bones": 1, "Zamorak robe top": 1, "Green charm": 1})
        self.assertEqual(bottom_only, {"Bones": 1, "Zamorak robe bottom": 1})

    def test_humanoid_quantity_range_drop_rolls(self):
        cases = (
            ("mugger", [0.0, 0.999999, 0.999999]),
            ("thief", [4 / 128, 0.999999, 0.999999]),
            ("al_kharid_warrior", [24 / 1024, 0.999999, 0.999999]),
        )
        for enemy_id, rolls in cases:
            with self.subTest(enemy_id):
                self.assertEqual(
                    _combat_roll_drops(COMBAT_ENEMY_DATA[enemy_id], _rng(rolls)),
                    {"Bones": 1, "Bronze bolts": 12},
                )

    def test_thug_drop_rolls_main_charms_and_tertiary_tables(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["thug"],
            _rng([120 / 128, 0.0, 0.0]),
        )

        self.assertEqual(drops, {"Bones": 1, "Gold charm": 1, "Clue scroll (easy)": 1})

    def test_guard_drop_rolls_quantity_range_medium_clue_and_charms(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["guard_varrock"],
            _rng([0.0, 0.999999, 0.999999, 0.0]),
        )

        self.assertEqual(
            drops,
            {"Bones": 1, "Iron bolts": 12, "Clue scroll (medium)": 1, "Gold charm": 1},
        )

    def test_humanoid_drop_tables_reach_nested_allotment_seeds(self):
        cases = (
            ("guard_sword", [120 / 146, 0.0, 0.0, 0.999999]),
            ("farmer", [18 / 128, 0.0, 0.999999]),
        )
        for enemy_id, rolls in cases:
            with self.subTest(enemy_id):
                self.assertEqual(
                    _combat_roll_drops(COMBAT_ENEMY_DATA[enemy_id], _rng(rolls)),
                    {"Bones": 1, "Potato seed": 4},
                )

    def test_black_knight_drop_rolls_nested_seed_table_and_charms(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["black_knight"],
            _rng([93 / 116, 0.0, 39 / 1000]),
        )

        self.assertEqual(drops, {"Bones": 1, "Potato seed": 4, "Green charm": 1})

    def test_white_knight_drop_rolls_quantity_ranges_nested_tables_and_tertiary(self):
        body_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["white_knight_level_36"],
            _rng([19 / 128, 0.999999, 0.999999]),
        )
        allotment_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["white_knight_level_42"],
            _rng([97 / 127, 0.0, 0.999999]),
        )
        gem_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["white_knight_level_38"],
            _rng([128 / 130, 512 / 1024, 0.999999]),
        )
        clue_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["white_knight_level_39"],
            _rng([0.999999, 0.0, 0.0]),
        )

        self.assertEqual(body_drops, {"Bones": 1, "Body rune": 13})
        self.assertEqual(allotment_drops, {"Bones": 1, "Potato seed": 4})
        self.assertEqual(gem_drops, {"Bones": 1, "Uncut sapphire": 1})
        self.assertEqual(clue_drops, {"Bones": 1, "Clue scroll (easy)": 1})

    def test_outlaw_drop_rolls_nested_herbs_and_charms(self):
        rope_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["outlaw"],
            _rng([25 / 127, 0.999999]),
        )
        herb_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["outlaw"],
            _rng([95 / 127, 0.0, 0.999999]),
        )
        charm_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["outlaw"],
            _rng([0.0, 360 / 1000]),
        )

        self.assertEqual(rope_drops, {"Bones": 1, "Rope": 1})
        self.assertEqual(herb_drops, {"Bones": 1, "Grimy guam": 1})
        self.assertEqual(charm_drops, {"Bones": 1, "Bronze med helm": 1, "Green charm": 1})

    def test_chaos_dwarf_drop_rolls_muddy_key_and_charms(self):
        muddy_key_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["chaos_dwarf"],
            _rng([113 / 128, 0.999999]),
        )
        charm_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["chaos_dwarf"],
            _rng([0.0, 100 / 1000]),
        )

        self.assertEqual(muddy_key_drops, {"Bones": 1, "Muddy key": 1})
        self.assertEqual(charm_drops, {"Bones": 1, "Steel full helm": 1, "Green charm": 1})

    def test_haakon_drop_rolls_tail_main_slot_and_easy_clue(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["haakon_the_champion"],
            _rng([1016 / 1024, 0.0]),
        )

        self.assertEqual(drops, {"Bones": 1, "Ring mould": 1, "Clue scroll (easy)": 1})

    def test_ham_guard_drop_rolls_quantity_ranges_nested_tables_and_tertiary(self):
        clothing_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["ham_guard_level_12"],
            _rng([180 / 648, 0.0]),
        )
        seed_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["ham_guard_level_22"],
            _rng([264 / 648, 0.0, 0.999999]),
        )
        thread_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["ham_guard_level_18"],
            _rng([636 / 648, 0.999999, 0.999999]),
        )

        self.assertEqual(clothing_drops, {"Bones": 1, "H.A.M. gloves": 1, "Clue scroll (easy)": 1})
        self.assertEqual(seed_drops, {"Bones": 1, "Potato seed": 4})
        self.assertEqual(thread_drops, {"Bones": 1, "Thread": 10})

    def test_imp_drop_rolls_beads_and_tail_slot(self):
        bead_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["imp"],
            _rng([120 / 1024]),
        )
        tail_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["imp"],
            _rng([1008 / 1024]),
        )

        self.assertEqual(bead_drops, {"Impious ashes": 1, "Yellow bead": 1})
        self.assertEqual(tail_drops, {"Impious ashes": 1, "Chef's hat": 1})

    def test_dwarf_drop_rolls_quantity_range_charms_and_tertiary_tables(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["dwarf_level_10"],
            _rng([20 / 128, 0.999999, 0.0, 0.0]),
        )

        self.assertEqual(
            drops,
            {"Bones": 1, "Bronze bolts": 12, "Gold charm": 1, "Clue scroll (easy)": 1},
        )

    def test_dwarf_drop_rolls_nested_gem_table(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["dwarf_level_11"],
            _rng([104 / 128, 512 / 1024, 0.999999, 0.999999]),
        )

        self.assertEqual(drops, {"Bones": 1, "Uncut sapphire": 1})

    def test_dwarf_drop_rolls_nested_mega_rare_table(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["dwarf_level_11"],
            _rng([104 / 128, 1016 / 1024, 1000 / 1024, 0.999999, 0.999999]),
        )

        self.assertEqual(drops, {"Bones": 1, "Dragon spear": 1})

    def test_low_level_enemy_drops_combine_main_charms_and_tertiary_tables(self):
        cases = (
            (
                "barbarian",
                {"Bones": 1, "Bronze hatchet": 1, "Gold charm": 1, "Clue scroll (easy)": 1},
            ),
            (
                "goblin_level_2_unarmed",
                {"Bones": 1, "Bronze sq shield": 1, "Gold charm": 1, "Clue scroll (easy)": 1},
            ),
        )
        for enemy_id, expected in cases:
            with self.subTest(enemy_id):
                self.assertEqual(
                    _combat_roll_drops(COMBAT_ENEMY_DATA[enemy_id], _rng([0.0, 0.0, 0.0])),
                    expected,
                )

    def test_barbarian_level_10_drop_rolls_include_tail_main_slot(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["barbarian_level_10"],
            _rng([0.999999, 0.999999, 0.999999]),
        )

        self.assertEqual(drops, {"Bones": 1, "Ring mould": 1})

    def test_barbarian_level_17_drop_rolls_include_source_charms(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["barbarian_level_17"],
            _rng([0.0, 60 / 1000, 0.999999]),
        )

        self.assertEqual(drops, {"Bones": 1, "Bronze hatchet": 1, "Crimson charm": 1})

    def test_hobgoblin_drop_rolls_nested_tables_and_charms(self):
        unarmed_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["hobgoblin_unarmed"],
            _rng([0.0, 0.0]),
        )
        armed_seed_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["hobgoblin_armed"],
            _rng([31 / 128, 0.0, 0.999999]),
        )

        self.assertEqual(unarmed_drops, {"Bones": 1, "Bronze spear": 1, "Gold charm": 1})
        self.assertEqual(armed_seed_drops, {"Bones": 1, "Limpwurt seed": 1})

    def test_tzhaar_ket_drop_rolls_quantity_ranges_obsidian_and_charms(self):
        tokkul_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["tzhaar_ket"],
            _rng([0.0, 0.999999, 0.999999, 0.999999]),
        )
        rare_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["tzhaar_ket"],
            _rng([127 / 128, 0.999999, 0.0, 0.0]),
        )

        self.assertEqual(tokkul_drops, {"Tokkul": 2000})
        self.assertEqual(rare_drops, {"Onyx bolt tips": 4, "Tzhaar-ket-om": 1, "Obsidian charm": 2})

    def test_chaos_druid_drop_rolls_quantity_range_and_nested_tables(self):
        bolt_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["chaos_druid"],
            _rng([7 / 128, 0.999999]),
        )
        herb_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["chaos_druid"],
            _rng([22 / 128, 0.0]),
        )
        gem_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["chaos_druid"],
            _rng([127 / 128, 512 / 1024]),
        )
        mould_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["chaos_druid"],
            _rng([126 / 128]),
        )

        self.assertEqual(bolt_drops, {"Bones": 1, "Mithril bolts": 12})
        self.assertEqual(herb_drops, {"Bones": 1, "Grimy guam": 1})
        self.assertEqual(gem_drops, {"Bones": 1, "Uncut sapphire": 1})
        self.assertEqual(mould_drops, {"Bones": 1, "Unholy mould": 1})

    def test_scorpion_and_higher_spider_drop_rolls_use_source_tables(self):
        scorpion_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["scorpion"], _rng([0.03]))
        king_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["king_scorpion"], _rng([]))
        pit_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["pit_scorpion"], _rng([]))
        scorpion_59_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["scorpion_level_59"], _rng([0.109]))
        deadly_red_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["deadly_red_spider"], _rng([0.259]))
        giant_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["giant_spider_level_50"],
            _rng([0.0, 0.999999, 0.999999, 0.999999, 0.999999]),
        )

        self.assertEqual(scorpion_drops, {"Green charm": 1})
        self.assertEqual(king_drops, {})
        self.assertEqual(pit_drops, {})
        self.assertEqual(scorpion_59_drops, {"Crimson charm": 1})
        self.assertEqual(deadly_red_drops, {"Gold charm": 1})
        self.assertEqual(giant_drops, {"Air rune": 6})

    def test_cow_calf_burst_grants_source_guaranteed_drops(self):
        player = _player(current_combat_target="cow_calf")

        # ticks=1 restricts the burst to a single player attack, isolating one
        # kill's guaranteed drops now that a burst chains kills across the window.
        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["combat_kill_counts"], {"cow_calf": 1})
        self.assertEqual(
            new_data["combat_observed_drops"]["cow_calf"],
            {
                "Bones": {"times_seen": 1, "quantity_seen": 1},
                "Raw beef": {"times_seen": 1, "quantity_seen": 1},
                "Cowhide": {"times_seen": 1, "quantity_seen": 1},
            },
        )
        self.assertEqual(new_data["inventory"]["Bones"], 1)
        self.assertEqual(new_data["inventory"]["Raw beef"], 1)
        self.assertEqual(new_data["inventory"]["Cowhide"], 1)
        reloaded = migrate_loaded_data(new_data, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(
            reloaded["combat_observed_drops"], new_data["combat_observed_drops"]
        )

    def test_combat_burst_kills_once_awards_xp_and_rolls_source_backed_drops(self):
        player = _player()

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=500,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["combat_kill_counts"], {"chicken": 1})
        self.assertEqual(new_data["combat_encounter"], {})
        self.assertGreater(new_data["attack_exp"], 0)
        self.assertGreater(new_data["constitution_exp"], 0)
        self.assertEqual(new_data["inventory"]["Bones"], 1)
        self.assertEqual(new_data["inventory"]["Raw chicken"], 1)
        self.assertEqual(new_data["inventory"]["Feather"], 5)

    def test_combat_burst_chains_multiple_kills_within_tick_budget(self):
        # A constant 0.5 roll always lands the player's near-max hit (one-shotting
        # a chicken) while the chicken's own attack always misses against defence
        # 99, so a full 50-tick burst should defeat several respawns rather than
        # stopping after the first kill and wasting the rest of the window.
        player = _player()

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=lambda: 0.5,
        )

        self.assertTrue(ok)
        self.assertGreater(result["kills"], 1)
        self.assertTrue(result["killed"])
        self.assertFalse(result["died"])
        self.assertEqual(new_data["combat_kill_counts"], {"chicken": result["kills"]})
        self.assertEqual(
            new_data["combat_observed_drops"]["chicken"]["Bones"],
            {"times_seen": result["kills"], "quantity_seen": result["kills"]},
        )
        # Each defeated chicken drops one guaranteed Bones, so the aggregated
        # loot scales with the kill count.
        self.assertEqual(new_data["inventory"]["Bones"], result["kills"])

    def test_aggressive_style_routes_melee_xp_to_strength(self):
        player = _player(combat_attack_style="aggressive")

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["attack_exp"], 0.0)
        self.assertGreater(new_data["strength_exp"], 0.0)

    def test_ranged_style_is_derived_from_supported_weapon_and_ammo(self):
        player = _player(combat_attack_style="ranged_accurate")

        self.assertEqual(
            combat_target_locked_reasons_pure(player, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

        with_bow = _player(combat_attack_style="ranged_accurate", equipment={"weapon": "Shortbow"})
        self.assertEqual(
            combat_target_locked_reasons_pure(with_bow, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("compatible ammunition",),
        )

        with_ammo = _player(
            combat_attack_style="ranged_accurate",
            equipment={"weapon": "Shortbow"},
            inventory={"Bronze arrows": 3},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(with_ammo, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

    def test_ranged_burst_consumes_bronze_arrows_and_awards_ranged_xp(self):
        player = _player(
            combat_attack_style="ranged_accurate",
            equipment={"weapon": "Shortbow"},
            combat_supply_loadout={"ammo": {"Bronze arrows": 2}},
        )

        # ticks=1 keeps the burst to one shot so this stays a single-kill ammo
        # check; chaining is covered separately.
        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(result["combat_class"], "ranged")
        self.assertEqual(result["weapon"], "Shortbow")
        self.assertEqual(result["ammo"], "Bronze arrows")
        self.assertEqual(result["ammo_used"], {"Bronze arrows": 1})
        self.assertEqual(result["formula_source"], RANGED_FORMULA_SOURCE_PATH)
        self.assertEqual(result["xp_source"], RANGED_STRATEGY_SOURCE_PATH)
        self.assertEqual(new_data["combat_supply_loadout"]["ammo"], {"Bronze arrows": 1})
        self.assertEqual(new_data["attack_exp"], 0.0)
        self.assertGreater(new_data["ranged_exp"], 0.0)
        self.assertGreater(new_data["constitution_exp"], 0.0)

    def test_ranged_burst_accepts_higher_arrow_tiers_for_supported_bows(self):
        player = _player(
            combat_attack_style="ranged_accurate",
            equipment={"weapon": "Magic shortbow"},
            inventory={"Bronze arrows": 1},
            combat_supply_loadout={"ammo": {"Rune arrows": 2}},
            current_combat_target="giant_rat",
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["weapon"], "Magic shortbow")
        self.assertEqual(result["ammo"], "Rune arrows")
        self.assertEqual(result["ammo_used"], {"Rune arrows": 1})
        self.assertEqual(new_data["combat_supply_loadout"]["ammo"], {"Rune arrows": 1})

    def test_ranged_longrange_splits_xp_between_ranged_and_defense(self):
        player = _player(
            combat_attack_style="ranged_longrange",
            equipment={"weapon": "Shortbow"},
            combat_supply_loadout={"ammo": {"Bronze arrows": 2}},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertGreater(new_data["ranged_exp"], 0.0)
        self.assertAlmostEqual(new_data["ranged_exp"], new_data["defense_exp"])
        self.assertEqual(new_data["attack_exp"], 0.0)

    def test_magic_style_requires_wind_strike_runes(self):
        player = _player(combat_attack_style="magic_standard", equipment={"weapon": "Staff"}, inventory={})

        self.assertEqual(
            combat_target_locked_reasons_pure(player, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("runes: Air rune x1, Mind rune x1",),
        )

        with_runes = _player(
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff"},
            inventory={"Air rune": 1, "Mind rune": 1},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(with_runes, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

        with_staff = _player(
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff of air"},
            inventory={"Mind rune": 1},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(with_staff, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

    def test_fire_strike_requires_level_and_uses_source_runes(self):
        underleveled = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_strike",
            magic_level=12,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 1, "Mind rune": 1, "Fire rune": 3},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(underleveled, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("Magic level 13",),
        )

        with_fire_staff = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_strike",
            magic_level=13,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 1, "Mind rune": 1},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(with_fire_staff, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

    def test_fire_wave_requires_level_and_blood_runes(self):
        underleveled = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_wave",
            magic_level=74,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 5, "Fire rune": 7, "Blood rune": 1},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(underleveled, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("Magic level 75",),
        )

        missing_blood = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_wave",
            magic_level=75,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 5},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(missing_blood, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("runes: Blood rune x1",),
        )

        with_fire_staff = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_wave",
            magic_level=75,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 5, "Blood rune": 1},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(with_fire_staff, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

    def test_magic_burst_consumes_wind_strike_runes_and_awards_magic_xp(self):
        player = _player(
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff"},
            combat_supply_loadout={"runes": {"Air rune": 2, "Mind rune": 2}},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.0, 0.999999, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["combat_class"], "magic")
        self.assertEqual(result["spell_id"], "wind_strike")
        self.assertEqual(result["spell"], "Wind Strike")
        self.assertEqual(result["runes_used"], {"Air rune": 1, "Mind rune": 1})
        self.assertEqual(result["formula_source"], MAGIC_FORMULA_SOURCE_PATH)
        self.assertEqual(result["xp_source"], MAGIC_STRATEGY_SOURCE_PATH)
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {"Air rune": 1, "Mind rune": 1})
        self.assertEqual(new_data["attack_exp"], 0.0)
        self.assertEqual(new_data["ranged_exp"], 0.0)
        self.assertGreater(new_data["magic_exp"], 5.5)
        self.assertGreater(new_data["constitution_exp"], 0.0)

    def test_borrowed_power_is_one_manual_combat_cast_not_autocast(self):
        player = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="wind_strike",
            combat_borrowed_power_spell="wind_wave",
            equipment={
                "weapon": "Staff of air",
                "neck": ARCANE_CAPACITOR_CHARGED,
            },
            combat_supply_loadout={"runes": {"Astral rune": 3}},
            quests={"lunar_diplomacy": {"completed": True}},
            livid_farm={
                "borrowed_power_claimed": True,
                "arcane_capacitor_spell": "wind_wave",
                "arcane_capacitor_charges": 2,
            },
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["ticks"], 1)
        self.assertTrue(result["borrowed_power"])
        self.assertEqual(result["spell_id"], "wind_wave")
        self.assertEqual(result["runes_used"], {"Astral rune": 3})
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {})
        self.assertEqual(new_data["combat_borrowed_power_spell"], "")
        self.assertEqual(
            new_data["livid_farm"]["arcane_capacitor_charges"],
            1,
        )
        self.assertEqual(
            new_data["equipment"]["neck"],
            ARCANE_CAPACITOR_CHARGED,
        )
        self.assertGreater(new_data["magic_exp"], 0.0)

    def test_borrowed_power_combat_cast_requires_the_bound_equipped_capacitor(self):
        player = _player(
            combat_attack_style="magic_standard",
            combat_borrowed_power_spell="fire_wave",
            equipment={"weapon": "Staff of fire"},
            combat_supply_loadout={"runes": {"Astral rune": 3}},
            quests={"lunar_diplomacy": {"completed": True}},
            livid_farm={
                "borrowed_power_claimed": True,
                "arcane_capacitor_spell": "wind_wave",
                "arcane_capacitor_charges": 1_000,
            },
        )

        self.assertEqual(
            combat_target_locked_reasons_pure(
                player,
                "chicken",
                COMBAT_ENEMY_DATA,
                equipment_data=EQUIPMENT_DATA,
            ),
            (
                "Equip the charged Arcane capacitor",
                "Charge the capacitor with this spell",
            ),
        )

    def test_magic_staff_substitution_does_not_load_or_consume_covered_rune(self):
        player = _player(
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff of air"},
            combat_supply_loadout={"runes": {"Air rune": 1, "Mind rune": 2}},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.0, 0.999999, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["runes_used"], {"Mind rune": 1})
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {"Air rune": 1, "Mind rune": 1})
        self.assertGreater(new_data["magic_exp"], 5.5)

    def test_fire_strike_with_staff_consumes_only_uncovered_runes(self):
        player = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_strike",
            magic_level=13,
            equipment={"weapon": "Staff of fire"},
            combat_supply_loadout={"runes": {"Air rune": 1, "Mind rune": 1}},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["spell_id"], "fire_strike")
        self.assertEqual(result["spell"], "Fire Strike")
        self.assertEqual(result["runes_used"], {"Air rune": 1, "Mind rune": 1})
        self.assertEqual(new_data["inventory"].get("Fire rune", 0), 0)
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {})
        self.assertAlmostEqual(new_data["magic_exp"], 11.5)

    def test_fire_wave_with_staff_consumes_blood_and_air_runes_and_awards_base_xp_on_splash(self):
        player = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_wave",
            magic_level=75,
            equipment={"weapon": "Staff of fire"},
            combat_supply_loadout={"runes": {"Air rune": 5, "Blood rune": 1}},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["spell_id"], "fire_wave")
        self.assertEqual(result["spell"], "Fire Wave")
        self.assertEqual(result["runes_used"], {"Air rune": 5, "Blood rune": 1})
        self.assertEqual(new_data["inventory"].get("Fire rune", 0), 0)
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {})
        self.assertAlmostEqual(new_data["magic_exp"], 42.5)
        self.assertEqual(new_data["constitution_exp"], 0.0)

    def test_magic_splash_consumes_runes_and_awards_base_spell_xp(self):
        player = _player(
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff"},
            combat_supply_loadout={"runes": {"Air rune": 1, "Mind rune": 1}},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["player_damage"], 0)
        self.assertEqual(result["runes_used"], {"Air rune": 1, "Mind rune": 1})
        self.assertAlmostEqual(new_data["magic_exp"], 5.5)
        self.assertEqual(new_data["constitution_exp"], 0.0)

    def test_enemy_class_protection_blocks_the_matching_player_style(self):
        enemy = {
            "warded_dummy": {
                "display_name": "Warded dummy",
                "level": 1,
                "group": "Test",
                "stats": {
                    "attack": 1,
                    "strength": 1,
                    "defence": 1,
                    "hitpoints": 10_000,
                },
                "bonuses": {},
                "attack_speed": 4,
                "drops": {"guaranteed": (), "tables": ()},
                "source": "test",
            }
        }
        player = _player(current_combat_target="warded_dummy")
        _control, control_ok, control = apply_combat_burst_pure(
            player, enemy, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0, 0.999999, 0.999999])
        )
        enemy["warded_dummy"]["protect_from_player_class"] = "melee"
        _blocked, blocked_ok, blocked = apply_combat_burst_pure(
            player, enemy, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0, 0.999999, 0.999999])
        )
        self.assertTrue(control_ok)
        self.assertTrue(blocked_ok)
        self.assertGreater(control["player_damage"], 0)
        self.assertEqual(blocked["player_damage"], 0)

    def test_active_magic_encounter_does_not_refill_runes_mid_fight(self):
        player = _player(
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff"},
            inventory={"Air rune": 5, "Mind rune": 5},
            combat_supply_loadout={"runes": {"Air rune": 1, "Mind rune": 1}},
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 30},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=10,
            rng=_rng([0.999999] * 8),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["stop_reason"], "out_of_runes")
        self.assertEqual(result["runes_used"], {"Air rune": 1, "Mind rune": 1})
        self.assertEqual(new_data["inventory"]["Air rune"], 5)
        self.assertEqual(new_data["inventory"]["Mind rune"], 5)
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {})

    def test_vengeance_pending_carries_across_reviews_without_recasting_from_bank(self):
        enemy_data = {
            "vengeance_dummy": {
                "display_name": "Vengeance dummy",
                "level": 99,
                "group": "Test",
                "stats": {"attack": 99, "strength": 20, "defence": 99, "hitpoints": 1000},
                "bonuses": {},
                "attack_speed": 1,
                "drops": {"guaranteed": (), "tables": ()},
                "source": "test",
            }
        }
        player = _player(
            current_combat_target="vengeance_dummy",
            combat_attack_style="magic_standard",
            current_combat_spell="wind_strike",
            equipment={"weapon": "Staff of air"},
            combat_vengeance=True,
            combat_spellbook_swap="vengeance",
            quests={"lunar_diplomacy": {"completed": True}},
            inventory={"Astral rune": 40, "Earth rune": 100, "Death rune": 20},
            combat_supply_loadout={
                "runes": {
                    "Astral rune": 7,
                    "Earth rune": 10,
                    "Death rune": 2,
                    "Cosmic rune": 2,
                    "Law rune": 1,
                    "Mind rune": 2,
                },
            },
        )

        first, ok, first_result = apply_combat_burst_pure(
            player,
            enemy_data,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.9]),
        )
        self.assertTrue(ok)
        self.assertEqual(
            first_result["runes_used"],
            {
                "Astral rune": 7,
                "Cosmic rune": 2,
                "Law rune": 1,
                "Earth rune": 10,
                "Death rune": 2,
                "Mind rune": 1,
            },
        )
        self.assertTrue(first["combat_encounter"]["vengeance_pending"])
        self.assertEqual(first["inventory"], player["inventory"])

        second, ok, second_result = apply_combat_burst_pure(
            first,
            enemy_data,
            EQUIPMENT_DATA,
            ticks=2,
            rng=_rng([0.0, 0.9, 0.0, 0.9]),
        )
        self.assertTrue(ok)
        self.assertEqual(second_result["runes_used"], {"Mind rune": 1})
        self.assertGreater(second_result["player_damage"], 0)
        self.assertFalse(second["combat_encounter"]["vengeance_pending"])
        self.assertEqual(second["inventory"], player["inventory"])
        self.assertLess(second["magic_exp"] - first["magic_exp"], 112.0)

    def test_spellbook_swap_cost_is_paid_once_per_active_fight(self):
        enemy_data = {
            "swap_dummy": {
                "display_name": "Swap dummy",
                "level": 1,
                "group": "Test",
                "stats": {"attack": 1, "strength": 1, "defence": 99, "hitpoints": 1000},
                "bonuses": {},
                "attack_speed": 4,
                "drops": {"guaranteed": (), "tables": ()},
                "source": "test",
            }
        }
        player = _player(
            current_combat_target="swap_dummy",
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff of air"},
            current_combat_spell="fire_strike",
            combat_dream_thrift=True,
            combat_spellbook_swap="dream",
            quests={
                "dream_mentor": {"completed": True},
                "lunar_diplomacy": {"completed": True},
            },
            inventory={"Astral rune": 30, "Cosmic rune": 20, "Law rune": 10},
            combat_supply_loadout={
                "runes": {"Astral rune": 3, "Cosmic rune": 2, "Law rune": 1, "Fire rune": 6, "Mind rune": 2},
            },
        )

        first, ok, first_result = apply_combat_burst_pure(
            player,
            enemy_data,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.9]),
        )
        self.assertTrue(ok)
        self.assertEqual(first_result["runes_used"]["Astral rune"], 3)
        self.assertTrue(first["combat_encounter"]["spellbook_swap_paid"])

        second, ok, second_result = apply_combat_burst_pure(
            first,
            enemy_data,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.9]),
        )
        self.assertTrue(ok)
        self.assertNotIn("Astral rune", second_result["runes_used"])
        self.assertEqual(second["inventory"], player["inventory"])
        self.assertGreaterEqual(first_result["xp_rewards"]["magic_exp"], 130.0)
        self.assertLess(second_result["xp_rewards"]["magic_exp"], 130.0)

    def test_low_hitpoints_do_not_auto_select_locked_dream_and_stop_combat(self):
        player, changed, reason = set_combat_pack_mode_pure(
            _player(
                magic_level=1,
                constitution_level=10,
                combat_lifepoints=42,
                current_combat_target="chicken",
            ),
            "max_safety",
            EQUIPMENT_DATA,
        )
        self.assertTrue(changed, reason)

        _new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["reason"], "combat_burst")
        self.assertFalse(player["combat_dream_thrift"])

    def test_locked_dream_is_removed_from_target_overrides_and_pinned_presets(self):
        cases = (
            {
                "combat_target_overrides": {
                    "chicken": {"combat_dream_thrift": True}
                }
            },
            {
                "combat_presets": {
                    "Dream": {"combat_dream_thrift": True}
                },
                "combat_target_presets": {"chicken": "Dream"},
                "combat_active_preset": "Dream",
            },
        )

        for overrides in cases:
            with self.subTest(overrides=overrides):
                player = _player(
                    magic_level=1,
                    quests={"dream_mentor": {"completed": False}},
                    current_combat_target="chicken",
                    **overrides,
                )
                new_data, ok, result = apply_combat_burst_pure(
                    player,
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                    ticks=1,
                    rng=_rng([0.999999]),
                )

                self.assertTrue(ok, result)
                self.assertEqual(result["reason"], "combat_burst")
                self.assertFalse(new_data["combat_dream_thrift"])
                for values in new_data["combat_target_overrides"].values():
                    self.assertFalse(values.get("combat_dream_thrift", False))
                for preset in new_data["combat_presets"].values():
                    self.assertFalse(preset.get("combat_dream_thrift", False))

    def test_dream_does_not_interrupt_an_active_fight(self):
        player = _player(
            combat_lifepoints=50,
            combat_dream_thrift=True,
            quests={"dream_mentor": {"completed": True}},
            inventory={"Astral rune": 2, "Cosmic rune": 1, "Body rune": 5},
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 30},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["reason"], "combat_burst")
        self.assertEqual(new_data["inventory"], player["inventory"])
        self.assertEqual(new_data["magic_exp"], 0.0)

    def test_vengeance_reflection_kill_counts_and_drops_normally(self):
        enemy_data = {
            "vengeance_target": {
                "display_name": "Vengeance target",
                "level": 99,
                "group": "Test",
                "stats": {"attack": 99, "strength": 20, "defence": 99, "hitpoints": 1000},
                "bonuses": {},
                "attack_speed": 1,
                "drops": {"guaranteed": (("Feather", 1),), "tables": ()},
                "source": "test",
            }
        }
        player = _player(
            current_combat_target="vengeance_target",
            combat_attack_style="magic_standard",
            current_combat_spell="wind_strike",
            equipment={"weapon": "Staff of air"},
            combat_auto_flee=False,
            combat_vengeance=True,
            combat_spellbook_swap="vengeance",
            quests={"lunar_diplomacy": {"completed": True}},
            combat_supply_loadout={"runes": {"Mind rune": 1}},
            combat_encounter={
                "target_id": "vengeance_target",
                "enemy_lifepoints": 5,
                "spellbook_swap_paid": True,
                "vengeance_pending": True,
            },
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            enemy_data,
            EQUIPMENT_DATA,
            ticks=2,
            rng=_rng([0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(result["kills"], 1)
        self.assertEqual(result["drops"], {"Feather": 1})
        self.assertEqual(new_data["combat_kill_counts"], {"vengeance_target": 1})

    def test_active_ranged_encounter_does_not_refill_ammo_mid_fight(self):
        player = _player(
            combat_attack_style="ranged_rapid",
            equipment={"weapon": "Shortbow"},
            inventory={"Bronze arrows": 5},
            combat_supply_loadout={"ammo": {"Bronze arrows": 1}},
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 30},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=10,
            rng=_rng([0.999999] * 8),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["stop_reason"], "out_of_ammo")
        self.assertEqual(result["ammo_used"], {"Bronze arrows": 1})
        self.assertEqual(new_data["inventory"]["Bronze arrows"], 5)
        self.assertEqual(new_data["combat_supply_loadout"]["ammo"], {})

    def test_ranged_rapid_uses_faster_bow_attack_speed(self):
        player = _player(
            combat_attack_style="ranged_rapid",
            equipment={"weapon": "Shortbow"},
            combat_supply_loadout={"ammo": {"Bronze arrows": 10}},
            current_combat_target="giant_rat",
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=7,
            rng=_rng([0.999999] * 12),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["ammo_used"], {"Bronze arrows": 3})
        self.assertEqual(new_data["combat_supply_loadout"]["ammo"], {"Bronze arrows": 7})

    def test_combat_burst_caps_to_one_kill_per_review_even_with_many_ticks(self):
        player = _player(current_combat_target="cow")

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1000,
            rng=_rng([0.0, 0.999999, 0.999999, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["combat_kill_counts"], {"cow": 1})

    def test_auto_eat_consumes_food_after_enemy_damage_under_threshold(self):
        player = _player(
            attack_level=1,
            strength_level=1,
            defense_level=1,
            combat_supply_loadout={"food": {"Shrimps": 1}},
            combat_lifepoints=20,
            combat_auto_eat_threshold_percent=90,
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["died"])
        self.assertEqual(new_data["combat_supply_loadout"]["food"], {})
        self.assertEqual(result["food_used"], ({"item": "Shrimps", "healed_by": 30},))
        self.assertGreater(new_data["combat_lifepoints"], 20)

    def test_tiger_shark_auto_eat_preserves_its_exact_overheal_cap(self):
        self.assertEqual(COMBAT_FOOD_DATA["Tiger shark"]["heal_lifepoints"], 250)
        self.assertEqual(
            COMBAT_FOOD_DATA["Tiger shark"]["max_overheal_lifepoints"],
            100,
        )
        player = _player(
            attack_level=1,
            strength_level=1,
            defense_level=1,
            combat_supply_loadout={"food": {"Tiger shark": 1}},
            combat_lifepoints=20,
            combat_auto_eat_threshold_percent=90,
            combat_auto_eat_food=["Tiger shark"],
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(new_data["combat_supply_loadout"]["food"], {})
        self.assertEqual(
            result["food_used"],
            ({"item": "Tiger shark", "healed_by": 250},),
        )
        self.assertEqual(new_data["combat_lifepoints"], 200)

    def test_active_encounter_starts_bank_run_for_banked_food_when_loadout_is_empty(self):
        player = _player(
            current_combat_target="giant_rat",
            attack_level=1,
            strength_level=1,
            defense_level=1,
            inventory={"Shrimps": 1},
            combat_lifepoints=20,
            combat_auto_eat_threshold_percent=90,
            combat_encounter={"target_id": "giant_rat", "enemy_lifepoints": 50},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(new_data["inventory"]["Shrimps"], 1)
        self.assertEqual(new_data["combat_supply_loadout"]["food"], {})
        self.assertEqual(new_data["combat_bank_run"], {"reviews_remaining": 1, "target_id": "giant_rat"})
        self.assertEqual(result["stop_reason"], "bank_run")
        self.assertEqual(result["food_used"], ())
        self.assertEqual(new_data["combat_lifepoints"], 20)

    def test_combat_burst_checks_locked_target_before_starting_bank_run(self):
        enemy_data = {
            "statless": {
                "display_name": "Statless",
                "level": 1,
                "stats": {},
                "drops": {"guaranteed": (), "tables": ()},
            }
        }
        player = _player(
            current_combat_target="statless",
            inventory={"Shrimps": 5},
            combat_auto_eat_food=["Shrimps"],
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            enemy_data,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.0]),
        )

        self.assertFalse(ok)
        self.assertIs(new_data, player)
        self.assertEqual(result["reason"], "combat_locked")
        self.assertEqual(result["locked_reasons"], ("missing source combat stats",))
        self.assertNotIn("combat_bank_run", new_data)

    def test_combat_bank_run_uses_supplied_enemy_data_for_antipoison(self):
        enemy_data = {
            "poison_dummy": {
                "display_name": "Poison dummy",
                "level": 1,
                "stats": {"attack": 1, "strength": 1, "defence": 1, "hitpoints": 100},
                "bonuses": {},
                "attack_speed": 4,
                "drops": {"guaranteed": (), "tables": ()},
                "poison_damage": 3,
            }
        }
        player = _player(
            current_combat_target="poison_dummy",
            inventory={"Antipoison (1)": 1},
            combat_auto_eat_food=[],
            combat_supply_loadout={},
        )

        traveling, ok, result = apply_combat_burst_pure(
            player,
            enemy_data,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.0]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["reason"], "combat_bank_run")
        self.assertEqual(traveling["combat_bank_run"], {"reviews_remaining": 1, "target_id": "poison_dummy"})
        self.assertEqual(traveling["inventory"]["Antipoison (1)"], 1)
        self.assertEqual(traveling["combat_supply_loadout"]["potions"], {})

        refilled, ok, result = apply_combat_burst_pure(
            traveling,
            enemy_data,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["bank_run_completed"])
        self.assertEqual(refilled["combat_bank_run"], {})
        self.assertEqual(refilled["inventory"]["Antipoison (1)"], 0)
        self.assertEqual(refilled["combat_supply_loadout"]["potions"], {"Antipoison (1)": 1})

    def test_combat_burst_regenerates_special_attack_energy_by_elapsed_ticks(self):
        player = _player(combat_special_attack_energy=40)

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng([0.999999] * 30),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["ticks_elapsed"], 50)
        self.assertEqual(new_data["combat_special_attack_energy"], 50)

    def test_poison_status_uses_source_tick_formula_and_summary(self):
        player = _player()

        poisoned, ok, reason = apply_combat_poison_effect_pure(player, 3)

        self.assertTrue(ok, reason)
        self.assertEqual(combat_poison_ticks_for_initial_damage_pure(3), 11)
        self.assertEqual(combat_poison_damage_for_ticks_pure(11), 30)
        self.assertEqual(
            poisoned["combat_status_effects"]["poison"],
            {
                "ticks_left": 11,
                "tick_progress": 0,
                "source": "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/poison/Poison.kt",
            },
        )
        self.assertEqual(combat_status_summary_pure(poisoned), "Poisoned: 30 LP in 30 ticks")

    def test_safe_recovery_advances_poison_status_after_healing(self):
        player = _player(
            combat_lifepoints=40,
            combat_status_effects={
                "poison": {
                    "ticks_left": combat_poison_ticks_for_initial_damage_pure(3),
                    "tick_progress": 0,
                }
            },
        )

        recovered = apply_safe_combat_recovery_pure(player)

        # Leave-combat rest heals a third of the missing 60 LP (40 -> 60), then the
        # poison tick subtracts 30 -> 30.
        self.assertEqual(recovered["combat_lifepoints"], 30)
        self.assertEqual(recovered["combat_status_effects"]["poison"]["ticks_left"], 10)
        self.assertEqual(recovered["combat_status_effects"]["poison"]["tick_progress"], 20)
        self.assertEqual(combat_status_summary_pure(recovered), "Poisoned: 30 LP in 10 ticks")

    def test_combat_burst_advances_poison_status_by_review_ticks(self):
        player = _player(
            combat_lifepoints=100,
            combat_status_effects={
                "poison": {
                    "ticks_left": combat_poison_ticks_for_initial_damage_pure(3),
                    "tick_progress": 29,
                }
            },
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["died"])
        self.assertEqual(result["status_damage"], {"poison": 30})
        self.assertEqual(new_data["combat_lifepoints"], 70)
        self.assertEqual(new_data["combat_status_effects"]["poison"]["ticks_left"], 10)
        self.assertEqual(new_data["combat_status_effects"]["poison"]["tick_progress"], 0)

    def test_antipoison_loadout_auto_cures_poison_before_safe_recovery_tick(self):
        player = _player(
            combat_lifepoints=50,
            combat_supply_loadout={"potions": {"Antipoison (2)": 1}},
            combat_status_effects={
                "poison": {
                    "ticks_left": combat_poison_ticks_for_initial_damage_pure(3),
                    "tick_progress": 29,
                }
            },
        )

        recovered = apply_safe_combat_recovery_pure(player)

        # Antipoison cures before the tick, so no poison damage; the leave-combat
        # rest heals a third of the missing 50 LP (50 -> 67).
        self.assertEqual(recovered["combat_lifepoints"], 67)
        self.assertNotIn("poison", recovered["combat_status_effects"])
        self.assertEqual(recovered["combat_status_effects"]["poison_immunity"]["ticks_left"], 1450)
        self.assertIn("PotionType.kt", recovered["combat_status_effects"]["poison_immunity"]["source"])
        self.assertEqual(recovered["combat_supply_loadout"]["potions"], {"Antipoison (1)": 1})
        self.assertEqual(combat_poison_immunity_ticks_pure(recovered), 1450)
        self.assertEqual(combat_status_summary_pure(recovered), "Poison immune: 1450 ticks")

    def test_poison_enemy_applies_player_poison_on_source_chance(self):
        player = _player(
            current_combat_target="poison_scorpion",
            defense_level=1,
            combat_lifepoints=100,
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.999999, 0.0, 0.0, 0.0]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["died"])
        self.assertEqual(result["status_applied"], {"poison": 30})
        self.assertEqual(result["status_damage"], {})
        self.assertEqual(new_data["combat_status_effects"]["poison"]["ticks_left"], 11)
        self.assertEqual(new_data["combat_status_effects"]["poison"]["tick_progress"], 0)
        self.assertEqual(combat_status_summary_pure(new_data), "Poisoned: 30 LP in 30 ticks")

    def test_source_poison_rows_reach_combat_state(self):
        cases = (
            ("cave_slime", 100, 30, 11, "poisonDamage=3"),
            ("cave_crawler", 200, 80, 36, "poisonDamage=8"),
        )
        for target_id, lifepoints, initial_damage, ticks_left, source_marker in cases:
            with self.subTest(target=target_id):
                player = _player(
                    current_combat_target=target_id,
                    defense_level=1,
                    combat_lifepoints=lifepoints,
                )

                new_data, ok, result = apply_combat_burst_pure(
                    player,
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                    ticks=5,
                    rng=_rng([0.999999, 0.999999, 0.0, 0.0, 0.0]),
                )

                self.assertTrue(ok)
                self.assertFalse(result["died"])
                self.assertEqual(result["status_applied"], {"poison": initial_damage})
                self.assertEqual(
                    new_data["combat_status_effects"]["poison"]["ticks_left"],
                    ticks_left,
                )
                self.assertIn(source_marker, COMBAT_ENEMY_DATA[target_id]["source"])

    def test_poison_enemy_antipoison_loadout_auto_cures_after_source_poison(self):
        player = _player(
            current_combat_target="poison_scorpion",
            defense_level=1,
            combat_lifepoints=100,
            combat_supply_loadout={"potions": {"Antipoison (1)": 1}},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.999999, 0.0, 0.0, 0.0]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["died"])
        self.assertEqual(result["status_applied"], {"poison": 30})
        self.assertEqual(
            result["potions_used"],
            (
                {
                    "item": "Antipoison (1)",
                    "replacement": "Vial",
                    "effect": "poison_cure",
                    "immunity_ticks": 1500,
                },
            ),
        )
        self.assertNotIn("poison", new_data["combat_status_effects"])
        self.assertEqual(new_data["combat_status_effects"]["poison_immunity"]["ticks_left"], 1500)
        self.assertEqual(new_data["inventory"]["Vial"], 1)
        self.assertEqual(new_data["combat_supply_loadout"]["potions"], {})

    def test_poison_immunity_blocks_enemy_poison_without_spending_antipoison(self):
        player = _player(
            current_combat_target="poison_scorpion",
            defense_level=1,
            combat_lifepoints=100,
            combat_supply_loadout={"potions": {"Antipoison (1)": 1}},
            combat_status_effects={"poison_immunity": {"ticks_left": 100}},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.999999, 0.0, 0.0, 0.0]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["status_applied"], {})
        self.assertEqual(result["potions_used"], ())
        self.assertEqual(new_data["combat_status_effects"]["poison_immunity"]["ticks_left"], 95)
        self.assertEqual(new_data["combat_supply_loadout"]["potions"], {"Antipoison (1)": 1})

    def test_safe_recovery_poison_death_uses_combat_grave_path(self):
        player = _player(
            combat_lifepoints=5,
            equipment={"weapon": "Iron sword"},
            combat_status_effects={
                "poison": {
                    "ticks_left": combat_poison_ticks_for_initial_damage_pure(11),
                    "tick_progress": 0,
                }
            },
        )

        recovered = apply_safe_combat_recovery_pure(player)

        self.assertEqual(recovered["combat_lifepoints"], 100)
        self.assertEqual(recovered["equipment"], {})
        self.assertEqual(recovered["combat_status_effects"], {})
        self.assertEqual(recovered["combat_grave"]["items"], ["Iron sword"])
        self.assertEqual(recovered["combat_grave"]["source"], "combat_poison_death")

    def test_safe_recovery_refills_loadout_regenerates_energy_and_recovers_drains(self):
        player = _player(
            inventory={"Shark": 30},
            combat_lifepoints=20,
            combat_special_attack_energy=35,
            combat_current_levels={"attack": 97, "strength": 98},  # base 99, drained
            combat_recovery_progress={"stat_drain_ticks": 50},
            combat_auto_eat_food=["Shark"],
            combat_pack_mode="max_safety",  # fill the 28-slot budget with food
        )

        recovered = apply_safe_combat_recovery_pure(player)

        # Leave-combat rest heals a third of the missing 80 LP (20 -> 47).
        self.assertEqual(recovered["combat_lifepoints"], 47)
        self.assertEqual(recovered["combat_special_attack_energy"], 45)
        # One recovery step (100 ticks): each current moves 1 toward base 99;
        # strength reaches base and drops, attack goes 97 -> 98.
        self.assertEqual(recovered["combat_current_levels"], {"attack": 98})
        self.assertEqual(recovered["combat_recovery_progress"], {})
        self.assertEqual(recovered["combat_supply_loadout"]["food"], {})
        self.assertEqual(recovered["inventory"]["Shark"], 30)
        self.assertEqual(recovered["combat_bank_run"], {"reviews_remaining": 1, "target_id": "chicken"})

        refilled = apply_safe_combat_recovery_pure(recovered)

        # max_safety caps food at 20 slots (rest of the 28 is potion/loot room);
        # 10 Shark stay banked.
        self.assertEqual(refilled["combat_supply_loadout"]["food"], {"Shark": 20})
        self.assertEqual(refilled["inventory"]["Shark"], 10)
        self.assertEqual(refilled["combat_bank_run"], {})

    def test_safe_recovery_resets_mismatched_bank_run_before_refill(self):
        player = _player(
            inventory={"Shark": 5},
            combat_auto_eat_food=["Shark"],
            combat_supply_loadout={},
            combat_bank_run={"reviews_remaining": 1, "target_id": "giant_rat"},
        )

        recovered = apply_safe_combat_recovery_pure(player)

        self.assertEqual(recovered["combat_bank_run"], {"reviews_remaining": 1, "target_id": "chicken"})
        self.assertEqual(recovered["combat_supply_loadout"]["food"], {})
        self.assertEqual(recovered["inventory"]["Shark"], 5)

    def test_safe_recovery_refills_ranged_ammo_at_safe_boundary(self):
        player = _player(
            combat_attack_style="ranged_accurate",
            equipment={"weapon": "Shortbow"},
            inventory={"Bronze arrows": 12},
            combat_supply_loadout={"ammo": {"Bronze arrows": 3}},
        )

        recovered = apply_safe_combat_recovery_pure(player)

        self.assertEqual(recovered["combat_supply_loadout"]["ammo"], {"Bronze arrows": 3})
        self.assertEqual(recovered["inventory"]["Bronze arrows"], 12)
        self.assertEqual(recovered["combat_bank_run"], {})

    def test_safe_recovery_ranged_bank_run_completes_ammo_refill(self):
        player = _player(
            combat_attack_style="accurate",
            equipment={"weapon": "Shortbow"},
            inventory={"Bronze arrows": 12},
            combat_auto_eat_food=[],
            combat_supply_loadout={},
        )

        traveling = apply_safe_combat_recovery_pure(player, EQUIPMENT_DATA)
        refilled = apply_safe_combat_recovery_pure(traveling, EQUIPMENT_DATA)

        self.assertEqual(traveling["combat_bank_run"], {"reviews_remaining": 1, "target_id": "chicken"})
        self.assertEqual(traveling["combat_supply_loadout"]["ammo"], {})
        self.assertEqual(refilled["combat_bank_run"], {})
        self.assertEqual(refilled["combat_supply_loadout"]["ammo"], {"Bronze arrows": 12})
        self.assertEqual(refilled["inventory"]["Bronze arrows"], 0)

    def test_safe_recovery_magic_bank_run_completes_uncovered_rune_refill(self):
        player = _player(
            combat_attack_style="accurate",
            current_combat_spell="fire_strike",
            magic_level=13,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 2, "Mind rune": 2, "Fire rune": 3},
            combat_auto_eat_food=[],
            combat_supply_loadout={},
        )

        traveling = apply_safe_combat_recovery_pure(player, EQUIPMENT_DATA)
        refilled = apply_safe_combat_recovery_pure(traveling, EQUIPMENT_DATA)

        self.assertEqual(traveling["combat_bank_run"], {"reviews_remaining": 1, "target_id": "chicken"})
        self.assertEqual(refilled["combat_bank_run"], {})
        self.assertEqual(refilled["combat_supply_loadout"]["runes"], {"Air rune": 2, "Mind rune": 2})
        self.assertEqual(refilled["inventory"]["Air rune"], 0)
        self.assertEqual(refilled["inventory"]["Mind rune"], 0)
        self.assertEqual(refilled["inventory"]["Fire rune"], 3)

    def test_stacked_combat_death_moves_existing_grave_to_death_office(self):
        player = _player(
            current_combat_target="killer",
            attack_level=1,
            strength_level=1,
            combat_lifepoints=1,
            combat_auto_flee=False,  # exercise the death path, not the auto-flee bail-out
            equipment={"weapon": "Iron sword"},
            combat_grave={"items": ["Bronze sword"], "reviews_remaining": 3, "source": "combat_death"},
            death_office={"items": ["Cape"], "source": "combat_stacked_grave"},
        )

        died, ok, result = apply_combat_burst_pure(
            player,
            _KILLER_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["died"])
        self.assertEqual(died["combat_grave"]["items"], ["Iron sword"])
        self.assertEqual(died["combat_grave"]["reviews_remaining"], 5)
        self.assertEqual(died["death_office"]["items"], ["Cape", "Bronze sword"])
        self.assertEqual(died["death_office"]["reclaim_cost"], 200)

    def test_combat_ticks_degrade_only_the_equipped_condition_instance(self):
        enemy_data = {
            "training_dummy": {
                "display_name": "Training dummy",
                "level": 1,
                "group": "Test",
                "stats": {
                    "attack": 1,
                    "strength": 1,
                    "defence": 999,
                    "hitpoints": 100_000,
                },
                "bonuses": {},
                "attack_speed": 4,
                "drops": {"guaranteed": (), "tables": ()},
                "source": "test",
            }
        }
        player = _player(
            current_combat_target="training_dummy",
            equipment={"head": "Combat hood 100"},
            equipment_instances={
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 72_001,
                    "location": "equipped:head",
                    "last_slot": "head",
                }
            },
            equipment_instance_next_id=2,
            combat_auto_eat_food=[],
        )

        updated, ok, result = apply_combat_burst_pure(
            player,
            enemy_data,
            EQUIPMENT_DATA,
            ticks=6,
            rng=lambda: 0.999999,
            live_cadence=True,
        )

        self.assertTrue(ok)
        self.assertEqual(result["ticks_elapsed"], 6)
        self.assertEqual(updated["equipment"]["head"], "Combat hood 80")
        self.assertEqual(updated["equipment_instances"]["equipment-1"]["condition"], 71_995)
        self.assertEqual(result["equipment_condition_events"][0]["after_name"], "Combat hood 80")

    def test_unsafe_death_discharges_gauntlets_and_grave_reclaim_keeps_instance(self):
        player = _player(
            equipment={"hands": "Bronze gauntlets"},
            equipment_instances={
                "equipment-1": {
                    "family_id": "bronze_gauntlets",
                    "item_name": "Bronze gauntlets",
                    "condition": 1,
                    "location": "equipped:hands",
                    "last_slot": "hands",
                }
            },
            equipment_instance_next_id=2,
        )

        _combat_apply_pvm_death(player, 100)

        self.assertEqual(player["combat_grave"]["items"], ["Worn-out bronze gauntlets"])
        self.assertEqual(
            player["equipment_instances"]["equipment-1"]["location"], "grave"
        )
        self.assertEqual(player["equipment_instances"]["equipment-1"]["condition"], 0)
        recovered, ok = start_combat_grave_walk_pure(player)
        self.assertTrue(ok)
        recovered = advance_combat_grave_review_pure(recovered)
        self.assertEqual(recovered["equipment"], {"hands": "Worn-out bronze gauntlets"})
        self.assertEqual(
            recovered["equipment_instances"]["equipment-1"]["location"],
            "equipped:hands",
        )

    def test_combat_death_drops_only_the_fought_targets_loot_not_dormant_packs(self):
        # Only the trip you are ON is in hand. `carried_inventory` also holds a saved
        # pack per skilling target; those are loadouts resting in the bank. Draining
        # them on a combat death dropped materials from skills the player was not
        # doing, and staged more than 28 slots of items — more than one inventory
        # can physically hold.
        player = _player(
            current_combat_target="killer",
            attack_level=1,
            strength_level=1,
            combat_lifepoints=1,
            combat_auto_flee=False,  # exercise the death path, not the auto-flee bail-out
            equipment={"weapon": "Iron sword"},
            inventory={"Bones": 10, "Coal": 30, "Coins": 100},
            carried_inventory={
                "killer": {"Bones": 3},        # loot from THIS fight -> at risk
                "copper_ore": {"Coal": 28},    # dormant Mining pack -> must survive
            },
            carried_churn={"copper_ore": 28},
            skilling_bank_run={"reviews_remaining": 1, "target_id": "copper_ore"},
        )

        died, ok, result = apply_combat_burst_pure(
            player,
            _KILLER_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["died"])
        # This fight's loot joins the equipment in the grave, one entry per unit.
        self.assertEqual(died["combat_grave"]["items"].count("Bones"), 3)
        self.assertIn("Iron sword", died["combat_grave"]["items"])
        # Looted bones are a view over the flat store, so they leave the bank.
        self.assertEqual(died["inventory"]["Bones"], 7)
        # The dormant Mining pack is untouched: coal stays banked, pack survives.
        self.assertEqual(died["inventory"]["Coal"], 30)
        self.assertEqual(died["carried_inventory"], {"copper_ore": {"Coal": 28}})
        self.assertEqual(died["carried_churn"], {"copper_ore": 28})
        self.assertEqual(died["skilling_bank_run"], {"reviews_remaining": 1, "target_id": "copper_ore"})
        # Coins (the money pouch) are never carried.
        self.assertEqual(died["inventory"]["Coins"], 100)

    def test_auto_flee_bails_out_when_low_lp_and_out_of_food(self):
        player = _player(
            current_combat_target="killer",
            combat_lifepoints=1,
            equipment={"weapon": "Iron sword"},
            combat_supply_loadout={},  # no food to auto-eat
        )

        fled, ok, result = apply_combat_burst_pure(
            player, _KILLER_ENEMY_DATA, EQUIPMENT_DATA, ticks=5, rng=lambda: 0.0,
        )

        self.assertTrue(ok)
        self.assertTrue(result["fled"])
        self.assertFalse(result["died"])
        self.assertEqual(result["stop_reason"], "auto_flee")
        # Fleeing keeps the gear on and clears the encounter — no grave, no death.
        self.assertEqual(fled["equipment"], {"weapon": "Iron sword"})
        self.assertEqual(fled["combat_grave"], {})
        self.assertEqual(fled["combat_encounter"], {})

    def test_void_shifter_escapes_after_nonlethal_damage_below_ten_percent(self):
        player = _player(
            current_combat_target="killer",
            combat_lifepoints=20,
            combat_auto_flee=False,
            combat_auto_eat_food=[],
            combat_supply_loadout={},
            summoning_state={
                "active_follower": {
                    "kind": "familiar",
                    "entity_id": "voidshifter",
                }
            },
        )

        escaped, ok, result = apply_combat_burst_pure(
            player,
            _KILLER_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.0, 0.1]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["fled"])
        self.assertTrue(result["familiar_escape"])
        self.assertFalse(result["died"])
        self.assertEqual(result["stop_reason"], "void_shifter")
        self.assertEqual(escaped["combat_encounter"], {})
        self.assertEqual(
            escaped["summoning_state"]["active_follower"]["entity_id"],
            "voidshifter",
        )

    def test_void_shifter_does_not_prevent_lethal_damage(self):
        player = _player(
            current_combat_target="killer",
            combat_lifepoints=1,
            combat_auto_flee=False,
            combat_auto_eat_food=[],
            combat_supply_loadout={},
            summoning_state={
                "active_follower": {
                    "kind": "familiar",
                    "entity_id": "voidshifter",
                }
            },
        )

        died, ok, result = apply_combat_burst_pure(
            player,
            _KILLER_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["died"])
        self.assertFalse(result["familiar_escape"])
        self.assertEqual(died["summoning_state"]["active_follower"], {})

    def test_combat_burst_resets_the_leave_combat_rest_window(self):
        player = _player(combat_rest_reviews=5)

        new_data, ok, _result = apply_combat_burst_pure(
            player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=lambda: 0.5,
        )

        self.assertTrue(ok)
        self.assertEqual(new_data["combat_rest_reviews"], 0)

    def test_leave_combat_rest_heals_to_full_over_three_reviews(self):
        player = _player(combat_lifepoints=10, combat_auto_eat_food=[], combat_supply_loadout={})

        first = apply_safe_combat_recovery_pure(player)
        second = apply_safe_combat_recovery_pure(first)
        third = apply_safe_combat_recovery_pure(second)

        self.assertEqual(first["combat_lifepoints"], 40)   # 10 + ceil(90/3)
        self.assertEqual(second["combat_lifepoints"], 70)  # 40 + ceil(60/2)
        self.assertEqual(third["combat_lifepoints"], 100)  # 70 + ceil(30/1) -> full
        self.assertEqual(third["combat_rest_reviews"], 3)

    def test_death_grave_snapshots_worn_loadout_and_reclaim_reequips_it(self):
        player = _player(
            current_combat_target="killer",
            attack_level=1,
            strength_level=1,
            combat_lifepoints=1,
            combat_auto_flee=False,
            equipment={"weapon": "Iron sword"},
            combat_auto_eat_food=[],
            combat_supply_loadout={},
        )

        died, ok, result = apply_combat_burst_pure(
            player,
            _KILLER_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["died"])
        self.assertEqual(died["combat_grave"]["loadout"], {"weapon": "Iron sword"})
        self.assertEqual(died["equipment"], {})

        # Grave auto-reclaims after COMBAT_GRAVE_RECOVERY_REVIEWS answered cards,
        # and the worn loadout re-equips into the empty slot instead of the bank.
        recovered, ok = start_combat_grave_walk_pure(died)
        self.assertTrue(ok)
        recovered = advance_combat_grave_review_pure(recovered)

        self.assertEqual(recovered["combat_grave"], {})
        self.assertEqual(recovered["equipment"], {"weapon": "Iron sword"})
        self.assertNotIn("Iron sword", recovered.get("inventory", {}))

    def test_death_office_reclaim_reequips_worn_loadout_into_empty_slots(self):
        player = _player(
            inventory={"Coins": 500},
            equipment={},
            death_office={
                "items": ["Iron sword", "Bones", "Bones"],
                "source": "combat_stacked_grave",
                "loadout": {"weapon": "Iron sword"},
            },
        )

        reclaimed, ok, reason = reclaim_death_office_items_pure(player)

        self.assertTrue(ok, reason)
        self.assertEqual(reclaimed["equipment"], {"weapon": "Iron sword"})
        self.assertEqual(reclaimed["inventory"]["Bones"], 2)
        self.assertNotIn("Iron sword", reclaimed["inventory"])
        self.assertEqual(reclaimed["death_office"], {})

    def test_legacy_mining_helmet_reclaims_as_the_exact_equipment_state(self):
        migrated = migrate_loaded_data(
            {
                "inventory": {"Coins": 100},
                "equipment": {},
                "death_office": {
                    "items": ["Mining helmet"],
                    "source": "combat_stacked_grave",
                    "loadout": {"head": "Mining helmet"},
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        reclaimed, ok, reason = reclaim_death_office_items_pure(migrated)

        self.assertTrue(ok, reason)
        self.assertEqual(reclaimed["equipment"], {"head": "Mining helmet (unlit)"})
        self.assertNotIn("Mining helmet", reclaimed["inventory"])
        self.assertEqual(reclaimed["death_office"], {})

    def test_reclaim_leaves_graved_piece_in_bank_when_slot_already_refilled(self):
        player = _player(
            inventory={"Coins": 500},
            equipment={"weapon": "Rune sword"},  # already re-geared since dying
            death_office={
                "items": ["Iron sword"],
                "source": "combat_stacked_grave",
                "loadout": {"weapon": "Iron sword"},
            },
        )

        reclaimed, ok, reason = reclaim_death_office_items_pure(player)

        self.assertTrue(ok, reason)
        self.assertEqual(reclaimed["equipment"], {"weapon": "Rune sword"})
        self.assertEqual(reclaimed["inventory"]["Iron sword"], 1)

    def test_death_office_reclaim_consumes_coins_and_returns_items_to_inventory(self):
        player = _player(
            inventory={"Coins": 250, "Bones": 1},
            death_office={"items": ["Bronze sword", "Cape"], "source": "combat_stacked_grave"},
        )

        self.assertEqual(combat_death_office_reclaim_cost_pure(player), 200)
        self.assertEqual(
            combat_death_office_summary_pure(player),
            {
                "items": ("Bronze sword", "Cape"),
                "item_count": 2,
                "reclaim_cost": 200,
                "coins": 250,
                "can_reclaim": True,
            },
        )

        reclaimed, ok, reason = reclaim_death_office_items_pure(player)

        self.assertTrue(ok, reason)
        self.assertEqual(reclaimed["inventory"]["Coins"], 50)
        self.assertEqual(reclaimed["inventory"]["Bones"], 1)
        self.assertEqual(reclaimed["inventory"]["Bronze sword"], 1)
        self.assertEqual(reclaimed["inventory"]["Cape"], 1)
        self.assertEqual(reclaimed["death_office"], {})

    def test_death_office_reclaim_requires_enough_coins(self):
        player = _player(
            inventory={"Coins": 99},
            death_office={"items": ["Bronze sword"], "source": "combat_stacked_grave"},
        )

        reclaimed, ok, reason = reclaim_death_office_items_pure(player)

        self.assertFalse(ok)
        self.assertIn("Need 100 Coins", reason)
        self.assertIs(reclaimed, player)
        self.assertEqual(player["inventory"], {"Coins": 99})

    def test_manual_refill_loadout_uses_food_queue_and_current_magic_spell(self):
        player = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_strike",
            equipment={"weapon": "Staff of fire"},
            inventory={"Shark": 30, "Antipoison (2)": 1, "Air rune": 5, "Mind rune": 5, "Fire rune": 5},
            combat_auto_eat_food=["Shark"],
            combat_pack_mode="max_safety",  # fill the 28-slot budget with food
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(player, EQUIPMENT_DATA)

        self.assertTrue(ok, reason)
        self.assertEqual(refilled["combat_supply_loadout"]["food"], {"Shark": 20})
        self.assertEqual(refilled["combat_supply_loadout"]["potions"], {"Antipoison (2)": 1})
        self.assertEqual(refilled["combat_supply_loadout"]["runes"], {"Air rune": 5, "Mind rune": 5})
        self.assertEqual(refilled["inventory"]["Shark"], 10)  # max_safety caps food at 20; 10 stay banked
        self.assertEqual(refilled["inventory"]["Antipoison (2)"], 0)
        self.assertEqual(refilled["inventory"]["Air rune"], 0)
        self.assertEqual(refilled["inventory"]["Mind rune"], 0)
        self.assertEqual(refilled["inventory"]["Fire rune"], 5)

    def test_manual_refill_loadout_excludes_melee_vengeance_runes(self):
        runes = {"Astral rune": 8, "Earth rune": 20, "Death rune": 4}
        player = _player(
            combat_pack_mode="max_output",
            combat_vengeance=True,
            quests={"lunar_diplomacy": {"completed": True}},
            inventory=runes,
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(player, EQUIPMENT_DATA)

        self.assertTrue(ok, reason)
        self.assertEqual(refilled["combat_supply_loadout"]["runes"], {})
        self.assertEqual(refilled["inventory"], runes)

    def test_fresh_melee_loadout_summary_has_no_runes(self):
        summary = combat_supply_loadout_summary_pure(_player(), EQUIPMENT_DATA)

        self.assertEqual(summary["runes_loaded"], {})

    def test_loadout_summary_hides_stale_melee_vengeance_runes(self):
        summary = combat_supply_loadout_summary_pure(
            _player(
                combat_vengeance=True,
                combat_supply_loadout={
                    "runes": {"Astral rune": 4, "Death rune": 2},
                },
            ),
            EQUIPMENT_DATA,
        )

        self.assertEqual(summary["runes_loaded"], {})

    def test_loadout_summary_shows_runes_for_a_magic_build(self):
        summary = combat_supply_loadout_summary_pure(
            _player(
                combat_attack_style="magic_standard",
                equipment={"weapon": "Staff of fire"},
                current_combat_spell="wind_strike",
                combat_supply_loadout={
                    "runes": {"Air rune": 5, "Mind rune": 5},
                },
            ),
            EQUIPMENT_DATA,
        )

        self.assertEqual(
            summary["runes_loaded"], {"Air rune": 5, "Mind rune": 5}
        )

    def test_loadout_summary_shows_ammo_for_a_ranged_build(self):
        summary = combat_supply_loadout_summary_pure(
            _player(
                combat_attack_style="ranged_accurate",
                equipment={"weapon": "Shortbow"},
                combat_supply_loadout={
                    "ammo": {"Bronze arrows": 10},
                },
            ),
            EQUIPMENT_DATA,
        )

        self.assertEqual(summary["ammo_loaded"], {"Bronze arrows": 10})

    def test_non_magic_vengeance_does_not_charge_or_arm_during_a_burst(self):
        cases = (
            ("melee", "accurate", {}, {}),
            (
                "ranged",
                "ranged_rapid",
                {"weapon": "Shortbow"},
                {"ammo": {"Bronze arrows": 1}},
            ),
        )
        for combat_class, style, equipment, loadout in cases:
            with self.subTest(combat_class=combat_class):
                player = _player(
                    combat_attack_style=style,
                    equipment=equipment,
                    combat_supply_loadout=loadout,
                    combat_pack_mode="max_output",
                    combat_vengeance=True,
                    quests={"lunar_diplomacy": {"completed": True}},
                )

                updated, ok, result = apply_combat_burst_pure(
                    player,
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                    ticks=1,
                    rng=_rng([0.999999]),
                )

                self.assertTrue(ok, result)
                self.assertEqual(result["reason"], "combat_burst")
                self.assertEqual(result["runes_used"], {})
                self.assertEqual(updated["magic_exp"], 0.0)
                self.assertFalse(
                    updated.get("combat_encounter", {}).get(
                        "vengeance_pending", False
                    )
                )

    def test_safe_recovery_repairs_a_stale_loadout_after_an_encounter_ends(self):
        recovered = apply_safe_combat_recovery_pure(
            _player(
                combat_encounter={},
                combat_supply_loadout={
                    "runes": {"Air rune": 5, "Mind rune": 5},
                },
            ),
            EQUIPMENT_DATA,
        )

        self.assertEqual(recovered["combat_supply_loadout"]["runes"], {})
        self.assertEqual(recovered["inventory"]["Air rune"], 5)
        self.assertEqual(recovered["inventory"]["Mind rune"], 5)

    def test_a_burst_kill_never_touches_the_bank_for_a_stale_loadout(self):
        # The burst engine is shared with 20 allow_bank_run=False instance
        # callers (Fight Caves, Barrows, Bork, ...), so it must never repair a
        # stale loadout itself: the runtime handler reconciles after the
        # encounter settles instead.
        player = _player(
            current_combat_target="chicken",
            combat_attack_style="accurate",
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 1},
            combat_supply_loadout={
                "runes": {"Air rune": 5, "Mind rune": 5},
            },
        )

        updated, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.0]),
            stop_after_first_kill=True,
            allow_bank_run=False,
        )

        self.assertTrue(ok, result)
        self.assertTrue(result["killed"])
        self.assertEqual(updated["combat_encounter"], {})
        self.assertEqual(
            updated["combat_supply_loadout"]["runes"],
            {"Air rune": 5, "Mind rune": 5},
        )
        self.assertNotIn("Air rune", updated["inventory"])
        self.assertNotIn("Mind rune", updated["inventory"])

    def test_combat_method_reconciliation_reloads_for_the_new_spell(self):
        player = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="wind_strike",
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 0, "Mind rune": 0, "Water rune": 7},
            combat_supply_loadout={
                "runes": {"Air rune": 5, "Mind rune": 5}
            },
        )

        updated, ok, reason = reconcile_combat_method_pure(
            player,
            {"current_combat_spell": "water_strike"},
            EQUIPMENT_DATA,
        )

        self.assertTrue(ok, reason)
        self.assertEqual(updated["current_combat_spell"], "water_strike")
        self.assertEqual(
            updated["combat_supply_loadout"]["runes"],
            {"Air rune": 5, "Mind rune": 5, "Water rune": 7},
        )
        self.assertEqual(
            updated["inventory"],
            {"Air rune": 0, "Mind rune": 0, "Water rune": 0},
        )

    def test_combat_method_reconciliation_rejects_a_live_encounter(self):
        player = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="wind_strike",
            equipment={"weapon": "Staff"},
            combat_supply_loadout={
                "runes": {"Air rune": 5, "Mind rune": 5}
            },
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 30},
        )

        updated, ok, reason = reconcile_combat_method_pure(
            player,
            {"current_combat_spell": "water_strike"},
            EQUIPMENT_DATA,
        )

        self.assertFalse(ok)
        self.assertEqual(reason, "Finish the active fight before changing combat method.")
        self.assertEqual(updated["current_combat_spell"], "wind_strike")
        self.assertEqual(
            updated["combat_supply_loadout"]["runes"],
            {"Air rune": 5, "Mind rune": 5},
        )

    def test_manual_refill_loadout_blocks_inside_active_encounter(self):
        player = _player(
            inventory={"Shark": 30},
            combat_auto_eat_food=["Shark"],
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 30},
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(player, EQUIPMENT_DATA)

        self.assertFalse(ok)
        self.assertIn("active fight", reason)
        self.assertEqual(refilled["inventory"]["Shark"], 30)
        self.assertEqual(refilled["combat_supply_loadout"], {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "finishers": {}, "hazards": {}, "cannonballs": 0})

    def test_manual_refill_loads_the_selected_targets_finisher(self):
        player = _player(
            current_combat_target="desert_lizard",
            inventory={
                "Ice cooler": 3,
                "Waterskin (4)": 2,
                "Waterskin (2)": 1,
            },
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(
            player, EQUIPMENT_DATA
        )

        self.assertTrue(ok, reason)
        self.assertEqual(
            refilled["combat_supply_loadout"]["finishers"],
            {"Ice cooler": 3},
        )
        self.assertEqual(
            refilled["combat_supply_loadout"]["hazards"],
            {"Waterskin (4)": 2, "Waterskin (2)": 1},
        )
        self.assertEqual(refilled["inventory"]["Ice cooler"], 0)

    def test_desert_hazard_pack_never_overfills_the_shared_inventory(self):
        from ankiscape.logic_pure.logic_pure import CARRIED_CAPACITY, _combat_supply_slots_used

        player = _player(
            current_combat_target="desert_lizard",
            combat_pack_mode="max_safety",
            combat_auto_eat_food=["Shark"],
            inventory={
                "Shark": 100,
                "Ice cooler": 10,
                "Waterskin (4)": 8,
            },
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(
            player, EQUIPMENT_DATA
        )

        self.assertTrue(ok, reason)
        self.assertEqual(
            _combat_supply_slots_used(refilled),
            CARRIED_CAPACITY,
        )
        self.assertEqual(
            refilled["combat_supply_loadout"]["hazards"],
            {"Waterskin (4)": 8},
        )
        self.assertEqual(
            refilled["combat_supply_loadout"]["finishers"],
            {"Ice cooler": 10},
        )
        self.assertEqual(
            refilled["combat_supply_loadout"]["food"],
            {"Shark": 19},
        )
        self.assertEqual(refilled["inventory"]["Shark"], 81)

    def test_refill_returns_the_previous_targets_context_supplies(self):
        player = _player(
            current_combat_target="chicken",
            combat_supply_loadout={
                "finishers": {"Ice cooler": 3},
                "hazards": {
                    "Waterskin (4)": 2,
                    "Waterskin (0)": 1,
                },
            },
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(
            player, EQUIPMENT_DATA
        )

        self.assertTrue(ok, reason)
        self.assertEqual(refilled["combat_supply_loadout"]["finishers"], {})
        self.assertEqual(refilled["combat_supply_loadout"]["hazards"], {})
        self.assertEqual(refilled["inventory"]["Ice cooler"], 3)
        self.assertEqual(refilled["inventory"]["Waterskin (4)"], 2)
        self.assertEqual(refilled["inventory"]["Waterskin (0)"], 1)

    def test_unload_combat_supply_loadout_returns_supplies_to_bank(self):
        player = _player(
            inventory={"Shark": 2},
            combat_supply_loadout={
                "food": {"Shark": 3},
                "potions": {"Antipoison (1)": 1},
                "ammo": {"Bronze arrows": 5},
                "runes": {"Air rune": 7},
                "finishers": {"Ice cooler": 2},
                "cannonballs": 2,
            },
        )

        unloaded, ok, reason = unload_combat_supply_loadout_pure(player)

        self.assertTrue(ok, reason)
        self.assertEqual(unloaded["inventory"]["Shark"], 5)
        self.assertEqual(unloaded["inventory"]["Antipoison (1)"], 1)
        self.assertEqual(unloaded["inventory"]["Bronze arrows"], 5)
        self.assertEqual(unloaded["inventory"]["Air rune"], 7)
        self.assertEqual(unloaded["inventory"]["Ice cooler"], 2)
        self.assertEqual(unloaded["inventory"]["Cannonball"], 2)
        self.assertEqual(unloaded["combat_supply_loadout"], {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "finishers": {}, "hazards": {}, "cannonballs": 0})

    def test_desert_lizard_manual_finisher_commits_one_atomic_kill(self):
        player = _player(
            current_combat_target="desert_lizard",
            combat_action="finisher",
            slayer_level=22,
            combat_encounter={
                "target_id": "desert_lizard",
                "enemy_lifepoints": 30,
            },
            combat_supply_loadout={"finishers": {"Ice cooler": 2}},
        )

        finished, ok, result = apply_combat_finisher_pure(
            player, COMBAT_ENEMY_DATA, rng=lambda: 0.999999
        )

        self.assertTrue(ok, result)
        self.assertEqual(result["kills"], 1)
        self.assertEqual(result["drops"], {"Bones": 1})
        self.assertEqual(result["finisher_item"], "Ice cooler")
        self.assertTrue(result["finisher_consumed"])
        self.assertEqual(
            finished["combat_supply_loadout"]["finishers"],
            {"Ice cooler": 1},
        )
        self.assertEqual(finished["combat_kill_counts"], {"desert_lizard": 1})
        self.assertEqual(
            finished["combat_observed_drops"]["desert_lizard"],
            {"Bones": {"times_seen": 1, "quantity_seen": 1}},
        )
        self.assertEqual(finished["inventory"]["Bones"], 1)
        self.assertEqual(finished["combat_encounter"], {})
        self.assertEqual(finished["combat_action"], "attack")
        self.assertNotIn(
            "Waterskin (4)",
            player["combat_supply_loadout"].get("hazards", {}),
        )

    def test_desert_lizard_manual_finisher_rejects_invalid_state_without_spending(self):
        cases = (
            (
                "above threshold",
                {"target_id": "desert_lizard", "enemy_lifepoints": 31},
                {"Ice cooler": 1},
                "finisher_not_ready",
            ),
            (
                "missing item",
                {"target_id": "desert_lizard", "enemy_lifepoints": 30},
                {},
                "finisher_item_missing",
            ),
        )
        for label, encounter, finishers, expected_reason in cases:
            with self.subTest(label=label):
                player = _player(
                    current_combat_target="desert_lizard",
                    combat_action="finisher",
                    slayer_level=22,
                    combat_encounter=encounter,
                    combat_supply_loadout={"finishers": finishers},
                    inventory={"Waterskin (4)": 1},
                )

                unchanged, ok, result = apply_combat_finisher_pure(
                    player, COMBAT_ENEMY_DATA
                )

                self.assertFalse(ok)
                self.assertIs(unchanged, player)
                self.assertEqual(result["reason"], expected_reason)
                self.assertEqual(
                    player["combat_supply_loadout"]["finishers"], finishers
                )

    def test_desert_lizard_finisher_cannot_bypass_the_slayer_level_gate(self):
        player = _player(
            current_combat_target="desert_lizard",
            combat_action="finisher",
            slayer_level=21,
            combat_encounter={
                "target_id": "desert_lizard",
                "enemy_lifepoints": 30,
            },
            combat_supply_loadout={"finishers": {"Ice cooler": 1}},
        )

        unchanged, ok, result = apply_combat_finisher_pure(
            player, COMBAT_ENEMY_DATA
        )

        self.assertFalse(ok)
        self.assertIs(unchanged, player)
        self.assertEqual(result["reason"], "combat_locked")
        self.assertEqual(result["locked_reasons"], ("Slayer level 22",))
        self.assertEqual(
            player["combat_supply_loadout"]["finishers"],
            {"Ice cooler": 1},
        )

    def test_desert_lizard_lethal_damage_requires_or_automates_the_finisher(self):
        cases = (
            ("manual required", False, 2, 0, 0, 2),
            ("quick unlocked", True, 2, 1, 1, 1),
            ("quick missing item", True, 0, 0, 0, 0),
        )
        for label, quick, loaded, kills, automatic, remaining in cases:
            with self.subTest(label=label):
                player = _player(
                    current_combat_target="desert_lizard",
                    slayer_level=22,
                    constitution_level=99,
                    combat_lifepoints=990,
                    combat_auto_flee=False,
                    combat_encounter={
                        "target_id": "desert_lizard",
                        "enemy_lifepoints": 20,
                    },
                    combat_supply_loadout={
                        "finishers": {"Ice cooler": loaded} if loaded else {},
                        "hazards": {"Waterskin (4)": 1},
                    },
                    slayer_quick_finishers_unlocked=quick,
                )

                fought, ok, result = apply_combat_burst_pure(
                    player,
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                    ticks=1,
                    rng=_rng([0.0, 0.999999]),
                )

                self.assertTrue(ok)
                self.assertEqual(result["kills"], kills)
                self.assertEqual(result["automatic_finishers"], automatic)
                if kills:
                    self.assertEqual(fought["combat_encounter"], {})
                else:
                    self.assertEqual(
                        fought["combat_encounter"]["enemy_lifepoints"], 1
                    )
                self.assertEqual(
                    fought["combat_supply_loadout"]["finishers"].get(
                        "Ice cooler", 0
                    ),
                    remaining,
                )
                self.assertEqual(
                    fought["combat_supply_loadout"]["hazards"],
                    {"Waterskin (3)": 1},
                )

    def test_gelatinous_abomination_requires_worn_spiked_gauntlets_to_die(self):
        without_gauntlets = _player(
            current_combat_target="gelatinous_abomination",
            combat_encounter={
                "target_id": "gelatinous_abomination",
                "enemy_lifepoints": 10,
            },
        )

        blocked, ok, result = apply_combat_burst_pure(
            without_gauntlets,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["kills"], 0)
        self.assertEqual(blocked["combat_encounter"]["enemy_lifepoints"], 1)

        wearing_gauntlets = _player(
            current_combat_target="gelatinous_abomination",
            equipment={"hands": "Spiked gauntlets"},
            combat_encounter={
                "target_id": "gelatinous_abomination",
                "enemy_lifepoints": 10,
            },
        )
        finished, ok, result = apply_combat_burst_pure(
            wearing_gauntlets,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["kills"], 1)
        self.assertEqual(result["automatic_finishers"], 1)
        self.assertEqual(finished["equipment"]["hands"], "Spiked gauntlets")
        self.assertEqual(
            finished["combat_supply_loadout"].get("finishers", {}),
            {},
        )

    def test_desert_targets_require_slayer_level_and_a_water_source(self):
        for target_id, required_level in (
            ("desert_lizard", 22),
            ("crocodile", 10),
        ):
            with self.subTest(target_id=target_id):
                low_level = _player(
                    current_combat_target=target_id,
                    slayer_level=required_level - 1,
                    inventory={"Waterskin (4)": 1},
                )
                dry = _player(
                    current_combat_target=target_id,
                    slayer_level=required_level,
                )
                ready = _player(
                    current_combat_target=target_id,
                    slayer_level=required_level,
                    inventory={"Waterskin (4)": 1},
                )

                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        low_level, target_id, COMBAT_ENEMY_DATA
                    ),
                    (f"Slayer level {required_level}",),
                )
                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        dry, target_id, COMBAT_ENEMY_DATA
                    ),
                    ("Desert heat: filled Waterskin",),
                )
                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        ready, target_id, COMBAT_ENEMY_DATA
                    ),
                    (),
                )

    def test_desert_lizard_bank_run_loads_finishers_and_preserves_water_doses(self):
        player = _player(
            current_combat_target="desert_lizard",
            slayer_level=22,
            constitution_level=99,
            combat_lifepoints=990,
            combat_auto_flee=False,
            inventory={"Ice cooler": 2, "Waterskin (4)": 2},
        )

        banking, ok, started = apply_combat_burst_pure(
            player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1
        )
        loaded, ok_loaded, completed = apply_combat_burst_pure(
            banking, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1
        )
        fought, ok_fought, result = apply_combat_burst_pure(
            loaded,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok and ok_loaded and ok_fought)
        self.assertTrue(started["bank_run_started"])
        self.assertTrue(completed["bank_run_completed"])
        self.assertEqual(
            loaded["combat_supply_loadout"]["finishers"],
            {"Ice cooler": 2},
        )
        self.assertEqual(
            loaded["combat_supply_loadout"]["hazards"],
            {"Waterskin (4)": 2},
        )
        self.assertEqual(
            fought["combat_supply_loadout"]["hazards"],
            {"Waterskin (4)": 1, "Waterskin (3)": 1},
        )
        self.assertEqual(
            result["hazard_supplies_used"],
            ({"item": "Waterskin (4)", "replacement": "Waterskin (3)"},),
        )

    def test_mutated_zygomite_requires_slayer_and_lost_city(self):
        low_level = _player(
            current_combat_target="mutated_zygomite_level_74",
            slayer_level=56,
        )
        missing_quest = _player(
            current_combat_target="mutated_zygomite_level_74",
            slayer_level=57,
        )
        ready = _player(
            current_combat_target="mutated_zygomite_level_74",
            slayer_level=57,
            quests={"lost_city": {"completed": True}},
        )

        self.assertEqual(
            combat_target_locked_reasons_pure(
                low_level, "mutated_zygomite_level_74", COMBAT_ENEMY_DATA
            ),
            ("Slayer level 57",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                missing_quest, "mutated_zygomite_level_74", COMBAT_ENEMY_DATA
            ),
            ("Complete Lost City",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                ready, "mutated_zygomite_level_74", COMBAT_ENEMY_DATA
            ),
            (),
        )

    def test_mutated_zygomite_manual_finisher_spends_one_charge_atomically(self):
        player = _player(
            current_combat_target="mutated_zygomite_level_74",
            combat_action="finisher",
            slayer_level=57,
            quests={"lost_city": {"completed": True}},
            combat_encounter={
                "target_id": "mutated_zygomite_level_74",
                "enemy_lifepoints": 19,
            },
            combat_supply_loadout={"finishers": {"Fungicide spray 10": 1}},
        )

        finished, ok, result = apply_combat_finisher_pure(
            player, COMBAT_ENEMY_DATA, rng=lambda: 0.999999
        )

        self.assertTrue(ok, result)
        self.assertEqual(result["kills"], 1)
        self.assertEqual(result["finisher_item"], "Fungicide spray")
        self.assertTrue(result["finisher_consumed"])
        self.assertEqual(
            finished["combat_supply_loadout"]["finishers"],
            {"Fungicide spray 9": 1},
        )
        self.assertEqual(
            finished["combat_kill_counts"],
            {"mutated_zygomite_level_74": 1},
        )
        self.assertEqual(finished["inventory"]["Ashes"], 1)

    def test_mutated_zygomite_spray_threshold_and_canister_reload_preserve_remainder(self):
        above_threshold = _player(
            current_combat_target="mutated_zygomite_level_74",
            combat_action="finisher",
            slayer_level=57,
            quests={"lost_city": {"completed": True}},
            combat_encounter={
                "target_id": "mutated_zygomite_level_74",
                "enemy_lifepoints": 20,
            },
            combat_supply_loadout={"finishers": {"Fungicide spray 1": 1}},
        )
        unchanged, ok, result = apply_combat_finisher_pure(
            above_threshold, COMBAT_ENEMY_DATA
        )
        self.assertFalse(ok)
        self.assertIs(unchanged, above_threshold)
        self.assertEqual(result["reason"], "finisher_not_ready")
        self.assertEqual(
            above_threshold["combat_supply_loadout"]["finishers"],
            {"Fungicide spray 1": 1},
        )

        first_kill = dict(above_threshold)
        first_kill["combat_encounter"] = {
            "target_id": "mutated_zygomite_level_74",
            "enemy_lifepoints": 19,
        }
        emptied, ok, _result = apply_combat_finisher_pure(
            first_kill, COMBAT_ENEMY_DATA, rng=lambda: 0.999999
        )
        self.assertTrue(ok)
        self.assertEqual(
            emptied["combat_supply_loadout"]["finishers"],
            {"Fungicide spray 0": 1},
        )

        emptied["combat_action"] = "finisher"
        emptied["combat_encounter"] = {
            "target_id": "mutated_zygomite_level_74",
            "enemy_lifepoints": 19,
        }
        emptied["combat_supply_loadout"]["finishers"]["Fungicide"] = 1
        reloaded, ok, _result = apply_combat_finisher_pure(
            emptied, COMBAT_ENEMY_DATA, rng=lambda: 0.999999
        )
        self.assertTrue(ok)
        self.assertEqual(
            reloaded["combat_supply_loadout"]["finishers"],
            {"Fungicide spray 9": 1},
        )

    def test_mutated_zygomite_quick_finisher_spends_exactly_one_spray_charge(self):
        player = _player(
            current_combat_target="mutated_zygomite_level_74",
            slayer_level=57,
            quests={"lost_city": {"completed": True}},
            constitution_level=99,
            combat_lifepoints=990,
            combat_auto_flee=False,
            slayer_quick_finishers_unlocked=True,
            combat_encounter={
                "target_id": "mutated_zygomite_level_74",
                "enemy_lifepoints": 10,
            },
            combat_supply_loadout={"finishers": {"Fungicide spray 10": 1}},
        )

        finished, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["kills"], 1)
        self.assertEqual(result["automatic_finishers"], 1)
        self.assertEqual(
            finished["combat_supply_loadout"]["finishers"],
            {"Fungicide spray 9": 1},
        )

    def test_mutated_zygomite_refill_uses_best_spray_and_respects_pack_capacity(self):
        from ankiscape.logic_pure.logic_pure import CARRIED_CAPACITY, _combat_supply_slots_used

        player = _player(
            current_combat_target="mutated_zygomite_level_74",
            slayer_level=57,
            quests={"lost_city": {"completed": True}},
            combat_pack_mode="max_safety",
            combat_auto_eat_food=["Shark"],
            inventory={
                "Shark": 100,
                "Fungicide spray 7": 1,
                "Fungicide spray 3": 1,
                "Fungicide": 20,
            },
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(
            player, EQUIPMENT_DATA
        )

        self.assertTrue(ok, reason)
        self.assertEqual(_combat_supply_slots_used(refilled), CARRIED_CAPACITY)
        self.assertEqual(
            refilled["combat_supply_loadout"]["finishers"],
            {"Fungicide spray 7": 1, "Fungicide": 7},
        )
        self.assertEqual(refilled["combat_supply_loadout"]["food"], {"Shark": 20})
        self.assertEqual(refilled["inventory"]["Fungicide spray 3"], 1)

        unloaded, ok, reason = unload_combat_supply_loadout_pure(refilled)
        self.assertTrue(ok, reason)
        self.assertEqual(unloaded["inventory"]["Fungicide spray 7"], 1)
        self.assertEqual(unloaded["inventory"]["Fungicide spray 3"], 1)
        self.assertEqual(unloaded["inventory"]["Fungicide"], 20)

    def test_mutated_zygomite_refill_turns_empty_spray_and_canister_into_full_spray(self):
        player = _player(
            current_combat_target="mutated_zygomite_level_86",
            slayer_level=57,
            quests={"lost_city": {"completed": True}},
            inventory={"Fungicide spray 0": 1, "Fungicide": 1},
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(
            player, EQUIPMENT_DATA
        )

        self.assertTrue(ok, reason)
        self.assertEqual(
            refilled["combat_supply_loadout"]["finishers"],
            {"Fungicide spray 10": 1},
        )
        self.assertEqual(refilled["inventory"]["Fungicide spray 0"], 0)
        self.assertEqual(refilled["inventory"]["Fungicide"], 0)

    def test_loaded_empty_spray_and_banked_canister_keep_zygomite_available(self):
        player = _player(
            current_combat_target="mutated_zygomite_level_74",
            slayer_level=57,
            quests={"lost_city": {"completed": True}},
            inventory={"Fungicide": 1},
            combat_supply_loadout={"finishers": {"Fungicide spray 0": 1}},
        )

        self.assertEqual(
            combat_target_locked_reasons_pure(
                player, "mutated_zygomite_level_74", COMBAT_ENEMY_DATA
            ),
            (),
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(
            player, EQUIPMENT_DATA
        )
        self.assertTrue(ok, reason)
        self.assertEqual(
            refilled["combat_supply_loadout"]["finishers"],
            {"Fungicide spray 10": 1},
        )

    def test_rockslug_finisher_consumes_salt_and_frozen_slug_cannot_retaliate(self):
        player = _player(
            current_combat_target="rockslug",
            slayer_level=99,
            combat_encounter={
                "target_id": "rockslug",
                "enemy_lifepoints": 39,
            },
            combat_supply_loadout={"finishers": {"Bag of salt": 2}},
        )

        finished, ok, result = apply_combat_finisher_pure(
            player, COMBAT_ENEMY_DATA, rng=lambda: 1.0
        )

        self.assertTrue(ok, result)
        self.assertTrue(result["finisher_consumed"])
        self.assertEqual(
            finished["combat_supply_loadout"]["finishers"],
            {"Bag of salt": 1},
        )

        frozen = _player(
            current_combat_target="rockslug",
            slayer_level=99,
            combat_encounter={
                "target_id": "rockslug",
                "enemy_lifepoints": 10,
            },
        )
        latched, ok, result = apply_combat_burst_pure(
            frozen,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: 1.0,
            live_cadence=True,
        )

        self.assertTrue(ok, result)
        self.assertTrue(latched["combat_encounter"]["retaliation_stopped"])

        latched["combat_encounter"]["enemy_lifepoints"] = 20
        fought, ok, result = apply_combat_burst_pure(
            latched,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=8,
            rng=lambda: 0.0,
            live_cadence=True,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["enemy_damage"], 0)
        self.assertTrue(result["enemy_retaliation_stopped"])
        self.assertEqual(fought["combat_lifepoints"], frozen["combat_lifepoints"])

    def test_gargoyle_finisher_is_reusable_and_refill_loads_only_one_hammer(self):
        player = _player(
            current_combat_target="gargoyle",
            slayer_level=99,
            inventory={"Rock hammer": 3},
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(
            player, EQUIPMENT_DATA
        )
        self.assertTrue(ok, reason)
        self.assertEqual(
            refilled["combat_supply_loadout"]["finishers"],
            {"Rock hammer": 1},
        )
        self.assertEqual(refilled["inventory"]["Rock hammer"], 2)

        refilled["combat_encounter"] = {
            "target_id": "gargoyle",
            "enemy_lifepoints": 89,
        }
        finished, ok, result = apply_combat_finisher_pure(
            refilled, COMBAT_ENEMY_DATA, rng=lambda: 1.0
        )

        self.assertTrue(ok, result)
        self.assertFalse(result["finisher_consumed"])
        self.assertEqual(
            finished["combat_supply_loadout"]["finishers"],
            {"Rock hammer": 1},
        )

    def test_gargoyle_quick_finisher_keeps_the_reusable_hammer(self):
        player = _player(
            current_combat_target="gargoyle",
            slayer_level=99,
            slayer_quick_finishers_unlocked=True,
            combat_encounter={
                "target_id": "gargoyle",
                "enemy_lifepoints": 1,
            },
            combat_supply_loadout={"finishers": {"Rock hammer": 1}},
        )
        rolls = iter((0.0, 1.0))

        finished, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: next(rolls, 1.0),
            live_cadence=True,
        )

        self.assertTrue(ok, result)
        self.assertTrue(result["killed"])
        self.assertEqual(result["automatic_finishers"], 1)
        self.assertEqual(
            finished["combat_supply_loadout"]["finishers"],
            {"Rock hammer": 1},
        )

    def test_gargoyle_regeneration_is_tick_exact_across_review_boundaries(self):
        player = _player(
            current_combat_target="gargoyle",
            slayer_level=99,
            attack_level=1,
            strength_level=1,
            combat_encounter={
                "target_id": "gargoyle",
                "enemy_lifepoints": 100,
            },
        )

        whole, ok_whole, whole_result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=lambda: 1.0,
            live_cadence=True,
        )
        first, ok_first, first_result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=2,
            rng=lambda: 1.0,
            live_cadence=True,
        )
        split, ok_split, split_result = apply_combat_burst_pure(
            first,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=3,
            rng=lambda: 1.0,
            live_cadence=True,
        )

        self.assertTrue(ok_whole and ok_first and ok_split)
        self.assertEqual(whole_result["enemy_healing"], 12)
        self.assertEqual(first_result["enemy_healing"], 4)
        self.assertEqual(split_result["enemy_healing"], 8)
        self.assertEqual(
            split["combat_encounter"]["enemy_lifepoints"],
            whole["combat_encounter"]["enemy_lifepoints"],
        )
        self.assertEqual(
            split["combat_encounter"]["regeneration_residual"],
            whole["combat_encounter"]["regeneration_residual"],
        )

    def test_combat_loadout_preferences_are_sanitized(self):
        player = _player(combat_auto_eat_food=["Shrimps", "Shark"], combat_auto_eat_threshold_percent=40)

        updated = set_combat_auto_eat_threshold_pure(player, 150)
        self.assertEqual(updated["combat_auto_eat_threshold_percent"], 99)

        updated, ok, reason = set_combat_auto_eat_food_pure(player, "Lobster")
        self.assertTrue(ok, reason)
        self.assertEqual(updated["combat_auto_eat_food"][:3], ["Lobster", "Shrimps", "Shark"])

        unchanged, ok, reason = set_combat_auto_eat_food_pure(player, "Burnt fish")
        self.assertFalse(ok)
        self.assertEqual(reason, "unsupported food")
        self.assertEqual(unchanged["combat_auto_eat_food"], ["Shrimps", "Shark"])

    def test_combat_preview_exposes_risk_and_source_metrics(self):
        preview = combat_target_preview_pure(_player(), "giant_rat", COMBAT_ENEMY_DATA, EQUIPMENT_DATA)

        self.assertEqual(preview["state"], "Ready")
        self.assertGreater(preview["accuracy"], 0)
        self.assertEqual(preview["enemy_max_lifepoints"], 50)
        self.assertTrue(str(preview["source"]).endswith("giant_rat_level_2.plugin.kts"))

    def test_earth_warrior_preview_exposes_wilderness_retention(self):
        player = _player(
            current_combat_target="earth_warrior",
            constitution_level=99,
            combat_lifepoints=990,
            equipment={
                "weapon": "Rune sword",
                "body": "Rune platebody",
                "head": "Rune full helm",
                "shield": "Iron kiteshield",
                "cape": "Cape",
            },
        )

        preview = combat_target_preview_pure(
            player,
            "earth_warrior",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )

        self.assertEqual(preview["state"], "Wilderness risk")
        self.assertEqual(preview["risk_band"], "Wilderness risk")
        risk = preview["wilderness_risk"]
        self.assertEqual(risk["ambush_chance"], 0.01)
        self.assertEqual(risk["max_hit"], 250)
        self.assertEqual(len(risk["kept_items"]), 3)
        self.assertEqual(len(risk["lost_items"]), 2)

    def test_green_dragon_preview_exposes_current_dragonfire_tier(self):
        player = _player(
            current_combat_target="green_dragon",
            constitution_level=99,
            combat_lifepoints=990,
            equipment={"shield": "Anti-dragon shield"},
        )

        preview = combat_target_preview_pure(
            player,
            "green_dragon",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )

        self.assertEqual(preview["state"], "Wilderness risk")
        self.assertEqual(preview["enemy_max_hit"], 85)
        self.assertEqual(
            preview["dragonfire"],
            {
                "protection_level": 1,
                "state": "Partial",
                "max_hit": 50,
                "shield_active": True,
                "shield_item": "Anti-dragon shield",
                "antifire_active": False,
                "super_antifire_active": False,
                "magic_prayer_active": False,
                "chance_numerator": 1,
                "chance_denominator": 4,
            },
        )

    def test_green_dragon_protection_layers_match_the_sourced_tiers(self):
        dragon = COMBAT_ENEMY_DATA["green_dragon"]

        none = combat_dragonfire_protection_pure(_player(), dragon)
        shield = combat_dragonfire_protection_pure(
            _player(equipment={"shield": "Anti-dragon shield"}), dragon
        )
        potion_and_shield = combat_dragonfire_protection_pure(
            _player(
                equipment={"shield": "Anti-dragon shield"},
                combat_antifire_ticks_remaining=1,
            ),
            dragon,
        )
        super_potion = combat_dragonfire_protection_pure(
            _player(combat_super_antifire_ticks_remaining=1), dragon
        )
        prayer_only = combat_dragonfire_protection_pure(
            _player(), dragon, magic_prayer_active=True
        )

        self.assertEqual((none["state"], none["max_hit"]), ("None", 500))
        self.assertEqual(
            (shield["state"], shield["max_hit"]), ("Partial", 50)
        )
        self.assertEqual(
            (potion_and_shield["state"], potion_and_shield["max_hit"]),
            ("Full", 0),
        )
        self.assertEqual(
            (super_potion["state"], super_potion["max_hit"]), ("Full", 0)
        )
        self.assertEqual(
            (prayer_only["state"], prayer_only["max_hit"]), ("Partial", 50)
        )

    def test_green_dragon_breath_bypasses_melee_accuracy_and_uses_tier_cap(self):
        dragon = {
            "green_dragon_test": {
                **COMBAT_ENEMY_DATA["green_dragon"],
                "wilderness_risk": {},
                "attack_speed": 1,
            }
        }

        def fight(**overrides):
            player = _player(
                current_combat_target="green_dragon_test",
                constitution_level=99,
                combat_lifepoints=990,
                combat_auto_flee=False,
                **overrides,
            )
            return apply_combat_burst_pure(
                player,
                dragon,
                EQUIPMENT_DATA,
                ticks=2,
                rng=_rng([1.0, 0.0, 0.999999]),
            )

        unprotected, ok, result = fight()
        partial, ok_partial, partial_result = fight(
            equipment={"shield": "Anti-dragon shield"}
        )
        full, ok_full, full_result = fight(
            combat_super_antifire_ticks_remaining=600
        )

        self.assertTrue(ok and ok_partial and ok_full)
        self.assertEqual(result["dragonfire_attacks"], 1)
        self.assertEqual(result["dragonfire_damage"], 500)
        self.assertEqual(unprotected["combat_lifepoints"], 490)
        self.assertEqual(partial_result["dragonfire_damage"], 50)
        self.assertEqual(partial["combat_lifepoints"], 940)
        self.assertEqual(full_result["dragonfire_damage"], 0)
        self.assertEqual(full["combat_lifepoints"], 990)

    def test_antifire_expires_and_auto_refreshes_inside_one_combat_review(self):
        dragon = {
            "green_dragon_test": {
                **COMBAT_ENEMY_DATA["green_dragon"],
                "wilderness_risk": {},
                "attack_speed": 1,
            }
        }
        player = _player(
            current_combat_target="green_dragon_test",
            constitution_level=99,
            combat_lifepoints=990,
            combat_auto_flee=False,
            equipment={"shield": "Anti-dragon shield"},
            combat_antifire_ticks_remaining=2,
            combat_supply_loadout={"potions": {"Antifire (4)": 1}},
        )

        out, ok, result = apply_combat_burst_pure(
            player,
            dragon,
            EQUIPMENT_DATA,
            ticks=4,
            rng=_rng([1.0, 0.0, 0.0, 0.0, 0.0]),
        )

        self.assertTrue(ok)
        self.assertEqual(
            result["potions_used"],
            ({"item": "Antifire (4)", "effect": "antifire", "ticks": 600},),
        )
        self.assertEqual(
            out["combat_supply_loadout"]["potions"], {"Antifire (3)": 1}
        )
        self.assertEqual(out["combat_antifire_ticks_remaining"], 598)

    def test_protect_item_keeps_a_fourth_wilderness_equipment_piece(self):
        player = _player(
            equipment={
                "weapon": "Rune sword",
                "body": "Rune platebody",
                "head": "Rune full helm",
                "shield": "Iron kiteshield",
                "cape": "Cape",
            },
            prayer_level=99,
            combat_prayer_points=990,
            combat_prayer_uptime="100",
            combat_selected_prayers=["protect_item"],
        )

        risk = combat_wilderness_equipment_risk_pure(
            player,
            COMBAT_ENEMY_DATA["earth_warrior"],
        )

        self.assertTrue(risk["protect_item"])
        self.assertEqual(len(risk["kept_items"]), 4)
        self.assertEqual(risk["lost_items"], ("Cape",))

    def test_fatal_earth_warrior_ambush_loses_equipment_without_a_grave(self):
        player = _player(
            current_combat_target="earth_warrior",
            constitution_level=99,
            combat_lifepoints=1,
            combat_auto_flee=False,
            equipment={
                "weapon": "Rune sword",
                "body": "Rune platebody",
                "head": "Rune full helm",
                "shield": "Iron kiteshield",
                "cape": "Cape",
            },
            inventory={"Coins": 500, "Lobster": 3},
            carried_inventory={"earth_warrior": {"Lobster": 3}},
        )

        died, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: 0.0,
        )

        self.assertTrue(ok)
        self.assertTrue(result["died"])
        self.assertTrue(result["wilderness_ambush"]["died"])
        self.assertEqual(len(died["equipment"]), 3)
        self.assertEqual(died.get("combat_grave", {}), {})
        self.assertEqual(died["inventory"], {"Coins": 500, "Lobster": 3})
        self.assertEqual(
            died["carried_inventory"],
            {"earth_warrior": {"Lobster": 3}},
        )

    def test_wilderness_death_honors_the_confirmed_protect_item_preview(self):
        player = _player(
            current_combat_target="earth_warrior",
            constitution_level=99,
            combat_lifepoints=1,
            combat_auto_flee=False,
            equipment={
                "weapon": "Rune sword",
                "body": "Rune platebody",
                "head": "Rune full helm",
                "shield": "Iron kiteshield",
                "cape": "Cape",
            },
            prayer_level=99,
            combat_prayer_points=1,
            combat_prayer_uptime="100",
            combat_selected_prayers=["protect_item"],
        )

        confirmed_risk = combat_wilderness_equipment_risk_pure(
            player,
            COMBAT_ENEMY_DATA["earth_warrior"],
        )
        player["combat_selected_prayers"] = []
        result = _combat_apply_wilderness_ambush(
            player,
            COMBAT_ENEMY_DATA["earth_warrior"],
            1,
            990,
            _rng([0.0, 0.0]),
            confirmed_risk,
        )

        self.assertTrue(result["died"])
        self.assertEqual(len(result["kept_items"]), 4)
        self.assertEqual(len(player["equipment"]), 4)
        self.assertEqual(player.get("combat_grave", {}), {})

    def test_safe_review_recovery_discards_wilderness_encounter_progress(self):
        player = _player(
            current_combat_target="earth_warrior",
            combat_encounter={
                "target_id": "earth_warrior",
                "enemy_lifepoints": 200,
            },
        )

        recovered = apply_safe_combat_recovery_pure(player)

        self.assertEqual(recovered["combat_encounter"], {})

    def test_sourced_enemy_max_hits_override_generic_melee_derivation(self):
        for target_id, lifepoints, max_hit, oldid in (
            ("jackal", 270, 80, "oldid=6493724"),
            ("goat", 210, 47, "oldid=5795580"),
            ("icefiend", 150, 20, "oldid=6419875"),
        ):
            with self.subTest(target=target_id):
                preview = combat_target_preview_pure(
                    _player(inventory={"Waterskin (4)": 1}),
                    target_id,
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                )

                self.assertEqual(preview["enemy_max_lifepoints"], lifepoints)
                self.assertEqual(preview["enemy_max_hit"], max_hit)
                self.assertIn(oldid, preview["source"])

    def test_goat_preserves_guaranteed_horn_drop_and_desert_context(self):
        goat = COMBAT_ENEMY_DATA["goat"]

        self.assertEqual(
            _combat_roll_drops(goat, _rng([])),
            {"Bones": 1, "Desert goat horn": 1},
        )
        self.assertTrue(goat["desert_context"])
        self.assertEqual(goat["environmental_hazard"]["display_name"], "Desert heat")
        self.assertIn("oldid=6555637", goat["source"])

    def test_combat_preview_marks_poison_enemies_as_food_advised(self):
        preview = combat_target_preview_pure(_player(), "poison_scorpion", COMBAT_ENEMY_DATA, EQUIPMENT_DATA)

        self.assertEqual(preview["risk_band"], "Food advised")
        self.assertEqual(preview["poison_damage"], 30)
        self.assertEqual(preview["poison_chance"], 0.4)

        immune_preview = combat_target_preview_pure(
            _player(combat_status_effects={"poison_immunity": {"ticks_left": 100}}),
            "poison_scorpion",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )
        self.assertEqual(immune_preview["poison_damage"], 0)
        self.assertEqual(immune_preview["poison_chance"], 0.0)
        self.assertEqual(immune_preview["poison_immunity_ticks"], 100)

    def test_unshielded_cockatrice_fixed_attack_drains_stats_to_period_floor(self):
        player = _player(
            current_combat_target="cockatrice",
            attack_level=60,
            strength_level=60,
            defense_level=60,
            ranged_level=60,
            agility_level=60,
            constitution_level=60,
            prayer_level=99,
            combat_lifepoints=600,
            combat_auto_flee=False,
            combat_prayer_points=990,
            combat_selected_prayers=["protect_from_melee"],
            combat_prayer_uptime="100",
        )

        out, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=17,
            rng=lambda: 0.999999,
        )

        self.assertTrue(ok)
        self.assertEqual(result["unprotected_attacks"], 4)
        self.assertEqual(result["enemy_damage"], 400)
        self.assertEqual(out["combat_lifepoints"], 200)
        self.assertEqual(
            out["combat_current_levels"],
            {"attack": 15, "strength": 15, "defense": 15, "ranged": 15, "agility": 15},
        )
        self.assertEqual(
            result["stat_drains"],
            {"attack": 45, "strength": 45, "defense": 45, "ranged": 45, "agility": 45},
        )

    def test_mirror_shield_restores_cockatrice_to_ordinary_accuracy_rolls(self):
        player = _player(
            current_combat_target="cockatrice",
            equipment={"shield": "Mirror shield"},
            attack_level=60,
            strength_level=60,
            defense_level=60,
            ranged_level=60,
            agility_level=60,
            constitution_level=60,
            combat_lifepoints=600,
            combat_auto_flee=False,
        )

        out, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=17,
            rng=lambda: 0.999999,
        )

        self.assertTrue(ok)
        self.assertEqual(result["unprotected_attacks"], 0)
        self.assertEqual(result["enemy_damage"], 0)
        self.assertEqual(out["combat_lifepoints"], 600)
        self.assertEqual(out["combat_current_levels"], {})

    def test_cockatrice_drains_reduce_later_attacks_in_the_same_review(self):
        base = dict(
            current_combat_target="cockatrice",
            attack_level=60,
            strength_level=60,
            defense_level=60,
            ranged_level=60,
            agility_level=60,
            constitution_level=99,
            combat_lifepoints=990,
            combat_auto_flee=False,
        )

        _unprotected, ok, unprotected_result = apply_combat_burst_pure(
            _player(**base),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=13,
            rng=lambda: 0.5,
        )
        _protected, protected_ok, protected_result = apply_combat_burst_pure(
            _player(**base, equipment={"shield": "Mirror shield"}),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=13,
            rng=lambda: 0.5,
        )

        self.assertTrue(ok)
        self.assertTrue(protected_ok)
        self.assertLess(unprotected_result["player_damage"], protected_result["player_damage"])

    def test_protective_gear_preview_warns_when_missing_and_clears_when_equipped(self):
        cases = (
            ("cockatrice", "shield", "Mirror shield", 60, 100),
            ("basilisk", "shield", "Mirror shield", 120, 120),
            ("banshee", "head", "Earmuffs", 99, 80),
        )
        for target_id, slot, item_name, constitution_level, expected_max_hit in cases:
            with self.subTest(target_id=target_id):
                unprotected = combat_target_preview_pure(
                    _player(
                        slayer_level=99,
                        constitution_level=constitution_level,
                        combat_lifepoints=constitution_level * 10,
                    ),
                    target_id,
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                )
                protected = combat_target_preview_pure(
                    _player(
                        slayer_level=99,
                        constitution_level=constitution_level,
                        combat_lifepoints=constitution_level * 10,
                        equipment={slot: item_name},
                    ),
                    target_id,
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                )

                self.assertEqual(unprotected["enemy_max_hit"], expected_max_hit)
                self.assertIn(item_name, unprotected["protection_warning"])
                self.assertEqual(protected["protection_warning"], "")
                self.assertLess(protected["enemy_max_hit"], unprotected["enemy_max_hit"])

    def test_basilisk_prayer_blocks_unshielded_damage_but_not_random_stat_drain(self):
        base = dict(
            current_combat_target="basilisk",
            slayer_level=40,
            attack_level=60,
            strength_level=60,
            defense_level=60,
            ranged_level=60,
            magic_level=60,
            prayer_level=99,
            constitution_level=60,
            combat_lifepoints=600,
            combat_auto_flee=False,
            combat_selected_prayers=["protect_from_melee"],
            combat_prayer_uptime="100",
            combat_prayer_points=990,
        )

        protected, ok, result = apply_combat_burst_pure(
            _player(**base),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=19,
            rng=lambda: 0.999999,
        )
        shielded, shielded_ok, shielded_result = apply_combat_burst_pure(
            _player(**base, equipment={"shield": "Mirror shield"}),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=19,
            rng=lambda: 0.999999,
        )

        self.assertTrue(ok)
        self.assertTrue(shielded_ok)
        self.assertEqual(result["unprotected_attacks"], 3)
        self.assertEqual(result["enemy_damage"], 0)
        self.assertEqual(result["stat_drains"], {"magic": 15})
        self.assertEqual(protected["combat_lifepoints"], 600)
        self.assertEqual(protected["combat_current_levels"], {"magic": 45})
        self.assertEqual(shielded_result["unprotected_attacks"], 0)
        self.assertEqual(shielded_result["stat_drains"], {})
        self.assertEqual(shielded["combat_current_levels"], {})

    def test_aberrant_spectre_prayer_blocks_drain_but_not_stench_damage(self):
        base = dict(
            current_combat_target="aberrant_spectre",
            slayer_level=60,
            quests={"priest_in_peril": {"completed": True}},
            attack_level=60,
            strength_level=60,
            defense_level=60,
            ranged_level=60,
            magic_level=60,
            prayer_level=99,
            constitution_level=60,
            combat_lifepoints=600,
            combat_auto_flee=False,
            combat_prayer_uptime="100",
            combat_prayer_points=990,
        )

        unprotected, ok, result = apply_combat_burst_pure(
            _player(**base),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=13,
            rng=lambda: 0.999999,
        )
        praying, praying_ok, praying_result = apply_combat_burst_pure(
            _player(
                **base,
                combat_selected_prayers=["protect_from_magic"],
            ),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=13,
            rng=lambda: 0.999999,
        )
        pegged, pegged_ok, pegged_result = apply_combat_burst_pure(
            _player(**base, equipment={"head": "Nose peg"}),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=13,
            rng=lambda: 0.999999,
        )

        self.assertTrue(ok, result)
        self.assertTrue(praying_ok, praying_result)
        self.assertTrue(pegged_ok, pegged_result)
        self.assertEqual(result["unprotected_attacks"], 2)
        self.assertEqual(result["enemy_damage"], 120)
        self.assertEqual(result["stat_drains"], {"magic": 10})
        self.assertEqual(unprotected["combat_lifepoints"], 480)
        self.assertEqual(praying_result["unprotected_attacks"], 2)
        self.assertEqual(praying_result["enemy_damage"], 120)
        self.assertEqual(praying_result["stat_drains"], {})
        self.assertEqual(praying["combat_lifepoints"], 480)
        self.assertEqual(pegged_result["unprotected_attacks"], 0)
        self.assertEqual(pegged_result["enemy_damage"], 0)
        self.assertEqual(pegged["combat_current_levels"], {})

    def test_cave_horror_requires_route_access_and_a_lit_light_source(self):
        base = {
            "current_combat_target": "cave_horror",
            "slayer_level": 58,
        }
        quest_locked = _player(**base, inventory={"Lit torch": 1})
        missing_light = _player(
            **base,
            quests={"cabin_fever": {"completed": True}},
        )
        ready = _player(
            **base,
            quests={"cabin_fever": {"completed": True}},
            equipment={"head": "Mining helmet (lit)"},
        )

        self.assertEqual(
            combat_target_locked_reasons_pure(
                quest_locked, "cave_horror", COMBAT_ENEMY_DATA
            ),
            ("Complete Cabin Fever",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                missing_light, "cave_horror", COMBAT_ENEMY_DATA
            ),
            (
                "One lit light source in inventory or equipped for "
                "Mos Le'Harmless Caves",
            ),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                ready, "cave_horror", COMBAT_ENEMY_DATA
            ),
            (),
        )

    def test_cave_horror_close_combat_protection_accepts_neck_or_helmet(self):
        base = dict(
            current_combat_target="cave_horror",
            slayer_level=58,
            quests={"cabin_fever": {"completed": True}},
            inventory={"Lit torch": 1},
            constitution_level=60,
            combat_lifepoints=600,
        )

        unprotected = combat_target_preview_pure(
            _player(**base),
            "cave_horror",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )
        icon = combat_target_preview_pure(
            _player(**base, equipment={"neck": "Witchwood icon"}),
            "cave_horror",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )
        helmet = combat_target_preview_pure(
            _player(**base, equipment={"head": "Full slayer helmet"}),
            "cave_horror",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )
        ranged = combat_target_preview_pure(
            _player(
                **{
                    **base,
                    "inventory": {
                        "Lit torch": 1,
                        "Bronze arrows": 10,
                    },
                },
                combat_attack_style="ranged_accurate",
                equipment={"weapon": "Shortbow"},
            ),
            "cave_horror",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )

        self.assertEqual(unprotected["enemy_max_hit"], 87)
        self.assertIn("Witchwood icon", unprotected["protection_warning"])
        self.assertEqual(icon["protection_warning"], "")
        self.assertEqual(helmet["protection_warning"], "")
        self.assertEqual(ranged["protection_warning"], "")

    def test_cave_horror_prayer_blocks_scream_damage_but_not_stat_drain(self):
        base = dict(
            current_combat_target="cave_horror",
            slayer_level=58,
            quests={"cabin_fever": {"completed": True}},
            inventory={"Lit torch": 1},
            attack_level=60,
            strength_level=60,
            defense_level=60,
            ranged_level=60,
            magic_level=60,
            prayer_level=99,
            constitution_level=60,
            combat_lifepoints=600,
            combat_auto_flee=False,
        )

        unprotected, ok, result = apply_combat_burst_pure(
            _player(**base),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=9,
            rng=lambda: 0.999999,
        )
        praying, praying_ok, praying_result = apply_combat_burst_pure(
            _player(
                **base,
                combat_selected_prayers=["protect_from_melee"],
                combat_prayer_uptime="100",
                combat_prayer_points=990,
            ),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=9,
            rng=lambda: 0.999999,
        )
        icon, icon_ok, icon_result = apply_combat_burst_pure(
            _player(**base, equipment={"neck": "Witchwood icon"}),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=9,
            rng=lambda: 0.999999,
        )

        self.assertTrue(ok, result)
        self.assertTrue(praying_ok, praying_result)
        self.assertTrue(icon_ok, icon_result)
        self.assertEqual(result["unprotected_attacks"], 2)
        self.assertEqual(result["enemy_damage"], 174)
        self.assertEqual(result["stat_drains"], {"magic": 10})
        self.assertEqual(unprotected["combat_lifepoints"], 426)
        self.assertEqual(praying_result["unprotected_attacks"], 2)
        self.assertEqual(praying_result["enemy_damage"], 0)
        self.assertEqual(praying_result["stat_drains"], {"magic": 10})
        self.assertEqual(praying["combat_lifepoints"], 600)
        self.assertEqual(icon_result["unprotected_attacks"], 0)
        self.assertEqual(icon_result["stat_drains"], {})
        self.assertEqual(icon["combat_current_levels"], {})

    def test_vampyre_requires_morytania_access_and_holy_symbol_weakens_it(self):
        locked = _player(current_combat_target="vampyre")
        unlocked = _player(
            current_combat_target="vampyre",
            quests={"priest_in_peril": {"completed": True}},
        )
        protected = _player(
            current_combat_target="vampyre",
            equipment={"neck": "Holy symbol"},
            quests={"priest_in_peril": {"completed": True}},
        )

        self.assertEqual(
            combat_target_locked_reasons_pure(
                locked, "vampyre", COMBAT_ENEMY_DATA
            ),
            ("Complete Priest in Peril",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                unlocked, "vampyre", COMBAT_ENEMY_DATA
            ),
            (),
        )
        ordinary_preview = combat_target_preview_pure(
            unlocked, "vampyre", COMBAT_ENEMY_DATA, EQUIPMENT_DATA
        )
        protected_preview = combat_target_preview_pure(
            protected, "vampyre", COMBAT_ENEMY_DATA, EQUIPMENT_DATA
        )
        self.assertEqual(ordinary_preview["enemy_max_hit"], 74)
        self.assertEqual(protected_preview["enemy_max_hit"], 59)
        self.assertFalse(
            ordinary_preview["weakening_equipment"]["active"]
        )
        self.assertTrue(
            protected_preview["weakening_equipment"]["active"]
        )

    def test_vampyre_bite_heals_and_drains_one_random_implemented_skill(self):
        player = _player(
            current_combat_target="vampyre",
            attack_level=10,
            defense_level=1,
            constitution_level=99,
            combat_lifepoints=990,
            combat_auto_flee=False,
            quests={"priest_in_peril": {"completed": True}},
            combat_encounter={
                "target_id": "vampyre",
                "enemy_lifepoints": 300,
                "enemy_attack_ticks_remaining": 0,
                "player_attack_ticks_remaining": 99,
            },
        )

        out, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng((0.0, 0.999999, 0.0, 0.0)),
            live_cadence=True,
        )

        self.assertTrue(ok, result)
        self.assertEqual(result["enemy_damage"], 73)
        self.assertEqual(result["vampyre_bites"], 1)
        self.assertEqual(result["vampyre_bite_healing"], 20)
        self.assertEqual(result["enemy_healing"], 20)
        self.assertEqual(result["enemy_lifepoints"], 320)
        self.assertEqual(result["stat_drains"], {"attack": 1})
        self.assertEqual(out["combat_current_levels"], {"attack": 9})

    def test_wall_beast_requires_spiny_helmet_only_when_starting_a_fight(self):
        missing = _player(
            current_combat_target="wall_beast",
            slayer_level=35,
        )
        equipped = _player(
            current_combat_target="wall_beast",
            slayer_level=35,
            equipment={"head": "Spiny helmet"},
        )
        continuing = _player(
            current_combat_target="wall_beast",
            slayer_level=35,
            combat_encounter={
                "target_id": "wall_beast",
                "enemy_lifepoints": 500,
            },
        )

        self.assertEqual(
            combat_target_locked_reasons_pure(
                missing, "wall_beast", COMBAT_ENEMY_DATA
            ),
            ("Equip a Spiny helmet to start fighting Wall beasts",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                equipped, "wall_beast", COMBAT_ENEMY_DATA
            ),
            (),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                continuing, "wall_beast", COMBAT_ENEMY_DATA
            ),
            (),
        )

    def test_dust_devil_requires_protective_headgear_throughout_the_fight(self):
        missing = _player(
            current_combat_target="dust_devil",
            slayer_level=65,
        )
        equipped = _player(
            current_combat_target="dust_devil",
            slayer_level=65,
            equipment={"head": "Face mask"},
        )
        active_but_unprotected = _player(
            current_combat_target="dust_devil",
            slayer_level=65,
            combat_encounter={
                "target_id": "dust_devil",
                "enemy_lifepoints": 500,
            },
        )

        warning = (
            "Equip a Face mask, Masked earmuffs, or a Slayer helmet "
            "to damage Dust devils"
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                missing, "dust_devil", COMBAT_ENEMY_DATA
            ),
            (warning,),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                equipped, "dust_devil", COMBAT_ENEMY_DATA
            ),
            (),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                active_but_unprotected, "dust_devil", COMBAT_ENEMY_DATA
            ),
            (warning,),
        )

        out, ok, result = apply_combat_burst_pure(
            active_but_unprotected,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=6,
            rng=_rng((0.0,)),
        )
        self.assertFalse(ok)
        self.assertEqual(out, active_but_unprotected)
        self.assertEqual(result["reason"], "combat_locked")
        self.assertEqual(result["locked_reasons"], (warning,))

    def test_dust_devil_keeps_rare_drop_and_charm_selectors_independent(self):
        devil = COMBAT_ENEMY_DATA["dust_devil"]

        self.assertEqual(
            _combat_roll_drops(
                devil,
                _rng((32512 / 32768, 0.999999)),
            ),
            {"Bones": 1, "Dragon chainbody": 1},
        )
        self.assertEqual(
            _combat_roll_drops(
                devil,
                _rng((0.999999, 44 / 606)),
            ),
            {"Bones": 1, "Crimson charm": 1},
        )

    def test_harpie_bug_swarm_requires_the_lit_lantern_throughout_the_fight(self):
        warning = "Equip a Lit bug lantern to damage Harpie bug swarms"
        missing = _player(
            current_combat_target="harpie_bug_swarm",
            slayer_level=33,
        )
        unlit = _player(
            current_combat_target="harpie_bug_swarm",
            slayer_level=33,
            equipment={"shield": "Unlit bug lantern"},
        )
        equipped = _player(
            current_combat_target="harpie_bug_swarm",
            slayer_level=33,
            equipment={"shield": "Lit bug lantern"},
        )
        active_but_unprotected = _player(
            current_combat_target="harpie_bug_swarm",
            slayer_level=33,
            combat_encounter={
                "target_id": "harpie_bug_swarm",
                "enemy_lifepoints": 100,
            },
        )

        for player_data in (missing, unlit, active_but_unprotected):
            with self.subTest(equipment=player_data.get("equipment", {})):
                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        player_data, "harpie_bug_swarm", COMBAT_ENEMY_DATA
                    ),
                    (warning,),
                )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                equipped, "harpie_bug_swarm", COMBAT_ENEMY_DATA
            ),
            (),
        )

    def test_harpie_bug_swarm_keeps_main_and_charm_selectors_independent(self):
        harpie = COMBAT_ENEMY_DATA["harpie_bug_swarm"]

        self.assertEqual(harpie["attack_speed"], 6)
        self.assertEqual(harpie["slayer_xp"], 25.0)
        self.assertEqual(
            _combat_roll_drops(harpie, _rng((0.0, 0.0))),
            {"Gold ore": 1, "Gold charm": 1},
        )
        self.assertEqual(
            _combat_roll_drops(harpie, _rng((0.999999, 3 / 202))),
            {"Green charm": 1},
        )

    def test_killerwatt_attack_channel_follows_player_distance_style(self):
        killerwatt = COMBAT_ENEMY_DATA["killerwatt"]

        self.assertEqual(
            _combat_enemy_attack_class(killerwatt, "melee"), "magic"
        )
        self.assertEqual(
            _combat_enemy_protection_class(killerwatt, "melee"), "melee"
        )
        for player_class in ("ranged", "magic"):
            with self.subTest(player_class=player_class):
                self.assertEqual(
                    _combat_enemy_attack_class(killerwatt, player_class),
                    "ranged",
                )
                self.assertEqual(
                    _combat_enemy_protection_class(killerwatt, player_class),
                    "ranged",
                )

    def test_killerwatt_uninsulated_cloud_damage_is_additive(self):
        base = _player(
            current_combat_target="killerwatt",
            slayer_level=37,
            quests={"ernest_the_chicken": {"completed": True}},
            combat_attack_style="melee_accurate",
            combat_lifepoints=990,
            constitution_level=99,
        )
        protected = {
            **base,
            "equipment": {"feet": "Insulated boots"},
        }

        _protected_data, protected_ok, protected_result = apply_combat_burst_pure(
            protected,
            COMBAT_ENEMY_DATA,
            {},
            rng=lambda: 0.999999,
            ticks=9,
        )
        _unprotected_data, unprotected_ok, unprotected_result = apply_combat_burst_pure(
            base,
            COMBAT_ENEMY_DATA,
            {},
            rng=lambda: 0.999999,
            ticks=9,
        )

        self.assertTrue(protected_ok)
        self.assertTrue(unprotected_ok)
        self.assertEqual(protected_result["enemy_damage"], 0)
        self.assertEqual(unprotected_result["enemy_damage"], 140)
        self.assertEqual(unprotected_result["unprotected_attacks"], 1)
        self.assertIn("0–140 LP", unprotected_result["protection_warning"])

    def test_killerwatt_preserves_exact_main_and_charm_selectors(self):
        killerwatt = COMBAT_ENEMY_DATA["killerwatt"]

        self.assertEqual(killerwatt["attack_speed"], 8)
        self.assertEqual(killerwatt["slayer_xp"], 51.0)
        self.assertEqual(
            _combat_roll_drops(killerwatt, _rng((0.0, 0.0))),
            {"Impious ashes": 1, "Grimy guam": 1, "Gold charm": 1},
        )
        self.assertEqual(
            _combat_roll_drops(killerwatt, _rng((0.999999, 42 / 303))),
            {"Impious ashes": 1, "Green charm": 1},
        )

    def test_bush_snake_preserves_period_combat_and_hide_range(self):
        snake = COMBAT_ENEMY_DATA["bush_snake"]

        self.assertEqual(snake["display_name"], "Bush snake")
        self.assertEqual(snake["group"], "Animals")
        self.assertEqual(snake["level"], 35)
        self.assertEqual(snake["stats"]["hitpoints"], 250)
        self.assertEqual(snake["max_hit"], 38)
        self.assertEqual(snake["poison_damage"], 7)
        self.assertEqual(snake["attack_style"], "melee")
        self.assertEqual(snake["attack_speed"], 7)
        self.assertEqual(snake["respawn_delay"], 59)
        self.assertEqual(snake["skill_requirements"], {"woodcutting": 10})
        self.assertEqual(snake["quest_gate"], "jungle_potion")
        self.assertEqual(snake["quest_gate_label"], "Complete Jungle Potion")
        self.assertEqual(snake["required_item_options"], (("Machete",),))
        self.assertEqual(snake["required_item_options_label"], "Machete")
        self.assertEqual(snake["drops"]["guaranteed"], (("Bones", 1),))
        (hide_table,) = snake["drops"]["tables"]
        self.assertEqual(hide_table["total"], 1)
        self.assertEqual(
            hide_table["slots"],
            ({"item": "Snake hide", "quantity_range": (1, 5), "slots": 1},),
        )
        self.assertEqual(
            _combat_roll_drops(snake, _rng((0.0, 0.0))),
            {"Bones": 1, "Snake hide": 1},
        )
        self.assertEqual(
            _combat_roll_drops(snake, _rng((0.999999, 0.999999))),
            {"Bones": 1, "Snake hide": 5},
        )
        for source_marker in (
            "oldids 6352282 and 5190727",
            "oldid 6009794",
            "oldid 6539724",
            "oldid 6555418",
            "OpenRS2 rev-742 NPCs 2489/2490 and item 6287",
            "bush_snake (noanims).json @ 14e49a561bab1441384022421d10dc03a8d837f0",
            "drops/bush_snake.json @ c6fbe036b1743f4dd6067ec178332c69c3708856",
        ):
            self.assertIn(source_marker, snake["source"])
        self.assertIn("attackDelay=3", snake["source_status"])
        self.assertIn("rounds 68 LP to 70 LP", snake["source_status"])
        self.assertIn(
            "combat.bush_snake_hide_quantity_distribution",
            snake["source_status"],
        )
        self.assertIn("combat.bush_snake_combat_bonuses", snake["source_status"])
        self.assertIn("without claiming an encounter frequency", snake["source_status"])

    def test_sea_snake_variants_preserve_cutoff_combat_and_poison(self):
        hatchling = COMBAT_ENEMY_DATA["sea_snake_hatchling"]
        young = COMBAT_ENEMY_DATA["sea_snake_young"]

        self.assertEqual(
            (
                hatchling["level"],
                hatchling["stats"]["hitpoints"],
                hatchling["max_hit"],
                hatchling["poison_damage"],
                hatchling["slayer_xp"],
            ),
            (62, 500, 69, 5, 50.0),
        )
        self.assertEqual(
            (
                young["level"],
                young["stats"]["hitpoints"],
                young["max_hit"],
                young["poison_damage"],
                young["slayer_xp"],
            ),
            (90, 850, 84, 7, 85.0),
        )
        self.assertEqual(hatchling["attack_speed"], 6)
        self.assertEqual(young["attack_speed"], 6)
        self.assertEqual(young["required_slayer_level"], 40)
        self.assertEqual(hatchling["quest_gate"], "royal_trouble")
        self.assertEqual(young["quest_gate"], "royal_trouble")

    def test_sea_snake_drop_tables_remain_independent_and_exact(self):
        hatchling = COMBAT_ENEMY_DATA["sea_snake_hatchling"]
        young = COMBAT_ENEMY_DATA["sea_snake_young"]

        for enemy in (hatchling, young):
            for table in enemy["drops"]["tables"]:
                with self.subTest(enemy=enemy["display_name"], table=table["name"]):
                    self.assertEqual(
                        sum(slot["slots"] for slot in table["slots"]),
                        table["total"],
                    )

        self.assertEqual(
            _combat_roll_drops(hatchling, _rng((0.0, 0.0))),
            {
                "Bones": 1,
                "Casket": 1,
                "Clue scroll (medium)": 1,
            },
        )
        self.assertEqual(
            _combat_roll_drops(
                hatchling,
                _rng((11700.5 / 13000, 0.0)),
            ),
            {
                "Bones": 1,
                "Pearl bolt tips": 3,
                "Clue scroll (medium)": 1,
            },
        )
        self.assertEqual(
            _combat_roll_drops(
                hatchling,
                _rng((11725.5 / 13000, 0.999999)),
            ),
            {"Bones": 1, "Spirit weed seed": 1},
        )
        self.assertEqual(
            _combat_roll_drops(
                hatchling,
                _rng((11726 / 13000, 0.999999)),
            ),
            {"Bones": 1},
        )
        self.assertEqual(
            _combat_roll_drops(young, _rng((0.0, 0.0, 0.0))),
            {
                "Big bones": 1,
                "Coins": 44,
                "Long bone": 1,
                "Clue scroll (medium)": 1,
            },
        )
        self.assertEqual(
            _combat_roll_drops(
                young,
                _rng((116.5 / 128, 0.999999, 0.999999)),
            ),
            {"Big bones": 1, "Broad arrows": 4},
        )

    def test_brine_rat_preserves_cutoff_combat_access_and_stats(self):
        brine_rat = COMBAT_ENEMY_DATA["brine_rat"]

        self.assertEqual(
            (
                brine_rat["level"],
                brine_rat["stats"]["hitpoints"],
                brine_rat["stats"]["attack"],
                brine_rat["stats"]["strength"],
                brine_rat["stats"]["defence"],
                brine_rat["max_hit"],
                brine_rat["slayer_xp"],
            ),
            (70, 500, 70, 79, 40, 93, 50.0),
        )
        self.assertEqual(brine_rat["attack_speed"], 6)
        self.assertEqual(brine_rat["required_slayer_level"], 47)
        self.assertEqual(brine_rat["quest_gate"], "olafs_quest")
        self.assertEqual(brine_rat["partial_quest_access"]["minimum_stage"], 40)
        self.assertEqual(brine_rat["required_items"], {"Spade": 1})

        underleveled = _player(
            current_combat_target="brine_rat",
            slayer_level=46,
            quests={"olafs_quest": {"completed": True}},
            inventory={"Spade": 1},
        )
        quest_locked = _player(
            current_combat_target="brine_rat",
            slayer_level=47,
            inventory={"Spade": 1},
        )
        missing_spade = _player(
            current_combat_target="brine_rat",
            slayer_level=47,
            quests={"olafs_quest": {"completed": True}},
        )
        ready = _player(
            current_combat_target="brine_rat",
            slayer_level=47,
            quests={"olafs_quest": {"completed": True}},
            inventory={"Spade": 1},
        )

        self.assertEqual(
            combat_target_locked_reasons_pure(
                underleveled, "brine_rat", COMBAT_ENEMY_DATA
            ),
            ("Slayer level 47",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                quest_locked, "brine_rat", COMBAT_ENEMY_DATA
            ),
            ("Complete Olaf's Quest",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                missing_spade, "brine_rat", COMBAT_ENEMY_DATA
            ),
            ("Spade x1 for Brine Rat Cavern (the toolbelt does not count)",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                ready, "brine_rat", COMBAT_ENEMY_DATA
            ),
            (),
        )

    def test_brine_rat_drop_selectors_are_independent_and_exact(self):
        brine_rat = COMBAT_ENEMY_DATA["brine_rat"]

        for table in brine_rat["drops"]["tables"]:
            with self.subTest(table=table["name"]):
                self.assertEqual(
                    sum(slot["slots"] for slot in table["slots"]),
                    table["total"],
                )

        self.assertEqual(
            _combat_roll_drops(brine_rat, _rng((0.0, 0.0, 0.0))),
            {
                "Bones": 1,
                "Raw rat meat": 1,
                "Coins": 1,
                "Gold charm": 1,
                "Clue scroll (medium)": 1,
            },
        )
        self.assertEqual(
            _combat_roll_drops(
                brine_rat,
                _rng((448.5 / 512, 0.999999, 0.999999)),
            ),
            {
                "Bones": 1,
                "Raw rat meat": 1,
                "Brine sabre": 1,
            },
        )
        self.assertEqual(
            _combat_roll_drops(
                brine_rat,
                _rng((0.999999, 133.5 / 606, 0.999999)),
            ),
            {
                "Bones": 1,
                "Raw rat meat": 1,
                "Green charm": 1,
            },
        )

    def test_molanisk_preserves_cutoff_combat_access_and_lure(self):
        molanisk = COMBAT_ENEMY_DATA["molanisk"]

        self.assertEqual(
            (
                molanisk["level"],
                molanisk["stats"]["hitpoints"],
                molanisk["stats"]["attack"],
                molanisk["stats"]["strength"],
                molanisk["stats"]["defence"],
                molanisk["max_hit"],
                molanisk["slayer_xp"],
            ),
            (51, 520, 40, 40, 50, 53, 52.0),
        )
        self.assertEqual(molanisk["attack_speed"], 6)
        self.assertEqual(molanisk["required_slayer_level"], 39)
        self.assertEqual(molanisk["quest_gate"], "death_to_the_dorgeshuun")
        self.assertEqual(molanisk["required_items"], {"Slayer bell": 1})
        self.assertFalse(molanisk["lure"]["consumed"])

        underleveled = _player(
            current_combat_target="molanisk",
            slayer_level=38,
            quests={"death_to_the_dorgeshuun": {"completed": True}},
            inventory={"Slayer bell": 1, "Lit torch": 1},
        )
        quest_locked = _player(
            current_combat_target="molanisk",
            slayer_level=39,
            inventory={"Slayer bell": 1, "Lit torch": 1},
        )
        missing_bell = _player(
            current_combat_target="molanisk",
            slayer_level=39,
            quests={"death_to_the_dorgeshuun": {"completed": True}},
            inventory={"Lit torch": 1},
        )
        missing_light = _player(
            current_combat_target="molanisk",
            slayer_level=39,
            quests={"death_to_the_dorgeshuun": {"completed": True}},
            inventory={"Slayer bell": 1},
        )
        ready = _player(
            current_combat_target="molanisk",
            slayer_level=39,
            quests={"death_to_the_dorgeshuun": {"completed": True}},
            inventory={"Slayer bell": 1},
            equipment={"head": "Mining helmet (lit)"},
        )

        self.assertEqual(
            combat_target_locked_reasons_pure(
                underleveled, "molanisk", COMBAT_ENEMY_DATA
            ),
            ("Slayer level 39",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                quest_locked, "molanisk", COMBAT_ENEMY_DATA
            ),
            ("Complete Death to the Dorgeshuun",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                missing_bell, "molanisk", COMBAT_ENEMY_DATA
            ),
            ("Slayer bell x1 to lure a Molanisk (not consumed)",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                missing_light, "molanisk", COMBAT_ENEMY_DATA
            ),
            (
                "One lit light source in inventory or equipped for the "
                "Dorgesh-Kaan South Dungeon",
            ),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                ready, "molanisk", COMBAT_ENEMY_DATA
            ),
            (),
        )

    def test_molanisk_drop_selectors_are_independent_and_exact(self):
        molanisk = COMBAT_ENEMY_DATA["molanisk"]

        for table in molanisk["drops"]["tables"]:
            with self.subTest(table=table["name"]):
                self.assertEqual(
                    sum(slot["slots"] for slot in table["slots"]),
                    table["total"],
                )

        self.assertEqual(
            _combat_roll_drops(molanisk, _rng((0.0, 0.0))),
            {
                "Bones": 1,
                "Grimy guam": 1,
                "Clue scroll (easy)": 1,
            },
        )
        self.assertEqual(
            _combat_roll_drops(
                molanisk,
                _rng((99396.5 / 100000, 0.999999)),
            ),
            {"Bones": 1, "Mole claw": 1},
        )
        self.assertEqual(
            _combat_roll_drops(
                molanisk,
                _rng((99603.5 / 100000, 0.999999)),
            ),
            {"Bones": 1, "Death rune": 50},
        )

    def test_turoth_preserves_cutoff_combat_and_effective_damage_routes(self):
        turoth = COMBAT_ENEMY_DATA["turoth"]

        self.assertEqual(
            (
                turoth["level"],
                turoth["stats"]["hitpoints"],
                turoth["stats"]["attack"],
                turoth["stats"]["strength"],
                turoth["stats"]["defence"],
                turoth["max_hit"],
                turoth["slayer_xp"],
            ),
            (83, 760, 53, 83, 83, 97, 76.0),
        )
        self.assertEqual(turoth["attack_speed"], 6)
        self.assertEqual(turoth["required_slayer_level"], 55)
        self.assertIs(turoth["poison_immune"], True)
        self.assertEqual(
            turoth["restricted_weapon"],
            {
                "melee_weapons": ("Leaf-bladed spear", "Leaf-bladed sword"),
                "ranged_ammunition": ("Broad arrows", "Broad-tipped bolts"),
                "magic_spells": ("magic_dart",),
            },
        )

        underleveled = _player(
            current_combat_target="turoth",
            slayer_level=54,
            equipment={"weapon": "Leaf-bladed spear"},
        )
        wrong_melee = _player(
            current_combat_target="turoth",
            slayer_level=55,
        )
        spear = _player(
            current_combat_target="turoth",
            slayer_level=55,
            equipment={"weapon": "Leaf-bladed spear"},
        )
        sword = _player(
            current_combat_target="turoth",
            slayer_level=55,
            equipment={"weapon": "Leaf-bladed sword"},
        )
        broad_arrow = _player(
            current_combat_target="turoth",
            slayer_level=55,
            ranged_level=52,
            equipment={"weapon": "Magic shortbow"},
            inventory={"Broad arrows": 10},
        )
        broad_bolt = _player(
            current_combat_target="turoth",
            slayer_level=55,
            ranged_level=61,
            equipment={"weapon": "Rune crossbow"},
            inventory={"Broad-tipped bolts": 10},
        )
        mixed_arrows = _player(
            current_combat_target="turoth",
            slayer_level=55,
            ranged_level=52,
            equipment={"weapon": "Magic shortbow"},
            combat_supply_loadout={
                "ammo": {"Rune arrows": 10, "Broad arrows": 10},
            },
        )
        low_ranged = _player(
            current_combat_target="turoth",
            slayer_level=55,
            ranged_level=51,
            equipment={"weapon": "Magic shortbow"},
            inventory={"Broad arrows": 10},
        )
        wrong_arrow = _player(
            current_combat_target="turoth",
            slayer_level=55,
            ranged_level=99,
            equipment={"weapon": "Magic shortbow"},
            inventory={"Rune arrows": 10},
        )
        magic_dart = _player(
            current_combat_target="turoth",
            slayer_level=55,
            magic_level=50,
            current_combat_spell="magic_dart",
            equipment={"weapon": "Slayer's staff"},
            inventory={"Mind rune": 4, "Death rune": 1},
        )
        wrong_spell = _player(
            current_combat_target="turoth",
            slayer_level=55,
            magic_level=50,
            current_combat_spell="wind_strike",
            equipment={"weapon": "Slayer's staff"},
            inventory={"Air rune": 1, "Mind rune": 1},
        )

        self.assertEqual(
            combat_target_locked_reasons_pure(
                underleveled,
                "turoth",
                COMBAT_ENEMY_DATA,
                equipment_data=EQUIPMENT_DATA,
            ),
            ("Slayer level 55",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                wrong_melee,
                "turoth",
                COMBAT_ENEMY_DATA,
                equipment_data=EQUIPMENT_DATA,
            ),
            ("Turoth weapon: Leaf-bladed spear or Leaf-bladed sword",),
        )
        for ready in (
            spear,
            sword,
            broad_arrow,
            broad_bolt,
            mixed_arrows,
            magic_dart,
        ):
            self.assertEqual(
                combat_target_locked_reasons_pure(
                    ready,
                    "turoth",
                    COMBAT_ENEMY_DATA,
                    equipment_data=EQUIPMENT_DATA,
                ),
                (),
            )
        self.assertEqual(
            combat_target_preview_pure(
                mixed_arrows,
                "turoth",
                COMBAT_ENEMY_DATA,
                EQUIPMENT_DATA,
            )["ammo"],
            "Broad arrows",
        )
        mixed_after, mixed_ok, mixed_result = apply_combat_burst_pure(
            {**mixed_arrows, "combat_auto_flee": False},
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.0, 0.999999, 0.0, 0.999999]),
        )
        self.assertTrue(mixed_ok)
        self.assertEqual(mixed_result["ammo"], "Broad arrows")
        self.assertEqual(mixed_result["ammo_used"], {"Broad arrows": 1})
        self.assertEqual(
            mixed_after["combat_supply_loadout"]["ammo"],
            {"Rune arrows": 10, "Broad arrows": 9},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                low_ranged,
                "turoth",
                COMBAT_ENEMY_DATA,
                equipment_data=EQUIPMENT_DATA,
            ),
            ("Ranged level 52",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                wrong_arrow,
                "turoth",
                COMBAT_ENEMY_DATA,
                equipment_data=EQUIPMENT_DATA,
            ),
            ("Turoth ammunition: Broad arrows or Broad-tipped bolts",),
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(
                wrong_spell,
                "turoth",
                COMBAT_ENEMY_DATA,
                equipment_data=EQUIPMENT_DATA,
            ),
            ("Turoth spell: Magic Dart",),
        )
        self.assertEqual(
            COMBAT_MAGIC_SPELL_DATA["magic_dart"]["required_weapon"],
            "Slayer's staff",
        )

    def test_turoth_drop_selectors_are_independent_and_exact(self):
        turoth = COMBAT_ENEMY_DATA["turoth"]

        for table in turoth["drops"]["tables"]:
            with self.subTest(table=table["name"]):
                self.assertEqual(
                    sum(slot["slots"] for slot in table["slots"]),
                    table["total"],
                )

        self.assertEqual(
            _combat_roll_drops(turoth, _rng((0.0, 0.0, 0.0))),
            {
                "Bones": 1,
                "Grimy guam": 1,
                "Gold charm": 1,
                "Clue scroll (hard)": 1,
            },
        )
        self.assertEqual(
            _combat_roll_drops(
                turoth,
                _rng((99654.5 / 100000, 0.999999, 0.999999)),
            ),
            {"Bones": 1, "Leaf-bladed sword": 1},
        )
        self.assertEqual(
            _combat_roll_drops(
                turoth,
                _rng((0.999999, 34.5 / 1212, 0.999999)),
            ),
            {"Bones": 1, "Green charm": 1},
        )

    def test_wall_beast_can_continue_after_helmet_swap_but_cannot_chain_a_respawn(self):
        continuing = _player(
            current_combat_target="wall_beast",
            slayer_level=35,
            combat_encounter={
                "target_id": "wall_beast",
                "enemy_lifepoints": 1,
            },
            combat_auto_flee=False,
        )

        out, ok, result = apply_combat_burst_pure(
            continuing,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng((0.0, 0.999999, 0.999999)),
        )

        self.assertTrue(ok, result)
        self.assertEqual(result["kills"], 1)
        self.assertEqual(out["combat_encounter"], {})
        self.assertEqual(
            combat_target_locked_reasons_pure(
                out, "wall_beast", COMBAT_ENEMY_DATA
            ),
            ("Equip a Spiny helmet to start fighting Wall beasts",),
        )

    def test_wall_beast_poison_immunity_suppresses_smoke_spell_poison_damage(self):
        player = _player(
            current_combat_target="wall_beast",
            current_combat_spell="smoke_rush",
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff"},
            slayer_level=35,
            quests={"desert_treasure": {"completed": True}},
            combat_supply_loadout={
                "runes": {
                    "Air rune": 1,
                    "Fire rune": 1,
                    "Chaos rune": 2,
                    "Death rune": 2,
                },
            },
            combat_encounter={
                "target_id": "wall_beast",
                "enemy_lifepoints": 1050,
            },
            combat_auto_flee=False,
        )

        out, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng((0.0, 0.999999)),
        )

        self.assertTrue(ok, result)
        self.assertEqual(result["spell_id"], "smoke_rush")
        self.assertEqual(result["player_damage"], 129)
        self.assertEqual(out["combat_encounter"]["enemy_lifepoints"], 921)

    def test_unprotected_banshee_uses_period_damage_and_flat_eight_skill_drain(self):
        player = _player(
            current_combat_target="banshee",
            attack_level=12,
            strength_level=11,
            defense_level=10,
            ranged_level=9,
            prayer_level=8,
            magic_level=7,
            agility_level=6,
            summoning_level=5,
            constitution_level=99,
            combat_lifepoints=990,
            combat_auto_flee=False,
        )

        out, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=13,
            rng=lambda: 0.999999,
        )

        self.assertTrue(ok)
        self.assertEqual(result["unprotected_attacks"], 2)
        self.assertEqual(result["enemy_damage"], 160)
        self.assertEqual(out["combat_lifepoints"], 830)
        self.assertEqual(
            out["combat_current_levels"],
            {
                "attack": 2,
                "strength": 1,
                "defense": 1,
                "ranged": 1,
                "prayer": 1,
                "magic": 1,
                "agility": 1,
                "summoning": 1,
            },
        )
        self.assertEqual(
            result["stat_drains"],
            {
                "attack": 10,
                "strength": 10,
                "defense": 9,
                "ranged": 8,
                "prayer": 7,
                "magic": 6,
                "agility": 5,
                "summoning": 4,
            },
        )

    def test_earmuffs_restore_banshee_to_ordinary_accuracy_rolls(self):
        out, ok, result = apply_combat_burst_pure(
            _player(
                current_combat_target="banshee",
                equipment={"head": "Earmuffs"},
                constitution_level=60,
                combat_lifepoints=600,
                combat_auto_flee=False,
            ),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=13,
            rng=lambda: 0.999999,
        )

        self.assertTrue(ok)
        self.assertEqual(result["unprotected_attacks"], 0)
        self.assertEqual(result["enemy_damage"], 0)
        self.assertEqual(out["combat_lifepoints"], 600)
        self.assertEqual(out["combat_current_levels"], {})

class CombatAttackTypeResolverTest(unittest.TestCase):
    """D1/D2/D3 attack-type feature: the equipped weapon's AttackStyleData slots
    drive which stab/slash/crush bonus the formula uses and which skill the XP
    trains, including the two-handed-sword aggressive/crush/SHARED anomaly."""

    def _melee(self, weapon, weapon_style, style_type="auto"):
        return _player(
            equipment={"weapon": weapon},
            combat_attack_style=weapon_style,
            combat_attack_style_type=style_type,
        )

    def test_resolver_picks_the_weapons_slot_for_each_style(self):
        cases = {
            # weapon, weapon_style -> (style_type, xp_style_id)
            ("Bronze dagger", "accurate"): ("stab", "accurate"),
            ("Bronze longsword", "controlled"): ("stab", "controlled"),
            ("Bronze mace", "accurate"): ("crush", "accurate"),
            ("Bronze spear", "controlled"): ("stab", "controlled"),
        }
        for (weapon, style), expected in cases.items():
            with self.subTest(weapon=weapon, style=style):
                self.assertEqual(
                    combat_melee_attack_type_pure(self._melee(weapon, style), EQUIPMENT_DATA),
                    expected,
                )

    def test_axe_aggressive_crush_slot_is_distinct_from_aggressive_slash(self):
        # AXE has two aggressive slots (slash then crush); the style_type
        # preference selects between them without changing the xp routing.
        battleaxe = "Bronze battleaxe"
        self.assertEqual(
            combat_melee_attack_type_pure(self._melee(battleaxe, "aggressive", "slash"), EQUIPMENT_DATA),
            ("slash", "aggressive"),
        )
        self.assertEqual(
            combat_melee_attack_type_pure(self._melee(battleaxe, "aggressive", "crush"), EQUIPMENT_DATA),
            ("crush", "aggressive"),
        )

    def test_two_handed_sword_aggressive_crush_shared_anomaly(self):
        # The 2h slot 3 is weaponStyle=AGGRESSIVE (so effective-level uses the
        # aggressive weapon_style) but xpMode=SHARED, so XP is split like
        # controlled. This is the only slot where the two diverge.
        crush_slot = self._melee("Bronze 2h sword", "aggressive", "crush")
        self.assertEqual(
            combat_melee_attack_type_pure(crush_slot, EQUIPMENT_DATA),
            ("crush", "controlled"),
        )
        # Same weapon_style with auto/slash stays the plain aggressive slot.
        self.assertEqual(
            combat_melee_attack_type_pure(self._melee("Bronze 2h sword", "aggressive"), EQUIPMENT_DATA),
            ("slash", "aggressive"),
        )

    def test_unarmed_falls_back_to_crush_and_snaps_unavailable_styles(self):
        # D3: bare fists use the UNARMED table (all crush). A stored style the
        # table does not offer (controlled) snaps to the first slot.
        self.assertEqual(
            combat_melee_attack_type_pure(self._melee(None, "accurate"), EQUIPMENT_DATA),
            ("crush", "accurate"),
        )
        fists = _player(equipment={}, combat_attack_style="controlled")
        self.assertEqual(
            combat_melee_attack_type_pure(fists, EQUIPMENT_DATA),
            ("crush", "accurate"),
        )

    def test_two_handed_crush_slot_shares_xp_through_a_full_burst(self):
        # End-to-end: the SHARED anomaly must route XP three ways even though the
        # weapon_style is aggressive. A plain aggressive slot trains strength only.
        shared = self._melee("Bronze 2h sword", "aggressive", "crush")
        new_shared, ok, result = apply_combat_burst_pure(
            shared, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=50, rng=_rng([0.0, 0.999999, 0.0])
        )
        self.assertTrue(ok and result["killed"])
        self.assertGreater(new_shared["attack_exp"], 0.0)
        self.assertGreater(new_shared["strength_exp"], 0.0)
        self.assertGreater(new_shared["defense_exp"], 0.0)

        pure = self._melee("Bronze 2h sword", "aggressive", "slash")
        new_pure, ok, result = apply_combat_burst_pure(
            pure, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=50, rng=_rng([0.0, 0.999999, 0.0])
        )
        self.assertTrue(ok and result["killed"])
        self.assertEqual(new_pure["attack_exp"], 0.0)
        self.assertEqual(new_pure["defense_exp"], 0.0)
        self.assertGreater(new_pure["strength_exp"], 0.0)

    def test_ranged_and_magic_have_no_style_type(self):
        bow = _player(
            equipment={"weapon": "Shortbow"},
            combat_attack_style="ranged_rapid",
            inventory={"Bronze arrows": 5},
        )
        self.assertEqual(combat_melee_attack_type_pure(bow, EQUIPMENT_DATA), (None, "ranged_rapid"))

    def test_weapon_style_options_name_the_attack_type_per_slot(self):
        options = combat_weapon_style_options_pure(
            self._melee("Bronze longsword", "aggressive"), EQUIPMENT_DATA
        )
        self.assertEqual(
            [(o["weapon_style"], o["style_type"], o["display_name"]) for o in options],
            [
                ("accurate", "slash", "Accurate (Slash)"),
                ("aggressive", "slash", "Aggressive (Slash)"),
                ("controlled", "stab", "Controlled (Stab)"),
                ("defensive", "slash", "Defensive (Slash)"),
            ],
        )
        # Exactly the aggressive/slash slot is current.
        self.assertEqual([o["is_current"] for o in options], [False, True, False, False])

    def test_slots_transcribe_the_unarmed_table_for_typeless_weapons(self):
        slots = combat_weapon_attack_style_slots_pure(_player(equipment={}), EQUIPMENT_DATA)
        self.assertEqual(
            [(s["weapon_style"], s["style_type"]) for s in slots],
            [("accurate", "crush"), ("aggressive", "crush"), ("defensive", "crush")],
        )


class CombatAttackTypeParityTest(unittest.TestCase):
    """D1 parity: the chosen attack type selects the exact per-type bonus rather
    than the old best-of-three max(). max() only survives when no concrete type is
    resolved (enemy-side rolls carry no melee sub-type)."""

    _TOTALS = {"attack_stab": 5, "attack_slash": 40, "attack_crush": 12,
               "defence_stab": 7, "defence_slash": 50, "defence_crush": 3}

    def test_attack_bonus_uses_the_specific_type(self):
        self.assertEqual(_combat_attack_bonus_from_totals(self._TOTALS, style_type="stab"), 5)
        self.assertEqual(_combat_attack_bonus_from_totals(self._TOTALS, style_type="crush"), 12)

    def test_defence_bonus_uses_the_specific_type(self):
        self.assertEqual(_combat_defence_bonus_from_totals(self._TOTALS, style_type="crush"), 3)
        self.assertEqual(_combat_defence_bonus_from_totals(self._TOTALS, style_type="slash"), 50)

    def test_unresolved_type_keeps_max_fallback(self):
        # No style_type (e.g. enemy-side rolls) -> best-of-three, as before.
        self.assertEqual(_combat_attack_bonus_from_totals(self._TOTALS), 40)
        self.assertEqual(_combat_defence_bonus_from_totals(self._TOTALS), 50)


if __name__ == "__main__":
    unittest.main()
