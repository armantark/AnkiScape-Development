"""The ordinary Oronwen transaction takes two eligible quest reviews."""

import copy
import json
import random
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest.oronwen_repair_data import (
    QUEST_ID, DAMAGED_TROUSERS, REPAIRED_TROUSERS, REPAIR_INPUTS,
    PENDING_KEY, MOURNER_ENCOUNTER, ORONWEN_REPAIR_ITEMS, STATE_SOURCE,
)
from ankiscape.data.quest_action_proof_data import ORONWEN_REPAIR_PROOF
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_combat_encounter_pure, apply_quest_progress_pure,
    can_attempt_quest_review_pure, can_progress_quest_pure,
    quest_current_stage_blockers_pure,
)
from ankiscape.logic_pure.quest.oronwen import (
    apply_oronwen_review_pure, oronwen_phase_pure,
    oronwen_requirement_pure, oronwen_review_ready_pure,
)
from ankiscape.logic_pure.quest_action_proofs import record_runtime_quest_action_proofs_pure

UNRELATED_INPUTS = {"Feather": 1, "Toad crunchies": 1, "Magic logs": 1, "Leather": 1, "Ogre bellows": 1}


def _player(stage=3):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["quests"][QUEST_ID] = dict(started=True, completed=False, progress=stage)
    player["current_quest"] = QUEST_ID
    player["inventory"] = dict(UNRELATED_INPUTS, **dict(REPAIR_INPUTS))
    return player


def _blockers(player):
    return quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA)


def _progress(player, **kwargs):
    return apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA, **kwargs)


def _inventory(player):
    return {name: quantity for name, quantity in player["inventory"].items() if quantity}


def _reload(player, version=None):
    saved = json.loads(json.dumps(player))
    if version is not None:
        saved["config_version"] = version
    return migrate_loaded_data(saved, ORE_DATA, ITEM_DEFINITIONS)


