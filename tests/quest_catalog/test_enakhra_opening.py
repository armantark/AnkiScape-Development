"""Canonical sandstone, ordered custody and stage-one service transactions."""

import copy
import json
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest.enakhra_opening import (
    QUEST_ID, MASS_KEY, SANDSTONE, BLOCK, BASE, PROOFS, SPLIT_OUTPUTS,
)
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, can_start_quest_pure, can_progress_quest_pure,
    can_attempt_quest_review_pure, quest_current_stage_blockers_pure,
)
from ankiscape.logic_pure.quest.enakhra import (
    apply_enakhra_opening_action_pure, enakhra_opening_phase_pure,
    enakhra_opening_next_action_pure, enakhra_opening_blockers_pure, INCONSISTENT,
)
from ankiscape.logic_pure.quest.review_services import (
    quest_service_review_ready_pure, apply_quest_service_review_pure,
)
from ankiscape.logic_pure.quest_action_proofs import record_runtime_quest_action_proofs_pure


def _player(progress=1, inventory=None, started=True):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["current_quest"] = QUEST_ID
    player["quests"][QUEST_ID] = dict(started=started, completed=False, progress=progress)
    player["inventory"] = dict(inventory if inventory is not None else {"Sandstone (10kg)": 3, "Sandstone (2kg)": 1})
    for skill, level in (("crafting", 50), ("firemaking", 45), ("prayer", 43), ("magic", 39)):
        player[skill + "_level"] = level
        player[skill + "_exp"] = EXP_TABLE[level - 1]
    return player


def _progress(player, **kwargs):
    return apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA, **kwargs)


def _act(player, action, item_id=None):
    candidate, ok, descriptor = apply_enakhra_opening_action_pure(player, action, item_id)
    if not ok:
        raise AssertionError(descriptor)
    return candidate


def _reload(player):
    return migrate_loaded_data(json.loads(json.dumps(player)), ORE_DATA, ITEM_DEFINITIONS)


def _route(player):
    snapshots = [player]
    for _ in range(60):
        candidate, ok, completed = _progress(snapshots[-1])
        if not ok or completed:
            raise AssertionError((ok, completed, enakhra_opening_next_action_pure(snapshots[-1])))
        snapshots.append(candidate)
        if candidate["quests"][QUEST_ID]["progress"] == 2:
            return snapshots
    raise AssertionError("Opening did not reach placement")


class EnakhraCatalogTest(unittest.TestCase):
    def test_only_opening_and_later_fuel_requirements_change(self):
        quest = QUEST_DATA[QUEST_ID]
        rows = {row["stage"]: row for row in quest["stage_requirements"]}
        opening = rows[1]
        for key in ("required_inventory", "required_tools", "consumed_inventory", "produced_inventory"):
            self.assertEqual(opening[key], {})
        self.assertEqual(opening["required_inventory_options"], ())
        self.assertEqual(opening["auto_actions"], ())
        self.assertEqual(opening["required_actions"], (PROOFS["place_base"],))
        self.assertEqual(rows[5]["required_inventory"], dict(Candle=1, Logs=1, **{
            "Oak logs": 1, "Willow logs": 1, "Maple logs": 1, "Coal": 1}))
        self.assertEqual(rows[5]["required_actions"], ("Cast Crumble Undead during the boneguard fight",))
        self.assertEqual(rows[4]["required_inventory"], {"Bread": 1})
        self.assertEqual(rows[2]["required_inventory"], {"Granite (5kg)": 1})
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        for stage in (2, 3, 6):
            original = next(row for row in generated["stage_requirements"] if row["stage"] == stage)
            self._assert_unchanged_stage(rows[stage], original)
        self.assertEqual(quest["stages"], 7)
        self.assertEqual(quest["point_reward"], 2)
        self.assertEqual(quest["rewards"], {"Big bones": 5, "Camel mask": 1, "Camulet": 1})
        self.assertEqual(quest["xp_rewards"], tuple(dict(skill_id=skill, amount=7000.0) for skill in ("crafting", "firemaking", "magic", "mining")))
        self.assertEqual(quest["lamp_rewards"], ())
        self.assertEqual(quest["unlocks"], ())

    def _assert_unchanged_stage(self, actual, original):
        for field in ("required_actions", "auto_actions", "required_skills", "combat_encounters"):
            self.assertEqual(actual[field], original.get(field, ()))
        inventory = dict(original["required_inventory"])
        if "Granite rock" in inventory:
            inventory["Granite (5kg)"] = inventory.pop("Granite rock")
        self.assertEqual(actual["required_inventory"], inventory)

    def test_entry_at_mining_one_requires_exactly_four_existing_skills(self):
        player = _player(started=False)
        self.assertEqual(player["mining_level"], 1)
        self.assertTrue(can_start_quest_pure(player, QUEST_ID, QUEST_DATA))
        self.assertEqual({r["skill_id"]: r["level"] for r in QUEST_DATA[QUEST_ID]["required_skills"]},
                         dict(crafting=50, firemaking=45, magic=39, prayer=43))
        for skill in ("crafting", "firemaking", "magic", "prayer"):
            locked = copy.deepcopy(player)
            locked[skill + "_level"] -= 1
            self.assertFalse(can_start_quest_pure(locked, QUEST_ID, QUEST_DATA))
            self.assertFalse(_progress(locked)[1])
        before = copy.deepcopy(player)
        descriptor = enakhra_opening_next_action_pure(player)
        self.assertEqual(descriptor["action_id"], "offer_help")
        self.assertEqual(player, before)
        self.assertFalse(apply_enakhra_opening_action_pure(player, "offer_help")[1])
        begun, ok, done = _progress(player)
        self.assertTrue(ok)
        self.assertFalse(done)
        self.assertEqual(begun["quests"][QUEST_ID]["progress"], 0)
        self.assertEqual(begun["quest_action_proofs"], [PROOFS["offer_help"]])


