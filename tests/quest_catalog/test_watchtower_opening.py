"""Watchtower's earned commission, search, custody and concluding explanation."""

import copy
import hashlib
import json
from pathlib import Path
import random
import struct
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA, QUEST_ITEM_IMAGES
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest import watchtower_opening as source
from ankiscape.data.quest.catalog import _catalog_stage_requirements, _apply_stage_item_name_overrides
from ankiscape.data.quest.serializers import _stage_requirement_dict
from ankiscape.data.quest_action_proof_data import QUEST_ACTION_PROOF_RULES, QUEST_ACTION_PROOF_AUDIT_SOURCES
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, can_start_quest_pure, start_quest_pure,
    quest_current_stage_blockers_pure, quest_journal_rows_pure,
)
from ankiscape.logic_pure.logic_pure_state import _copy_player_data_with_nested
from ankiscape.logic_pure.quest import watchtower as service
from ankiscape.logic_pure.quest_action_proofs import quest_action_proofs_after_event_pure

QUEST_ID = 'watchtower'
PROOFS = source.OPENING_PROOFS
GENERATED = next(q for q in PRE_EOC_QUEST_CATALOG if q['id'] == QUEST_ID)
OPTIONAL_FINDS = ('Old robe', 'Damaged dagger', 'Unusual armour', 'Tattered eye patch')


def player(phase=0, *, started=True, stage=1):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data['inventory'] = {}
    data['quest_action_proofs'] = sorted(PROOFS[:phase])
    data['quests'][QUEST_ID] = dict(started=started, completed=False, progress=stage)
    data['current_quest'] = QUEST_ID
    for skill in source.WATCHTOWER_SKILLS:
        data[f'{skill.skill_id}_level'] = skill.level
    if phase == 2:
        data['inventory']['Fingernails'] = source.CLUE_QUANTITY
    return data


def blockers(data):
    return quest_current_stage_blockers_pure(data, QUEST_ID, QUEST_DATA)


def advance(data, **kwargs):
    return apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA, **kwargs)


def journal(data):
    return quest_journal_rows_pure(data, QUEST_ID, QUEST_DATA)


