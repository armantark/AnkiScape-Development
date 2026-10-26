"""Ordered deeds, atomic custody and retained source/item bindings."""

import copy
import hashlib
import json
from pathlib import Path
import struct
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA, QUEST_ITEM_IMAGES
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest.one_small_favour import (
    QUEST_ID, BLUNT_HATCHET, OPENING_DEEDS, OPENING_PROOFS, OPENING_SOURCE,
    REPLACEMENT_EVENT_ID, BLUNT_HATCHET_ITEMS, BLUNT_HATCHET_ICON, PERIOD_SOURCES,
)
from ankiscape.data.quest_action_proof_data import QUEST_ACTION_PROOF_RULES
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic.inventory_pure import discard_inventory_quantity_pure
from ankiscape.logic.summoning_logic import (
    familiar_storage_transfer_pure, dismiss_familiar_pure, reclaim_familiar_cargo_pure,
)
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, quest_current_stage_blockers_pure, can_attempt_quest_review_pure,
)
from ankiscape.logic_pure.quest.one_small_favour import (
    apply_opening_review_pure, opening_phase_pure, opening_blockers_pure,
    opening_review_ready_pure, opening_hatchet_custody_pure,
    ORDER_REASON, FORESTER_REASON, EXCESS_REASON, RECOVER_REASON, BRIAN_REASON,
)


def player(prefix=0, *, started=True):
    """Declared setup for refusal/transaction fixtures; earned route lives separately."""
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    quest = QUEST_DATA[QUEST_ID]
    for requirement in quest['required_skills']:
        data[requirement['skill_id'] + '_level'] = requirement['level']
    for requirement in quest['required_quests']:
        data['quests'][requirement['quest_id']] = dict(started=True, completed=True, progress=99)
    data['quests'][QUEST_ID] = dict(started=started, completed=False, progress=1 if prefix else 0)
    data['current_quest'] = QUEST_ID
    data['quest_action_proofs'] = sorted(OPENING_PROOFS[:prefix])
    data['inventory'] = {'Coins': 100, BLUNT_HATCHET: int(prefix in (2, 3))}
    return data


def progress(data, **kwargs):
    return apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA, **kwargs)


def blockers(data):
    return quest_current_stage_blockers_pure(data, QUEST_ID, QUEST_DATA)


