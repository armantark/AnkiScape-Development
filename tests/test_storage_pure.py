import ast
import importlib
from pathlib import Path
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.storage_pure import (
    _SUPPORTED_ACTIVITY_SESSION_IDS,
    default_player_data,
    migrate_loaded_data,
    CURRENT_CONFIG_VERSION,
)
from ankiscape.logic.inventory_pure import DEFAULT_LOOT_VALUE_THRESHOLD
from ankiscape.logic_pure.logic_pure import refill_combat_supply_loadout_pure
from ankiscape.logic.wicked_hood_logic import default_wicked_hood_state_pure
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.data.daily_challenges_data import DAILY_CHALLENGE_DATA
from ankiscape.data.stronghold_player_safety_data import (
    STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS,
)
from ankiscape.core.constants import (
    BAR_DATA,
    CONSTITUTION_STARTING_EXP,
    CRAFTING_DATA,
    DUNGEONEERING_EXP_TABLE,
    EQUIPMENT_DATA,
    FIREMAKING_DATA,
    FIREMAKING_LOG_ITEMS,
    FIREMAKING_OUTPUT_ITEMS,
    FISHING_DATA,
    FISHING_OUTPUT_ITEMS,
    COOKING_DATA,
    COOKING_OUTPUT_ITEMS,
    FLETCHING_DATA,
    GEM_DATA,
    HUNTER_DATA,
    HUNTER_OUTPUT_ITEMS,
    ITEM_DEFINITIONS,
    MINING_OUTPUT_ITEMS,
    ORE_DATA,
    RUNECRAFTING_ACCESS_ITEMS,
    RUNECRAFTING_EXTRA_ITEM_DATA,
    RUNECRAFTING_OUTPUT_ITEMS,
    UTILITY_ACTIVITY_DATA,
    WOODCUTTING_LOG_ITEMS,
)


