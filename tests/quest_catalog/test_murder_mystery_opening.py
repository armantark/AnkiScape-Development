"""The sourced opening is a genuine two-item deed, including on old saves."""

import copy
import json
import unittest
from datetime import datetime
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA, UTILITY_ACTIVITY_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest import murder_mystery as source
from ankiscape.data.quest.catalog import _catalog_stage_requirements, _apply_stage_item_name_overrides
from ankiscape.data.quest.contract import QuestStage
from ankiscape.data.quest.serializers import _stage_requirement_dict
from ankiscape.data.quest_item_acquisition_data import quest_item_acquisition_extra_items_as_dict
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, quest_current_stage_blockers_pure,
    quest_journal_rows_pure, start_quest_pure,
)
from ankiscape.logic_pure.quest.murder_mystery import (
    _grant_opening_item_pure, apply_murder_mystery_opening_items_pure,
    murder_mystery_journal_row_pure,
)
from tests.reachability.live_report import live_reachability_report

QUEST_ID = 'murder_mystery'
ACTION = "Search the eastern murder scene and collect the Pungent pot and Criminal's dagger"
POT, DAGGER = 'Pungent pot', "Criminal's dagger"
GRANT = 'ankiscape.logic_pure.quest.murder_mystery._grant_opening_item_pure'
APPLY = 'ankiscape.logic_pure.logic_pure_quest.apply_murder_mystery_opening_items_pure'
GENERATED = next(row for row in PRE_EOC_QUEST_CATALOG if row['id'] == QUEST_ID)
OPENING_LINES = (
    "At Sinclair Mansion, north of Seers' Village, a guard reports that Lord Sinclair has been murdered and the guards cannot identify the killer.",
    "Offer your help. The guard asks you to question the family to gather information about the murder.",
    "First, search the eastern murder scene and collect one Pungent pot and one Criminal's dagger.",
)
LATER_LINES = (
    "Talk to the guard at the smashed window, then search it for the Criminal's thread.",
    "Investigate the wooden gate.",
    "Search Anna's bedroom barrel for the Silver necklace. (Pending)",
    "Search Bob's bedroom barrel for the Silver cup. (Pending)",
    "Search Carol's bedroom barrel for the Silver bottle. (Pending)",
    "Search David's bedroom barrel for the Silver book. (Pending)",
    "Search Elizabeth's bedroom barrel for the Silver needle. (Pending)",
    "Search Frank's bedroom barrel for the Silver pot. (Pending)",
)
NEUTRAL_LINES = (
    "The guards at Sinclair Mansion, north of Seers' Village, cannot identify Lord Sinclair's murderer and ask for help gathering information from the family.",
    "The eastern murder scene contains a Pungent pot and Criminal's dagger.",
)


def player(stage=0, completed=False):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data['inventory'] = {'Coins': 37}
    data['quest_action_proofs'] = []
    data['quests'][QUEST_ID] = dict(started=True, progress=stage, completed=completed)
    data['current_quest'] = QUEST_ID
    return data


def journal(data):
    return quest_journal_rows_pure(data, QUEST_ID, QUEST_DATA)


def advance(data, **kwargs):
    return apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA, **kwargs)


def reload_player(data):
    return migrate_loaded_data(json.loads(json.dumps(data)), ORE_DATA, ITEM_DEFINITIONS)


def refuse_second(inventory, name, quantity):
    if name == DAGGER:
        return False
    return _grant_opening_item_pure(inventory, name, quantity)