class OronwenCatalogTest(unittest.TestCase):
    def test_encounter_moves_once_with_only_damaged_trousers_and_unchanged_combat(self):
        rows = QUEST_DATA[QUEST_ID]["stage_requirements"]
        located = [(row["stage"], encounter) for row in rows for encounter in row["combat_encounters"]]
        self.assertEqual(len(located), 1)
        stage, encounter = located[0]
        self.assertEqual(stage, 2)
        self.assertEqual(encounter["encounter_id"], MOURNER_ENCOUNTER)
        self.assertEqual(encounter["guaranteed_drops"], {DAMAGED_TROUSERS: 1})
        generated = next(q for q in PRE_EOC_QUEST_CATALOG if q["id"] == QUEST_ID)
        original = next(e for row in generated["stage_requirements"] for e in row["combat_encounters"])
        for key, value in original.items():
            self.assertEqual(encounter[key], value, key)
        self.assertFalse(next(row for row in rows if row["stage"] == 6)["combat_encounters"])
        second = next(row for row in rows if row["stage"] == 2)
        self.assertEqual(second["required_inventory"], {"Bucket of water": 1})
        self.assertEqual(second["required_actions"], ())
        self.assertEqual(second["produced_inventory"], {})
        self.assertEqual(second["auto_actions"], ("Take the damaged mourner trousers from the defeated Mourner",))

    def test_stage_three_requires_exact_inputs_unrelated_items_and_real_proof(self):
        row = next(r for r in QUEST_DATA[QUEST_ID]["stage_requirements"] if r["stage"] == 3)
        self.assertEqual(row["required_inventory"], dict(UNRELATED_INPUTS, **dict(REPAIR_INPUTS)))
        self.assertEqual(row["required_actions"], (ORONWEN_REPAIR_PROOF,))
        self.assertEqual(row["auto_actions"], ())
        for field in ("consumed_inventory", "produced_inventory", "required_tools"):
            self.assertEqual(row[field], {})
        self.assertEqual(row["required_skills"], ())

    def test_distinct_registered_inventory_states_without_numeric_or_equipment_binding(self):
        items = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for name in (DAMAGED_TROUSERS, REPAIRED_TROUSERS):
            self.assertEqual(ORONWEN_REPAIR_ITEMS[name], dict(
                category="material", stackable=False, tradeable=False, source=STATE_SOURCE,
            ))
            item = items[name]
            self.assertEqual(item.category, "material")
            self.assertFalse(item.tradeable)
            self.assertFalse(item.stackable)
            self.assertIsNone(item.source_item_id)
            self.assertIsNone(item.equipment_slot)
            self.assertIsNone(item.asset_path)
        self.assertNotEqual(items[DAMAGED_TROUSERS].id, items[REPAIRED_TROUSERS].id)
        self.assertNotIn("Mourner trousers", ORONWEN_REPAIR_ITEMS)
        self.assertFalse({DAMAGED_TROUSERS, REPAIRED_TROUSERS} & QUEST_DATA[QUEST_ID]["rewards"].keys())

    def test_only_winning_combat_grants_trousers_then_stage_two_progresses(self):
        player = _player(2)
        player["inventory"] = {"Bucket of water": 1}
        player.update(attack_level=50, strength_level=50, defense_level=99,
                      constitution_level=99, combat_lifepoints=990)
        rng = random.Random(12)
        self.assertEqual(_reload(player)["inventory"].get(DAMAGED_TROUSERS, 0), 0)
        refused, ok, _ = _progress(player)
        self.assertFalse(ok)
        self.assertEqual(refused, player)
        results = []
        for _ in range(300):
            before = copy.deepcopy(player)
            player, ok, result = apply_quest_combat_encounter_pure(
                player, QUEST_ID, QUEST_DATA, MOURNER_ENCOUNTER,
                rng=rng.random, equipment_data=EQUIPMENT_DATA, ticks=1, live_cadence=True,
            )
            self.assertTrue(ok)
            results.append(result)
            self.assertNotIn(DAMAGED_TROUSERS, before["inventory"])
            if result.get("killed"):
                break
            self.assertNotIn(DAMAGED_TROUSERS, player["inventory"])
        else:
            self.fail("Deterministic Mourner fight did not finish")
        self.assertGreater(len(results), 1)
        self.assertFalse(results[0].get("killed"))
        self.assertEqual(player["inventory"][DAMAGED_TROUSERS], 1)
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 2)
        self.assertEqual(player["quest_action_proofs"], [])
        advanced, ok, completed = _progress(player)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(advanced["quests"][QUEST_ID]["progress"], 3)
        self.assertEqual(advanced["inventory"][DAMAGED_TROUSERS], 1)
        again, ok, _ = apply_quest_combat_encounter_pure(advanced, QUEST_ID, QUEST_DATA, MOURNER_ENCOUNTER)
        self.assertFalse(ok)
        self.assertEqual(again, advanced)

    def test_losing_combat_never_grants_trousers(self):
        player = _player(2)
        player["inventory"] = {"Bucket of water": 1}
        player.update(combat_lifepoints=1, constitution_level=1)
        rng = random.Random(2)
        for _ in range(40):
            player, ok, result = apply_quest_combat_encounter_pure(
                player, QUEST_ID, QUEST_DATA, MOURNER_ENCOUNTER,
                rng=rng.random, equipment_data=EQUIPMENT_DATA, ticks=6, live_cadence=True,
            )
            self.assertTrue(ok)
            self.assertNotIn(DAMAGED_TROUSERS, player["inventory"])
            if result.get("died"):
                break
        else:
            self.fail("Deterministic losing fight did not finish")
        self.assertNotIn(MOURNER_ENCOUNTER, player["quest_combat_encounters"].get(QUEST_ID, ()))


