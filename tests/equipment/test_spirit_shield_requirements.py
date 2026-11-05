"""Spirit shield eligibility, Bank return on load, and ordinary equip Undo."""

import copy
from dataclasses import asdict
from itertools import product
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    EQUIPMENT_DATA, EQUIPMENT_ITEM_DATA, ITEM_DEFINITIONS, ORE_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data,
)
from ankiscape.data.equipment_data import EQUIPMENT_DATA as GENERATED_EQUIPMENT_DATA
from ankiscape.logic_pure.logic_pure import (
    can_equip_item_pure, equipment_stat_totals_pure,
    return_ineligible_spirit_shield_to_bank_pure as repair,
)
from ankiscape.data.equipment_overrides.spirit_shield import (
    SPIRIT_SHIELD_WIELD_SOURCE, spirit_shield_equipment_data_as_dict,
)


QUEST_REFUSAL = "Requires completion of Summer's End"
FAILURES = (
    ("Defence", {"defense_level": 39},
     "Requires level 40 Defense"),
    ("Prayer", {"prayer_level": 54}, "Requires level 55 Prayer"),
    ("quest absent", {"quests": {}}, QUEST_REFUSAL),
    ("quest unstarted", {"quests": {"summers_end": {"started": False, "completed": False}}}, QUEST_REFUSAL),
    ("quest incomplete", {"quests": {"summers_end": {"started": True, "completed": False}}}, QUEST_REFUSAL),
)
RUNTIME_MAPS = (("records", EQUIPMENT_DATA), ("serialized", EQUIPMENT_ITEM_DATA))


def _player(**updates):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(
        defense_level=40, prayer_level=55,
        quests={"summers_end": {"started": True, "completed": True, "progress": 0}},
        inventory={"Spirit shield": 1, "Coins": 17},
        equipment={"shield": "Bronze sq shield", "head": "Bronze full helm"},
    )
    player.update(copy.deepcopy(updates))
    return player


def _xp(player):
    return {key: value for key, value in player.items() if key.endswith("_exp")}


def _migrate(player):
    return migrate_loaded_data(copy.deepcopy(player), ORE_DATA, ITEM_DEFINITIONS)