def _activity_session_writer_ids():
    project_root = Path(__file__).resolve().parents[1]
    owner_ids = set()
    unresolved = []
    parameterized_writers = set()
    for directory in ("logic", "logic_pure"):
        for path in sorted((project_root / directory).glob("*.py")):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            module = None
            assignment_owners = {}
            for function in (
                node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            ):
                for child in ast.walk(function):
                    if isinstance(child, ast.Assign):
                        assignment_owners[id(child)] = function
            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign):
                    continue
                writes_session = any(
                    isinstance(target, ast.Subscript)
                    and isinstance(target.slice, ast.Constant)
                    and target.slice.value == "activity_session"
                    for target in node.targets
                )
                if not writes_session:
                    continue
                value = node.value
                if (
                    isinstance(value, ast.Call)
                    and isinstance(value.func, ast.Name)
                    and value.func.id.startswith("_empty")
                ):
                    continue
                if not isinstance(value, ast.Dict):
                    unresolved.append((path.name, node.lineno, ast.unparse(value)))
                    continue
                entries = {
                    key.value: entry
                    for key, entry in zip(value.keys, value.values)
                    if isinstance(key, ast.Constant)
                }
                active_id = entries.get("active_id")
                if isinstance(active_id, ast.Constant) and isinstance(
                    active_id.value, str
                ):
                    resolved = active_id.value
                elif isinstance(active_id, ast.Name):
                    if module is None:
                        relative = path.relative_to(project_root).with_suffix("")
                        module = importlib.import_module(
                            f"ankiscape.{'.'.join(relative.parts)}"
                        )
                    if hasattr(module, active_id.id):
                        resolved = getattr(module, active_id.id)
                    else:
                        function = assignment_owners.get(id(node))
                        parameters = (
                            {
                                argument.arg
                                for argument in (
                                    function.args.posonlyargs
                                    + function.args.args
                                    + function.args.kwonlyargs
                                )
                            }
                            if function is not None
                            else set()
                        )
                        if active_id.id not in parameters:
                            unresolved.append(
                                (path.name, node.lineno, active_id.id)
                            )
                            continue
                        parameterized_writers.add(function.name)
                        continue
                else:
                    unresolved.append(
                        (
                            path.name,
                            node.lineno,
                            ast.unparse(active_id) if active_id is not None else "",
                        )
                    )
                    continue
                if resolved:
                    owner_ids.add(resolved)

    for directory in ("logic", "logic_pure"):
        for path in sorted((project_root / directory).glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            module = None
            for node in ast.walk(tree):
                if not (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id in parameterized_writers
                ):
                    continue
                value = next(
                    (keyword.value for keyword in node.keywords if keyword.arg == "activity_id"),
                    None,
                )
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    owner_ids.add(value.value)
                elif isinstance(value, ast.Name):
                    if module is None:
                        relative = path.relative_to(project_root).with_suffix("")
                        module = importlib.import_module(
                            f"ankiscape.{'.'.join(relative.parts)}"
                        )
                    owner_ids.add(getattr(module, value.id))
                else:
                    unresolved.append(
                        (path.name, node.lineno, ast.unparse(value) if value else "")
                    )
    return owner_ids, unresolved


class TestStoragePure(unittest.TestCase):
    def test_pre_toolbelt_ceremony_schema_preserves_auto_resolved_bank_tools(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 105,
                "inventory": {
                    "Rune pickaxe": 1,
                    "Rune hatchet": 1,
                    "Inferno adze": 1,
                },
                "toolbelt": {
                    "mining": ["bronze_pickaxe"],
                    "woodcutting": ["bronze_hatchet"],
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertIn("rune_pickaxe", migrated["toolbelt"]["mining"])
        self.assertIn("rune_hatchet", migrated["toolbelt"]["woodcutting"])
        self.assertIn("inferno_adze", migrated["toolbelt"]["mining"])
        self.assertIn("inferno_adze", migrated["toolbelt"]["woodcutting"])
        self.assertEqual(migrated["inventory"]["Rune pickaxe"], 0)
        self.assertEqual(migrated["inventory"]["Rune hatchet"], 0)
        self.assertEqual(migrated["inventory"]["Inferno adze"], 0)

    def test_current_schema_does_not_auto_attach_newly_bought_tools(self):
        migrated = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "inventory": {"Dragon pickaxe": 1},
                "toolbelt": {
                    "mining": ["bronze_pickaxe"],
                    "woodcutting": ["bronze_hatchet"],
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["inventory"]["Dragon pickaxe"], 1)
        self.assertNotIn("dragon_pickaxe", migrated["toolbelt"]["mining"])

    def test_v85_migrates_and_repairs_treasure_trail_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 82,
                "inventory": {"Clue scroll (easy)": 1},
                "activity_session": {"active_id": "treasure_trail"},
                "treasure_trail": {
                    "tier": "easy",
                    "steps": ["simple_port_sarim_sailor", "not_a_real_step"],
                    "index": 40,
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["treasure_trail"]["steps"], ["simple_port_sarim_sailor"]
        )
        self.assertEqual(migrated["treasure_trail"]["index"], 0)
        self.assertEqual(migrated["treasure_trails_completed"], 0)

    def test_v84_migrates_and_repairs_daily_challenge_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 81,
                "inventory": {"Challenge Mystery Bag": 1},
                "daily_challenges": [
                    {"challenge_id": "gone_from_the_catalog", "progress": 3},
                    {
                        "instance_id": "mining_clay-2",
                        "challenge_id": "mining_clay",
                        "day": 2,
                        "progress": 500,
                    },
                ],
                "daily_challenge_pinned": "gone_from_the_catalog-1",
                "daily_challenge_bag_values": [40, 50, 60],
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(len(migrated["daily_challenges"]), 1)
        self.assertEqual(
            migrated["daily_challenges"][0]["progress"],
            DAILY_CHALLENGE_DATA["mining_clay"]["required"],
        )
        self.assertEqual(migrated["daily_challenge_pinned"], "")
        self.assertEqual(migrated["daily_challenge_bag_values"], [40])

    def test_a_new_save_starts_with_an_empty_noticeboard_and_no_trail(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(data["treasure_trail"], {})
        self.assertEqual(data["daily_challenges"], [])
        self.assertEqual(data["daily_challenge_day"], 0)
        self.assertEqual(data["daily_challenge_blocked_skills"], [])

    def test_v81_migrates_and_repairs_tzhaar_fight_pit_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 80,
                "inventory": {},
                "activity_session": {"active_id": "tzhaar_fight_pit"},
                "tzhaar_fight_pit_policy": "invalid",
                "tzhaar_fight_pit": {
                    "match_number": 1,
                    "review": -4,
                    "policy": "invalid",
                    "roster": [
                        {
                            "opponent_id": "rival",
                            "combat_level": 999,
                            "lifepoints": 99999,
                        }
                    ],
                    "engaged_opponent_id": "rival",
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["activity_session"], {"active_id": "tzhaar_fight_pit"})
        self.assertEqual(migrated["tzhaar_fight_pit_policy"], "casual")
        self.assertEqual(migrated["tzhaar_fight_pit"]["review"], 0)
        rival = migrated["tzhaar_fight_pit"]["roster"][0]
        self.assertEqual(rival["combat_level"], 138)
        self.assertLessEqual(rival["lifepoints"], rival["maximum_lifepoints"])

    def test_v80_migrates_and_repairs_shades_of_mortton_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 79,
                "inventory": {},
                "activity_session": {"active_id": "shades_of_mortton"},
                "shades_of_mortton_policy": {
                    "automation_mode": "invalid",
                    "duty": "invalid",
                },
                "shades_of_mortton": {
                    "active": True,
                    "temple_repair": 999,
                    "sanctity_tenths": -8,
                    "resources": 999,
                    "sanctity_decay_progress": 99,
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["shades_of_mortton_policy"],
            {"automation_mode": "casual", "duty": "repair"},
        )
        self.assertEqual(migrated["shades_of_mortton"]["temple_repair"], 100)
        self.assertEqual(migrated["shades_of_mortton"]["sanctity_tenths"], 0)
        self.assertEqual(migrated["shades_of_mortton"]["resources"], 100)
        self.assertEqual(migrated["shades_of_mortton"]["sanctity_decay_progress"], 9)

    def test_v79_migrates_and_repairs_soul_wars_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 78,
                "inventory": {},
                "activity_session": {"active_id": "soul_wars"},
                "soul_wars_zeal": 99_999,
                "soul_wars_policy": {
                    "automation_mode": "invalid",
                    "duty": "invalid",
                    "team": "invalid",
                },
                "soul_wars": {"review": 999, "control_balance": 99},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["soul_wars_zeal"], 50_000)
        self.assertEqual(
            migrated["soul_wars_policy"],
            {"automation_mode": "casual", "duty": "fragments", "team": "balance"},
        )
        self.assertEqual(migrated["soul_wars"]["review"], 11)
        self.assertEqual(migrated["soul_wars"]["control_balance"], 3)

    def test_default_player_data_has_expected_keys(self):
        data = default_player_data(ORE_DATA)
        # Core keys
        for key in [
            "config_version",
            "mining_level",
            "woodcutting_level",
            "smithing_level",
            "crafting_level",
            "fletching_level",
            "firemaking_level",
            "fishing_level",
            "cooking_level",
            "runecrafting_level",
            "hunter_level",
            "mining_exp",
            "woodcutting_exp",
            "smithing_exp",
            "crafting_exp",
            "fletching_exp",
            "firemaking_exp",
            "fishing_exp",
            "cooking_exp",
            "runecrafting_exp",
            "hunter_exp",
            "current_craft",
            "current_fletch",
            "current_firemaking",
            "current_fishing",
            "current_cooking",
            "current_runecrafting",
            "current_hunter",
            "current_utility",
            "current_quest",
            "current_combat_target",
            "combat_attack_style",
            "current_combat_spell",
            "combat_lifepoints",
            "combat_auto_eat_threshold_percent",
            "combat_auto_eat_food",
            "combat_supply_loadout",
            "combat_special_attack_energy",
            "combat_current_levels",
            "combat_status_effects",
            "combat_recovery_progress",
            "combat_encounter",
            "combat_kill_counts",
            "combat_last_result",
            "combat_grave",
            "death_office",
            "current_ore",
            "current_tree",
            "current_smith",
            "inventory",
            "progress_to_next",
            "completed_achievements",
            "toolbelt",
            "equipment",
            "attack_level",
            "defense_level",
            "dungeoneering_level",
            "dungeoneering_exp",
            "ranged_level",
            "strength_level",
            "agility_level",
            "agility_exp",
            "constitution_level",
            "cooking_success_count",
            "cooking_burn_count",
            "hunter_success_count",
            "action_telemetry",
            "achievement_progress",
            "quests",
            "quest_points",
            "quest_combat_config",
            "quest_combat_encounters",
            "quest_combat_encounter_counts",
            "quest_action_proofs",
            "quest_route_states",
            "pending_skill_exp_rewards",
            "claims",
            "wicked_hood",
            "runecrafting_pouches",
            "item_charges",
            "unlocked_abilities",
            "carried_inventory",
            "loot_value_threshold",
            "shop_data_version",
            "shop_market_clock",
            "shop_stock_state",
            "shop_events",
            "shop_next_event_id",
            "ge_state_version",
            "ironman_mode",
            "ironman_account_type",
            "ge_settings",
            "ge_market_state",
            "ge_player_orders",
            "ge_next_order_id",
            "ge_buy_limit_usage",
            "ge_trade_history",
            "ge_fill_log",
            "hunter_private_ground_targets",
            "big_chinchompa",
            "shooting_star",
            "fist_of_guthix",
        ]:
            self.assertIn(key, data)
        # Inventory uses real item names; Mining targets use stable IDs.
        for ore in MINING_OUTPUT_ITEMS:
            self.assertIn(ore, data["inventory"])  # zero by default
        self.assertEqual(data["config_version"], CURRENT_CONFIG_VERSION)
        self.assertIn("bronze_pickaxe", data["toolbelt"]["mining"])
        self.assertEqual(data["equipment"], {})
        self.assertEqual(data["attack_level"], 1)
        self.assertEqual(data["defense_level"], 1)
        self.assertEqual(data["dungeoneering_level"], 1)
        self.assertEqual(data["dungeoneering_exp"], 0)
        self.assertEqual(data["agility_level"], 1)
        self.assertEqual(data["agility_exp"], 0)
        self.assertEqual(data["slayer_level"], 1)
        self.assertEqual(data["slayer_exp"], 0)
        self.assertEqual(data["slayer_assignment"], {})
        self.assertEqual(data["slayer_tasks_completed"], 0)
        self.assertFalse(data["slayer_combat_filter"])
        self.assertEqual(data["constitution_level"], 10)
        self.assertEqual(data["constitution_exp"], CONSTITUTION_STARTING_EXP)
        self.assertEqual(data["current_runecrafting"], "craft_air_runes")
        self.assertEqual(data["current_hunter"], "catch_crimson_swift")
        self.assertEqual(data["hunter_success_count"], 0)
        self.assertNotIn("world_population_profile", data)
        self.assertEqual(data["hunter_private_ground_targets"], [])
        self.assertEqual(data["big_chinchompa"]["competence_points"], 0)
        self.assertEqual(data["shooting_star"]["active_event"], {})
        self.assertEqual(data["shooting_star"]["last_exchange_day"], -1)
        self.assertEqual(data["shooting_star"]["notice"], {})
        self.assertEqual(data["shooting_star"]["watched_event_id"], "")
        self.assertFalse(data["fist_of_guthix"]["tutorial_complete"])
        self.assertEqual(data["fist_of_guthix"]["rating"], 1_000)
        self.assertEqual(data["action_telemetry"], {"version": 1, "actions": {}})
        self.assertEqual(
            data["achievement_progress"],
            {
                "version": 1,
                "skills": {"dungeoneering": {"actions": {}, "outputs": {}}},
            },
        )
        self.assertEqual(data["current_combat_target"], "chicken")
        self.assertEqual(data["combat_action"], "attack")
        self.assertEqual(data["combat_attack_style"], "accurate")
        self.assertEqual(data["current_combat_spell"], "wind_strike")
        self.assertEqual(data["combat_lifepoints"], 100)
        self.assertEqual(data["combat_auto_eat_threshold_percent"], 40)
        self.assertIn("Shrimps", data["combat_auto_eat_food"])
        self.assertEqual(data["combat_supply_loadout"], {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "finishers": {}, "hazards": {}, "cannonballs": 0})
        self.assertEqual(data["combat_special_attack_energy"], 100)
        self.assertEqual(data["combat_current_levels"], {})
        self.assertEqual(data["combat_status_effects"], {})
        self.assertEqual(data["combat_recovery_progress"], {})
        self.assertEqual(data["combat_encounter"], {})
        self.assertEqual(data["combat_kill_counts"], {})
        self.assertEqual(data["combat_last_result"], {})
        self.assertEqual(data["combat_grave"], {})
        self.assertEqual(data["death_office"], {})
        self.assertEqual(data["current_quest"], "rune_mysteries")
        self.assertEqual(data["quest_points"], 0)
        self.assertEqual(data["quests"]["rune_mysteries"], {"started": False, "progress": 0, "completed": False})
        self.assertIn("lost_city", data["quests"])
        self.assertIn("lunar_diplomacy", data["quests"])
        self.assertEqual(data["quest_combat_config"], {"version": 1, "resolver_enabled": False})
        self.assertEqual(data["quest_combat_encounters"], {})
        self.assertEqual(data["quest_combat_encounter_counts"], {})
        self.assertNotIn("quest_stage_actions", data)
        self.assertEqual(data["quest_route_states"], {})
        self.assertEqual(data["pending_skill_exp_rewards"], {})
        self.assertEqual(data["claims"]["wicked_hood"], {"claimed": False})
        self.assertEqual(data["claims"]["tutorial_island_starter_kit"], {"claimed": False})
        self.assertEqual(data["wicked_hood"], default_wicked_hood_state_pure())
        self.assertEqual(data["runecrafting_pouches"], {})
        self.assertEqual(data["item_charges"], {})
        self.assertEqual(data["unlocked_abilities"], [])
        self.assertEqual(data["carried_inventory"], {})
        self.assertEqual(data["loot_value_threshold"], DEFAULT_LOOT_VALUE_THRESHOLD)
        self.assertEqual(data["shop_market_clock"], {"version": 1, "answered_cards": 0, "market_tick": 0})
        self.assertFalse(data["magic_charge_active"])
        self.assertEqual(data["magic_charge_ticks_remaining"], 0)
        self.assertEqual(data["shop_stock_state"], {})
        self.assertEqual(data["shop_events"], [])
        self.assertEqual(data["shop_next_event_id"], 1)
        self.assertFalse(data["ironman_mode"])
        self.assertEqual(data["ironman_account_type"], "unselected")
        self.assertEqual(data["ge_player_orders"], [])
        self.assertEqual(data["ge_next_order_id"], 1)
        self.assertEqual(data["ge_market_state"]["last_processed_tick"], 0)
        self.assertEqual(data["review_context_preferences"], {})

    def test_v118_migration_retires_completion_rewards_already_granted(self):
        legacy = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        legacy["config_version"] = 117
        for quest_id in ("cabin_fever", "rocking_out"):
            legacy["quests"][quest_id] = {
                "started": True,
                "progress": 1,
                "completed": True,
            }
        legacy["claims"].pop("cabin_fever_bill_teach_coins")
        legacy["claims"].pop("rocking_out_bill_teach_magical_cage")

        migrated = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(
            migrated["claims"]["cabin_fever_bill_teach_coins"],
            {"claimed": True},
        )
        self.assertEqual(
            migrated["claims"]["rocking_out_bill_teach_magical_cage"],
            {"claimed": True},
        )

        current = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for quest_id in ("cabin_fever", "rocking_out"):
            current["quests"][quest_id]["completed"] = True
        current = migrate_loaded_data(current, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(
            current["claims"]["cabin_fever_bill_teach_coins"],
            {"claimed": False},
        )
        self.assertEqual(
            current["claims"]["rocking_out_bill_teach_magical_cage"],
            {"claimed": False},
        )

    def test_v119_migration_maps_druidic_ritual_progress_forward(self):
        cases = (
            (False, 0, False, 0),
            (True, 0, False, 0),
            (True, 1, False, 1),
            (True, 2, False, 2),
            (True, 3, False, 6),
            (True, 4, False, 4),
            (True, 4, True, 8),
        )
        for started, old_progress, completed, new_progress in cases:
            with self.subTest(
                started=started, old_progress=old_progress, completed=completed
            ):
                legacy = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                legacy["config_version"] = 118
                legacy["quests"]["druidic_ritual"] = {
                    "started": started,
                    "progress": old_progress,
                    "completed": completed,
                }

                migrated = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)

                state = migrated["quests"]["druidic_ritual"]
                self.assertEqual(state["started"], started)
                self.assertEqual(state["progress"], new_progress)
                self.assertEqual(state["completed"], completed)
                if old_progress == 2:
                    self.assertEqual(migrated["inventory"]["Vial"], 1)
                elif old_progress == 3:
                    self.assertEqual(migrated["inventory"]["Living water"], 1)
                    self.assertEqual(migrated["inventory"]["Wandering wyrmwood"], 1)
                    self.assertEqual(migrated["inventory"]["Stone scales"], 1)

    def test_v119_migration_returns_retired_meats_and_drops_legacy_stage_actions(self):
        legacy = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        legacy["config_version"] = 118
        legacy["quests"]["druidic_ritual"] = {
            "started": True,
            "progress": 3,
            "completed": False,
        }
        legacy["inventory"].update(
            {
                "Raw bear meat": 2,
                "Enchanted bear meat": 1,
                "Enchanted rat meat": 2,
                "Enchanted beef": 3,
                "Enchanted chicken": 4,
            }
        )
        legacy["quest_stage_actions"] = {
            "druidic_ritual": [
                "Speak to Sanfew about the ritual ingredients",
                "Dip the raw meats in the Cauldron of Thunder",
                "Give Sanfew the enchanted meats and return to Kaqemeex",
                "Keep this action",
            ]
        }

        migrated = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["inventory"]["Raw bear meat"], 3)
        self.assertEqual(migrated["inventory"]["Raw rat meat"], 2)
        self.assertEqual(migrated["inventory"]["Raw beef"], 3)
        self.assertEqual(migrated["inventory"]["Raw chicken"], 4)
        for item_name in (
            "Enchanted bear meat",
            "Enchanted rat meat",
            "Enchanted beef",
            "Enchanted chicken",
        ):
            self.assertNotIn(item_name, migrated["inventory"])
        self.assertNotIn("quest_stage_actions", migrated)

        migrated_again = migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated_again["inventory"]["Raw bear meat"], 3)
        self.assertEqual(migrated_again["inventory"]["Raw rat meat"], 2)
        self.assertEqual(migrated_again["inventory"]["Raw beef"], 3)
        self.assertEqual(migrated_again["inventory"]["Raw chicken"], 4)

    def test_current_schema_drops_legacy_stage_actions_without_remigrating_druidic_ritual(self):
        current = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        current["quests"]["druidic_ritual"] = {
            "started": True,
            "progress": 3,
            "completed": False,
        }
        current["inventory"]["Enchanted bear meat"] = 1
        current["quest_stage_actions"] = {
            "druidic_ritual": ["Dip the raw meats in the Cauldron of Thunder"]
        }

        migrated = migrate_loaded_data(current, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["quests"]["druidic_ritual"]["progress"], 3)
        self.assertEqual(migrated["inventory"]["Enchanted bear meat"], 1)
        self.assertEqual(migrated["inventory"].get("Living water", 0), 0)
        self.assertNotIn("quest_stage_actions", migrated)

    def test_v111_migration_restores_constitution_starting_xp_once(self):
        untouched = migrate_loaded_data({"config_version": 110}, ORE_DATA)
        migrated = migrate_loaded_data(
            {
                "config_version": 110,
                "constitution_level": 10,
                "constitution_exp": 353.883075,
            },
            ORE_DATA,
        )

        self.assertEqual(untouched["constitution_exp"], CONSTITUTION_STARTING_EXP)
        self.assertEqual(untouched["constitution_level"], 10)
        self.assertAlmostEqual(
            migrated["constitution_exp"],
            CONSTITUTION_STARTING_EXP + 353.883075,
        )
        self.assertEqual(migrated["constitution_level"], 11)
        self.assertEqual(
            migrate_loaded_data(migrated, ORE_DATA)["constitution_exp"],
            migrated["constitution_exp"],
        )

    def test_migration_removes_population_dial_and_sanitizes_big_chinchompa(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 49,
                "world_population_profile": "crowded",
                "hunter_private_ground_targets": [
                    "catch_swamp_lizard",
                    "not_a_hunter_target",
                    "catch_swamp_lizard",
                ],
                "big_chinchompa": {
                    "competence_points": 99_999,
                    "active_event": {"event_id": "invalid"},
                },
            },
            ORE_DATA,
        )

        self.assertNotIn("world_population_profile", migrated)
        self.assertEqual(
            migrated["hunter_private_ground_targets"],
            ["catch_swamp_lizard"],
        )
        self.assertEqual(
            migrated["big_chinchompa"]["competence_points"],
            20_000,
        )
        self.assertEqual(migrated["big_chinchompa"]["active_event"], {})

    def test_migration_removes_shooting_star_preferences_and_sanitizes_bonus(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 51,
                "shooting_star": {
                    "automation_mode": "ADVANCED",
                    "preferred_sizes": [0, 3, 3, 50],
                    "ore_bonus_ticks_remaining": -20,
                    "active_event": {"event_id": "invalid"},
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertNotIn("automation_mode", migrated["shooting_star"])
        self.assertNotIn("preferred_sizes", migrated["shooting_star"])
        self.assertEqual(
            migrated["shooting_star"]["ore_bonus_ticks_remaining"], 0
        )
        self.assertEqual(migrated["shooting_star"]["active_event"], {})

    def test_migration_preserves_a_bounded_shooting_star_notice_and_watch(self):
        migrated = migrate_loaded_data(
            {
                "shooting_star": {
                    "notice": {
                        "kind": "unminable",
                        "event_id": "shooting-star-20",
                        "current_size": 9,
                        "required_level": 90,
                    },
                    "watched_event_id": "shooting-star-20",
                }
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(
            migrated["shooting_star"]["notice"]["kind"],
            "unminable",
        )
        self.assertEqual(
            migrated["shooting_star"]["watched_event_id"],
            "shooting-star-20",
        )

    def test_migration_sanitizes_fist_of_guthix_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 53,
                "fist_of_guthix": {
                    "tutorial_complete": True,
                    "tokens": -2,
                    "rating": "bad",
                    "selected_stance": "teleport",
                    "active_match": {"opponent": "invalid"},
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertTrue(migrated["fist_of_guthix"]["tutorial_complete"])
        self.assertEqual(migrated["fist_of_guthix"]["tokens"], 0)
        self.assertEqual(migrated["fist_of_guthix"]["rating"], 1_000)
        self.assertEqual(migrated["fist_of_guthix"]["selected_stance"], "hybrid")
        self.assertEqual(migrated["fist_of_guthix"]["active_match"], {})

    def test_migration_sanitizes_grand_exchange_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 43,
                "inventory": {"Coins": 1_000},
                "ironman_mode": False,
                "ge_player_orders": [
                    {
                        "id": 4,
                        "side": "buy",
                        "item_name": "Logs",
                        "original_quantity": 2,
                        "remaining_quantity": 2,
                        "submitted_unit_price": 100,
                        "escrow_coins": 200,
                        "status": "open",
                    }
                ],
                "ge_next_order_id": 2,
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["ge_next_order_id"], 5)
        self.assertEqual(migrated["ge_player_orders"][0]["escrow_coins"], 200)
        self.assertEqual(migrated["ironman_account_type"], "regular")

    def test_migration_preserves_legacy_ironman_account_type(self):
        migrated = migrate_loaded_data(
            {"config_version": 43, "ironman_mode": True},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["ironman_account_type"], "ironman")

    def test_migration_defaults_missing_legacy_ironman_field_to_regular(self):
        migrated = migrate_loaded_data(
            {"config_version": 43},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["ironman_account_type"], "regular")

    def test_migration_without_config_version_defaults_to_regular(self):
        migrated = migrate_loaded_data(
            {},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["ironman_account_type"], "regular")

    def test_v45_migration_adds_and_sanitizes_review_context_preferences(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 44,
                "review_context_preferences": {
                    "pit_reward": "gamble",
                    "unknown_family": "choice",
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["review_context_preferences"],
            {"pit_reward": "gamble"},
        )

    def test_default_player_data_can_seed_registered_items(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        fletching_outputs = [spec["output_item"] for spec in FLETCHING_DATA.values()]
        fletching_materials = [
            material
            for spec in FLETCHING_DATA.values()
            for material in spec.get("requirements", {})
            if material not in WOODCUTTING_LOG_ITEMS
        ]
        utility_outputs = [spec["output_item"] for spec in UTILITY_ACTIVITY_DATA.values() if "output_item" in spec]
        utility_bundle_outputs = [
            item_name
            for spec in UTILITY_ACTIVITY_DATA.values()
            if isinstance(spec.get("outputs"), dict)
            for item_name in spec.get("outputs", {})
        ]
        hunter_materials = [
            material
            for spec in HUNTER_DATA.values()
            for material in spec.get("requirements", {})
        ]
        for item_name in (
            list(MINING_OUTPUT_ITEMS)
            + list(WOODCUTTING_LOG_ITEMS)
            + list(FIREMAKING_LOG_ITEMS)
            + list(BAR_DATA)
            + list(GEM_DATA)
            + [spec["output_item"] for spec in CRAFTING_DATA.values()]
            + fletching_outputs
            + fletching_materials
            + list(FIREMAKING_OUTPUT_ITEMS)
            + list(FISHING_OUTPUT_ITEMS)
            + list(COOKING_OUTPUT_ITEMS)
            + utility_outputs
            + utility_bundle_outputs
            + list(RUNECRAFTING_OUTPUT_ITEMS)
            + list(RUNECRAFTING_ACCESS_ITEMS)
            + list(RUNECRAFTING_EXTRA_ITEM_DATA)
            + list(HUNTER_OUTPUT_ITEMS)
            + hunter_materials
            + ["Beer", "Silk", "Newspaper", "Cowhide", "Leather", "Oak plank"]
        ):
            self.assertIn(item_name, data["inventory"])
            self.assertEqual(data["inventory"][item_name], 0)

    def test_migrate_from_old_schema_total_exp(self):
        old = {
            "total_exp": 123,
            "inventory": {"Copper ore": 2},
            # missing many keys on purpose
        }
        migrated = migrate_loaded_data(old, ORE_DATA)
        # total_exp -> mining_exp, and other exp fields defaulted
        self.assertEqual(migrated["mining_exp"], 123)
        self.assertIn("woodcutting_exp", migrated)
        self.assertIn("smithing_exp", migrated)
        self.assertIn("crafting_exp", migrated)
        self.assertIn("hunter_exp", migrated)
        # Ensure smithing/crafting defaults
        self.assertEqual(migrated["smithing_level"], 1)
        self.assertEqual(migrated["crafting_level"], 1)
        self.assertEqual(migrated["current_smith"], "smelt_bronze_bar")
        self.assertEqual(migrated["current_craft"], "form_pot_unfired")
        self.assertEqual(migrated["current_firemaking"], "logs")
        self.assertEqual(migrated["current_fishing"], "catch_crayfish")
        self.assertEqual(migrated["current_cooking"], "cook_shrimps")
        self.assertEqual(migrated["current_runecrafting"], "craft_air_runes")
        self.assertEqual(migrated["current_hunter"], "catch_crimson_swift")
        self.assertEqual(migrated["hunter_success_count"], 0)
        self.assertEqual(migrated["action_telemetry"], {"version": 1, "actions": {}})
        self.assertEqual(migrated["current_combat_target"], "chicken")
        self.assertEqual(migrated["combat_action"], "attack")
        self.assertEqual(migrated["combat_attack_style"], "accurate")
        self.assertEqual(migrated["current_combat_spell"], "wind_strike")
        self.assertEqual(migrated["combat_lifepoints"], 100)
        self.assertEqual(migrated["combat_supply_loadout"], {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "finishers": {}, "hazards": {}, "cannonballs": 0})
        self.assertEqual(migrated["combat_special_attack_energy"], 100)
        self.assertEqual(migrated["combat_current_levels"], {})
        self.assertNotIn("combat_stat_drains", migrated)
        self.assertEqual(migrated["combat_status_effects"], {})
        self.assertEqual(migrated["combat_recovery_progress"], {})
        self.assertEqual(migrated["combat_encounter"], {})
        self.assertEqual(migrated["combat_kill_counts"], {})
        self.assertEqual(migrated["current_quest"], "rune_mysteries")
        self.assertEqual(migrated["quests"]["rune_mysteries"], {"started": False, "progress": 0, "completed": False})
        self.assertIn("swan_song", migrated["quests"])
        self.assertEqual(migrated["claims"]["wicked_hood"], {"claimed": False})
        self.assertEqual(migrated["claims"]["tutorial_island_starter_kit"], {"claimed": False})
        self.assertEqual(migrated["wicked_hood"], default_wicked_hood_state_pure())
        self.assertEqual(migrated["runecrafting_pouches"], {})
        self.assertEqual(migrated["item_charges"], {})
        self.assertEqual(migrated["current_utility"], "make_soft_clay")
        self.assertEqual(migrated["shop_market_clock"], {"version": 1, "answered_cards": 0, "market_tick": 0})
        self.assertEqual(migrated["shop_stock_state"], {})
        self.assertEqual(migrated["shop_events"], [])
        self.assertEqual(migrated["carried_inventory"], {})
        self.assertEqual(migrated["loot_value_threshold"], DEFAULT_LOOT_VALUE_THRESHOLD)
        # Inventory preserved and completed with ore keys
        self.assertEqual(migrated["inventory"]["Copper ore"], 2)
        for ore in MINING_OUTPUT_ITEMS:
            self.assertIn(ore, migrated["inventory"])  # completed
        # Version bumped
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)

    def test_future_schema_version_is_preserved(self):
        migrated = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION + 7,
                "inventory": {"Future item": 1},
                "farming_exp": float("inf"),
                "farming_level": float("nan"),
                "farm_clock_minutes": float("nan"),
                "farm_patches": {"future_patch": {"future": True}},
                "pending_skill_exp_rewards": {"farming_exp": float("nan"), "summoning_exp": 250},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION + 7)
        self.assertEqual(migrated["inventory"]["Future item"], 1)
        self.assertEqual(migrated["farming_exp"], 0.0)
        self.assertEqual(migrated["farming_level"], 1)
        self.assertEqual(migrated["farm_clock_minutes"], 0)
        self.assertEqual(migrated["farm_patches"]["future_patch"], {"future": True})
        self.assertEqual(migrated["summoning_exp"], 250.0)
        self.assertEqual(migrated["summoning_level"], 3)
        self.assertEqual(migrated["pending_skill_exp_rewards"], {})

    def test_legacy_active_charge_migrates_to_a_full_review_driven_duration(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 37,
                "magic_charge_active": True,
                "inventory": {},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertTrue(migrated["magic_charge_active"])
        self.assertEqual(migrated["magic_charge_ticks_remaining"], 700)

    def test_load_cleans_only_above_base_stale_prayer_current_level(self):
        cleaned = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "prayer_level": 70,
                "combat_current_levels": {"prayer": 80, "attack": 65, "future_skill": 123},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(cleaned["combat_current_levels"], {"attack": 65, "future_skill": 123})

        drained = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "prayer_level": 70,
                "combat_current_levels": {"prayer": 60, "attack": 65},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(drained["combat_current_levels"], {"prayer": 60, "attack": 65})

    def test_migrate_preserves_existing_action_telemetry_rows(self):
        migrated = migrate_loaded_data(
            {
                "action_telemetry": {
                    "version": 1,
                    "actions": {
                        "fishing:catch_mackerel_cod_bass": {
                            "skill_id": "fishing",
                            "action_id": "catch_mackerel_cod_bass",
                            "attempts": 3,
                            "successes": 1,
                            "failures": 2,
                            "expected_successes": 1.2,
                            "current_dry_streak": 2,
                            "longest_dry_streak": 2,
                            "outputs": {"Raw mackerel": 1},
                            "failure_kinds": {"dry": 2},
                        }
                    },
                }
            },
            ORE_DATA,
        )

        telemetry = migrated["action_telemetry"]["actions"]["fishing:catch_mackerel_cod_bass"]
        self.assertEqual(telemetry["attempts"], 3)
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(telemetry["outputs"], {"Raw mackerel": 1})

    def test_v37_migration_seeds_progress_from_telemetry_and_holdings_without_summing(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 36,
                "inventory": {"Iron ore": 7, "Ashes": 3},
                "action_telemetry": {
                    "version": 1,
                    "actions": {
                        "mining:iron_rock": {
                            "skill_id": "mining",
                            "action_id": "iron_rock",
                            "successes": 5,
                            "outputs": {"Iron ore": 5},
                        },
                        "firemaking:normal_logs": {
                            "skill_id": "firemaking",
                            "action_id": "normal_logs",
                            "successes": 10,
                            "outputs": {"Ashes": 10},
                        },
                    },
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        mining = migrated["achievement_progress"]["skills"]["mining"]
        firemaking = migrated["achievement_progress"]["skills"]["firemaking"]
        self.assertEqual(mining["actions"], {"iron_rock": 5})
        self.assertEqual(mining["outputs"]["Iron ore"], 7)
        self.assertEqual(firemaking["outputs"]["Ashes"], 10)

    def test_migrate_drops_legacy_stage_actions_and_sanitizes_quest_side_state(self):
        migrated = migrate_loaded_data(
            {
                "quest_combat_config": {"resolver_enabled": True},
                "quest_combat_encounters": {"dragon_slayer": {"elvarg": True, "unused": False}},
                "quest_combat_encounter_counts": {"toktz_ket_dill": {"lava_monster": "1", "bad": 0, 123: 1}},
                "quest_stage_actions": {"the_knights_sword": "Mine blurite ore"},
                "quest_route_states": {"heroes_quest": ["member_route", 123]},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["quest_combat_config"], {"version": 1, "resolver_enabled": True})
        self.assertEqual(migrated["quest_combat_encounters"], {"dragon_slayer": ["elvarg"]})
        self.assertEqual(migrated["quest_combat_encounter_counts"], {"toktz_ket_dill": {"lava_monster": 1}})
        self.assertNotIn("quest_stage_actions", migrated)
        self.assertEqual(migrated["quest_route_states"], {"heroes_quest": ["member_route"]})

    def test_migrate_can_seed_registered_items_without_losing_custom_entries(self):
        migrated = migrate_loaded_data(
            {"inventory": {"Mystery item": 7, "Oak": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["inventory"]["Mystery item"], 7)
        self.assertNotIn("Oak", migrated["inventory"])
        self.assertEqual(migrated["inventory"]["Oak logs"], 3)
        self.assertIn("Bronze bar", migrated["inventory"])
        self.assertIn("Uncut sapphire", migrated["inventory"])
        self.assertIn("Arrow shafts", migrated["inventory"])
        self.assertIn("Feather", migrated["inventory"])
        self.assertIn("Fishing bait", migrated["inventory"])
        self.assertIn("Raw crayfish", migrated["inventory"])
        self.assertIn("Shrimps", migrated["inventory"])
        self.assertIn("Burnt fish", migrated["inventory"])
        self.assertIn("Air rune", migrated["inventory"])
        self.assertIn("Air talisman", migrated["inventory"])
        self.assertIn("Binding necklace", migrated["inventory"])
        self.assertIn("Wicked hood", migrated["inventory"])
        self.assertIn("Dramen staff", migrated["inventory"])
        self.assertIn("Red feather", migrated["inventory"])
        self.assertIn("Impling jar", migrated["inventory"])
        self.assertIn("Imp-in-a-box (2)", migrated["inventory"])
        self.assertIn("Coins", migrated["inventory"])
        self.assertIn("Soft clay", migrated["inventory"])
        self.assertIn("Ashes", migrated["inventory"])
        self.assertIn("Arctic pine logs", migrated["inventory"])
        self.assertIn("Wool", migrated["inventory"])
        self.assertIn("Flax", migrated["inventory"])
        self.assertIn("bronze_hatchet", migrated["toolbelt"]["woodcutting"])
        self.assertIn("bronze_pickaxe", migrated["toolbelt"]["mining"])
        self.assertEqual(migrated["equipment"], {})
        self.assertNotIn("owned_equipment", migrated)

    def test_migrate_pending_skill_exp_rewards_applies_trainable_keys_once(self):
        migrated = migrate_loaded_data(
            {
                "runecrafting_exp": 100,
                "attack_exp": 25,
                "slayer_exp": 0,
                "pending_skill_exp_rewards": {
                    "runecrafting_exp": 5000,
                    "attack_exp": 1000,
                    "farming_exp": 250,
                    "slayer_exp": 5000,
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["runecrafting_exp"], 5100.0)
        self.assertEqual(migrated["attack_exp"], 1025.0)
        self.assertGreater(migrated["attack_level"], 1)
        self.assertEqual(migrated["farming_exp"], 250.0)
        self.assertGreater(migrated["farming_level"], 1)
        self.assertEqual(migrated["slayer_exp"], 5000.0)
        self.assertGreater(migrated["slayer_level"], 1)
        self.assertEqual(migrated["pending_skill_exp_rewards"], {})

    def test_v99_releases_and_sanitizes_parked_dungeoneering_xp(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 98,
                "dungeoneering_exp": float("nan"),
                "dungeoneering_level": 999,
                "pending_skill_exp_rewards": {
                    "dungeoneering_exp": DUNGEONEERING_EXP_TABLE[-1],
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["dungeoneering_exp"],
            float(DUNGEONEERING_EXP_TABLE[-1]),
        )
        self.assertEqual(migrated["dungeoneering_level"], 120)
        self.assertEqual(migrated["pending_skill_exp_rewards"], {})
        self.assertEqual(
            migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS)[
                "dungeoneering_exp"
            ],
            float(DUNGEONEERING_EXP_TABLE[-1]),
        )

    def test_nonzero_dungeoneering_save_derives_its_level_without_pending_xp(self):
        migrated = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "dungeoneering_exp": DUNGEONEERING_EXP_TABLE[99],
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["dungeoneering_level"], 100)

    def test_v90_migration_adds_and_sanitizes_diary_telemetry_ledgers(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 89,
                "shop_events": [
                    {
                        "event_id": "shop_evt_1",
                        "type": "buy",
                        "shop_id": "aemads_adventuring_supplies",
                        "row_id": "aemads_adventuring_supplies:9:227",
                    },
                    {
                        "event_id": "shop_evt_2",
                        "type": "buy",
                        "shop_id": "aemads_adventuring_supplies",
                        "row_id": "aemads_adventuring_supplies:9:227",
                    },
                ],
                "fight_caves": {
                    "kill_counts": {"ket_zek": "3", "tz_kih": 40}
                },
                "achievement_progress": {"version": 1, "skills": {}},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["shop_transaction_counts"], {"aemads_vial_of_water": 2}
        )
        self.assertIn(
            "ardougne_easy_vial_deeds",
            migrated["achievement_diaries"]["completed_tasks"],
        )
        self.assertEqual(migrated["fight_caves"]["kill_counts"], {"ket_zek": 3})
        self.assertEqual(
            migrated["achievement_progress"]["skills"]["dungeoneering"],
            {"actions": {}, "outputs": {}},
        )

    def test_v108_seeds_new_deed_outputs_and_preserves_durable_shop_counts(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 107,
                "inventory": {
                    "Clay ring": 1,
                    "Vial": 3,
                    "Raw manta ray": 1,
                },
                "achievement_progress": {
                    "version": 1,
                    "skills": {
                        "crafting": {
                            "actions": {},
                            "outputs": {"Clay ring": 0},
                        }
                    },
                },
                "shop_events": [],
                "shop_transaction_counts": {"aemads_vial_of_water": 2},
                "achievement_diaries": {
                    "version": 1,
                    "completed_tasks": [
                        "ardougne_easy_the_essence_of_magic",
                        "ardougne_hard_who_wants_to_watch_the_watchtower",
                        "lumbridge_easy_artisan_crafting",
                    ],
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["achievement_progress"]["skills"]["crafting"]["outputs"],
            {"Clay ring": 1, "Vial": 3},
        )
        self.assertEqual(
            migrated["achievement_progress"]["skills"]["utility"]["outputs"],
            {"Raw manta ray": 1},
        )
        self.assertEqual(
            migrated["shop_transaction_counts"], {"aemads_vial_of_water": 2}
        )
        completed = migrated["achievement_diaries"]["completed_tasks"]
        self.assertTrue(
            {
                "ardougne_easy_vial_deeds",
                "ardougne_elite_catching_some_rays",
                "lumbridge_easy_artisan_crafting",
                "fremennik_medium_only_takes_a_little_vial",
            }.issubset(completed)
        )
        self.assertNotIn(
            "ardougne_hard_who_wants_to_watch_the_watchtower",
            completed,
        )
        self.assertNotIn("ardougne_easy_the_essence_of_magic", completed)

    def test_v121_drops_dormant_proxy_completions_once(self):
        dormant_ids = {
            task.id
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if not task.conditions
        }
        real_deed_id = "ardougne_easy_vial_deeds"
        self.assertTrue(dormant_ids)
        self.assertNotIn(real_deed_id, dormant_ids)

        migrated = migrate_loaded_data(
            {
                "config_version": 120,
                "achievement_diaries": {
                    "version": 1,
                    "completed_tasks": [*sorted(dormant_ids), real_deed_id],
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        completed = migrated["achievement_diaries"]["completed_tasks"]
        self.assertTrue(dormant_ids.isdisjoint(completed))
        self.assertIn(real_deed_id, completed)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS),
            migrated,
        )

    def test_v110_adds_and_sanitizes_observed_drop_log_without_disturbing_save(self):
        prior_save = {
            "config_version": 109,
            "attack_exp": 4321.0,
            "inventory": {"Bronze sword": 1, "Bones": 7},
            "equipment": {"weapon": "Bronze sword"},
            "current_combat_target": "cow_calf",
            "combat_kill_counts": {"cow_calf": 7},
            "quests": {"rune_mysteries": {"completed": True}},
            "achievement_progress": {
                "version": 1,
                "skills": {"combat": {"actions": {}, "outputs": {}}},
            },
        }

        migrated = migrate_loaded_data(prior_save, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["combat_observed_drops"], {})
        self.assertEqual(migrated["attack_exp"], 4321.0)
        self.assertEqual(migrated["inventory"]["Bones"], 7)
        self.assertEqual(migrated["equipment"], {"weapon": "Bronze sword"})
        self.assertEqual(migrated["combat_kill_counts"], {"cow_calf": 7})
        self.assertTrue(migrated["quests"]["rune_mysteries"]["completed"])
        self.assertEqual(
            migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS), migrated
        )

        malformed = dict(migrated)
        malformed["combat_observed_drops"] = {
            "cow_calf": {
                "Bones": {"times_seen": "3", "quantity_seen": "7"},
                "Cowhide": {"times_seen": -1, "quantity_seen": 2},
                "": {"times_seen": 1, "quantity_seen": 1},
                "Raw beef": "bad",
            },
            "bad": "not an item map",
            123: {"Coins": {"times_seen": 1, "quantity_seen": 1}},
        }
        sanitized = migrate_loaded_data(malformed, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(
            sanitized["combat_observed_drops"],
            {
                "cow_calf": {
                    "Bones": {"times_seen": 3, "quantity_seen": 7}
                }
            },
        )

    def test_migrate_equipment_state_and_removes_owned_equipment(self):
        migrated = migrate_loaded_data(
            {
                "equipment": {"body": "Bronze platebody", "bad_slot": "Mystery"},
                "owned_equipment": ["amulet_of_glory_4"],
                "inventory": {"Bronze platebody": 0},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["equipment"], {"body": "Bronze platebody"})
        self.assertNotIn("owned_equipment", migrated)

    def test_migrate_combat_grave_state_is_sanitized(self):
        malformed = migrate_loaded_data(
            {"combat_grave": "not a grave"},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(malformed["combat_grave"], {})

        clamped = migrate_loaded_data(
            {
                "combat_grave": {
                    "items": ["Iron sword", "", 123],
                    "reviews_remaining": 99,
                    "source": "",
                }
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(
            clamped["combat_grave"],
            {"items": ["Iron sword"], "reviews_remaining": 5, "source": "combat_death"},
        )

    def test_equipment_condition_instances_are_added_and_sanitized(self):
        default = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(default["equipment_instances"], {})
        self.assertEqual(default["equipment_instance_next_id"], 1)

        migrated = migrate_loaded_data(
            {
                "inventory": {"Combat hood 80": 1},
                "equipment": {"hands": "Bronze gauntlets"},
                "equipment_instances": {
                    "bad": {"family_id": "missing", "location": "bank"},
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(len(migrated["equipment_instances"]), 2)
        records = list(migrated["equipment_instances"].values())
        self.assertIn(
            {
                "family_id": "combat_hood",
                "item_name": "Combat hood 80",
                "condition": 72_000,
                "location": "bank",
            },
            records,
        )
        self.assertTrue(
            any(
                record["family_id"] == "bronze_gauntlets"
                and record["location"] == "equipped:hands"
                for record in records
            )
        )

    def test_migrate_legacy_target_names_without_losing_inventory(self):
        cases = (
            ("mining", {"current_ore": "Iron ore", "inventory": {"Iron ore": 2}}, "current_ore", "iron", "Iron ore", 2),
            (
                "crafting",
                {"current_craft": "Bow string", "inventory": {"Flax": 3}},
                "current_craft",
                "spin_flax_to_bow_string",
                "Flax",
                3,
            ),
        )
        for name, original, target_key, target_id, item_name, quantity in cases:
            with self.subTest(name):
                migrated = migrate_loaded_data(original, ORE_DATA, ITEM_DEFINITIONS)
                self.assertEqual(migrated[target_key], target_id)
                self.assertEqual(migrated["inventory"][item_name], quantity)

    def test_migrate_unknown_mining_target_to_default(self):
        migrated = migrate_loaded_data(
            {"current_ore": "Not a rock", "inventory": {}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_ore"], "rune_essence")

    def test_migrate_firemaking_target_to_stable_default(self):
        migrated = migrate_loaded_data(
            {"current_firemaking": "Not a log", "inventory": {"Mystery ash": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_firemaking"], "logs")
        self.assertEqual(migrated["inventory"]["Mystery ash"], 3)
        self.assertIn("Cursed magic logs", migrated["inventory"])
        self.assertEqual(FIREMAKING_DATA["logs"]["output_item"], "Ashes")

    def test_migrate_fishing_target_to_stable_default_and_seeds_items(self):
        migrated = migrate_loaded_data(
            {"current_fishing": "Not a fish", "inventory": {"Mystery fish": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_fishing"], "catch_crayfish")
        self.assertEqual(migrated["inventory"]["Mystery fish"], 3)
        self.assertIn("Raw crayfish", migrated["inventory"])
        self.assertIn("Fishing bait", migrated["inventory"])
        self.assertEqual(FISHING_DATA["catch_crayfish"]["fish"][0]["output_item"], "Raw crayfish")

    def test_migrate_cooking_target_to_stable_default_and_seeds_items(self):
        migrated = migrate_loaded_data(
            {"current_cooking": "Not food", "inventory": {"Mystery food": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_cooking"], "cook_shrimps")
        self.assertEqual(migrated["inventory"]["Mystery food"], 3)
        self.assertIn("Raw shrimps", migrated["inventory"])
        self.assertIn("Shrimps", migrated["inventory"])
        self.assertIn("Burnt shrimp", migrated["inventory"])
        self.assertEqual(COOKING_DATA["cook_shrimps"]["output_item"], "Shrimps")

    def test_migrate_deferred_daemonheim_herblore_target_without_losing_items(self):
        migrated = migrate_loaded_data(
            {
                "current_herblore": "clean_sagawort",
                "inventory": {
                    "Grimy sagewort": 2,
                    "Clean sagewort": 1,
                    "Strong survivalist's potion": 3,
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_herblore"], "clean_guam")
        self.assertEqual(migrated["inventory"]["Grimy sagewort"], 2)
        self.assertEqual(migrated["inventory"]["Clean sagewort"], 1)
        self.assertEqual(migrated["inventory"]["Strong survivalist's potion"], 3)

    def test_migrate_hunter_target_to_stable_default_and_seeds_items(self):
        migrated = migrate_loaded_data(
            {"current_hunter": "Not a creature", "inventory": {"Mystery catch": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_hunter"], "catch_crimson_swift")
        self.assertEqual(migrated["inventory"]["Mystery catch"], 3)
        self.assertIn("Red feather", migrated["inventory"])
        self.assertIn("Butterfly jar", migrated["inventory"])
        self.assertIn("Impling jar", migrated["inventory"])
        self.assertIn("Imp-in-a-box (2)", migrated["inventory"])
        self.assertEqual(HUNTER_DATA["catch_crimson_swift"]["output_item"], "Red feather")

    def test_migrate_legacy_woodcutting_target_and_logs(self):
        migrated = migrate_loaded_data(
            {
                "current_tree": "Magic",
                "inventory": {"Tree": 2, "Magic": 4, "Redwood": 99, "Mystery item": 1},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_tree"], "magic")
        self.assertEqual(migrated["inventory"]["Logs"], 2)
        self.assertEqual(migrated["inventory"]["Magic logs"], 4)
        self.assertNotIn("Tree", migrated["inventory"])
        self.assertNotIn("Magic", migrated["inventory"])
        self.assertNotIn("Redwood", migrated["inventory"])
        self.assertEqual(migrated["inventory"]["Mystery item"], 1)

    def test_migrate_legacy_smithing_target_and_bar_names(self):
        migrated = migrate_loaded_data(
            {
                "current_bar": "Runite bar",
                "inventory": {"Runite bar": 3, "Adamantite bar": 2, "Mystery bar": 1},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_smith"], "smelt_rune_bar")
        self.assertEqual(migrated["inventory"]["Rune bar"], 3)
        self.assertEqual(migrated["inventory"]["Adamant bar"], 2)
        self.assertNotIn("Runite bar", migrated["inventory"])
        self.assertNotIn("Adamantite bar", migrated["inventory"])
        self.assertEqual(migrated["inventory"]["Mystery bar"], 1)

    def test_migrate_moves_legacy_soft_clay_target_to_utility(self):
        migrated = migrate_loaded_data(
            {"current_craft": "Soft clay", "inventory": {"Clay": 4}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["current_craft"], "")
        self.assertEqual(migrated["current_utility"], "make_soft_clay")
        self.assertEqual(migrated["inventory"]["Clay"], 4)

    def test_migrate_legacy_crafting_inventory_names(self):
        migrated = migrate_loaded_data(
            {
                "inventory": {
                    "Unfired pot": 120,
                    "Pot": 4,
                    "Unfired pie dish": 3,
                    "Pot (unfired)": 2,
                    "Candle lantern": 1,
                    "Oil lamp": 2,
                    "Oil lantern": 3,
                    "Bullseye lantern": 4,
                    "Emerald lantern": 5,
                    "Mining helmet": 1,
                },
                "equipment": {"head": "Mining helmet"},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["inventory"]["Pot (unfired)"], 122)
        self.assertEqual(migrated["inventory"]["Empty pot"], 4)
        self.assertEqual(migrated["inventory"]["Pie dish (unfired)"], 3)
        self.assertNotIn("Unfired pot", migrated["inventory"])
        self.assertNotIn("Pot", migrated["inventory"])
        self.assertNotIn("Unfired pie dish", migrated["inventory"])
        self.assertEqual(migrated["inventory"]["Candle lantern (empty)"], 1)
        self.assertEqual(migrated["inventory"]["Oil lamp (empty)"], 2)
        self.assertEqual(migrated["inventory"]["Oil lantern (unlit)"], 3)
        self.assertEqual(migrated["inventory"]["Bullseye lantern (empty)"], 4)
        self.assertEqual(migrated["inventory"]["Emerald lantern (unlit)"], 5)
        self.assertEqual(migrated["inventory"]["Mining helmet (unlit)"], 1)
        self.assertEqual(migrated["equipment"], {"head": "Mining helmet (unlit)"})
        for legacy_key in (
            "Candle lantern",
            "Oil lamp",
            "Oil lantern",
            "Bullseye lantern",
            "Emerald lantern",
            "Mining helmet",
        ):
            self.assertNotIn(legacy_key, migrated["inventory"])

    def test_migrate_legacy_shop_arrows_into_canonical_stacks(self):
        migrated = migrate_loaded_data(
            {
                "inventory": {
                    "Bronze arrow": 10,
                    "Bronze arrows": 5,
                    "Rune arrow": 3,
                    "Broad arrow": 2,
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["inventory"]["Bronze arrows"], 15)
        self.assertEqual(migrated["inventory"]["Rune arrows"], 3)
        self.assertEqual(migrated["inventory"]["Broad arrows"], 2)
        for legacy_name in ("Bronze arrow", "Rune arrow", "Broad arrow"):
            self.assertNotIn(legacy_name, migrated["inventory"])

    def test_migrate_legacy_crafting_names_across_persisted_item_stores(self):
        migrated = migrate_loaded_data(
            {
                "inventory": {"Mining helmet": 1, "Oil lamp": 2},
                "carried_inventory": {
                    "dorgesh_kaan": {"Mining helmet": 1, "Oil lamp": 1},
                },
                "carried_layout": {
                    "dorgesh_kaan": {"Mining helmet": 1, "Oil lamp": 1},
                },
                "loot_overrides": {"Mining helmet": "keep", "Oil lamp": "leave"},
                "combat_grave": {
                    "items": ["Mining helmet", "Oil lamp"],
                    "reviews_remaining": 1,
                    "loadout": {"head": "Mining helmet"},
                },
                "death_office": {
                    "items": ["Mining helmet", "Oil lamp"],
                    "loadout": {"head": "Mining helmet"},
                },
                "magic_alchemy_item": "Mining helmet",
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        expected_view = {"Mining helmet (unlit)": 1, "Oil lamp (empty)": 1}
        self.assertEqual(migrated["carried_inventory"]["dorgesh_kaan"], expected_view)
        self.assertEqual(migrated["carried_layout"]["dorgesh_kaan"], expected_view)
        self.assertEqual(
            migrated["loot_overrides"],
            {"Mining helmet (unlit)": "keep", "Oil lamp (empty)": "leave"},
        )
        for state_key in ("combat_grave", "death_office"):
            self.assertEqual(
                migrated[state_key]["items"],
                ["Mining helmet (unlit)", "Oil lamp (empty)"],
            )
            self.assertEqual(migrated[state_key]["loadout"], {"head": "Mining helmet (unlit)"})
        self.assertEqual(migrated["magic_alchemy_item"], "Mining helmet (unlit)")

    def test_migrate_moves_legacy_agility_circus_state_to_atomic_activity(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 71,
                "inventory": {},
                "agility_circus_last_week": 4,
                "agility_activity_state": {
                    "circus": {"attempted": ["small_hop"]},
                },
                "agility_activity_currencies": {
                    "brianpoints": 2,
                    "circus_audience": 654,
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertNotIn("agility_circus_last_week", migrated)
        self.assertNotIn("circus", migrated["agility_activity_state"])
        self.assertEqual(migrated["agility_activity_currencies"], {"brianpoints": 2})
        self.assertEqual(
            migrated["circus"]["used_week_by_performance"],
            {"agility": 4},
        )
        self.assertEqual(migrated["circus"]["lifetime_score"], 654)

    def test_migrate_adds_and_sanitizes_trouble_brewing_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 72,
                "inventory": {},
                "trouble_brewing": {"review": 999, "boilers": [99]},
                "activity_session": {"active_id": "trouble_brewing"},
                "trouble_brewing_pieces_of_eight": -4,
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["trouble_brewing"]["review"], 15)
        self.assertEqual(migrated["trouble_brewing"]["boilers"], [10, 3, 3])
        self.assertEqual(migrated["trouble_brewing_pieces_of_eight"], 0)
        self.assertEqual(
            migrated["trouble_brewing_policy"],
            {"automation_mode": "casual", "duty": "water"},
        )

    def test_migrate_adds_and_sanitizes_castle_wars_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 73,
                "inventory": {},
                "castle_wars": {
                    "review": 999,
                    "barricades": 999,
                    "gate_integrity": -1,
                },
                "activity_session": {"active_id": "castle_wars"},
                "castle_wars_tickets": -4,
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["castle_wars"]["review"], 9)
        self.assertEqual(migrated["castle_wars"]["barricades"], 10)
        self.assertEqual(migrated["castle_wars"]["gate_integrity"], 0)
        self.assertEqual(migrated["castle_wars_tickets"], 0)
        self.assertEqual(
            migrated["castle_wars_policy"],
            {"automation_mode": "casual", "duty": "capture", "team": "balance"},
        )

    def test_migrate_adds_and_sanitizes_pest_control_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 74,
                "inventory": {},
                "pest_control": {
                    "review": 999,
                    "portal_index": 999,
                    "portal_lifepoints": -1,
                    "knight_lifepoints": 999_999,
                    "lander_id": "unknown",
                },
                "activity_session": {"active_id": "pest_control"},
                "pest_control_commendations": 999,
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["pest_control"]["review"], 11)
        self.assertEqual(migrated["pest_control"]["portal_index"], 3)
        self.assertEqual(migrated["pest_control"]["portal_lifepoints"], 1)
        self.assertEqual(migrated["pest_control"]["knight_lifepoints"], 2_000)
        self.assertEqual(migrated["pest_control_commendations"], 500)
        self.assertEqual(
            migrated["pest_control_policy"],
            {"automation_mode": "casual", "lander_id": "novice", "duty": "assault"},
        )

    def test_migrate_adds_and_sanitizes_varrock_museum_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 75,
                "inventory": {},
                "varrock_museum": {
                    "route": "broken",
                    "quiz_completed": ["Lizard", "Lizard", "Fake"],
                    "specimens_displayed": ["pottery", "fake"],
                    "digsite_pendant_unlocked": 1,
                    "quest_stories_claimed": ["demon_slayer", "fake"],
                    "threshold_rewards_claimed": ["kudos_51", "fake"],
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["varrock_museum"]["route"], "quiz")
        self.assertEqual(migrated["varrock_museum"]["quiz_completed"], ["Lizard"])
        self.assertEqual(migrated["varrock_museum"]["specimens_displayed"], ["pottery"])
        self.assertTrue(migrated["varrock_museum"]["digsite_pendant_unlocked"])
        self.assertEqual(
            migrated["varrock_museum"]["quest_stories_claimed"],
            ["demon_slayer"],
        )
        self.assertEqual(
            migrated["varrock_museum"]["threshold_rewards_claimed"],
            ["kudos_51"],
        )

    def test_migrate_adds_and_sanitizes_barbarian_assault_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 76,
                "inventory": {},
                "activity_session": {"active_id": "barbarian_assault"},
                "barbarian_assault": {
                    "wave": 3,
                    "phase": "queen",
                    "queen_lifepoints": 1,
                    "omega_eggs": 7,
                    "role": "unknown",
                },
                "barbarian_assault_policy": {
                    "automation_mode": "unknown",
                    "role": "unknown",
                },
                "barbarian_assault_points": {
                    "attacker": -3,
                    "collector": 7,
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["barbarian_assault"]["wave"], 3)
        self.assertEqual(migrated["barbarian_assault"]["phase"], "wave")
        self.assertEqual(migrated["barbarian_assault"]["queen_lifepoints"], 2_500)
        self.assertEqual(migrated["barbarian_assault"]["omega_eggs"], 0)
        self.assertEqual(
            migrated["barbarian_assault_policy"],
            {"automation_mode": "casual", "role": "attacker"},
        )
        self.assertEqual(
            migrated["barbarian_assault_points"],
            {"attacker": 0, "collector": 7, "defender": 0, "healer": 0},
        )

    def test_v120_migrates_old_stronghold_lamp_counts_once(self):
        expected_claimed_by_count = {
            2: (False, False),
            1: (True, False),
            0: (True, True),
        }
        for lamps_remaining, expected_claimed in expected_claimed_by_count.items():
            with self.subTest(lamps_remaining=lamps_remaining):
                migrated = migrate_loaded_data(
                    {
                        "config_version": 119,
                        "inventory": {},
                        "claims": {"wicked_hood": {"claimed": True}},
                        "stronghold_player_safety": {
                            "stage": 3,
                            "crevice_unlocked": True,
                            "chest_claimed": True,
                            "lamps_remaining": lamps_remaining,
                            "safety_first_emote_unlocked": True,
                        },
                    },
                    ORE_DATA,
                    ITEM_DEFINITIONS,
                )

                self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
                self.assertNotIn(
                    "lamps_remaining", migrated["stronghold_player_safety"]
                )
                self.assertTrue(
                    migrated["stronghold_player_safety"]["chest_claimed"]
                )
                self.assertTrue(migrated["claims"]["wicked_hood"]["claimed"])
                for claim_id, claimed in zip(
                    STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS,
                    expected_claimed,
                ):
                    self.assertEqual(
                        migrated["claims"][claim_id],
                        {"claimed": claimed, "delivered": True},
                    )

                self.assertEqual(
                    migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS),
                    migrated,
                )

    def test_migrate_idempotent(self):
        base = {"mining_exp": 10, "inventory": {}}
        first = migrate_loaded_data(base, ORE_DATA)
        second = migrate_loaded_data(first, ORE_DATA)
        self.assertEqual(first, second)

    def test_migrate_handles_bad_inventory(self):
        base = {"mining_exp": 10, "inventory": 5}  # not a dict
        migrated = migrate_loaded_data(base, ORE_DATA)
        self.assertIsInstance(migrated["inventory"], dict)
        for ore in MINING_OUTPUT_ITEMS:
            self.assertIn(ore, migrated["inventory"])  # seeded

    def test_migrate_sanitizes_non_string_blackjack_phases(self):
        for malformed_phase in ([], {}, ["knocked_out"]):
            with self.subTest(malformed_phase=malformed_phase):
                migrated = migrate_loaded_data(
                    {
                        "thieving_blackjack_phase": malformed_phase,
                        "thieving_blackjack_picks_remaining": 2,
                    },
                    ORE_DATA,
                    ITEM_DEFINITIONS,
                )

                self.assertEqual(migrated["thieving_blackjack_phase"], "needs_lure")
                self.assertEqual(migrated["thieving_blackjack_picks_remaining"], 0)

    def test_migrate_adds_and_sanitizes_livid_farm_progress(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 45,
                "inventory": {},
                "livid_farm": {
                    "farm_routine": "conserve",
                    "cadence_credit": 8,
                    "distraction_credit": 14,
                    "produce_points": -2,
                    "cycles_completed": 7,
                    "unlocked_spells": [
                        "south_falador_teleport",
                        "future_spell",
                    ],
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["livid_farm"]["farm_routine"], "conserve")
        self.assertEqual(migrated["livid_farm"]["cadence_credit"], 3)
        self.assertEqual(migrated["livid_farm"]["distraction_credit"], 2)
        self.assertEqual(migrated["livid_farm"]["produce_points"], 0)
        self.assertEqual(migrated["livid_farm"]["cycles_completed"], 7)
        self.assertEqual(
            migrated["livid_farm"]["unlocked_spells"],
            ["south_falador_teleport"],
        )
        self.assertEqual(migrated["livid_farm"]["lunar_lumber_residual"], 0)
        self.assertEqual(
            migrated["livid_farm"]["more_planks_reviews_remaining"],
            0,
        )
        self.assertFalse(migrated["farm_livid_patch_active"])
        self.assertIsNone(migrated["farm_livid_protection_crop_id"])
        self.assertEqual(migrated["farm_livid_protection_uses_remaining"], 0)

    def test_migration_repairs_reported_star_and_dream_save_state(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 103,
                "current_utility": "shooting_stars",
                "activity_session": {"active_id": "shooting_stars"},
                "magic_level": 1,
                "quests": {"dream_mentor": {"completed": False}},
                "combat_dream_thrift": True,
                "combat_pack_mode": "max_output",
                "combat_encounter": {
                    "target_id": "citizen",
                    "enemy_lifepoints": 67,
                },
                "combat_supply_loadout": {"food": {"Shrimps": 1}},
                "inventory": {"Shrimps": 89},
                "combat_auto_eat_food": [
                    "Shark",
                    "Swordfish",
                    "Lobster",
                    "Tuna",
                    "Salmon",
                    "Trout",
                    "Cooked meat",
                    "Cooked chicken",
                    "Shrimps",
                    "Crayfish",
                ],
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["activity_session"], {"active_id": ""})
        self.assertEqual(migrated["current_utility"], "shooting_stars")
        self.assertFalse(migrated["combat_dream_thrift"])
        self.assertEqual(migrated["combat_encounter"], {})
        self.assertEqual(migrated["combat_supply_loadout"]["food"], {"Shrimps": 8})
        self.assertEqual(migrated["inventory"]["Shrimps"], 82)
        self.assertEqual(
            migrated["combat_auto_eat_food"],
            [
                "Shark",
                "Monkfish",
                "Swordfish",
                "Bass",
                "Lobster",
                "Tuna",
                "Salmon",
                "Pike",
                "Trout",
                "Cod",
                "Mackerel",
                "Herring",
                "Cooked meat",
                "Cooked chicken",
                "Sardine",
                "Shrimps",
                "Crayfish",
            ],
        )

    def test_load_repairs_class_incompatible_runes_once(self):
        saved = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        saved.update(
            {
                "inventory": {},
                "equipment": {},
                "combat_attack_style": "accurate",
                "combat_encounter": {},
                "combat_supply_loadout": {
                    "runes": {"Air rune": 5, "Mind rune": 5},
                },
            }
        )

        migrated = migrate_loaded_data(saved, ORE_DATA, ITEM_DEFINITIONS)
        reloaded = migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["combat_supply_loadout"]["runes"], {})
        self.assertEqual(migrated["inventory"]["Air rune"], 5)
        self.assertEqual(migrated["inventory"]["Mind rune"], 5)
        self.assertEqual(reloaded["inventory"]["Air rune"], 5)
        self.assertEqual(reloaded["inventory"]["Mind rune"], 5)

    def test_load_preserves_wind_strike_runes_for_a_magic_staff(self):
        saved = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        saved.update(
            {
                "inventory": {},
                "equipment": {"weapon": "Staff of fire"},
                "combat_attack_style": "magic_standard",
                "current_combat_spell": "wind_strike",
                "combat_encounter": {},
                "combat_supply_loadout": {
                    "runes": {"Air rune": 5, "Mind rune": 5},
                },
            }
        )

        migrated = migrate_loaded_data(saved, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(
            migrated["combat_supply_loadout"]["runes"],
            {"Air rune": 5, "Mind rune": 5},
        )
        self.assertEqual(migrated["inventory"].get("Air rune", 0), 0)
        self.assertEqual(migrated["inventory"].get("Mind rune", 0), 0)

    def test_load_leaves_an_active_encounter_loadout_untouched(self):
        saved = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        saved.update(
            {
                "inventory": {},
                "equipment": {},
                "combat_attack_style": "accurate",
                "current_combat_target": "chicken",
                "combat_encounter": {
                    "target_id": "chicken",
                    "enemy_lifepoints": 1,
                },
                "combat_supply_loadout": {
                    "runes": {"Air rune": 5, "Mind rune": 5},
                },
            }
        )

        migrated = migrate_loaded_data(saved, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(
            migrated["combat_supply_loadout"]["runes"],
            {"Air rune": 5, "Mind rune": 5},
        )
        self.assertEqual(migrated["inventory"].get("Air rune", 0), 0)
        self.assertEqual(migrated["inventory"].get("Mind rune", 0), 0)

    def test_activity_session_allowlist_covers_every_runtime_writer(self):
        writer_ids, unresolved = _activity_session_writer_ids()
        self.assertEqual(
            unresolved,
            [],
            f"activity_session writers need an explicit active_id: {unresolved}",
        )
        missing = sorted(writer_ids - _SUPPORTED_ACTIVITY_SESSION_IDS)
        self.assertEqual(
            missing,
            [],
            "runtime activity_session owners absent from "
            f"_SUPPORTED_ACTIVITY_SESSION_IDS: {missing}",
        )

    def test_migration_preserves_legitimate_activity_session_owners(self):
        session_ids = (
            "barbarian_assault",
            "castle_wars",
            "conquest",
            "familiarisation",
            "flash_powder_factory",
            "pest_control",
            "shades_of_mortton",
            "soul_wars",
            "treasure_trail",
            "trouble_brewing",
        )

        for session_id in session_ids:
            with self.subTest(session_id=session_id):
                saved = {
                    "config_version": CURRENT_CONFIG_VERSION,
                    "activity_session": {"active_id": session_id},
                }
                if session_id == "conquest":
                    from ankiscape.logic.conquest_logic import enter_conquest_pure

                    saved = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                    for level_key in (
                        "attack_level",
                        "strength_level",
                        "defense_level",
                        "constitution_level",
                        "ranged_level",
                        "magic_level",
                        "prayer_level",
                    ):
                        saved[level_key] = 40
                    saved, ok, reason = enter_conquest_pure(
                        saved, {}, lambda: 0.0
                    )
                    self.assertTrue(ok, reason)
                migrated = migrate_loaded_data(
                    saved,
                    ORE_DATA,
                    ITEM_DEFINITIONS,
                )
                self.assertEqual(
                    migrated["activity_session"], {"active_id": session_id}
                )

    def test_v105_food_order_refills_monkfish_before_cooked_chicken(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 104,
                "inventory": {"Monkfish": 50, "Cooked chicken": 50},
                "combat_pack_mode": "max_output",
                "combat_supply_loadout": {},
                "combat_auto_eat_food": [
                    "Shark",
                    "Swordfish",
                    "Lobster",
                    "Tuna",
                    "Salmon",
                    "Trout",
                    "Cooked meat",
                    "Cooked chicken",
                    "Shrimps",
                    "Crayfish",
                ],
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(
            migrated, EQUIPMENT_DATA
        )
        self.assertTrue(ok, reason)
        self.assertEqual(refilled["combat_supply_loadout"]["food"], {"Monkfish": 8})

    def test_v105_food_order_preserves_explicit_added_food_order(self):
        saved_order = ["Shrimps", "Sardine", "Shark", "Herring"]
        migrated = migrate_loaded_data(
            {
                "config_version": 103,
                "combat_auto_eat_food": saved_order,
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(
            migrated["combat_auto_eat_food"],
            [
                "Monkfish",
                "Bass",
                "Pike",
                "Cod",
                "Mackerel",
                "Shrimps",
                "Sardine",
                "Shark",
                "Herring",
            ],
        )

    def test_migration_clears_any_selection_only_activity_session(self):
        for activity_id in ("shooting_stars", "make_soft_clay"):
            with self.subTest(activity_id=activity_id):
                migrated = migrate_loaded_data(
                    {
                        "config_version": CURRENT_CONFIG_VERSION,
                        "current_utility": activity_id,
                        "activity_session": {"active_id": activity_id},
                    },
                    ORE_DATA,
                    ITEM_DEFINITIONS,
                )
                self.assertEqual(migrated["current_utility"], activity_id)
                self.assertEqual(migrated["activity_session"], {"active_id": ""})


if __name__ == "__main__":
    unittest.main()