class WatchtowerCatalogTest(unittest.TestCase):
    def test_catalog_keeps_later_requirements_combat_rewards_and_unlocks(self):
        quest = QUEST_DATA[QUEST_ID]
        baseline = tuple(_stage_requirement_dict(row) for row in _apply_stage_item_name_overrides(
            _catalog_stage_requirements(GENERATED['stage_requirements'])))
        self.assertEqual(quest['stage_requirements'][1:], baseline[1:])
        self.assertEqual(quest['stages'], 7)
        self.assertEqual(quest['required_quests'], ())
        self.assertEqual(quest['required_quest_points'], 0)
        for key in ('combat', 'point_reward', 'xp_rewards', 'unlocks'):
            self.assertEqual(quest[key], GENERATED[key], key)
        self.assertEqual(quest['rewards'], {'Coins': 5000, 'Spell scroll': 1})
        self.assertEqual(quest['journal_stages'], {
            r['stage']: source.PENDING_JOURNAL if r['stage'] == 1 else tuple(r['journal'])
            for r in GENERATED['journal_stages']
        })
        opening = source.opening_stage_requirements(QUEST_ID, _catalog_stage_requirements(GENERATED['stage_requirements']))[0]
        self.assertEqual(quest['stage_requirements'][0], _stage_requirement_dict(opening))
        self.assertEqual(opening.required_actions, PROOFS)
        self.assertEqual(opening.required_skills, (source.QuestSkillRequirement('agility', 'Agility', 18),))
        self.assertEqual(opening.description, 'Investigate the missing power crystals for the Watchtower Wizard.')
        for key in ('required_inventory', 'required_tools', 'consumed_inventory', 'produced_inventory',
                    'required_inventory_options', 'consumed_inventory_options', 'auto_actions', 'required_routes', 'combat_encounters'):
            self.assertFalse(getattr(opening, key), key)
        self.assertFalse(opening.repeatable_until_consumed)
        self.assertEqual(opening.variant, '')
        self.assertEqual(GENERATED['journal_stages'][0]['journal'],
                         ('Complete Watchtower stage 1 objective using the pinned source guide.',))

    def test_other_quests_and_later_objects_are_unchanged(self):
        from ankiscape.data.quest import catalog
        from ankiscape.data.quest.ledger import QUESTS
        generated = {row['id']: row for row in PRE_EOC_QUEST_CATALOG}
        for quest in QUESTS:
            if quest.id == QUEST_ID or quest.id not in generated:
                continue
            with self.subTest(quest=quest.id):
                baseline = catalog._quest_with_stage_requirements(quest, generated[quest.id])
                with patch.object(catalog, '_watchtower_opening_requirements', side_effect=lambda _id, rows: rows):
                    self.assertEqual(catalog._quest_with_stage_requirements(quest, generated[quest.id]), baseline)
        original = _catalog_stage_requirements(GENERATED['stage_requirements'])
        self.assertIs(source.opening_stage_requirements('other', original), original)
        self.assertTrue(all(a is b for a, b in zip(original[1:], source.opening_stage_requirements(QUEST_ID, original)[1:])))

    def test_skill_readouts_and_every_start_boundary(self):
        self.assertEqual(QUEST_DATA[QUEST_ID]['requirements'], source.WATCHTOWER_REQUIREMENTS)
        self.assertEqual([(r['skill_id'], r['level']) for r in QUEST_DATA[QUEST_ID]['required_skills']],
                         [('agility', 25), ('herblore', 14), ('magic', 14), ('mining', 40), ('thieving', 15)])
        for skill in source.WATCHTOWER_SKILLS:
            data = player(started=False, stage=0)
            data[f'{skill.skill_id}_level'] = skill.level - 1
            before = copy.deepcopy(data)
            self.assertFalse(can_start_quest_pure(data, QUEST_ID, QUEST_DATA), skill)
            self.assertEqual(start_quest_pure(data, QUEST_ID, QUEST_DATA), (data, False))
            self.assertEqual(advance(data), (data, False, False))
            self.assertEqual(data, before)
            data[f'{skill.skill_id}_level'] = skill.level
            self.assertTrue(can_start_quest_pure(data, QUEST_ID, QUEST_DATA))
        data = player(started=False, stage=0)
        before = copy.deepcopy(data)
        started, ok = start_quest_pure(data, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(started['quest_action_proofs'], [])
        self.assertEqual(started['inventory'], {})
        self.assertEqual(started['quests'][QUEST_ID]['progress'], 0)
        self.assertEqual(data, before)

    def test_exact_event_mapping_and_no_static_acquisition_claim(self):
        expected = (
            ('commission', 'watchtower_commission', (), PROOFS[0]),
            ('search', 'watchtower_bush_search', PROOFS[:1], PROOFS[1]),
            ('present', 'watchtower_present_fingernails', PROOFS[:2], PROOFS[2]),
        )
        for phase, event_id, required, emitted in expected:
            event = ('quest_service', event_id)
            self.assertEqual(source.PHASE_EVENTS[phase], event)
            self.assertEqual(source.PHASE_PROOFS[phase], emitted)
            self.assertEqual(QUEST_ACTION_PROOF_RULES[event], (required, (emitted,)))
            self.assertEqual(quest_action_proofs_after_event_pure(required, *event), sorted((*required, emitted)))
            self.assertNotIn(event, QUEST_ACTION_PROOF_AUDIT_SOURCES)
        self.assertEqual(quest_action_proofs_after_event_pure([], *source.PHASE_EVENTS['search']), [])
        self.assertEqual(quest_action_proofs_after_event_pure(PROOFS[:1], *source.PHASE_EVENTS['present']), list(PROOFS[:1]))

    def test_exact_source_pins_and_qualified_conflicts(self):
        expected = {
            'W6525573': ('2012-11-03T08:25:45Z', '8e6725ed4adcb188e8dcaaf682f86eea4c62008909b59197b474062d93a3c142'),
            'F6407465': ('2012-10-14T21:36:01Z', '9c3b51255ef0860a7922463b826b452fed830512a486a687006e56dc9c82bbca'),
            'RuneHQ': ('2012-11-03T18:32:41Z', 'c60e0a8515bf710bafb6c105abaeb31f14c9ed65f688b3a3c8693eeb5812b838'),
            'TipIt': ('2012-11-19T22:12:12Z', 'f89dd6db5e9f6e8e74f6d056078a4d5df6e6e545f2ceb7f4a63f4a479e585cfe'),
            'Sals': ('2012-09-20T04:18:41Z', 'f3398c0675fa54650bc58eb18cedb686e54739f3442cc1cc311ede3e0e7c9537'),
            'asset': ('2012-10-15T02:21:48Z', '8babb6a54becb9d2e6a943b9ceb507d71eca44786579244440b382559a14b3e4'),
        }
        for key, (timestamp, digest) in expected.items():
            row = source.SOURCE_RECORDS[key]
            self.assertEqual((row['timestamp'], row['sha256']), (timestamp, digest))
            self.assertTrue(row['url'].startswith('https://'))
            self.assertTrue(row['body'].startswith('sources/'))
            for field in ('locators', 'conditions', 'quantities_units', 'corroboration', 'disagreements', 'missing_fields'):
                self.assertTrue(row[field], (key, field))
        for build, date in ((727, '2012-07-24'), (742, '2012-11-07')):
            self.assertEqual(source.SOURCE_RECORDS[f'cache{build}_items']['sha256'], 'f5350a071b252e060c983744fd678b88c0f4f047b5972852a764e4e8be05323d')
            self.assertEqual(source.SOURCE_RECORDS[f'cache{build}_struct627']['sha256'], 'f1eb7ae9df53afb7f128c5aea8c0a230ac3fba563e3515c0a3133aeb85d8b454')
            self.assertEqual(source.SOURCE_RECORDS[f'cache{build}_items']['timestamp'], date)
        conflicts = source.SOURCE_RECORDS['W6525573']['disagreements']
        for phrase in ('Magic 15', 'Magic 14', 'optional', 'collect-all', 'No independent directional', 'single-wiki'):
            self.assertIn(phrase, conflicts)
        self.assertEqual(source.SOURCE_RECORDS['W6525573']['return_dialogue'], "'What should I do?' then 'So what do I do?\"")
        self.assertEqual(source.PROVISIONAL_COUNT_DECISION['value'], 1)
        self.assertEqual(source.PROVISIONAL_COUNT_DECISION['historical_quantity'], 'not stated')
        self.assertEqual(source.PROVISIONAL_COUNT_DECISION['authority'], 'Owner answer 2026-10-24 08:54 PDT')
        self.assertEqual(source.__all__, ())

    def test_registered_identity_and_byte_exact_packaged_asset(self):
        item = next(i for i in ITEM_DEFINITIONS if i.storage_key == 'Fingernails')
        self.assertEqual((item.id, item.source_item_id, item.category), ('material_fingernails', 2384, 'material'))
        self.assertFalse(item.stackable)
        self.assertFalse(item.tradeable)
        self.assertIsNone(item.equipment_slot)
        self.assertIsNone(item.equipment_type)
        metadata = source.WATCHTOWER_ITEMS['Fingernails']
        self.assertEqual((metadata['model_id'], metadata['client_options']), (1787, ('Destroy',)))
        self.assertEqual(metadata['destroy_warning'], 'This item will likely break if you put it down here, and you will have to go looking for another.')
        self.assertEqual(item.license_note, metadata['license_note'])
        self.assertEqual(item.asset_path, QUEST_ITEM_IMAGES['Fingernails'])
        body = Path(item.asset_path).read_bytes()
        self.assertEqual(len(body), 1210)
        self.assertEqual(struct.unpack('>II', body[16:24]), (29, 25))
        self.assertEqual(hashlib.sha256(body).hexdigest(), 'ee15a818232c7cb563574bd77dcd7ab75e118e56382debe95b9c4edf71437e99')
        self.assertEqual(hashlib.sha1(body).hexdigest(), 'c352bdb1f569fc4914628e56b1f023c279edb8d5')
        provenance = json.loads(Path(metadata['asset_provenance']).read_text())
        self.assertEqual(provenance['file_revision']['revid'], 6410504)
        self.assertEqual(provenance['file_revision']['timestamp'], '2012-10-15T02:21:48Z')
        self.assertEqual(provenance['upload']['timestamp'], '2011-11-21T01:58:16Z')
        self.assertEqual(provenance['upload']['url'], 'https://runescape.wiki/images/archive/20140502073535%21Fingernails.png?fcd15')
        self.assertEqual(provenance['raw_file_body_sha256'], source.SOURCE_RECORDS['asset']['sha256'])
        self.assertIn('terms not resolved', provenance['license_note'])
        self.assertEqual([r['http'] for r in provenance['requests']], ['200', '200'])
        self.assertNotIn('Fingernails', QUEST_DATA[QUEST_ID]['rewards'])
        ordinary = next(i for i in ITEM_DEFINITIONS if i.storage_key == 'Logs')
        self.assertEqual(ordinary.license_note, 'private-fork asset; provenance not audited')


class WatchtowerTransactionsTest(unittest.TestCase):
    def assert_refused(self, data, *, requested_phase=None, quest_id=QUEST_ID, reasons=None):
        original = copy.deepcopy(data)
        nested = (data['inventory'], data['quests'], data['quest_action_proofs'])
        result = service.apply_watchtower_review_pure(
            data, quest_id, blockers(data) if reasons is None else reasons, requested_phase=requested_phase)
        self.assertIs(result[0], data)
        self.assertEqual(result, (original, 'unchanged'))
        self.assertEqual(data, original)
        self.assertEqual(nested, (original['inventory'], original['quests'], original['quest_action_proofs']))

    def test_three_exact_pure_transactions_and_both_progress_shapes(self):
        for optional in (False, True):
            data = player(started=False, stage=0)
            for index, phase in enumerate(('commission', 'search', 'present')):
                data = self._assert_transaction(data, phase, index, optional)
            self.assertEqual(data['inventory'], {'Fingernails': 0})
            self.assertEqual(data['quests'][QUEST_ID]['progress'], 2)

    def _assert_transaction(self, data, phase, index, optional):
        before = copy.deepcopy(data)
        stores = (data['inventory'], data['quests'], data['quest_action_proofs'])
        self.assertEqual(service.watchtower_phase_pure(data, QUEST_ID), phase)
        direct, result = service.apply_watchtower_review_pure(data, QUEST_ID, blockers(data))
        expected = _copy_player_data_with_nested(data)
        expected['quests'][QUEST_ID] = dict(started=True, completed=False, progress=1)
        expected['quest_action_proofs'] = sorted(PROOFS[:index + 1])
        if index:
            expected['inventory']['Fingernails'] = 1 if index == 1 else 0
        self.assertEqual(direct, expected)
        self.assertEqual(result, 'completed' if index == 2 else 'pending')
        progressed = advance(data, include_clue_refusal=optional)
        expected['current_quest'] = QUEST_ID
        expected['quests'][QUEST_ID]['progress'] = 2 if index == 2 else 1
        self.assertEqual(progressed, (expected, True, False, '') if optional else (expected, True, False))
        self.assertEqual(data, before)
        self.assertEqual(stores, (before['inventory'], before['quests'], before['quest_action_proofs']))
        self.assertIsNot(direct['inventory'], stores[0])
        self.assertIsNot(direct['quests'][QUEST_ID], stores[1][QUEST_ID])
        self.assertIsNot(direct['quest_action_proofs'], stores[2])
        return progressed[0]

    def test_trellis_access_and_earned_ladder_permission(self):
        data = player()
        data['agility_level'] = 17
        self.assert_refused(data)
        self.assertEqual(advance(data), (data, False, False))
        data['agility_level'] = 18
        commissioned = advance(data)[0]
        self.assertIn(PROOFS[0], commissioned['quest_action_proofs'])
        commissioned['agility_level'] = 1
        searched = advance(commissioned)[0]
        self.assertEqual(searched['inventory']['Fingernails'], 1)
        self.assertEqual(advance(searched)[0]['quests'][QUEST_ID]['progress'], 2)

    def test_requirement_copy_only_removes_trellis_and_custody_at_right_time(self):
        requirement = copy.deepcopy(QUEST_DATA[QUEST_ID]['stage_requirements'][0])
        requirement['required_skills'] += ({'skill_id': 'magic', 'level': 7},)
        requirement['required_inventory'] = {'Coins': 2}
        before = copy.deepcopy(requirement)
        for phase in range(4):
            adjusted = service.watchtower_requirement_pure(player(phase), QUEST_ID, requirement)
            self.assertEqual(adjusted['required_inventory'], {'Coins': 2, 'Fingernails': 1} if phase == 2 else {'Coins': 2})
            self.assertEqual(len(adjusted['required_skills']), 2 if phase == 0 else 1)
            self.assertEqual(adjusted['required_actions'], PROOFS)
        self.assertEqual(requirement, before)
        self.assertIs(service.watchtower_requirement_pure(player(), 'other', requirement), requirement)
        later = dict(requirement, stage=2)
        self.assertIs(service.watchtower_requirement_pure(player(), QUEST_ID, later), later)

    def test_explicit_deeds_require_their_own_earned_phase(self):
        self.assert_refused(player(), requested_phase='search')
        self.assert_refused(player(), requested_phase='present')
        self.assert_refused(player(1), requested_phase='present')
        possessed = player(1)
        possessed['inventory']['Fingernails'] = 9
        self.assert_refused(possessed, requested_phase='present')
        self.assert_refused(player(2), requested_phase='search')
        self.assert_refused(player(3), requested_phase='present')
        self.assert_refused(player(), requested_phase='invalid')

    def test_optional_items_missing_clue_and_malformed_counts_refuse_fully(self):
        for name in OPTIONAL_FINDS:
            data = player(2)
            data['inventory'] = {name: 1}
            self.assert_refused(data)
            self.assertIn('Needs Fingernails x1', [b['reason'] for b in blockers(data)])
        data = player(2)
        data['inventory']['Fingernails'] = 0
        self.assert_refused(data)
        self.assertEqual(advance(data), (data, False, False))
        for phase in (1, 2):
            for count in (-1, 1.0, True, '1', None, [], {}):
                malformed = player(phase)
                malformed['inventory']['Fingernails'] = count
                self.assert_refused(malformed)
                self.assertEqual(advance(malformed), (malformed, False, False))

    def test_generic_possession_and_location_saves_still_earn_three_deeds(self):
        fixtures = (
            {'quest_action_proofs': ['Complete Watchtower stage 1 objective']},
            {'inventory': {'Fingernails': 4}},
            {'quest_route_states': {QUEST_ID: {'bushes': True, 'wizard': True}}, 'location': 'Watchtower'},
        )
        for fixture in fixtures:
            data = player()
            data.update(fixture)
            self.assert_refused(data, requested_phase='present')
            original_inventory = copy.deepcopy(data['inventory'])
            self.assertEqual(service.watchtower_phase_pure(data, QUEST_ID), 'commission')
            commissioned = advance(data)[0]
            self.assertEqual(commissioned['inventory'], original_inventory)
            searched = advance(commissioned)[0]
            self.assertEqual(searched['inventory']['Fingernails'], original_inventory.get('Fingernails', 0) + 1)
            presented = advance(searched)[0]
            self.assertEqual(presented['inventory']['Fingernails'], original_inventory.get('Fingernails', 0))
            self.assertEqual(presented['quests'][QUEST_ID]['progress'], 2)

    def test_wrong_quest_stage_completed_and_unrelated_blockers_refuse(self):
        self.assert_refused(player(), quest_id='murder_mystery')
        self.assert_refused(player(stage=2))
        completed = player()
        completed['quests'][QUEST_ID]['completed'] = True
        self.assert_refused(completed)
        self.assert_refused(player(), reasons=({'kind': 'missing_item', 'reason': 'Needs other'},))
        self.assert_refused(player(), reasons=({'kind': 'required_action', 'action_id': 'Other deed'},))
        catalog = copy.deepcopy(QUEST_DATA)
        row = dict(catalog[QUEST_ID]['stage_requirements'][0], required_actions=PROOFS + ('Other deed',))
        catalog[QUEST_ID]['stage_requirements'] = (row, *catalog[QUEST_ID]['stage_requirements'][1:])
        data = player()
        self.assertEqual(apply_quest_progress_pure(data, QUEST_ID, catalog), (data, False, False))

    def test_independent_validation_does_not_trust_supplied_empty_blockers(self):
        data = player()
        data['agility_level'] = 17
        self.assert_refused(data, reasons=())
        data = player(2)
        data['inventory'] = {}
        self.assert_refused(data, reasons=())

    def test_failed_mutation_or_proof_discards_entire_candidate(self):
        for phase in range(3):
            data = player(phase)

            def refuse_mutation(candidate, _phase):
                candidate['inventory']['Fingernails'] = 900
                candidate['quests'][QUEST_ID]['progress'] = 99
                return False
            with patch.object(service, '_apply_phase_mutations', side_effect=refuse_mutation):
                self.assert_refused(data)

            def refuse_proof(candidate, *_event):
                candidate['quest_action_proofs'].append('unrelated')
                return False
            with patch.object(service, 'record_runtime_quest_action_proofs_pure', side_effect=refuse_proof):
                self.assert_refused(data)
                self.assertEqual(advance(data), (data, False, False))
            with patch.object(service, 'record_runtime_quest_action_proofs_pure', return_value=True):
                self.assert_refused(data)

    def test_journals_are_exact_observations_and_legacy_rows_claim_no_deeds(self):
        expected = (
            source.PENDING_JOURNAL,
            source.COMMISSION_JOURNAL + source.PENDING_JOURNAL[1:],
            source.COMMISSION_JOURNAL + (source.SEARCH_JOURNAL, source.PENDING_JOURNAL[2]),
            source.COMPLETED_JOURNAL,
        )
        for phase, lines in enumerate(expected):
            data = player(phase)
            before, rng = copy.deepcopy(data), random.getstate()
            self.assertEqual(journal(data), (dict(stage=1, lines=lines, completed=False, current=True),))
            self.assertEqual(data, before)
            self.assertEqual(random.getstate(), rng)
        earned = player(3, stage=2)
        self.assertEqual(journal(earned)[0], dict(stage=1, lines=source.COMPLETED_JOURNAL, completed=True, current=False))
        self.assertFalse(journal(earned)[1]['completed'])
        for completed in (False, True):
            data = player(stage=5)
            data['quests'][QUEST_ID]['completed'] = completed
            before = copy.deepcopy(data)
            rows = journal(data)
            self.assertEqual(rows[0], dict(stage=1, lines=source.LEGACY_JOURNAL, completed=False, current=False))
            for row in rows[1:]:
                self.assertEqual(row['lines'], QUEST_DATA[QUEST_ID]['journal_stages'][row['stage']])
            self.assertEqual(data, before)
