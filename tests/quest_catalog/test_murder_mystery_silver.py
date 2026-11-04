"""Six independent performed searches, historical identities and durable custody."""

import copy
import hashlib
import json
import struct
import unittest
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, QUEST_DATA
from ankiscape.data.quest.murder_mystery import INVESTIGATION_JOURNAL, CONFIGURATION_PROVENANCE
from ankiscape.data.quest.murder_mystery_silver import (
    SILVER_SEARCHES, MURDER_MYSTERY_SILVER_ITEMS, murder_mystery_silver_equipment_data_as_dict,
)
from ankiscape.data.quest_item_acquisition_data import quest_item_acquisition_extra_items_as_dict
from ankiscape.logic_pure.logic_pure_equipment import equip_item_pure, unequip_item_pure
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, can_attempt_quest_review_pure, start_quest_pure,
    _apply_quest_xp_rewards, quest_eligibility_reasons_pure,
)
from ankiscape.logic_pure.quest import murder_mystery as silver
from ankiscape.logic_pure.quest.completion_rewards import _quest_xp_reward_row_pure
from tests.quest_catalog.test_murder_mystery_opening import (
    QUEST_ID, ACTION, POT, DAGGER, player, journal, reload_player,
)

ROOT = Path(__file__).resolve().parents[2]
GRANT = 'ankiscape.logic_pure.quest.murder_mystery._grant_opening_item_pure'
EXPECTED = (
    ('Anna', 2656, 'Silver necklace', 1796, 1797, 1816, 5144754),
    ('Bob', 2657, 'Silver cup', 1798, 1799, 1817, 5144752),
    ('Carol', 2658, 'Silver bottle', 1800, 1801, 1818, 5144751),
    ('David', 2659, 'Silver book', 1802, 1803, 1819, 6391161),
    ('Elizabeth', 2660, 'Silver needle', 1804, 1805, 1820, 5144755),
    ('Frank', 2661, 'Silver pot', 1806, 1807, 1821, 5144756),
)
ICON_DIGESTS = (
    '990d091048b9ee71a012d220ae8b60e2f9cb97fe124858a46341307908b8955e',
    '160244305f573158098f3b189328ccc2b0358c0f206ed9d6173d66c4f951e8f3',
    '6d09fa48215952ad7ed180aff30f93a81f8525998eec9a1f187a1bea45086f0b',
    '5b69de03e6f3f959986f5a6d1c1b4953bc6c737609320e53598e9f538c88c1a6',
    '0048dacb43b8c91b79f6468f7f3a162e04bac3805277b941e82f9f37f24e9cbc',
    '877eef26441efdddd6803194bb235fad5e25bbf035df89976b20b0bea07d6ad1',
)
ICON_DIMENSIONS = ((24, 27), (33, 30), (21, 31), (29, 27), (22, 31), (26, 27))
SOURCE_DIGESTS = (
    '584de5d8cac22861ae4cd101ba28e5b4e606206611d54ffe37a6907bea5d3b0a',
    'd363d2b015b9827b81c1937771f20e7baf5c42b5122a736438bbeb17bfbb2cf4',
    'a9b4a7a9490ed49def8450716d6c7f92b6f2d2b6c7de109f05cb682b4c11c4bb',
    '7b611f0c35b6c70dbee2ac5130451149a45589ba70f54e75e1ae0fc8f4104723',
    '8f4987f078658bd6dc2dcdb0fcfc2fc8463f75b094e4d8851d6f0df10631590b',
    '689fb6ab024aae051cf25e1124f9a04395151d0e81004b274ec737841ce1e600',
)


def family(row):
    return row['name'], row['dusted_name'], row['print_name']


def advance(data, optional=False, catalog=QUEST_DATA):
    return apply_quest_progress_pure(data, QUEST_ID, catalog, include_clue_refusal=optional)


def all_searched():
    data = player(2)
    data['quest_action_proofs'] = [row['proof_id'] for row in SILVER_SEARCHES]
    data['inventory'].update({row['name']: 1 for row in SILVER_SEARCHES})
    return data