class TestSpiritShieldRequirements(unittest.TestCase):
    def test_live_overlay_preserves_generated_row(self):
        base = GENERATED_EQUIPMENT_DATA["Spirit shield"]
        before = asdict(base)
        generated_before = dict(GENERATED_EQUIPMENT_DATA)
        for name, equipment_data in RUNTIME_MAPS:
            with self.subTest(representation=name):
                row = equipment_data["Spirit shield"]
                row = asdict(row) if name == "records" else row
                self.assertEqual(row["source_item_id"], 13734)
                self.assertEqual(row["slot"], "shield")
                self.assertEqual(row["combat_skill"], "defense")
                self.assertEqual(row["required_level"], 40)
                self.assertEqual(row["skill_requirements"], (("defense", 40), ("prayer", 55)))
                bonuses = row["bonuses"]
                self.assertEqual(tuple(bonuses[f"defence_{style}"] for style in
                                       ("stab", "slash", "crush", "magic", "ranged")),
                                 (39, 41, 50, 1, 45))
                self.assertEqual(bonuses["prayer"], 1)
                self.assertEqual(tuple(bonuses[f"attack_{style}"] for style in
                                       ("stab", "slash", "crush", "magic", "ranged")),
                                 (0, 0, 0, 0, 0))
        self.assertEqual(SPIRIT_SHIELD_WIELD_SOURCE,
                         "https://runescape.wiki/w/index.php?title=Spirit_shield&oldid=5197774; "
                         "https://web.archive.org/web/20120904064334id_/http://www.tip.it:80/runescape/?page=prayer_guide.htm")
        first = spirit_shield_equipment_data_as_dict()
        second = spirit_shield_equipment_data_as_dict()
        self.assertEqual(set(first), {"Spirit shield"})
        self.assertIsNot(first, second)
        self.assertIsNot(first["Spirit shield"], base)
        expected = {**before, "required_level": 40,
                    "skill_requirements": (("defense", 40), ("prayer", 55)),
                    "source": f"{base.source}; {SPIRIT_SHIELD_WIELD_SOURCE}"}
        self.assertEqual(asdict(first["Spirit shield"]), expected)
        self.assertEqual(asdict(EQUIPMENT_DATA["Spirit shield"]), expected)
        self.assertEqual(EQUIPMENT_ITEM_DATA["Spirit shield"], expected)
        first.clear()
        self.assertEqual(set(second), {"Spirit shield"})
        self.assertIs(GENERATED_EQUIPMENT_DATA["Spirit shield"], base)
        self.assertEqual(asdict(base), before)
        self.assertEqual(base.required_level, 1)
        self.assertEqual(base.skill_requirements, ())
        self.assertEqual(GENERATED_EQUIPMENT_DATA, generated_before)
        for url in SPIRIT_SHIELD_WIELD_SOURCE.split("; "):
            self.assertIn(url, EQUIPMENT_DATA["Spirit shield"].source)

    def test_equip_boundaries_for_both_representations(self):
        cases = (
            ("Defence 39", 39, 55, (False, "Requires level 40 Defense")),
            ("Prayer 54", 40, 54, (False, "Requires level 55 Prayer")),
            ("both below", 39, 54, (False, "Requires level 40 Defense")),
            ("eligible", 40, 55, (True, "")),
            ("missing Defence", None, 55, (False, "Requires level 40 Defense")),
            ("missing Prayer", 40, None, (False, "Requires level 55 Prayer")),
            ("missing both", None, None, (False, "Requires level 40 Defense")),
        )
        for (name, equipment_data), (case, defense, prayer, expected) in product(RUNTIME_MAPS, cases):
            with self.subTest(representation=name, boundary=case):
                player = _player(defense_level=defense, prayer_level=prayer)
                player = {key: value for key, value in player.items() if value is not None}
                before = copy.deepcopy(player)
                self.assertEqual(can_equip_item_pure("Spirit shield", equipment_data, player), expected)
                self.assertEqual(player, before)
                if not expected[0]:
                    player["quests"] = {}
                    before = copy.deepcopy(player)
                    self.assertEqual(can_equip_item_pure("Spirit shield", equipment_data, player), expected)
                    self.assertEqual(player, before)

        cases = (
            ("absent", None, False),
            ("unstarted", {"started": False, "completed": False}, False),
            ("incomplete", {"started": True, "completed": False}, False),
            ("journal progress", {"started": True, "progress": 999}, False),
            ("completed", {"completed": True}, True),
        )
        for (name, equipment_data), (case, state, completed) in product(RUNTIME_MAPS, cases):
            with self.subTest(representation=name, quest=case):
                player = _player(inventory={"Spirit shield": 1, "Jennica's ring": 1})
                if state is None:
                    player.pop("quests")
                else:
                    player["quests"] = {"summers_end": state}
                before = copy.deepcopy(player)
                self.assertEqual(can_equip_item_pure("Spirit shield", equipment_data, player),
                                 (True, "") if completed else (False, QUEST_REFUSAL))
                self.assertEqual(player, before)

    def test_saved_levels_determine_wield_gate(self):
        cases = product(RUNTIME_MAPS, (0, 99), (0, 99), (*FAILURES, ("eligible", {}, "")))
        for (name, equipment_data), current_level, current_prayer, (failure, updates, reason) in cases:
            with self.subTest(representation=name, current_level=current_level,
                              current_prayer=current_prayer, requirement=failure):
                player = _player(
                    combat_current_levels={"defense": current_level,
                                           "prayer": current_level},
                    combat_prayer_points=current_prayer, **updates,
                )
                before = copy.deepcopy(player)
                self.assertEqual(
                    can_equip_item_pure("Spirit shield", equipment_data, player),
                    (failure == "eligible", reason),
                )
                self.assertEqual(player, before)

    def test_repair_returns_only_ineligible_worn_copy(self):
        for (name, equipment_data), (failure, updates, _reason), quantity in product(RUNTIME_MAPS, FAILURES, (0, 2)):
            with self.subTest(representation=name, requirement=failure, bank_quantity=quantity):
                player = _player(**updates)
                player["equipment"]["shield"] = "Spirit shield"
                player["inventory"]["Spirit shield"] = quantity
                player.update(
                    carried_inventory={"goblin": {"Coins": 1}},
                    combat_grave={"items": ["Spirit shield"]},
                    death_office={"items": ["Spirit shield"]},
                    unrelated={"nested": [1, 2]},
                )
                before = copy.deepcopy(player)
                updated = repair(player, equipment_data)
                expected = copy.deepcopy(before)
                expected["inventory"]["Spirit shield"] += 1
                del expected["equipment"]["shield"]
                self.assertEqual(updated, expected)
                self.assertEqual(player, before)
                self.assertIsNot(updated, player)
                self.assertIsNot(updated["inventory"], player["inventory"])
                self.assertIsNot(updated["equipment"], player["equipment"])
                self.assertIs(updated["unrelated"], player["unrelated"])
                self.assertIs(repair(updated, equipment_data), updated)

    def test_repair_preserves_eligible_or_bank_only_shields(self):
        for control, player in (
            ("eligible worn", _player(equipment={"shield": "Spirit shield"})),
            ("Bank only", _player(quests={}, equipment={})),
            ("other shield", _player(quests={})),
            ("other slot", _player(quests={}, equipment={"head": "Spirit shield"})),
            ("no equipment", {"inventory": {"Spirit shield": 1}}),
            ("None equipment", {"inventory": {"Spirit shield": 1}, "equipment": None}),
        ):
            with self.subTest(control=control):
                before = copy.deepcopy(player)
                updated = repair(player, EQUIPMENT_DATA)
                self.assertEqual(updated, before)
                self.assertIs(updated, player)
                self.assertEqual(player, before)

    def test_migration_is_idempotent_for_each_schema_version(self):
        self.assertEqual(CURRENT_CONFIG_VERSION, 127)
        for version, (failure, updates, _reason), quantity in product((1, 125, 126), FAILURES, (0, 2)):
            with self.subTest(version=version, requirement=failure, bank_quantity=quantity):
                player = _player(config_version=version, **updates)
                player["equipment"]["shield"] = "Spirit shield"
                player["inventory"]["Spirit shield"] = quantity
                player["inventory"]["Unknown saved item"] = 7
                player["unrelated"] = {"nested": [1, 2]}
                result = _migrate(player)
                self.assertEqual(result["config_version"], max(version, CURRENT_CONFIG_VERSION))
                self.assertNotIn("shield", result["equipment"])
                self.assertEqual(result["equipment"]["head"], "Bronze full helm")
                self.assertEqual(result["inventory"]["Spirit shield"], quantity + 1)
                self.assertEqual(result["bank_layout"]["items"]["Spirit shield"]["quantity"], quantity + 1)
                self.assertEqual(result["inventory"]["Coins"], 17)
                self.assertEqual(result["inventory"]["Unknown saved item"], 7)
                self.assertEqual(result["unrelated"], player["unrelated"])
                self.assertEqual(
                    equipment_stat_totals_pure(result["equipment"], EQUIPMENT_DATA),
                    EQUIPMENT_DATA["Bronze full helm"].bonuses,
                )
                control = _migrate(_player(config_version=version, **updates))
                self.assertEqual(_xp(result), _xp(control))
                self.assertEqual(result["quests"]["summers_end"]["completed"],
                                 player["quests"].get("summers_end", {}).get("completed", False))
                again = _migrate(result)
                self.assertEqual(again["equipment"], result["equipment"])
                self.assertEqual(
                    {item: count for item, count in again["inventory"].items() if count},
                    {item: count for item, count in result["inventory"].items() if count},
                )
                unsaved_reload = _migrate(player)
                self.assertEqual(unsaved_reload["inventory"]["Spirit shield"], quantity + 1)

        for version, (control, player) in product((1, 125, 126), (
            ("eligible worn", _player(equipment={"shield": "Spirit shield", "head": "Bronze full helm"})),
            ("Bank only", _player(quests={}, equipment={"head": "Bronze full helm"})),
        )):
            with self.subTest(version=version, control=control):
                player["config_version"] = version
                result = _migrate(player)
                self.assertEqual(result["equipment"], player["equipment"])
                self.assertEqual(result["inventory"]["Spirit shield"], 1)
                again = _migrate(result)
                self.assertEqual(again["equipment"], result["equipment"])
                self.assertEqual(again["inventory"]["Spirit shield"], 1)
                self.assertEqual(again["config_version"], max(version, CURRENT_CONFIG_VERSION))

    def test_migration_initializes_missing_inventory(self):
        for version, inventory, (failure, updates, _reason) in product((1, 125, 126), ("absent", None), FAILURES):
            with self.subTest(version=version, inventory=inventory, requirement=failure):
                player = _player(config_version=version, **updates)
                player["equipment"]["shield"] = "Spirit shield"
                if inventory == "absent":
                    player.pop("inventory")
                else:
                    player["inventory"] = None
                result = _migrate(player)
                self.assertEqual(result["inventory"]["Spirit shield"], 1)
                self.assertEqual(result["equipment"], {"head": "Bronze full helm"})
                again = _migrate(result)
                self.assertEqual(again["inventory"]["Spirit shield"], 1)
                self.assertEqual(
                    {item: count for item, count in again["inventory"].items() if count},
                    {item: count for item, count in result["inventory"].items() if count},
                )
                self.assertEqual(again["equipment"], result["equipment"])
                self.assertEqual(again["config_version"], max(version, CURRENT_CONFIG_VERSION))

    def test_returned_shield_no_longer_supplies_bonuses(self):
        for name, equipment_data in RUNTIME_MAPS:
            with self.subTest(representation=name):
                player = _player(defense_level=39, equipment={"shield": "Spirit shield"})
                before = copy.deepcopy(player)
                worn = equipment_stat_totals_pure(player["equipment"], equipment_data)
                self.assertEqual(worn, GENERATED_EQUIPMENT_DATA["Spirit shield"].bonuses)
                self.assertTrue(any(asdict(worn).values()))
                returned = repair(player, equipment_data)
                self.assertEqual(asdict(equipment_stat_totals_pure(returned["equipment"], equipment_data)),
                                 dict.fromkeys(asdict(worn), 0))
                self.assertEqual(player, before)
                returned.update(defense_level=40)
                self.assertEqual(can_equip_item_pure("Spirit shield", equipment_data, returned), (True, ""))