class OronwenTransactionTest(unittest.TestCase):
    def test_two_reviews_debit_once_record_once_and_preserve_input_objects_and_rewards(self):
        for include_clue_refusal in (False, True):
            with self.subTest(four_values=include_clue_refusal):
                self._assert_repair_transaction(include_clue_refusal)

    def _assert_repair_transaction(self, include_clue_refusal):
        player = _player()
        self.assertEqual(player["crafting_level"], 1)
        self.assertNotIn("Needle", player["inventory"])
        self.assertNotIn("Thread", player["inventory"])
        for name, quantity in REPAIR_INPUTS:
            player["inventory"][name] = quantity + 3
        before = copy.deepcopy(player)
        first = _progress(player, include_clue_refusal=include_clue_refusal)
        handed, ok, completed = first[:3]
        self.assertEqual(len(first), 4 if include_clue_refusal else 3)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(player, before)
        self.assertEqual(handed["quests"][QUEST_ID]["progress"], 3)
        self.assertIs(handed[PENDING_KEY], True)
        self.assertNotIn(REPAIRED_TROUSERS, handed["inventory"])
        self.assertNotIn(ORONWEN_REPAIR_PROOF, handed["quest_action_proofs"])
        for name, _ in REPAIR_INPUTS:
            self.assertEqual(handed["inventory"][name], 3)
        in_custody = copy.deepcopy(handed)
        with patch("ankiscape.logic_pure.quest.oronwen.record_runtime_quest_action_proofs_pure", wraps=record_runtime_quest_action_proofs_pure) as recorder:
            second = _progress(handed, include_clue_refusal=include_clue_refusal)
        collected, ok, completed = second[:3]
        self.assertEqual(len(second), len(first))
        self.assertEqual(handed, in_custody)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(collected["quests"][QUEST_ID]["progress"], 4)
        self.assertIs(collected[PENDING_KEY], False)
        self.assertEqual(collected["inventory"][REPAIRED_TROUSERS], 1)
        self.assertEqual(collected["quest_action_proofs"], [ORONWEN_REPAIR_PROOF])
        recorder.assert_called_once_with(collected, "quest_service", "oronwen_repair")
        self.assertEqual(collected["quest_points"], before["quest_points"])
        for key in before:
            if key.endswith("_exp") or key == "pending_skill_exp_rewards":
                self.assertEqual(handed[key], before[key])
                self.assertEqual(collected[key], before[key])
        for name, _ in REPAIR_INPUTS:
            self.assertEqual(collected["inventory"][name], 3)
        for name, quantity in UNRELATED_INPUTS.items():
            self.assertEqual(collected["inventory"][name], quantity)
        repeated, ok, _ = _progress(collected)
        self.assertFalse(ok)
        self.assertEqual(repeated, collected)

    def test_each_missing_input_and_each_unrelated_material_refuses_atomically(self):
        for name, quantity in dict(UNRELATED_INPUTS, **dict(REPAIR_INPUTS)).items():
            with self.subTest(item=name):
                player = _player()
                player["inventory"][name] = quantity - 1
                before = copy.deepcopy(player)
                self.assertFalse(oronwen_review_ready_pure(player, QUEST_ID, _blockers(player)))
                self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))
                for four in (False, True):
                    result = _progress(player, include_clue_refusal=four)
                    self.assertFalse(result[1])
                    self.assertEqual(result[0], before)
                self.assertEqual(player, before)

    def test_readiness_and_strict_progression_before_pending_and_after_proof(self):
        player = _player()
        for expected_phase in ("hand_in", "collect"):
            self.assertEqual(oronwen_phase_pure(player, QUEST_ID), expected_phase)
            self.assertEqual([(b["kind"], b.get("action_id")) for b in _blockers(player)], [("required_action", ORONWEN_REPAIR_PROOF)])
            self.assertFalse(can_progress_quest_pure(player, QUEST_ID, QUEST_DATA))
            self.assertTrue(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))
            self.assertTrue(oronwen_review_ready_pure(player, QUEST_ID, _blockers(player)))
            if expected_phase == "hand_in":
                player = _progress(player)[0]
        for name, _ in REPAIR_INPUTS:
            self.assertEqual(player["inventory"][name], 0)
        complete, result = apply_oronwen_review_pure(player, QUEST_ID, _blockers(player))
        self.assertEqual(result, "collected")
        self.assertEqual(oronwen_phase_pure(complete, QUEST_ID), "complete")
        complete[PENDING_KEY] = True  # Proof takes precedence over stale custody.
        self.assertEqual(oronwen_phase_pure(complete, QUEST_ID), "complete")
        self.assertFalse(oronwen_review_ready_pure(complete, QUEST_ID, ()))
        self.assertEqual(_blockers(complete), ())
        self.assertTrue(can_progress_quest_pure(complete, QUEST_ID, QUEST_DATA))
        same, result = apply_oronwen_review_pure(complete, QUEST_ID, ())
        self.assertIs(same, complete)
        self.assertEqual(result, "unchanged")

    def test_pending_still_requires_unrelated_materials(self):
        pending = _progress(_player())[0]
        for item in UNRELATED_INPUTS:
            player = copy.deepcopy(pending)
            player["inventory"][item] = 0
            before = copy.deepcopy(player)
            self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))
            self.assertFalse(_progress(player)[1])
            self.assertEqual(player, before)

    def test_repaired_pair_does_not_replace_payment_or_proof(self):
        player = _player()
        player["inventory"][REPAIRED_TROUSERS] = 1
        del player["inventory"][DAMAGED_TROUSERS]
        self.assertFalse(_progress(player)[1])
        self.assertFalse(can_progress_quest_pure(player, QUEST_ID, QUEST_DATA))
        player["inventory"][DAMAGED_TROUSERS] = 1
        pending = _progress(player)[0]
        self.assertEqual(pending["inventory"][REPAIRED_TROUSERS], 1)
        self.assertNotIn(ORONWEN_REPAIR_PROOF, pending["quest_action_proofs"])
        self.assertEqual(_progress(pending)[0]["inventory"][REPAIRED_TROUSERS], 2)

    def test_requirement_copy_removes_only_paid_inputs_and_keeps_every_other_predicate(self):
        row = next(r for r in QUEST_DATA[QUEST_ID]["stage_requirements"] if r["stage"] == 3)
        before = copy.deepcopy(row)
        player = _player()
        self.assertIs(oronwen_requirement_pure(player, QUEST_ID, row), row)
        player = _progress(player)[0]
        adjusted = oronwen_requirement_pure(player, QUEST_ID, row)
        self.assertIsNot(adjusted, row)
        self.assertIsNot(adjusted["required_inventory"], row["required_inventory"])
        self.assertEqual(adjusted, dict(row, required_inventory=UNRELATED_INPUTS))
        self.assertEqual(row, before)
        other_stage = dict(row, stage=2)
        self.assertIs(oronwen_requirement_pure(player, QUEST_ID, other_stage), other_stage)

    def test_wrong_quest_stage_unstarted_and_completed_never_enter_service(self):
        for quest_id, stage, started, completed in (
            ("rune_mysteries", 3, True, False), (QUEST_ID, 2, True, False),
            (QUEST_ID, 4, True, False), (QUEST_ID, 3, False, False),
            (QUEST_ID, 3, True, True),
        ):
            with self.subTest(quest=quest_id, stage=stage, started=started, completed=completed):
                player = _player(stage)
                player["quests"][quest_id] = dict(started=started, completed=completed, progress=stage)
                player[PENDING_KEY] = True
                before = copy.deepcopy(player)
                self.assertIsNone(oronwen_phase_pure(player, quest_id))
                same, result = apply_oronwen_review_pure(player, quest_id, ())
                self.assertIs(same, player)
                self.assertEqual(result, "unchanged")
                self.assertEqual(player, before)

    def test_readiness_independently_checks_inputs_and_rejects_every_other_blocker(self):
        player = _player()
        for name, quantity in REPAIR_INPUTS:
            missing = copy.deepcopy(player)
            missing["inventory"][name] = quantity - 1
            self.assertFalse(oronwen_review_ready_pure(missing, QUEST_ID, ()))
        for blocker in ({"kind": "required_action", "action_id": "Other action"},
                        {"kind": "missing_item", "action_id": ORONWEN_REPAIR_PROOF}):
            self.assertFalse(oronwen_review_ready_pure(player, QUEST_ID, (blocker,)))