class TestMurderMysterySilverSources(unittest.TestCase):
    def test_exact_table_registry_and_period_flags(self):
        self.assertEqual(len(SILVER_SEARCHES), 6)
        for row, expected in zip(SILVER_SEARCHES, EXPECTED):
            owner, barrel, name, clean, dusted, print_id, pin = expected
            with self.subTest(owner=owner):
                self.assertEqual(tuple(row[k] for k in ('owner', 'barrel_id', 'name', 'clean_id', 'dusted_id', 'print_id')),
                                 (owner, barrel, name, clean, dusted, print_id))
                self.assertEqual(row['dusted_name'], name + ' (dusted)')
                self.assertEqual(row['print_name'], owner + "'s print")
                self.assertEqual(row['proof_id'], f'murder_mystery.search_{owner.lower()}_barrel')
                self._assert_registry(row, pin)
        self.assertEqual(len({1806, 1931, 1812}), 3)
        self.assertEqual(CONFIGURATION_PROVENANCE['ids']['Empty pot'], 1931)
        self.assertNotEqual(next(i for i in ITEM_DEFINITIONS if i.storage_key == 'Empty pot').source_item_id, 1806)
        self.assertEqual(next(i for i in ITEM_DEFINITIONS if i.storage_key == POT).source_item_id, 1812)

    def _assert_registry(self, row, pin):
        registered = [item for item in ITEM_DEFINITIONS if item.storage_key == row['name']]
        self.assertEqual(len(registered), 1)
        item = registered[0]
        self.assertEqual(item.source_item_id, row['clean_id'])
        self.assertNotIn(item.source_item_id, (row['dusted_id'], row['print_id']))
        self.assertFalse(item.stackable)
        self.assertFalse(item.tradeable)
        meta = MURDER_MYSTERY_SILVER_ITEMS[row['name']]
        self.assertEqual(meta['category'], 'equipment' if row['owner'] == 'Anna' else 'material')
        self.assertIn(f'oldid={pin}', meta['source'])
        self.assertEqual([meta[k] for k in ('members', 'quest', 'store', 'value')], ['Yes', 'Yes', 'No', 1])
        self.assertEqual(meta['equipable'], 'Yes' if row['owner'] == 'Anna' else 'No')
        self.assertEqual((meta['high'], meta['low']), (0, 0) if row['owner'] == 'Anna' else ('No', 'No'))
        self.assertEqual(meta.get('weight'), {'Anna': 1, 'Elizabeth': 0}.get(row['owner']))
        extras = quest_item_acquisition_extra_items_as_dict()
        extras[row['name']]['item_id'] = -1
        self.assertEqual(MURDER_MYSTERY_SILVER_ITEMS[row['name']]['item_id'], row['clean_id'])
        keys = {i.storage_key for i in ITEM_DEFINITIONS}
        self.assertFalse(set(family(row)[1:]) & keys)

    def test_historical_source_records_and_icon_bytes(self):
        packet = json.loads((ROOT / 'data/quest/murder_mystery_silver.sources.json').read_text())
        self.assertEqual(packet['evidence_packet'], '2220-murder-mystery-six-silver-object-pickups')
        records = {r['key']: r for r in packet['source-register.json']}
        for index, expected in enumerate(EXPECTED):
            record = records[f'S{index + 1}']
            self.assertEqual(record['revision'], expected[-1])
            self.assertEqual(record['sha256'], SOURCE_DIGESTS[index])
            self.assertTrue(record['extracts'])
            self.assertTrue(record['path'].startswith('sources/'))
        self.assertEqual(records['A1']['revision'], 'Wayback20121018060902')
        self.assertEqual(records['A2']['revision'], 'Wayback20121103153756')
        self.assertEqual(records['D1']['revision'], 'bdea22f7f98391da022256269db4fac4f095247b')
        self.assertEqual(packet['mapping_recovery_revision'], 'ef60e6e839010c18e3a52a1b9c7d7930eac24d15')
        icons = json.loads((ROOT / 'data/quest/assets/murder_mystery_silver.provenance.json').read_text())
        self.assertEqual(len(icons), 6)
        for index, row in enumerate(icons):
            self._assert_icon(row, index)

    def _assert_icon(self, row, index):
        path = ROOT / row['saved_path']
        payload = path.read_bytes()
        self.assertEqual(payload[:8], b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>II', payload[16:24]), ICON_DIMENSIONS[index])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), ICON_DIGESTS[index])
        self.assertEqual(row['sha256'], ICON_DIGESTS[index])
        self.assertEqual(hashlib.sha1(payload).hexdigest(), row['sha1'])
        self.assertEqual(len(payload), row['bytes'])
        self.assertLess(datetime.fromisoformat(row['upload_utc']), datetime.fromisoformat('2012-11-20T00:00:00Z'))
        self.assertEqual(row['licence'], 'not stated in imageinfo extmetadata')
        self.assertTrue(row['url'].startswith('https://runescape.wiki/images/'))
        self.assertTrue(row['metadata_path'].startswith('sources/file-'))
        item = next(i for i in ITEM_DEFINITIONS if i.storage_key == row['item_name'])
        self.assertEqual(Path(item.asset_path), path)

    def test_necklace_ordinary_equipment_has_no_copy_or_bonus(self):
        spec = EQUIPMENT_DATA['Silver necklace']
        self.assertEqual((spec.slot, spec.source_item_id, spec.combat_skill, spec.required_level), ('neck', 1796, None, 1))
        self.assertEqual((spec.two_handed, spec.equipment_type, spec.attack_speed, spec.skill_requirements, spec.weapon_type),
                         (False, 'neck', 0, (), -1))
        self.assertEqual(set(asdict(spec.bonuses).values()), {0})
        self.assertEqual(murder_mystery_silver_equipment_data_as_dict()['Silver necklace'], spec)
        item = next(i for i in ITEM_DEFINITIONS if i.storage_key == 'Silver necklace')
        self.assertEqual(item.equipment_slot, 'neck')
        inventory, equipment, ok = equip_item_pure('Silver necklace', {'Silver necklace': 1}, {}, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual((inventory, equipment), ({'Silver necklace': 0}, {'neck': 'Silver necklace'}))
        inventory, equipment, ok = unequip_item_pure('neck', inventory, equipment)
        self.assertEqual((inventory, equipment, ok), ({'Silver necklace': 1}, {}, True))


class TestMurderMysterySilverTransactions(unittest.TestCase):
    def assert_search(self, data, row, grant=True):
        before = copy.deepcopy(data)
        expected = copy.deepcopy(data)
        if grant:
            expected['inventory'][row['name']] = expected['inventory'].get(row['name'], 0) + 1
        expected['quest_action_proofs'] = sorted(set(expected['quest_action_proofs']) | {row['proof_id']})
        result, ok, reason = silver.search_murder_mystery_barrel_pure(data, row['barrel_id'])
        self.assertEqual((ok, reason), (True, ''))
        self.assertEqual(result, expected)
        self.assertEqual(data, before)
        if 'nested' in result:
            result['nested']['list'].append(99)
        self.assertEqual(data, before)
        return result

    def test_every_direct_barrel_requires_only_active_quest(self):
        for row in SILVER_SEARCHES:
            for stage in (0, 1, 2, 3, 4):
                with self.subTest(owner=row['owner'], stage=stage):
                    data = player(stage)
                    data['nested'] = {'list': [{'untouched': True}]}
                    data['graves'] = [{'inventory': {row['name']: 4}}]
                    data['dropped_items'] = {row['dusted_name']: 3}
                    data['inventory'][SILVER_SEARCHES[(stage + 1) % 6]['name']] = 7
                    # Other suspects' custody never suppresses the selected row.
                    data['inventory'].pop(row['name'], None)
                    self.assert_search(data, row)

    def test_ordinary_reviews_are_six_separate_deltas_and_never_advance(self):
        for optional in (False, True):
            data = player(0)
            data, ok, done = advance(data)
            self.assertEqual((ok, done), (True, False))
            self.assertEqual((data['inventory'][POT], data['inventory'][DAGGER]), (1, 1))
            for row in SILVER_SEARCHES:
                before = copy.deepcopy(data)
                self.assertTrue(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
                self.assertEqual(silver.next_murder_mystery_silver_search_pure(data), row)
                result = advance(data, optional)
                self.assertEqual(result[1:], (True, False, '') if optional else (True, False))
                data = result[0]
                expected = copy.deepcopy(before)
                expected['inventory'][row['name']] = 1
                expected['quest_action_proofs'] = sorted(before['quest_action_proofs'] + [row['proof_id']])
                self.assertEqual(data, expected)
            self.assertIsNone(silver.next_murder_mystery_silver_search_pure(data))
            self.assertFalse(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
            self.assertEqual(advance(data, optional)[1:], (False, False, '') if optional else (False, False))
            self.assertEqual(data['quests'][QUEST_ID], dict(started=True, progress=2, completed=False))
            self.assertEqual(set(data['quest_action_proofs']), {ACTION} | {r['proof_id'] for r in SILVER_SEARCHES})

    def test_every_family_preserves_clean_dusted_print_and_equipped_custody(self):
        for row in SILVER_SEARCHES:
            for name in family(row):
                with self.subTest(owner=row['owner'], held=name):
                    data = player(2)
                    data['inventory'][name] = 4
                    result = self.assert_search(data, row, False)
                    self.assert_refused(result, row['barrel_id'], silver.NO_SEARCH)
                    data = player(2)
                    data['equipment']['neck'] = name
                    result = self.assert_search(data, row, False)
                    self.assert_refused(result, row['barrel_id'], silver.NO_SEARCH)

    def test_active_legacy_final_stage_searches_then_refuses_without_completing(self):
        data = player(QUEST_DATA[QUEST_ID]['stages'])
        for row in SILVER_SEARCHES:
            before = copy.deepcopy(data)
            self.assertTrue(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
            data, ok, completed = advance(data)
            expected = copy.deepcopy(before)
            expected['inventory'][row['name']] = 1
            expected['quest_action_proofs'] = sorted(before['quest_action_proofs'] + [row['proof_id']])
            self.assertEqual((ok, completed), (True, False))
            self.assertEqual(data, expected)
        self.assertFalse(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
        self.assertEqual(advance(data), (data, False, False))
        self.assertEqual(data['quests'][QUEST_ID], dict(started=True, progress=5, completed=False))

    def test_zero_absent_carried_overlay_and_other_stores(self):
        for row in SILVER_SEARCHES:
            data = player(2)
            data['inventory'].update({name: 0 for name in family(row)})
            data['carried_inventory'] = {name: 28 for name in family(row)}
            data['graves'] = {row['name']: 2}
            data['dropped_items'] = {row['name']: 3}
            self.assert_search(data, row)
            data['inventory'][row['name']] = 5
            self.assert_search(data, row, False)

    def test_all_families_recover_on_separate_review_after_total_loss(self):
        data = all_searched()
        for row in SILVER_SEARCHES:
            before_proofs = list(data['quest_action_proofs'])
            data['inventory'].pop(row['name'])
            self.assertEqual(silver.next_murder_mystery_silver_search_pure(data), row)
            result = advance(data)
            self.assertEqual(result[1:], (True, False))
            expected = copy.deepcopy(data)
            expected['inventory'][row['name']] = 1
            self.assertEqual(result[0], expected)
            self.assertEqual(result[0]['quest_action_proofs'], before_proofs)
            data = result[0]
            self.assertFalse(advance(data)[1])

    def assert_refused(self, data, barrel_id, reason):
        before = copy.deepcopy(data)
        result, ok, actual = silver.search_murder_mystery_barrel_pure(data, barrel_id)
        self.assertIs(result, data)
        self.assertEqual((ok, actual), (False, reason))
        self.assertEqual(data, before)

    def test_unknown_boolean_or_noninteger_targets_and_inactive_states(self):
        for barrel_id in (True, False, 2655, 2662, '2656', 2656.0, None):
            self.assert_refused(player(2), barrel_id, silver.INVALID_BARREL)
        for row in SILVER_SEARCHES:
            inactive = player(2)
            inactive['quests'][QUEST_ID]['started'] = False
            self.assert_refused(inactive, row['barrel_id'], silver.INACTIVE)
            self.assert_refused(player(5, True), row['barrel_id'], silver.COMPLETED)

    def test_invalid_counts_and_containers_refuse_without_fallback(self):
        for row in SILVER_SEARCHES:
            for name in family(row):
                for count in (-1, True, '1', 1.5, None):
                    data = player(2)
                    data['inventory'][name] = count
                    self.assert_refused(data, row['barrel_id'], silver.INVALID_CUSTODY)
        for key in ('inventory', 'equipment'):
            for value in (None, [], 'invalid', 2):
                data = player(2)
                data[key] = value
                self.assert_refused(data, 2656, silver.INVALID_CUSTODY)
                self.assertEqual(advance(data), (data, False, False))
        data = all_searched()
        data['inventory']['Silver necklace'] = -1
        data['inventory'].pop('Silver cup')
        self.assertEqual(silver.next_murder_mystery_silver_search_pure(data), SILVER_SEARCHES[0])
        self.assertEqual(advance(data), (data, False, False))

    def test_rechecked_eligibility_and_failed_grant_are_atomic(self):
        isolated = copy.deepcopy(QUEST_DATA)
        isolated[QUEST_ID]['required_quest_points'] = 999
        data = player(2)
        before = copy.deepcopy(data)
        self.assertFalse(can_attempt_quest_review_pure(data, QUEST_ID, isolated))
        self.assertEqual(advance(data, catalog=isolated), (data, False, False))
        self.assertEqual(silver.murder_mystery_silver_refusal_reason_pure(
            data, QUEST_ID, isolated, quest_eligibility_reasons_pure,
        ), '999 quest points')
        with patch(GRANT, return_value=False):
            self.assert_refused(data, 2656, silver.INVALID_CUSTODY)
            self.assertEqual(advance(data), (data, False, False))
        self.assertEqual(data, before)
        readiness = silver.murder_mystery_silver_review_ready_pure(
            data, QUEST_ID, QUEST_DATA, quest_eligibility_reasons_pure,
        )
        self.assertTrue(readiness)
        with patch('ankiscape.logic_pure.logic_pure_quest.quest_eligibility_reasons_pure', return_value=('new requirement',)):
            self.assertEqual(advance(data), (data, False, False))

    def test_review_adapters_recheck_the_supplied_eligibility_owner(self):
        data = player(2)
        before = copy.deepcopy(data)
        eligibility = Mock(return_value=('new requirement',))
        with patch(GRANT) as grant:
            self.assertFalse(silver.murder_mystery_silver_review_ready_pure(
                data, QUEST_ID, QUEST_DATA, eligibility,
            ))
            eligibility.assert_called_once_with(data, QUEST_ID, QUEST_DATA)
            eligibility.reset_mock()
            self.assertEqual(silver.apply_murder_mystery_silver_review_pure(
                data, QUEST_ID, QUEST_DATA, eligibility,
            ), (data, False))
            eligibility.assert_called_once_with(data, QUEST_ID, QUEST_DATA)
            eligibility.reset_mock()
            self.assertEqual(silver.murder_mystery_silver_refusal_reason_pure(
                data, QUEST_ID, QUEST_DATA, eligibility,
            ), 'new requirement')
            eligibility.assert_called_once_with(data, QUEST_ID, QUEST_DATA)
            grant.assert_not_called()
        self.assertEqual(data, before)


class TestMurderMysterySilverPersistence(unittest.TestCase):
    def test_start_inspection_journal_and_migration_never_fabricate_proofs(self):
        for stage, completed in ((2, False), (3, False), (4, False), (5, True)):
            data = reload_player(player(stage, completed))
            data['inventory'].update({row['name']: 4 for row in SILVER_SEARCHES})
            data['quest_action_proofs'] = ['Complete Murder Mystery stage 2 objective']
            before = copy.deepcopy(data)
            for _ in range(3):
                journal(data)
                can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA)
                silver.next_murder_mystery_silver_search_pure(data)
                started, _ = start_quest_pure(data, QUEST_ID, QUEST_DATA)
                self.assertEqual(started, data)
                migrated = reload_player(data)
                self.assertEqual(migrated['quests'][QUEST_ID], before['quests'][QUEST_ID])
                self.assertEqual(migrated['quest_action_proofs'], before['quest_action_proofs'])
                self.assertEqual(migrated['inventory'], before['inventory'])
            self.assertEqual(data, before)
            if completed:
                self.assertEqual(advance(data), (data, False, False))
            else:
                earned, ok, _ = advance(data)
                self.assertTrue(ok)
                self.assertEqual(earned['quests'][QUEST_ID]['progress'], stage)

    def test_journal_projects_each_deed_without_window_gate_completion(self):
        data = player(2)
        base = INVESTIGATION_JOURNAL
        self.assertEqual(journal(data)[1]['lines'], base[:2] + tuple(line + ' (Pending)' for line in base[2:]))
        for row in SILVER_SEARCHES:
            data, _, _ = silver.search_murder_mystery_barrel_pure(data, row['barrel_id'])
        projected = journal(data)[1]
        self.assertEqual(projected['lines'], base[:2] + tuple(f'<s>{line}</s> (Searched)' for line in base[2:]))
        self.assertFalse(projected['completed'])
        data['inventory'].pop('Silver necklace')
        self.assertEqual(journal(data)[1]['lines'][2], f'<s>{base[2]}</s> (Searched) Replacement pending: search the barrel again.')
        legacy = player(5, True)
        self.assertEqual(journal(legacy)[1]['lines'], base[:2] + tuple(line + ' (No recorded search)' for line in base[2:]))
        legacy['quest_action_proofs'] = [SILVER_SEARCHES[0]['proof_id']]
        self.assertEqual(journal(legacy)[1]['lines'][2], f'<s>{base[2]}</s> (Searched)')
        self.assertFalse(journal(legacy)[1]['completed'])

    def test_each_initial_and_replacement_reload_keeps_target_and_advanced_copies(self):
        data = reload_player(player(2))
        data['inventory'].update({'Silver cup (dusted)': 3, "Carol's print": 2, 'Silver book': 5})
        for row in SILVER_SEARCHES:
            data, ok, _ = advance(data)
            self.assertTrue(ok)
            data = self.assert_reload(data)
        self.assertEqual(data['inventory']['Silver cup (dusted)'], 3)
        self.assertEqual(data['inventory']["Carol's print"], 2)
        self.assertEqual(data['inventory']['Silver book'], 5)
        for row in SILVER_SEARCHES:
            for name in family(row):
                data['inventory'].pop(name, None)
            self.assertEqual(silver.next_murder_mystery_silver_search_pure(data), row)
            data, ok, _ = advance(data)
            self.assertTrue(ok)
            self.assertEqual(data['inventory'][row['name']], 1)
            data = self.assert_reload(data)

    def assert_reload(self, data):
        before = copy.deepcopy(data)
        target = silver.next_murder_mystery_silver_search_pure(data)
        reloaded = reload_player(data)
        for key in ('inventory', 'equipment', 'quests', 'quest_action_proofs', 'quest_points', 'pending_skill_exp_rewards'):
            self.assertEqual(reloaded[key], before[key])
        self.assertEqual(reload_player(reloaded), reloaded)
        self.assertEqual(silver.next_murder_mystery_silver_search_pure(reloaded), target)
        self.assertEqual(journal(reloaded), journal(before))
        self.assertEqual(data, before)
        return reloaded

    def test_xp_extraction_preserves_implemented_pending_and_invalid_rewards(self):
        data = {'crafting_exp': 12, 'pending_skill_exp_rewards': {'future_exp': 7}}
        _apply_quest_xp_rewards(data, {'xp_rewards': (
            {'skill_id': 'crafting', 'amount': '20.5'},
            {'skill_id': 'future', 'amount': 3},
            None, 'bad', {'skill_id': None, 'amount': 5},
            {'skill_id': 'crafting', 'amount': 0},
            {'skill_id': 'crafting', 'amount': -2},
            {'skill_id': 'crafting', 'amount': 'bad'},
            {'skill_id': 'crafting', 'amount': None},
        )})
        self.assertEqual(data, {'crafting_exp': 32.5, 'pending_skill_exp_rewards': {'future_exp': 10.0}})
        for reward in (None, {}, {'skill_id': 5}, {'skill_id': 'crafting', 'amount': 0}):
            self.assertIsNone(_quest_xp_reward_row_pure(reward))
        data = {'pending_skill_exp_rewards': []}
        _apply_quest_xp_rewards(data, {})
        self.assertEqual(data, {'pending_skill_exp_rewards': {}})
