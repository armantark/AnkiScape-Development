"""Spirit shield eligibility, Bank return on load, and ordinary equip Undo."""

import copy
from dataclasses import asdict
from itertools import product
import sys
from types import SimpleNamespace
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    EQUIPMENT_DATA, EQUIPMENT_ITEM_DATA, ITEM_DEFINITIONS, ORE_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data,
)
from ankiscape.data.equipment_data import EQUIPMENT_DATA as GENERATED_EQUIPMENT_DATA
from ankiscape.logic_pure.logic_pure import can_equip_item_pure
from ankiscape.logic_pure.logic_pure_equipment import equipment_stat_totals_pure
from tests import test_direct_action_undo_seam as undo_seam
from tests.test_storage_runtime import _LegacyTextCollection, _load_storage_module


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


class SpiritShieldWieldTest(unittest.TestCase):
    def test_runtime_equipment_maps_have_source_requirements(self):
        base = GENERATED_EQUIPMENT_DATA["Spirit shield"]
        before = asdict(base)
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
        from ankiscape.data.spirit_shield_data import (
            SPIRIT_SHIELD_WIELD_SOURCE, spirit_shield_equipment_data_as_dict,
        )
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

    def test_wield_skill_boundaries(self):
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

    def test_completion_is_required(self):
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

    def test_use_saved_levels_despite_drains_and_boosts(self):
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

    def test_other_shields_keep_existing_eligibility(self):
        for name, equipment_data in RUNTIME_MAPS:
            with self.subTest(representation=name):
                self.assertEqual(can_equip_item_pure("Bronze sq shield", equipment_data, {}), (True, ""))

    def test_worn_shield_repair_conserves_items(self):
        from ankiscape.logic_pure.logic_pure_equipment import return_ineligible_spirit_shield_to_bank_pure as repair

        for (failure, updates, _reason), quantity in product(FAILURES, (0, 2)):
            with self.subTest(requirement=failure, bank_quantity=quantity):
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
                updated = repair(player, EQUIPMENT_DATA)
                expected = copy.deepcopy(before)
                expected["inventory"]["Spirit shield"] += 1
                del expected["equipment"]["shield"]
                self.assertEqual(updated, expected)
                self.assertEqual(player, before)
                self.assertIsNot(updated, player)
                self.assertIsNot(updated["inventory"], player["inventory"])
                self.assertIsNot(updated["equipment"], player["equipment"])
                self.assertIs(updated["unrelated"], player["unrelated"])
                self.assertIs(repair(updated, EQUIPMENT_DATA), updated)
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

    def test_load_repairs_old_and_current_saves(self):
        self.assertEqual(CURRENT_CONFIG_VERSION, 125)
        for version, (failure, updates, _reason), quantity in product((1, 125, 126), FAILURES, (0, 2)):
            with self.subTest(version=version, requirement=failure, bank_quantity=quantity):
                player = _player(config_version=version, **updates)
                player["equipment"]["shield"] = "Spirit shield"
                player["inventory"]["Spirit shield"] = quantity
                player["unrelated"] = {"nested": [1, 2]}
                result = _migrate(player)
                self.assertEqual(result["config_version"], max(version, 125))
                self.assertNotIn("shield", result["equipment"])
                self.assertEqual(result["equipment"]["head"], "Bronze full helm")
                self.assertEqual(result["inventory"]["Spirit shield"], quantity + 1)
                self.assertEqual(result["bank_layout"]["items"]["Spirit shield"]["quantity"], quantity + 1)
                self.assertEqual(result["inventory"]["Coins"], 17)
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
                self.assertNotIn("shield", again["equipment"])
                self.assertEqual(again["inventory"]["Spirit shield"], quantity + 1)
                unsaved_reload = _migrate(player)
                self.assertEqual(unsaved_reload["inventory"]["Spirit shield"], quantity + 1)

    def test_load_preserves_eligible_worn_and_bank_only_shields(self):
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
                self.assertEqual(again["config_version"], max(version, 125))

    def test_load_initializes_absent_or_none_bank(self):
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
                self.assertEqual(again["config_version"], max(version, 125))

    def test_repaired_save_survives_save_and_reload(self):
        original_modules = dict(sys.modules)
        self.addCleanup(sys.modules.update, original_modules)
        self.addCleanup(sys.modules.clear)
        for eligible in (False, True):
            with self.subTest(eligible=eligible):
                player = _player(quests={"summers_end": {"completed": eligible}},
                                 equipment={"shield": "Spirit shield"})
                player["inventory"]["Spirit shield"] = 2
                collection = _LegacyTextCollection()
                collection.legacy_row = False
                collection.values = {"ankiscape_player_data": player,
                                     "ankiscape_current_skill": "None"}
                persisted = copy.deepcopy(collection.values)
                storage = _load_storage_module(collection)
                loaded, skill = storage.load_player_data()
                self.assertEqual(collection.values, persisted)
                self.assertEqual(player, persisted["ankiscape_player_data"])
                expected_quantity = 2 if eligible else 3
                self.assertEqual(loaded["inventory"]["Spirit shield"], expected_quantity)
                self.assertEqual(loaded["equipment"].get("shield"), "Spirit shield" if eligible else None)
                # An unsaved record derives the same return without changing config.
                self.assertEqual(storage.load_player_data()[0]["inventory"]["Spirit shield"], expected_quantity)
                self.assertEqual(collection.values, persisted)
                storage.save_player_data(loaded, skill)
                for _ in range(2):
                    loaded, skill = storage.load_player_data()
                    self.assertEqual(loaded["inventory"]["Spirit shield"], expected_quantity)
                    self.assertEqual(loaded["equipment"].get("shield"), "Spirit shield" if eligible else None)
                    self.assertEqual(_xp(loaded), _xp(player))
                    self.assertEqual(loaded["quests"]["summers_end"]["completed"], eligible)