class OronwenMigrationTest(unittest.TestCase):
    def test_old_stranded_stage_rewinds_without_grants_or_other_mutations(self):
        player = _player()
        player["inventory"] = {"Silk": 2, "Bear fur": 1, REPAIRED_TROUSERS: 1}
        player[PENDING_KEY] = True
        player["quest_stage_actions"] = {QUEST_ID: [ORONWEN_REPAIR_PROOF]}
        player["action_counts"] = {"quest_service:oronwen_repair": 20}
        migrated = _reload(player, 124)
        self.assertEqual(migrated["quests"][QUEST_ID]["progress"], 2)
        self.assertIs(migrated[PENDING_KEY], False)
        self.assertEqual(_inventory(migrated), _inventory(player))
        self.assertNotIn(ORONWEN_REPAIR_PROOF, migrated["quest_action_proofs"])
        for key in ("quest_points", "crafting_exp", "quest_combat_encounters", "quest_combat_encounter_counts"):
            self.assertEqual(migrated[key], player[key])
        self.assertEqual(_reload(migrated), migrated)

    def test_old_save_rewind_exemptions(self):
        cases = (
            ("unstarted", lambda p: p["quests"][QUEST_ID].update(started=False)),
            ("completed", lambda p: p["quests"][QUEST_ID].update(completed=True)),
            ("earlier", lambda p: p["quests"][QUEST_ID].update(progress=2)),
            ("later", lambda p: p["quests"][QUEST_ID].update(progress=4)),
            ("damaged", lambda p: p["inventory"].update({DAMAGED_TROUSERS: 1})),
            ("proof", lambda p: p["quest_action_proofs"].append(ORONWEN_REPAIR_PROOF)),
            ("flag", lambda p: p["quest_combat_encounters"].update({QUEST_ID: [MOURNER_ENCOUNTER]})),
            ("count", lambda p: p["quest_combat_encounter_counts"].update({QUEST_ID: {MOURNER_ENCOUNTER: 1}})),
        )
        for name, change in cases:
            with self.subTest(exemption=name):
                player = _player()
                del player["inventory"][DAMAGED_TROUSERS]
                change(player)
                migrated = _reload(player, 124)
                self.assertEqual(migrated["quests"][QUEST_ID], player["quests"][QUEST_ID])
                self.assertEqual(_inventory(migrated), _inventory(player))
                self.assertEqual(migrated["quest_action_proofs"], player["quest_action_proofs"])
                self.assertIs(migrated[PENDING_KEY], False)
                for key in ("quest_combat_encounters", "quest_combat_encounter_counts"):
                    self.assertEqual(migrated[key], player[key])

    def test_current_pending_is_strict_boolean_and_valid_only_at_unfinished_stage_three(self):
        for version in (125, 126):
            for raw in (True, False, 1, 0, "true", "False", [], {}, None):
                with self.subTest(version=version, pending=raw):
                    player = _player()
                    player[PENDING_KEY] = raw
                    migrated = _reload(player, version)
                    self.assertIs(migrated[PENDING_KEY], raw is True)
                    self.assertEqual(_inventory(migrated), _inventory(player))
                    self.assertEqual(migrated["quest_action_proofs"], [])
                    self.assertEqual(migrated["quests"][QUEST_ID]["progress"], 3)
                    self.assertEqual(_reload(migrated), migrated)
        for fields, proof in ((dict(started=False), False), (dict(completed=True), False),
                              (dict(progress=2), False), (dict(progress=4), False), ({}, True)):
            player = _player()
            player[PENDING_KEY] = True
            player["quests"][QUEST_ID].update(fields)
            if proof:
                player["quest_action_proofs"] = [ORONWEN_REPAIR_PROOF]
            self.assertIs(_reload(player)[PENDING_KEY], False)

    def test_current_stranded_save_does_not_rewind_or_infer_a_repair(self):
        player = _player()
        del player["inventory"][DAMAGED_TROUSERS]
        migrated = _reload(player)
        self.assertEqual(migrated["quests"][QUEST_ID]["progress"], 3)
        self.assertFalse(can_attempt_quest_review_pure(migrated, QUEST_ID, QUEST_DATA))
        self.assertEqual(migrated["inventory"].get(REPAIRED_TROUSERS, 0), 0)
        self.assertEqual(migrated["quest_action_proofs"], [])

    def test_save_reload_between_phases_retains_custody_without_free_output_or_proof(self):
        pending = _progress(_player())[0]
        reloaded = _reload(pending)
        self.assertEqual(_inventory(reloaded), _inventory(pending))
        self.assertIs(reloaded[PENDING_KEY], True)
        self.assertEqual(reloaded["quest_action_proofs"], [])
        self.assertEqual(reloaded["inventory"].get(REPAIRED_TROUSERS, 0), 0)
        collected, ok, completed = _progress(reloaded)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(collected["quests"][QUEST_ID]["progress"], 4)
        self.assertEqual(collected["inventory"][REPAIRED_TROUSERS], 1)
        loaded = _reload(collected)
        for key in ("inventory", "quests", "quest_action_proofs", PENDING_KEY, "quest_points", "crafting_exp"):
            self.assertEqual(loaded[key], collected[key])
        self.assertEqual(_reload(loaded), loaded)