class TestMurderMysteryOpening(unittest.TestCase):
    def test_source_pins_and_conflicts(self):
        expected = {
            'W1': ('revision', '6569570', '2012-11-17T21:22:05Z', '31126f1476e5bf3f743f191b078d60124a031734683be709428a483dcb47cc4a'),
            'W2': ('revision', '6512948', '2012-10-31T18:08:41Z', '6a70bea37dc7a128a27d7f4c08f4b6d6f674bfa774c8335a4410e0036a86212b'),
            'W3': ('revision', '5133180', '2012-01-09T23:59:00Z', '84a1d0c7c02505c0fb906a0c86e5c6512ef78c776179f34ec6943e1fce555fcb'),
            'W4': ('revision', '6260613', '2012-09-18T19:18:26Z', '3b4f40a7e3423291617febd854280424eaeedc1518820086075794a2ed1abfb4'),
            'A1': ('replay', '20121018060902', '2012-10-18T06:09:02Z', 'd49436b57a19bd67412ad9347138d2acd16fc89aa279750d1a98b72fbe5246a0'),
            'A2': ('replay', '20121103153756', '2012-11-03T15:37:56Z', 'd336f6838bc74b6d5c9357392df54faec96ce009f769b102a586a4cf5bcf718f'),
        }
        self.assertEqual(set(source.PERIOD_SOURCES), set(expected))
        for key, (kind, pin, timestamp, digest) in expected.items():
            row = source.PERIOD_SOURCES[key]
            with self.subTest(source=key):
                self.assertEqual((row[kind], row['timestamp'], row['sha256']), (pin, timestamp, digest))
                self.assertIn(pin, row['url'])
                self.assertTrue(row['title'])
                self.assertTrue(row['saved_body'].startswith('sources/'))
                self.assertEqual(tuple(row['extracts']), row['original_lines'])
                self.assertLess(datetime.fromisoformat(timestamp), datetime.fromisoformat(source.SOURCE_CUTOFF))
        self._assert_source_boundaries()

    def _assert_source_boundaries(self):
        self.assertEqual(source.PERIOD_SOURCES['W1']['extracts'][39],
                         "First, search the murder scene, which is on the eastern side of the mansion. Inside will be a [[pungent pot]] which you should collect, along with the [[criminal's dagger]].")
        self.assertEqual(source.PERIOD_SOURCES['W2']['extracts'][19], "*Take the [[Pungent pot]] and [[Criminal's dagger]].")
        self.assertIn('Head back', source.PERIOD_SOURCES['A2']['extracts'][310])
        self.assertIn('delays the dagger', source.SOURCE_DECISIONS['A2_disagreement'])
        self.assertIn('every conversation/option', source.SOURCE_DECISIONS['A2_disagreement'])
        self.assertIn('sequential partial grants are excluded', source.SOURCE_DECISIONS['Darkan_disagreement'])
        provenance = source.CONFIGURATION_PROVENANCE
        self.assertEqual(provenance['ids'], {POT: 1812, 'clean dagger': 1813, 'dusted dagger': 1814, 'Empty pot': 1931})
        self.assertEqual(provenance['builds'], (727, 728, 729, 736, 741, 742))
        self.assertEqual(provenance['darkan_commit'], 'bdea22f7f98391da022256269db4fac4f095247b')
        self.assertIn('not period server code', provenance['darkan_qualification'])
        self.assertIn('1746–1748', provenance['configured_667'])
        self.assertEqual(source.ASSET_SEARCH['sha256'], '48f0128ebd9429bc0a2ff33adc35868e6028abb902a05bd46e4f64241e0c544a')
        for key in ('historical_spawn', 'historical_capacity', 'historical_repeat_pickup'):
            self.assertEqual(source.SOURCE_DECISIONS[key], 'not stated')
        for name, page in ((POT, 'W3'), (DAGGER, 'W4')):
            row = source.MURDER_MYSTERY_OPENING_ITEMS[name]
            self.assertEqual(set(row), {'category', 'item_id', 'stackable', 'tradeable', 'source'})
            for key in (page, 'W1', 'W2', 'A1'):
                self.assertIn(source.PERIOD_SOURCES[key]['url'], row['source'])
            self.assertIn('cache-row-verification.json', row['source'])

    def test_opening_catalog_replaces_only_stage_one_and_journals_one_two(self):
        quest = QUEST_DATA[QUEST_ID]
        baseline = tuple(_stage_requirement_dict(row) for row in _apply_stage_item_name_overrides(
            _catalog_stage_requirements(GENERATED['stage_requirements'])))
        self.assertEqual(quest['stage_requirements'][1:], baseline[1:])
        row = quest['stage_requirements'][0]
        expected = dict(baseline[0], required_inventory={}, required_actions=(),
                        auto_actions=(ACTION,), produced_inventory={POT: 1, DAGGER: 1},
                        source=source.MURDER_MYSTERY_OPENING_CLEANUPS[0].source)
        self.assertEqual(row, expected)
        self.assertEqual(quest['stages'], max(GENERATED['stages'], max(r['stage'] for r in baseline) + 1))
        self.assertEqual(quest['journal_stages'][1], OPENING_LINES)
        self.assertEqual(quest['journal_stages'][2], tuple(line.removesuffix(' (Pending)') for line in LATER_LINES))
        self.assertEqual({n: lines for n, lines in quest['journal_stages'].items() if n >= 3},
                         {r['stage']: tuple(r['journal']) for r in GENERATED['journal_stages'] if r['stage'] >= 3})
        stages = tuple(QuestStage(r['stage'], tuple(r['journal'])) for r in GENERATED['journal_stages'])
        replaced = source.murder_mystery_opening_journal_stages(QUEST_ID, stages)
        self.assertTrue(all(a is b for a, b in zip(stages[2:], replaced[2:])))
        self.assertIs(source.murder_mystery_opening_journal_stages('other', stages), stages)
        report = live_reachability_report()
        for name in (POT, DAGGER):
            self.assertEqual(report['routes'].get(name), 'quest-stage:murder_mystery:1')
        self.assertFalse(any(r.get('output_item') in (POT, DAGGER) for r in UTILITY_ACTIVITY_DATA.values()))

    def test_registry_and_missing_asset_fallback(self):
        for name, identity, item_id in ((POT, 'material_pungent_pot', 1812), (DAGGER, 'material_criminal_s_dagger', 1813)):
            rows = [item for item in ITEM_DEFINITIONS if item.storage_key == name]
            self.assertEqual(len(rows), 1)
            item = rows[0]
            self.assertEqual((item.id, item.category, item.source_item_id), (identity, 'material', item_id))
            self.assertFalse(item.stackable)
            self.assertFalse(item.tradeable)
            self.assertIsNone(item.equipment_slot)
            self.assertIsNone(item.equipment_type)
            self.assertIsNone(item.asset_path)
        ordinary = next(i for i in ITEM_DEFINITIONS if i.storage_key == 'Empty pot')
        self.assertNotEqual(ordinary.id, 'material_pungent_pot')
        self.assertNotIn(ordinary.source_item_id, (1812, 1813, 1814))
        self.assertEqual(source.CONFIGURATION_PROVENANCE['ids']['Empty pot'], 1931)
        extra = quest_item_acquisition_extra_items_as_dict()
        extra[POT]['item_id'] = -1
        self.assertEqual(quest_item_acquisition_extra_items_as_dict()[POT]['item_id'], 1812)
        self.assertIn('Ugthanki dung', extra)
        self.assertEqual(set(source.MURDER_MYSTERY_OPENING_ITEMS), {POT, DAGGER})

    def test_start_and_inspection_never_grant(self):
        data = player()
        data['quests'].pop(QUEST_ID)
        before = copy.deepcopy(data)
        started, ok = start_quest_pure(data, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        prepared = copy.deepcopy(started)
        for _ in range(3):
            self.assertEqual(journal(started)[0]['lines'], OPENING_LINES)
            started, ok = start_quest_pure(started, QUEST_ID, QUEST_DATA)
            self.assertTrue(ok)
        self.assertEqual(started, prepared)
        self.assertEqual(data, before)
        self.assertEqual(started['quests'][QUEST_ID], dict(started=True, progress=0, completed=False))
        for key in ('inventory', 'quest_action_proofs', 'quest_points', 'pending_skill_exp_rewards'):
            self.assertEqual(started[key], before[key])

    def test_first_review_grants_one_each_and_only_opening_proof(self):
        for stage in (0, 1):
            for optional in (False, True):
                with self.subTest(stage=stage, optional=optional):
                    self._assert_first_review(stage, optional)

    def _assert_first_review(self, stage, optional):
        data = player(stage)
        data['crafting_exp'] = 123.0
        before = copy.deepcopy(data)
        catalog_before = copy.deepcopy(QUEST_DATA[QUEST_ID])
        result = advance(data, include_clue_refusal=optional)
        self.assertEqual(len(result), 4 if optional else 3)
        after, ok, completed = result[:3]
        self.assertTrue(ok)
        self.assertFalse(completed)
        if optional:
            self.assertEqual(result[3], '')
        self.assertEqual(after['inventory'], dict(before['inventory'], **{POT: 1, DAGGER: 1}))
        self.assertEqual(after['quest_action_proofs'], [ACTION])
        self.assertEqual(after['quests'][QUEST_ID], dict(started=True, progress=2, completed=False))
        self.assertEqual(data, before)
        self.assertEqual(QUEST_DATA[QUEST_ID], catalog_before)
        expected = copy.deepcopy(before)
        expected['inventory'].update({POT: 1, DAGGER: 1})
        expected['quest_action_proofs'] = [ACTION]
        expected['quests'][QUEST_ID]['progress'] = 2
        self.assertEqual(after, expected)

    def test_existing_stock_and_full_pack_use_ordinary_quest_custody(self):
        for stock in ({}, {POT: 3, DAGGER: 5}):
            data = player(1)
            data['inventory'].update(stock, **{'Empty pot': 7, 'Logs': 28})
            data['carried_inventory'] = {'chop_normal': {'Logs': 28}}
            data['carried_churn'] = {'chop_normal': 17}
            data['bank_layout'] = {'items': {'Logs': {'section': 'main', 'order': 1}}}
            data['equipment']['weapon'] = 'Bronze axe'
            before = copy.deepcopy(data)
            after, ok, _ = advance(data)
            self.assertTrue(ok)
            expected = dict(before['inventory'])
            expected.update({POT: stock.get(POT, 0) + 1, DAGGER: stock.get(DAGGER, 0) + 1})
            self.assertEqual(after['inventory'], expected)
            for key in before.keys() - {'inventory', 'quests', 'quest_action_proofs'}:
                self.assertEqual(after[key], before[key], key)
            self.assertEqual(data, before)

    def test_second_grant_refusal_is_atomic(self):
        for invalid in (-1, True, '1', 1.5, None):
            for optional in (False, True):
                data = player(1)
                data['inventory'].update({POT: 4, DAGGER: invalid})
                with self.subTest(invalid=invalid, optional=optional):
                    self._assert_refused(data, optional)
        with patch(GRANT, side_effect=refuse_second) as grant:
            self._assert_refused(player(1), True)
            self.assertEqual([call.args[1] for call in grant.call_args_list], [POT, DAGGER])
        for invalid in (-1, False, '0', 0.0):
            inventory = {POT: invalid, 'Coins': 37}
            before = dict(inventory)
            self.assertFalse(_grant_opening_item_pure(inventory, POT, 1))
            self.assertEqual(inventory, before)

    def _assert_refused(self, data, optional):
        before, rows = copy.deepcopy(data), journal(data)
        result = advance(data, include_clue_refusal=optional)
        self.assertIs(result[0], data)
        self.assertEqual(result[1:], (False, False, '') if optional else (False, False))
        self.assertEqual(data, before)
        self.assertEqual(journal(result[0]), rows)

    def test_stage_blockers_refuse_before_any_grant(self):
        isolated = {QUEST_ID: copy.deepcopy(QUEST_DATA[QUEST_ID])}
        isolated[QUEST_ID]['stage_requirements'][0]['required_inventory'] = {'Copper ore': 1}
        data = player(1)
        before = copy.deepcopy(data)
        blockers = quest_current_stage_blockers_pure(data, QUEST_ID, isolated)
        self.assertEqual([row['item_name'] for row in blockers], ['Copper ore'])
        with patch(APPLY) as grant:
            result = apply_quest_progress_pure(data, QUEST_ID, isolated)
        grant.assert_not_called()
        self.assertEqual(result, (before, False, False))
        self.assertEqual(data, before)

    def test_later_or_completed_state_never_replays_opening(self):
        for stage, completed in ((0, False), (2, False), (4, False), (5, True)):
            data = player(stage, completed)
            if stage == 0:
                data['quests'][QUEST_ID]['started'] = False
            before = copy.deepcopy(data)
            self.assertFalse(apply_murder_mystery_opening_items_pure(data))
            self.assertEqual(data, before)
        earned, _, _ = advance(player())
        earned['inventory'].pop(POT)
        earned['inventory'].pop(DAGGER)
        for completed in (False, True):
            data = copy.deepcopy(earned)
            data['quests'][QUEST_ID].update(completed=completed, progress=5 if completed else 2)
            before = copy.deepcopy(data)
            for _ in range(2):
                data, _ = start_quest_pure(data, QUEST_ID, QUEST_DATA)
                journal(data)
                data, ok, done = advance(data)
                self.assertEqual(ok, not completed)
                self.assertFalse(done)
                self.assertNotIn(POT, data['inventory'])
                self.assertNotIn(DAGGER, data['inventory'])
                self.assertIn(ACTION, data['quest_action_proofs'])
            if completed:
                self.assertEqual(data, before)
            else:
                self.assertEqual(data['quests'][QUEST_ID], before['quests'][QUEST_ID])
                self.assertEqual(data['inventory'], dict(before['inventory'], **{'Silver necklace': 1, 'Silver cup': 1}))
                self.assertEqual(set(data['quest_action_proofs']) - set(before['quest_action_proofs']),
                                 {'murder_mystery.search_anna_barrel', 'murder_mystery.search_bob_barrel'})

    def test_earned_journal_marks_only_opening_done(self):
        data, _, _ = advance(player())
        opening, next_row = journal(data)
        self.assertEqual(opening, dict(stage=1, lines=OPENING_LINES, completed=True, current=False))
        self.assertEqual(next_row, dict(stage=2, lines=LATER_LINES, completed=False, current=True))
        self.assertFalse(any(word in ' '.join(opening['lines']) for word in ('window', 'gate', 'barrels')))

    def test_legacy_journal_never_claims_new_deed(self):
        for completed, stage in ((False, 2), (False, 4), (True, 5)):
            data = player(stage, completed)
            data['inventory'].update({POT: 3, DAGGER: 2})
            data['quest_action_proofs'] = ['Complete Murder Mystery stage 1 objective']
            before = copy.deepcopy(data)
            for _ in range(2):
                self.assertEqual(journal(data)[0], dict(stage=1, lines=NEUTRAL_LINES, completed=False, current=False))
            self.assertEqual(data, before)
        row = dict(stage=1, lines=('other',), current=False, completed=True)
        self.assertIs(murder_mystery_journal_row_pure({}, 'other', row), row)

    def test_legacy_migration_preserves_progress_without_backfill(self):
        for completed, stage in ((False, 2), (False, 4), (True, 5)):
            data = player(stage, completed)
            data['inventory'].update({POT: 3, DAGGER: 2})
            data['quest_action_proofs'] = ['Complete Murder Mystery stage 1 objective', 'unrelated supported proof']
            before = copy.deepcopy(data)
            migrated = reload_player(data)
            self.assertEqual(migrated['quests'][QUEST_ID], data['quests'][QUEST_ID])
            self.assertEqual(migrated['quest_action_proofs'], sorted(data['quest_action_proofs']))
            for name in (POT, DAGGER, 'Coins'):
                self.assertEqual(migrated['inventory'][name], data['inventory'][name])
            for key in ('quest_points', 'pending_skill_exp_rewards', 'crafting_exp'):
                self.assertEqual(migrated[key], data[key])
            self.assertEqual(journal(migrated)[0]['lines'], NEUTRAL_LINES)
            self.assertEqual(reload_player(migrated), migrated)
            self.assertEqual(data, before)
        fresh = reload_player(player())
        self.assertEqual((fresh['inventory'].get(POT, 0), fresh['inventory'].get(DAGGER, 0)), (0, 0))
        self.assertNotIn(ACTION, fresh['quest_action_proofs'])