class OpeningTransactionTest(unittest.TestCase):
    def assert_refused(self, data, event_id=None, reason=None):
        before = copy.deepcopy(data)
        after, result = apply_opening_review_pure(data, event_id=event_id)
        self.assertIs(after, data)
        self.assertEqual(result, 'unchanged')
        self.assertEqual(data, before)
        self.assertFalse(opening_review_ready_pure(data, event_id=event_id))
        if reason:
            row, = opening_blockers_pure(data, event_id=event_id)
            self.assertEqual(row['reason'], reason)
            self.assertEqual((row['stage'], row['kind'], row['source']), (1, 'required_action', OPENING_SOURCE))

    def test_every_prefix_emits_only_its_deed_and_exact_hatchet_sequence(self):
        data = player(started=False)
        before_rewards = {key: value for key, value in data.items() if key.endswith('_exp') or key in ('quest_points', 'claims')}
        for index, deed in enumerate(OPENING_DEEDS):
            before = copy.deepcopy(data)
            after, ok, completed = progress(data)
            self.assertTrue(ok)
            self.assertFalse(completed)
            self.assertEqual(data, before)
            self.assertIsNot(after, data)
            self.assertEqual(set(after['quest_action_proofs']) - set(data['quest_action_proofs']), {deed['proof']})
            self.assertEqual(after['quests'][QUEST_ID]['progress'], 2 if index == 6 else 1)
            self.assertEqual(after['inventory'][BLUNT_HATCHET], int(index in (1, 2)))
            self.assertEqual(after['inventory']['Coins'], 100)
            self.assertEqual({k: after[k] for k in before_rewards}, before_rewards)
            self.assertFalse(any('chicken' in name.lower() and count for name, count in after['inventory'].items()))
            data = after
        self.assertNotIn('Complete One Small Favour stage 2 objective', data['quest_action_proofs'])

    def test_all_skipped_repeated_stale_and_future_events_refuse(self):
        for prefix in range(7):
            data = player(prefix)
            for index, deed in enumerate(OPENING_DEEDS):
                if prefix != index:
                    with self.subTest(prefix=prefix, event=index):
                        self.assert_refused(data, deed['event_id'], ORDER_REASON)
            self.assert_refused(data, 'unknown', ORDER_REASON)
            self.assertTrue(opening_review_ready_pure(data, blockers=blockers(data)))

    def test_unstarted_other_quest_later_and_completed_states_are_unhandled(self):
        cases = ((False, 0, False, QUEST_ID), (True, 2, False, QUEST_ID),
                 (True, 8, True, QUEST_ID), (True, 1, False, 'rune_mysteries'))
        for started, stage, completed, quest_id in cases:
            data = player()
            data['quests'][QUEST_ID].update(started=started, progress=stage, completed=completed)
            before = copy.deepcopy(data)
            after, status = apply_opening_review_pure(data, quest_id)
            self.assertIs(after, data)
            self.assertEqual(status, 'unchanged')
            self.assertEqual(data, before)

    def test_unlimited_bank_does_not_add_a_carried_capacity_gate(self):
        data = player(1)
        data['inventory'].update({f'Owned material {index}': 1 for index in range(50)})
        data['carried_inventory'] = {'mining': dict(data['inventory'])}
        after, result = apply_opening_review_pure(data)
        self.assertEqual(result, 'partial')
        self.assertEqual(after['inventory'][BLUNT_HATCHET], 1)
        self.assertEqual(after['carried_inventory'], data['carried_inventory'])

    def test_noncontiguous_proofs_refuse_without_repair(self):
        for missing in range(6):
            for future in range(missing + 1, 7):
                data = player(missing)
                data['quest_action_proofs'].append(OPENING_PROOFS[future])
                self.assert_refused(data, reason=ORDER_REASON)
                self.assertEqual(opening_blockers_pure(data)[0]['action_id'], OPENING_PROOFS[missing])
                self.assertFalse(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
                after, ok, _ = progress(data)
                self.assertFalse(ok)
                self.assertIs(after, data)

    def test_seeded_input_excess_and_missing_input_are_not_deeds(self):
        seeded = player(1)
        seeded['inventory'][BLUNT_HATCHET] = 1
        self.assert_refused(seeded, reason=FORESTER_REASON)
        excess = player(3)
        excess['inventory'][BLUNT_HATCHET] = 2
        self.assert_refused(excess, reason=EXCESS_REASON)
        absent = player(3)
        absent['inventory'][BLUNT_HATCHET] = 0
        self.assert_refused(absent, OPENING_DEEDS[3]['event_id'], BRIAN_REASON)
        # A custom blocker using the same action id cannot bypass custody checks.
        self.assertFalse(opening_review_ready_pure(excess, blockers=blockers(excess)))

    def test_recorder_failure_discards_inventory_and_progress_transaction(self):
        for prefix in range(7):
            data = player(prefix)
            before = copy.deepcopy(data)
            with patch('ankiscape.logic_pure.quest.one_small_favour.record_runtime_quest_action_proofs_pure', return_value=False):
                after, status = apply_opening_review_pure(data)
                self.assertIs(after, data)
                self.assertEqual(status, 'unchanged')
                for shape in (False, True):
                    result = progress(data, include_clue_refusal=shape)
                    self.assertEqual(len(result), 4 if shape else 3)
                    self.assertIs(result[0], data)
                    self.assertEqual(result[1:3], (False, False))
            self.assertEqual(data, before)

    def test_success_preserves_both_progress_return_shapes(self):
        for shape in (False, True):
            for prefix in range(7):
                result = progress(player(prefix), include_clue_refusal=shape)
                self.assertEqual(len(result), 4 if shape else 3)
                self.assertEqual(result[1:3], (True, False))

    def test_loss_before_shanks_then_repeated_real_loss_costs_extra_reviews(self):
        data = player(2)
        data['inventory'], ok = discard_inventory_quantity_pure(data['inventory'], BLUNT_HATCHET, 1)
        self.assertTrue(ok)
        self.assert_refused(data, REPLACEMENT_EVENT_ID, ORDER_REASON)
        data, result = apply_opening_review_pure(data)
        self.assertEqual(result, 'partial')
        self.assertIn(OPENING_PROOFS[2], data['quest_action_proofs'])
        for _ in range(2):
            before = copy.deepcopy(data)
            self.assertEqual(opening_phase_pure(data), REPLACEMENT_EVENT_ID)
            data, result = apply_opening_review_pure(data)
            self.assertEqual(result, 'partial')
            self.assertEqual(data['quest_action_proofs'], before['quest_action_proofs'])
            self.assertEqual(data['quests'], before['quests'])
            self.assertEqual(data['inventory'][BLUNT_HATCHET], 1)
            self.assert_refused(data, REPLACEMENT_EVENT_ID, ORDER_REASON)
            data['inventory'], ok = discard_inventory_quantity_pure(data['inventory'], BLUNT_HATCHET, 1)
            self.assertTrue(ok)
        data, _ = apply_opening_review_pure(data)
        data, _ = apply_opening_review_pure(data)
        self.assertEqual(data['inventory'][BLUNT_HATCHET], 0)
        self.assertIn(OPENING_PROOFS[3], data['quest_action_proofs'])
        self.assert_refused(data, REPLACEMENT_EVENT_ID, ORDER_REASON)

    def test_loss_after_shanks_is_replaced_without_proof_credit(self):
        data = player(3)
        data['inventory'], _ = discard_inventory_quantity_pure(data['inventory'], BLUNT_HATCHET, 1)
        recovered, ok, completed = progress(data)
        self.assertEqual((ok, completed), (True, False))
        self.assertEqual(recovered['quest_action_proofs'], data['quest_action_proofs'])
        handed, ok, _ = progress(recovered)
        self.assertTrue(ok)
        self.assertEqual(handed['inventory'][BLUNT_HATCHET], 0)

    def test_recoverable_custody_blocks_grants_and_handoff_without_mutating_stores(self):
        stores = (
            {'equipment': {'weapon': BLUNT_HATCHET}},
            {'combat_grave': {'items': [BLUNT_HATCHET], 'loadout': {'weapon': BLUNT_HATCHET}}},
            {'death_office': {'items': [BLUNT_HATCHET], 'loadout': {'weapon': BLUNT_HATCHET}}},
            {'summoning_state': {'active_follower': {'kind': 'familiar', 'entity_id': 'spiritterrorbird', 'storage': {BLUNT_HATCHET: 1}}}},
            {'summoning_state': {'cargo_events': [{'event_id': 1, 'items': {BLUNT_HATCHET: 1}, 'remaining_ticks': 10}]}},
        )
        for store in stores:
            for prefix, reason in ((1, FORESTER_REASON), (3, RECOVER_REASON)):
                data = player(prefix)
                data['inventory'][BLUNT_HATCHET] = 0
                data.update(copy.deepcopy(store))
                self.assertEqual(opening_hatchet_custody_pure(data), (0, 1))
                self.assert_refused(data, reason=reason)
            data['inventory'][BLUNT_HATCHET] = 1
            self.assert_refused(data, reason=EXCESS_REASON)

    def test_actual_familiar_transfer_dismissal_and_reclamation_own_the_hatchet(self):
        data = player(3)
        data['summoning_state']['active_follower'] = {
            'kind': 'familiar', 'entity_id': 'spiritterrorbird', 'storage': {},
            'remaining_ticks': 1000, 'max_ticks': 1000,
        }
        data, ok = familiar_storage_transfer_pure(data, BLUNT_HATCHET, 1, to_familiar=True)
        self.assertTrue(ok)
        self.assert_refused(data, reason=RECOVER_REASON)
        data, ok, _ = dismiss_familiar_pure(data)
        self.assertTrue(ok)
        self.assert_refused(data, reason=RECOVER_REASON)
        event = data['summoning_state']['cargo_events'][0]
        data, ok, items = reclaim_familiar_cargo_pure(data, event['event_id'])
        self.assertTrue(ok)
        self.assertEqual(items, {BLUNT_HATCHET: 1})
        data, result = apply_opening_review_pure(data)
        self.assertEqual(result, 'partial')
        self.assertEqual(data['inventory'][BLUNT_HATCHET], 0)

    def test_expired_cargo_and_carried_loadout_projections_do_not_duplicate_custody(self):
        data = player(3)
        data['carried_inventory'] = {'quest': {BLUNT_HATCHET: 1}}
        data['combat_loadout'] = {'weapon': BLUNT_HATCHET}
        data['summoning_state']['cargo_events'] = [{'event_id': 1, 'items': {BLUNT_HATCHET: 1}, 'remaining_ticks': 0}]
        self.assertEqual(opening_hatchet_custody_pure(data), (1, 1))
        data, result = apply_opening_review_pure(data)
        self.assertEqual(result, 'partial')
        self.assertEqual(data['inventory'][BLUNT_HATCHET], 0)

    def test_unrelated_blockers_are_preserved_and_cannot_be_bypassed(self):
        data = player()
        unrelated = {'kind': 'missing_item', 'reason': 'Unrelated gate', 'stage': 1}
        self.assertFalse(opening_review_ready_pure(data, blockers=(*blockers(data), unrelated)))
        result, status = apply_opening_review_pure(data, blockers=(unrelated,))
        self.assertIs(result, data)
        self.assertEqual(status, 'unchanged')


class OpeningBindingsTest(unittest.TestCase):
    def test_exact_rules_require_the_entire_preceding_prefix(self):
        for index, deed in enumerate(OPENING_DEEDS):
            self.assertEqual(QUEST_ACTION_PROOF_RULES[(deed['event_type'], deed['event_id'])],
                             (OPENING_PROOFS[:index], (OPENING_PROOFS[index],)))
        self.assertNotIn(('quest_service', REPLACEMENT_EVENT_ID), QUEST_ACTION_PROOF_RULES)
        self.assertNotIn(('quest', QUEST_ID), QUEST_ACTION_PROOF_RULES)

    def test_only_opening_requirements_change_and_journal_stays_unchanged(self):
        original = next(q for q in PRE_EOC_QUEST_CATALOG if q['id'] == QUEST_ID)
        quest = QUEST_DATA[QUEST_ID]
        opening = quest['stage_requirements'][0]
        self.assertEqual(opening['required_actions'], OPENING_PROOFS)
        for field in ('required_inventory', 'consumed_inventory', 'produced_inventory', 'auto_actions'):
            self.assertFalse(opening[field])
        for old, current in zip(original['stage_requirements'][1:], quest['stage_requirements'][1:]):
            self.assertEqual(dict(old)['stage'], current['stage'])
            self.assertEqual(dict(dict(old)['required_inventory']), current['required_inventory'])
            self.assertEqual(tuple(dict(old)['required_actions']), current['required_actions'])
        self.assertEqual(quest['journal_stages'][1], tuple(original['journal_stages'][0]['journal']))
        self.assertEqual(len(quest['journal_stages'][1]), 6)

    def test_item_properties_packaged_icon_provenance_and_revision_pins(self):
        item = BLUNT_HATCHET_ITEMS[BLUNT_HATCHET]
        self.assertEqual(item['source_item_id'], 4415)
        self.assertFalse(item['stackable'])
        self.assertFalse(item['tradeable'])
        self.assertNotIn('equipment_slot', item)
        self.assertIn(BLUNT_HATCHET, {item.storage_key for item in ITEM_DEFINITIONS})
        self.assertEqual(QUEST_ITEM_IMAGES[BLUNT_HATCHET], BLUNT_HATCHET_ICON)
        content = Path(BLUNT_HATCHET_ICON).read_bytes()
        self.assertEqual(hashlib.sha256(content).hexdigest(), 'f77e78293dd6f01d55c0ac968e3c8f33b67e32fadff360cda59c9d3708c3ae9a')
        self.assertEqual(hashlib.sha1(content).hexdigest(), 'eb95c613df4a9477d2fe1cf4d8b7e764b59463fe')
        self.assertEqual(struct.unpack('>II', content[16:24]), (22, 27))
        provenance = json.loads(Path(BLUNT_HATCHET_ICON).with_suffix('.provenance.json').read_text())
        self.assertEqual(provenance['byte_length'], len(content))
        self.assertEqual(provenance['upload_timestamp_utc'], '2011-11-18T05:39:54Z')
        self.assertEqual(set(PERIOD_SOURCES), {'W', 'Q', 'B', 'G', 'T', 'H', 'C', 'K', 'D', 'DH', 'DT', 'I'})
        self.assertEqual(PERIOD_SOURCES['W']['revision_or_build'], '6546338')
        self.assertEqual(PERIOD_SOURCES['Q']['revision_or_build'], '6178350')
        self.assertEqual(PERIOD_SOURCES['B']['revision_or_build'], '5806478')
        self.assertIsNone(PERIOD_SOURCES['DH']['timestamp_utc'])
        self.assertEqual(PERIOD_SOURCES['K']['date_utc'], 'not stated')
