import unittest
from unittest.mock import patch
import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core import constants
from ankiscape.core.constants import ITEM_DEFINITIONS, QUEST_DATA
from ankiscape.data import combat_data
from ankiscape.logic_pure.logic_pure import target_unlock_locked_reasons_pure
from tools.audit_item_reachability import _close_quest_reachability, build_reachability_report
from tests.reachability.live_report import live_reachability_report


class TestItemReachabilityAudit(unittest.TestCase):
    def test_named_encounter_only_targets_do_not_seed_drops(self):
        target_ids = (
            "menaphite_thug",
            "cockroach_soldier",
            "temple_trekking_ambush",
            "troll_invasion_wave_front",
        )
        marker_by_target = {
            target_id: f"Encounter-only marker: {target_id}"
            for target_id in target_ids
        }
        encounter_targets = {
            target_id: {
                **combat_data.COMBAT_ENEMY_DATA[target_id],
                "drops": {
                    "guaranteed": ((marker_by_target[target_id], 1),),
                },
            }
            for target_id in target_ids
        }

        with patch.dict(
            combat_data.COMBAT_ENEMY_DATA,
            encounter_targets,
            clear=True,
        ):
            report = build_reachability_report()

        for target_id, marker in marker_by_target.items():
            with self.subTest(target=target_id):
                self.assertIsNone(report["routes"].get(marker))

    def test_combat_sources_use_every_runtime_access_gate(self):
        gated_fields = {
            "encounter": {"encounter_only": True},
            "slayer": {"required_slayer_level": 1000},
            "skill": {"skill_requirements": {"agility": 1000}},
            "item": {"required_items": {"Missing combat key": 1}},
            "item_option": {
                "required_item_options": (("Missing option A", "Missing option B"),),
            },
            "finisher": {
                "finisher": {
                    "item": "Missing finisher",
                    "threshold_lifepoints": 1,
                    "consume": True,
                },
            },
            "quest": {"required_quest": "missing_combat_quest"},
            "start_equipment": {
                "start_equipment": {
                    "slot": "head",
                    "items": ("Missing combat helmet",),
                },
            },
            "hazard": {
                "environmental_hazard": {
                    "display_name": "Test hazard",
                    "dose_items": ("Missing hazard dose",),
                },
            },
            "restricted_weapon": {
                "restricted_weapon": {
                    "melee_weapons": ("Missing restricted weapon",),
                },
            },
            "warriors_guild": {
                "warriors_guild_gate": True,
                "warriors_guild_target": "cyclossus",
            },
        }
        targets = {
            target_id: {
                "display_name": target_id.title(),
                "stats": {"hitpoints": 1},
                "drops": {"guaranteed": ((f"{target_id} marker", 1),)},
                **fields,
            }
            for target_id, fields in gated_fields.items()
        }
        targets["open"] = {
            "display_name": "Open",
            "stats": {"hitpoints": 1},
            "drops": {"guaranteed": (("open marker", 1),)},
        }

        with patch.dict(combat_data.COMBAT_ENEMY_DATA, targets, clear=True):
            report = build_reachability_report()

        for target_id in gated_fields:
            with self.subTest(target=target_id):
                self.assertIsNone(report["routes"].get(f"{target_id} marker"))
        self.assertEqual(report["routes"].get("open marker"), "combat:open")

    def test_warriors_guild_progression_unlocks_defender_drops(self):
        report = live_reachability_report()

        for defender in (
            "Bronze defender",
            "Iron defender",
            "Steel defender",
            "Black defender",
            "Mithril defender",
            "Adamant defender",
            "Rune defender",
        ):
            with self.subTest(defender=defender):
                self.assertEqual(report["routes"].get(defender), "combat:cyclops")
        self.assertEqual(
            report["routes"].get("Cyclopean helmet"),
            "combat:cyclossus",
        )
        self.assertEqual(
            report["routes"].get("Dragon defender"),
            "combat:cyclossus",
        )

    def test_combat_sources_accept_runtime_finisher_loadout_variants(self):
        input_source = {
            "finisher_gate_test_inputs": {
                "status": "implemented",
                "outputs": {
                    "Simple finisher": 1,
                    "Worn finisher": 1,
                    "Empty finisher": 1,
                    "Finisher reload": 1,
                },
            },
        }
        targets = {
            "simple_finisher": {
                "stats": {"hitpoints": 1},
                "finisher": {
                    "item": "Simple finisher",
                    "threshold_lifepoints": 1,
                    "consume": True,
                },
                "drops": {"guaranteed": (("simple finisher marker", 1),)},
            },
            "worn_finisher": {
                "stats": {"hitpoints": 1},
                "finisher": {
                    "item": "Worn finisher",
                    "threshold_lifepoints": 1,
                    "must_be_worn": True,
                },
                "drops": {"guaranteed": (("worn finisher marker", 1),)},
            },
            "reloadable_finisher": {
                "stats": {"hitpoints": 1},
                "finisher": {
                    "item": "Reloadable finisher",
                    "threshold_lifepoints": 1,
                    "charge_items": (("Charged finisher", 10),),
                    "empty_item": "Empty finisher",
                    "reload_item": "Finisher reload",
                    "reload_charges": 10,
                },
                "drops": {"guaranteed": (("reloadable finisher marker", 1),)},
            },
        }

        with (
            patch.dict(constants.UTILITY_ACTIVITY_DATA, input_source),
            patch.dict(combat_data.COMBAT_ENEMY_DATA, targets, clear=True),
        ):
            report = build_reachability_report()

        for marker in (
            "simple finisher marker",
            "worn finisher marker",
            "reloadable finisher marker",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, report["routes"])

    def test_combat_sources_accept_runtime_equipment_and_hazard_loadouts(self):
        input_source = {
            "combat_gate_test_inputs": {
                "status": "implemented",
                "outputs": {
                    "Required combat helmet": 1,
                    "Waterskin (4)": 1,
                    "Magic shortbow": 1,
                    "Broad arrows": 1,
                    "Slayer's staff": 1,
                    "Mind rune": 4,
                    "Death rune": 1,
                },
            },
        }
        targets = {
            "start_equipment": {
                "stats": {"hitpoints": 1},
                "start_equipment": {
                    "slot": "head",
                    "items": ("Required combat helmet",),
                },
                "drops": {"guaranteed": (("start equipment marker", 1),)},
            },
            "environmental_hazard": {
                "stats": {"hitpoints": 1},
                "environmental_hazard": {
                    "display_name": "Desert heat",
                    "dose_items": ("Waterskin (4)",),
                },
                "drops": {"guaranteed": (("hazard marker", 1),)},
            },
            "ranged_restriction": {
                "stats": {"hitpoints": 1},
                "restricted_weapon": {
                    "melee_weapons": ("Missing spear",),
                    "ranged_ammunition": ("Broad arrows",),
                },
                "drops": {"guaranteed": (("ranged restriction marker", 1),)},
            },
            "magic_restriction": {
                "stats": {"hitpoints": 1},
                "restricted_weapon": {
                    "melee_weapons": ("Missing spear",),
                    "magic_spells": ("magic_dart",),
                },
                "drops": {"guaranteed": (("magic restriction marker", 1),)},
            },
        }

        with (
            patch.dict(constants.UTILITY_ACTIVITY_DATA, input_source),
            patch.dict(combat_data.COMBAT_ENEMY_DATA, targets, clear=True),
        ):
            report = build_reachability_report()

        for marker in (
            "start equipment marker",
            "hazard marker",
            "ranged restriction marker",
            "magic restriction marker",
        ):
            with self.subTest(marker=marker):
                self.assertIsNotNone(report["routes"].get(marker))

    def test_rune_essence_to_rune_dust_chain_remains_reachable(self):
        registered_items = {
            definition.storage_key for definition in ITEM_DEFINITIONS
        }
        _blocked, completed, _startable, _proofs = _close_quest_reachability(
            (),
            {},
            {},
            set(),
            {"rune_mysteries": QUEST_DATA["rune_mysteries"]},
            registered_items,
            lambda _encounter: True,
        )
        report = live_reachability_report()
        locked_player = {"quests": {}}
        unlocked_player = {
            "quests": {
                "rune_mysteries": {"started": True, "completed": True},
            },
        }

        self.assertEqual(completed, {"rune_mysteries"})
        self.assertEqual(
            target_unlock_locked_reasons_pure(
                locked_player,
                "mining",
                "rune_essence",
                constants.QUEST_UNLOCK_RULES,
            ),
            ("Rune Mysteries",),
        )
        self.assertEqual(
            target_unlock_locked_reasons_pure(
                unlocked_player,
                "mining",
                "rune_essence",
                constants.QUEST_UNLOCK_RULES,
            ),
            (),
        )
        self.assertNotIn(
            "Mining:rune_essence",
            {action["id"] for action in report["unresolved_actions"]},
        )
        self.assertIn("Rune essence", report["routes"])
        self.assertEqual(report["routes"].get("Rune shards"), "Utility:make_rune_shards")
        self.assertEqual(report["routes"].get("Rune dust"), "Utility:grind_rune_shards")

    def test_unlock_target_alias_uses_the_canonical_runtime_gate(self):
        report = live_reachability_report()

        self.assertIsNone(report["routes"].get("Death talisman staff"))
        self.assertIn(
            "Runecrafting:bind_death_talisman_staff",
            {action["id"] for action in report["unresolved_actions"]},
        )

    def test_magic_sources_use_runtime_state_gates(self):
        unavailable_target = {
            "runtime_unavailable_test": {
                "id": "runtime_unavailable_test",
                "display_name": "Runtime unavailable test",
                "status": "implemented",
                "level": 1,
                "consumer_unavailable": "Runtime consumer unavailable",
                "outputs": {"Unavailable Magic marker": 1},
            },
        }

        with patch.dict(constants.MAGIC_DATA, unavailable_target):
            report = build_reachability_report()

        self.assertIsNone(report["routes"].get("Digsite pendant (5)"))
        self.assertEqual(report["routes"].get("Peach"), "Magic:bones_to_peaches")
        self.assertIsNone(report["routes"].get("Unavailable Magic marker"))