class SpiritShieldRuntimeTest(unittest.TestCase):
    setUp = undo_seam.DirectActionUndoSeamTest.setUp
    tearDown = undo_seam.DirectActionUndoSeamTest.tearDown

    def _capture_refusals(self):
        errors = []
        self.addon.show_error_message = lambda title, message: errors.append((title, message))
        return errors

    def _undo(self):
        self.addon._on_state_did_undo(SimpleNamespace(operation=self.collection.entries.pop()))

    def _assert_refused(self, player, reason):
        self.addon._state.player_data = player
        errors = self._capture_refusals()
        before = copy.deepcopy(player)
        entries = list(self.collection.entries)
        snapshots = list(self.addon._state.direct_action_undo_stack)
        self.assertFalse(self.addon.on_equip_item("Spirit shield"))
        self.assertEqual(errors, [("Cannot equip item", reason)])
        self.assertEqual(self.addon._state.player_data, before)
        self.assertEqual(player, before)
        self.assertEqual(self.saves, [])
        self.assertEqual(self.collection.entries, entries)
        self.assertEqual(self.addon._state.direct_action_undo_stack, snapshots)

    def _assert_equip_and_undo(self, player):
        self.addon._state.player_data = player
        errors = self._capture_refusals()
        before = copy.deepcopy(player)
        depth = len(self.addon._state.direct_action_undo_stack)
        self.assertTrue(self.addon.on_equip_item("Spirit shield"))
        result = self.addon._state.player_data
        self.assertEqual(errors, [])
        self.assertEqual(result["inventory"]["Spirit shield"], before["inventory"]["Spirit shield"] - 1)
        self.assertEqual(result["equipment"]["shield"], "Spirit shield")
        displaced = before["equipment"].get("shield")
        if displaced:
            self.assertEqual(result["inventory"][displaced], before["inventory"].get(displaced, 0) + 1)
        self.assertEqual(result["quests"], before["quests"])
        self.assertEqual(_xp(result), _xp(before))
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(self.addon._state.direct_action_undo_stack), depth + 1)
        self.assertEqual(len(self.saves), 1)
        self._undo()
        self.assertEqual(self.addon._state.player_data, before)
        self.assertEqual(len(self.addon._state.direct_action_undo_stack), depth)

    def test_runtime_refusals_preserve_save(self):
        for failure, updates, reason in FAILURES:
            with self.subTest(requirement=failure):
                self._assert_refused(_player(**updates), reason)

    def test_runtime_equip_and_undo(self):
        self._assert_equip_and_undo(_player())

    def test_runtime_still_requires_owned_shield(self):
        self._assert_refused(_player(inventory={"Coins": 17}),
                             "You need Spirit shield in your bank to equip it.")

    def test_returned_shield_cannot_be_re_equipped_until_eligible(self):
        player = _player(defense_level=39, prayer_level=54, quests={},
                         equipment={"shield": "Spirit shield", "head": "Bronze full helm"},
                         inventory={"Coins": 17})
        repaired = _migrate(player)
        self.assertNotIn("shield", repaired["equipment"])
        self.assertEqual(repaired["inventory"]["Spirit shield"], 1)
        self._assert_refused(repaired, "Requires level 40 Defense")
        self.assertEqual(self.collection.entries, [])
        repaired.update(defense_level=40, prayer_level=55,
                        quests={"summers_end": {"completed": True}})
        self._assert_equip_and_undo(repaired)