class EnakhraTransactionTest(unittest.TestCase):
    def assert_refused(self, player, action, item_id=None, notice=None):
        before = copy.deepcopy(player)
        same, ok, descriptor = apply_enakhra_opening_action_pure(player, action, item_id)
        self.assertFalse(ok)
        self.assertIs(same, player)
        self.assertEqual(player, before)
        if notice:
            self.assertEqual(descriptor["notice"], notice)

    def test_ordered_reviews_preserve_progress_and_rewards_until_placement(self):
        for incoming in (0, 1):
            for four in (False, True):
                self._assert_ordered_reviews(incoming, four)

    def _assert_ordered_reviews(self, incoming, four):
        player = _player(incoming)
        original = copy.deepcopy(player)
        actions = []
        for expected in ("offer_help", "deliver_sandstone", "deliver_sandstone", "deliver_sandstone",
                         "receive_32kg", "chisel_base", "talk_after_base", "place_base"):
            self.assertEqual(enakhra_opening_next_action_pure(player)["action_id"], expected)
            self.assertFalse(can_progress_quest_pure(player, QUEST_ID, QUEST_DATA))
            self.assertTrue(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))
            before = copy.deepcopy(player)
            with patch("ankiscape.logic_pure.quest.enakhra.record_runtime_quest_action_proofs_pure", wraps=record_runtime_quest_action_proofs_pure) as recorder:
                result = _progress(player, include_clue_refusal=four)
            actions.append(expected)
            self.assertEqual(player, before)
            self.assertTrue(result[1])
            self.assertFalse(result[2])
            self.assertEqual(len(result), 4 if four else 3)
            player = result[0]
            recorder.assert_called_once()
            self.assertEqual(recorder.call_args.args[1:], ("quest_service", "enakhras_lament_" + expected))
            self.assertEqual(player["quests"][QUEST_ID]["progress"], 2 if expected == "place_base" else incoming)
            self.assertFalse(player["quests"][QUEST_ID]["completed"])
            self.assertEqual(player["quest_points"], original["quest_points"])
            for key in original:
                if key.endswith("_exp") or key == "pending_skill_exp_rewards":
                    self.assertEqual(player[key], original[key])
        self.assertEqual(player[MASS_KEY], 32)
        self.assertEqual(player["inventory"].get(BLOCK, 0), 0)
        self.assertEqual(player["inventory"].get(BASE, 0), 0)
        self.assertEqual(len(actions), 8)

    def test_each_canonical_size_and_mixed_incremental_delivery(self):
        for item_id, (name, mass) in SANDSTONE.items():
            player = _act(_player(inventory={name: 1}), "offer_help")
            before = copy.deepcopy(player)
            player, ok, descriptor = apply_enakhra_opening_action_pure(player, "deliver_sandstone", item_id)
            self.assertTrue(ok)
            self.assertEqual(player[MASS_KEY], mass)
            self.assertEqual(player["inventory"][name], 0)
            self.assertEqual(descriptor["item_id"], item_id)
            self.assertEqual(descriptor["input_mass"], mass)
            self.assertEqual(before["inventory"][name], 1)
            self.assertNotIn(BLOCK, player["inventory"])
        player = _act(_player(inventory={name: 4 for name, _ in SANDSTONE.values()}), "offer_help")
        for item_id, total in ((6977, 10), (6975, 15), (6973, 17), (6971, 18), (6977, 28), (6973, 30), (6973, 32)):
            player = _act(player, "deliver_sandstone", item_id)
            self.assertEqual(player[MASS_KEY], total)
            self.assertEqual(player["inventory"].get(BLOCK, 0), int(total == 32))
        self.assertIn(PROOFS["receive_32kg"], player["quest_action_proofs"])

    def test_thirty_plus_two_receives_once_but_thirty_one_plus_two_refuses_whole(self):
        player = _act(_player(inventory={"Sandstone (10kg)": 3, "Sandstone (1kg)": 1, "Sandstone (2kg)": 1}), "offer_help")
        for _ in range(3):
            player = _act(player, "deliver_sandstone", 6977)
        exact = _act(player, "deliver_sandstone", 6973)
        self.assertEqual(exact["inventory"][BLOCK], 1)
        player = _act(player, "deliver_sandstone", 6971)
        self.assertEqual(player[MASS_KEY], 31)
        self.assert_refused(player, "deliver_sandstone", 6973)
        self.assertEqual(enakhra_opening_next_action_pure(player)["action_id"], "split_2kg")
        for action in ("deliver_sandstone", "receive_32kg"):
            self.assert_refused(exact, action, 6973)

    def test_explicit_receipt_requires_the_final_selected_block(self):
        player = _act(_player(), "offer_help")
        self.assert_refused(player, "receive_32kg", 6977)
        for _ in range(3):
            player = _act(player, "deliver_sandstone", 6977)
        received = _act(player, "receive_32kg", 6973)
        self.assertEqual(received[MASS_KEY], 32)
        self.assertEqual(received["inventory"][BLOCK], 1)
        self.assert_refused(received, "receive_32kg", 6973)

    def test_generic_noted_absent_invalid_and_similar_inputs_are_never_payment(self):
        player = _act(_player(inventory={"Sandstone": 50, "Sandstone (2kg) noted": 1, "sandstone (2kg)": 1,
                                          "Coal": 100, "Chisel": 1}), "offer_help")
        for item_id in (None, True, 2.0, "6973", "Sandstone (2kg)", 6972, 6974, 6976, 6978, 453, 1755, 6986, 6988, -1, {}, []):
            self.assert_refused(player, "deliver_sandstone", item_id)
        self.assert_refused(player, "deliver_sandstone", 6973)
        self.assertEqual(enakhra_opening_blockers_pure(player)[0]["reason"], "Needs sandstone: 32 kg still to give Lazim")
        self.assertFalse(_progress(player)[1])

    def test_all_split_recipes_conserve_mass_retain_tools_and_take_their_own_review(self):
        for item_id, outputs in SPLIT_OUTPUTS.items():
            name, mass = SANDSTONE[item_id]
            player = _act(_player(0, inventory={name: 3, "Chisel": 1}), "offer_help")
            experience = player["crafting_exp"], player["mining_exp"]
            for _ in range(2):
                player = _act(player, f"split_{mass}kg", item_id)
                self.assertEqual((player["crafting_exp"], player["mining_exp"]), experience)
            self.assertEqual(player["inventory"][name], 1)
            self.assertEqual(player["inventory"]["Chisel"], 1)
            self.assertEqual(player[MASS_KEY], 0)
            self.assertEqual(player["quests"][QUEST_ID]["progress"], 0)
            self.assertNotIn(PROOFS["deliver_sandstone"], player["quest_action_proofs"])
            self.assertEqual(sum(SANDSTONE[i][1] * n for i, n in outputs), mass)
            for output_id, quantity in outputs:
                self.assertEqual(player["inventory"][SANDSTONE[output_id][0]], quantity * 2)
        player = _act(_player(inventory={"Sandstone (10kg)": 4}), "offer_help")
        for _ in range(3):
            player = _act(player, "deliver_sandstone", 6977)
        split, ok, _ = _progress(player)
        self.assertTrue(ok)
        self.assertEqual(split[MASS_KEY], 30)
        self.assertEqual(split["inventory"]["Sandstone (5kg)"], 2)
        self.assertEqual(enakhra_opening_next_action_pure(split)["action_id"], "split_5kg")
        self.assert_refused(player, "split_1kg", 6971)
        self.assert_refused(player, "split_10kg", 6975)

    def test_largest_fitting_and_then_largest_oversized_selection(self):
        player = _act(_player(inventory={name: 9 for name, _ in SANDSTONE.values()}), "offer_help")
        for total, selected in ((0, 6977), (23, 6975), (29, 6973), (31, 6971)):
            player[MASS_KEY] = total
            player["quest_action_proofs"] = [PROOFS["offer_help"]] + ([PROOFS["deliver_sandstone"]] if total else [])
            self.assertEqual(enakhra_opening_next_action_pure(player)["item_id"], selected)
        player["inventory"].pop("Sandstone (1kg)")
        self.assertEqual(enakhra_opening_next_action_pure(player)["item_id"], 6977)
        player["inventory"].pop("Sandstone (10kg)")
        self.assertEqual(enakhra_opening_next_action_pure(player)["item_id"], 6975)

    def test_chisel_uses_held_or_existing_belt_resolver_and_retains_it(self):
        received = _route(_player())[5]
        self.assertEqual(received["inventory"][BLOCK], 1)
        for held in (False, True):
            player = copy.deepcopy(received)
            player.update(crafting_level=1, crafting_exp=0.0)
            if held:
                player["inventory"]["Chisel"] = 1
            with patch("ankiscape.logic_pure.quest.enakhra.tool_on_belt", return_value=not held):
                chiseled = _act(player, "chisel_base")
            self.assertEqual(chiseled["inventory"][BLOCK], 0)
            self.assertEqual(chiseled["inventory"][BASE], 1)
            self.assertEqual(chiseled["inventory"].get("Chisel", 0), int(held))
        with patch("ankiscape.logic_pure.quest.enakhra.tool_on_belt", return_value=False):
            self.assert_refused(received, "chisel_base")
            player = _act(_player(inventory={"Sandstone (10kg)": 1}), "offer_help")
            self.assert_refused(player, "split_10kg", 6977)
            self.assertFalse(_progress(received)[1])
        chiseled = _act(received, "chisel_base")
        self.assert_refused(chiseled, "chisel_base")
        self.assert_refused(chiseled, "place_base")
        talked = _act(chiseled, "talk_after_base")
        self.assert_refused(talked, "talk_after_base")
        placed = _act(talked, "place_base")
        self.assertEqual(placed["inventory"][BASE], 0)
        for action in ("chisel_base", "talk_after_base", "place_base"):
            self.assert_refused(placed, action)

    def test_premature_wrong_stage_and_duplicate_actions_refuse(self):
        player = _player()
        for action in ("deliver_sandstone", "receive_32kg", "chisel_base", "talk_after_base", "place_base", "split_10kg"):
            self.assert_refused(player, action, 6977)
        player = _act(player, "offer_help")
        self.assert_refused(player, "offer_help")
        self.assert_refused(player, "chisel_base")
        self.assert_refused(player, "receive_32kg", 6977)
        self.assert_refused(player, "talk_after_base")
        for progress, started, completed in ((0, False, False), (2, True, False), (7, True, True)):
            other = _player(progress, started=started)
            other["quests"][QUEST_ID]["completed"] = completed
            self.assert_refused(other, "offer_help")
        self.assert_refused(player, None)
        self.assert_refused(player, [])

    def test_contradictory_proofs_mass_and_output_custody_are_atomic(self):
        cases = []
        for mass in (-1, 33, True, 2.5, "32", None):
            player = _player()
            player[MASS_KEY] = mass
            cases.append(player)
        for proof in ("deliver_sandstone", "receive_32kg", "chisel_base", "talk_after_base", "place_base", "split_2kg"):
            player = _player()
            player["quest_action_proofs"] = [PROOFS[proof]]
            cases.append(player)
        for name in (BLOCK, BASE):
            player = _player(inventory={name: 1})
            cases.append(player)
        for player in cases:
            self.assert_refused(player, "offer_help", notice=INCONSISTENT)
        received = _route(_player())[5]
        for name in (BLOCK, BASE, "Chisel", "Sandstone (1kg)"):
            for count in (True, -1, 1.5, "1", None):
                malformed = copy.deepcopy(received)
                malformed["inventory"][name] = count
                self.assert_refused(malformed, "chisel_base", notice=INCONSISTENT)
        for name, count in ((BLOCK, 2), (BASE, 1)):
            malformed = copy.deepcopy(received)
            malformed["inventory"][name] = count
            self.assert_refused(malformed, "chisel_base", notice=INCONSISTENT)
        received["inventory"][BLOCK] = 0
        self.assert_refused(received, "chisel_base")
        missing_base = _route(_player())[6]
        missing_base["inventory"][BASE] = 0
        self.assert_refused(missing_base, "talk_after_base")

    def test_unrelated_blockers_cannot_be_bypassed_by_service_or_inventory(self):
        player = _player(inventory={BLOCK: 1, BASE: 1})
        self.assertFalse(_progress(player)[1])
        player = _player()
        for blocker in ({"kind": "missing_item"}, {"kind": "required_action", "action_id": "Other deed"}):
            self.assertFalse(quest_service_review_ready_pure(player, QUEST_ID, (blocker,)))
            same, result = apply_quest_service_review_pure(player, QUEST_ID, (blocker,))
            self.assertIs(same, player)
            self.assertEqual(result, "unchanged")
        self.assertIsNone(enakhra_opening_phase_pure(_player(2)))
        self.assertEqual(enakhra_opening_blockers_pure(player, "rune_mysteries"), ())
        self.assertEqual(quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA)[0]["action_id"], PROOFS["place_base"])

    def test_every_proof_chain_dependency_is_required_at_positive_mass(self):
        received = _route(_player())[5]
        chiseled = _act(received, "chisel_base")
        talked = _act(chiseled, "talk_after_base")
        for player, action in ((received, "chisel_base"), (chiseled, "talk_after_base"), (talked, "place_base")):
            for proof in player["quest_action_proofs"]:
                broken = copy.deepcopy(player)
                broken["quest_action_proofs"].remove(proof)
                self.assert_refused(broken, action)
        partial = _act(_act(_player(), "offer_help"), "deliver_sandstone", 6977)
        partial["quest_action_proofs"].append(PROOFS["receive_32kg"])
        self.assert_refused(partial, "deliver_sandstone", 6977, INCONSISTENT)

    def test_malformed_supply_and_split_outputs_refuse_without_copy_or_recording(self):
        player = _act(_player(inventory={"Sandstone (10kg)": 1}), "offer_help")
        for name in (*[name for name, _ in SANDSTONE.values()], BLOCK, BASE, "Chisel"):
            for value in (True, -1, 1.5, "1", None):
                broken = copy.deepcopy(player)
                broken["inventory"][name] = value
                with patch("ankiscape.logic_pure.quest.enakhra._copy_player_data_with_nested") as copier:
                    self.assert_refused(broken, "split_10kg", 6977, INCONSISTENT)
                    self.assert_refused(broken, "deliver_sandstone", 6977, INCONSISTENT)
                copier.assert_not_called()
        for inventory in (None, [], "Sandstone (10kg)"):
            broken = copy.deepcopy(player)
            broken["inventory"] = inventory
            self.assert_refused(broken, "deliver_sandstone", 6977, INCONSISTENT)
