"""Sourced opening, owned-store custody and performed-scan atomicity."""
import copy
import hashlib
import json
import struct
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest.stage_overrides.members.later import the_slug_menace as source
from ankiscape.data.quest_item_acquisition_data import (
    quest_item_acquisition_extra_items_as_dict, quest_item_acquisition_item_images_as_dict,
)
from ankiscape.data.quest.contract import QuestStage
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, start_quest_pure, quest_locked_reasons_pure,
    quest_current_stage_blockers_pure, quest_journal_rows_pure,
)
from ankiscape.logic_pure.quest import the_slug_menace as transaction
from ankiscape.logic_pure.quest.card_view import quest_journal_view_rows_pure

QUEST_ID = 'the_slug_menace'
ACTIONS = (
    "Receive Tiffy's Witchaven mission, password and Commorb v2",
    "Finish O'Niall's referral to Mayor Hobb, Brother Maledict and Holgart",
    "Talk to Mayor Hobb about the Saradomin shrine and receive Savant's scan request",
    'Scan Mayor Hobb with Commorb v2',
)
LINES = (
    "Talk to Sir Tiffy Cashien in Falador Park about a job. He sends you to investigate Witchaven and report to Col. Jake O'Niall.",
    'Tiffy upgrades your Commorb to Commorb v2, or supplies Commorb v2 if you do not have a Commorb. The password is: "In Falador, the geese fly backwards on Tuesday."',
    "In Witchaven, finish O'Niall's referral to Mayor Hobb, Brother Maledict and Holgart.",
    'Talk to Mayor Hobb about the shrine to Saradomin. Savant asks you to scan him.',
    'Use Commorb v2 to scan Mayor Hobb. Savant detects two life forms but is unsure what it means.',
)
DEEDS = ('_perform_commission_pure', '_perform_referral_pure',
         '_perform_mayor_conversation_pure', '_perform_mayor_scan_pure')
ROOT = Path(source.__file__).resolve().parents[3]
PINS = {
    'W1': ('6588246', '2b47b11e8513544dbd597e0ce25849e057de0942ef6885c46a505fb1af419532'),
    'C1': ('5775688', '1d78df1688f0c07cb910ad7c01f355a419b0ed4c3212a994d46db4edacbf66c3'),
    'C2': ('5783735', '2acc1a1043e8a1f5d979598f6cc93c0be91322a62c215a7e0238934de25aa95f'),
    'Q1': ('6552449', '02c5d8c2cd510450ad1117a49693b4cf31dab273ff7d86e01e176ff101277105'),
    'K1': ('6555554', '6776376d2c748749f0b1643aa789e33cd938d9d7099d7a43b26985f29b45686e'),
    'T1': ('20121119222000', '0032a46ff431526fc46e915065486e0e6ee7e3a99c1fd82b58a90e2e7e433b6d'),
    'S1': ('20121018051313', '0691ea9fe4b473274d58c46e579ebe3e2be241097a90c363bd4f668bb494e7fa'),
    'B1': ('727/728/729/736/741/742', '2c116f78747b18cbc105c60cc4c5483a03172237c1d0005dc1161309b176a0ff'),
    'B2': ('727/728/729/736/741/742', 'a887c0514af9428d52d5de2e0bb7b36fe00c3c57ac9995cc28e594535238a2ab'),
    'I1': ('6408875', '1cd5e9b3804f886223ffe85f0d0f446a44cf4bbaf3908b0409444f64d0a07e15'),
    'I2': ('6408876', '59fbd73a3572d096a342a20cad3ba6b3dfceab368c339e775a6403e01d030b50'),
}


def eligible(data):
    """An isolated eligible save; this makes no upstream-route acceptance claim."""
    for quest in ('sea_slug', 'wanted', 'recruitment_drive'):
        data['quests'][quest] = dict(started=True, completed=True, progress=QUEST_DATA[quest]['stages'])
    for skill in ('crafting', 'runecrafting', 'slayer', 'thieving'):
        data[skill + '_level'] = 30
    return data


def player(progress=0, started=True, completed=False):
    data = eligible(default_player_data(ORE_DATA, ITEM_DEFINITIONS))
    data['inventory'] = {'Coins': 37}
    data['quests'][QUEST_ID] = dict(started=started, progress=progress, completed=completed)
    data['current_quest'] = QUEST_ID
    return data


def journal(data):
    return quest_journal_rows_pure(data, QUEST_ID, QUEST_DATA)


def advance(data):
    return apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA)


class TestSlugMenaceSources(unittest.TestCase):
    def test_source_pins_boundaries_conflicts_and_qualifications(self):
        record = json.loads((ROOT / 'the_slug_menace_sources.json').read_text())
        self.assertEqual(set(record['sources']), set(PINS))
        for key, (pin, digest) in PINS.items():
            with self.subTest(key=key):
                row = record['sources'][key]
                self.assertEqual((row['pin'], row['sha256']), (pin, digest))
                self.assertTrue(bool(row['timestamp']))
                self.assertTrue(row['saved_body'].startswith('sources/'))
        self.assertIn('two life forms', record['sources']['W1']['literal_extracts']['72'])
        self.assertIn('Brother Maledict', record['sources']['W1']['literal_extracts']['76'])
        self.assertIn('Brother Maledict', record['sources']['S1']['literal_extracts']['116'])
        self.assertEqual(record['sources']['C1']['original_response_sha256'],
                         '4b45c3dda490c5aff4df687c2600a478b2f8bb42906292ae3ce5f3ea210e22ce')
        self.assertEqual(set(record['not_stated'].values()), {'not stated'})
        self.assertIn('Tuesdays', record['source_conflicts']['password'])
        self.assertIn('neither interview', record['source_conflicts']['route'])
        self.assertIn('10+', record['source_conflicts']['essence'])
        self.assertIn('reconstruction', record['source_conflicts']['darkan'])
        for name in ('prior-root-binding.json', 'prior-qualification.json', 'file-manifest.json',
                     'body-checks.json', 'latest-replay-verification.json', 'ledger-reconciliation.json',
                     'reuse-manifest.json', 'local-binding-receipt.json'):
            self.assertIn(name, record['receipts'])

    def test_selected_source_transaction_bindings(self):
        record = json.loads((ROOT / 'the_slug_menace_sources.json').read_text())
        selected = {row['selection']: row for row in record['selected_transactions']}
        self.assertEqual(len(selected), 17)
        for name, registry_id in (('Original Commorb', 'material_commorb'),
                                  ('Commorb v2', 'material_commorb_v2')):
            self.assertIn(registry_id, selected[name]['treatment'])
        self.assertEqual(selected['Examine']['treatment'],
                         'A Temple Knight Communication Orb. Top Secret!')
        self.assertIn('directed at Mayor Hobb', selected['Scan']['treatment'])
        self.assertIn('two life forms', selected['Reading']['treatment'])
        self.assertIn('does not perform their interviews', selected['Endpoint']['treatment'])
        for row in selected.values():
            for reference in row['references']:
                self.assertIn(reference.split()[0].split(':')[0], record['sources'])
        for name, key in (('Commorb', 'C1'), ('Commorb v2', 'C2')):
            metadata = quest_item_acquisition_extra_items_as_dict()[name]
            for source_key in (key, 'W1', 'T1', 'S1', 'B2' if key == 'C1' else 'B1'):
                self.assertIn(source_key, metadata['source'])
        self.assertIn('upgrade', record['sources']['W1']['literal_extracts']['55'].lower())
        self.assertIn('scan', record['sources']['W1']['literal_extracts']['72'].lower())

    def test_registry_fresh_metadata_and_exact_period_images(self):
        rows = quest_item_acquisition_extra_items_as_dict()
        images = quest_item_acquisition_item_images_as_dict()
        self.assertEqual(set(images), {'Commorb', 'Commorb v2'})
        provenance = json.loads((ROOT / 'slug_menace_assets/provenance.json').read_text())
        for name, item_id, key, size in [('Commorb', 6635, 'I1', (24, 25)), ('Commorb v2', 9681, 'I2', (24, 24))]:
            with self.subTest(name=name):
                row = rows[name]
                self.assertEqual(row['item_id'], item_id)
                self.assertEqual(row['category'], 'material')
                self.assertIs(row['stackable'], False)
                self.assertIs(row['tradeable'], False)
                self.assertNotIn('equipment_slot', row)
                self.assertNotIn('equipment_type', row)
                definition = next(d for d in ITEM_DEFINITIONS if d.id == 'material_' + name.lower().replace(' ', '_'))
                self.assertEqual(definition.storage_key, name)
                self.assertEqual(len([d for d in ITEM_DEFINITIONS if d.storage_key == name]), 1)
                self.assertEqual(definition.asset_path, images[name])
                raw = Path(images[name]).read_bytes()
                self.assertEqual(struct.unpack('>II', raw[16:24]), size)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), PINS[key][1])
                self.assertEqual(provenance[Path(images[name]).name]['sha256'], PINS[key][1])
                row['item_id'] = -1
                self.assertEqual(quest_item_acquisition_extra_items_as_dict()[name]['item_id'], item_id)
        self.assertIn('Commorb v2', QUEST_DATA[QUEST_ID]['stage_requirements'][0]['produced_inventory'])

    def test_catalog_fields_and_unchanged_later_content(self):
        quest = QUEST_DATA[QUEST_ID]
        self.assertEqual((quest['stages'], len(quest['journal_stages']), len(quest['stage_requirements'])), (8, 7, 7))
        self.assertEqual(quest['journal_stages'][1], LINES)
        self.assertEqual(source.OPENING_ACTIONS, ACTIONS)
        stage = quest['stage_requirements'][0]
        for key in ('required_inventory', 'required_tools', 'consumed_inventory'):
            self.assertEqual(stage[key], {})
        for key in ('required_inventory_options', 'required_actions', 'combat_encounters'):
            self.assertEqual(stage[key], ())
        self.assertEqual(stage['auto_actions'], ACTIONS)
        self.assertEqual(stage['produced_inventory'], {'Commorb v2': 1})
        self.assertEqual(quest['stage_requirements'][4]['required_inventory'], {'Swamp paste': 1})
        rune = quest['stage_requirements'][5]
        self.assertEqual(rune['required_tools'], {'Chisel': 1})
        self.assertEqual(rune['required_inventory_options'], (
            ({'Rune essence': 5}, {'Pure essence': 5}),
            ({'Earth talisman': 1}, {'Elemental talisman': 1}, {'Omni-talisman': 1}),
            ({'Water talisman': 1}, {'Elemental talisman': 1}, {'Omni-talisman': 1}),
            ({'Fire talisman': 1}, {'Elemental talisman': 1}, {'Omni-talisman': 1}),
            ({'Air talisman': 1}, {'Elemental talisman': 1}, {'Omni-talisman': 1}),
            ({'Mind talisman': 1}, {'Omni-talisman': 1})))
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row['id'] == QUEST_ID)
        for index in range(1, 7):
            self.assertEqual(quest['journal_stages'][index + 1], tuple(generated['journal_stages'][index]['journal']))
            row = quest['stage_requirements'][index]
            self.assertEqual(row['required_actions'], (f'Complete The Slug Menace stage {index + 1} objective',))
            self.assertEqual(row['auto_actions'], ())
            self.assertEqual(row['produced_inventory'], {})
        self.assertEqual(rune['combat_encounters'][0]['display_name'], 'Slug Prince')
        self.assertEqual(quest['rewards'], {'Proselyte armour': 1})
        self.assertEqual(quest['point_reward'], 1)
        self.assertEqual(quest['unlocks'], ())
        other = (QuestStage(1, ('untouched',)),)
        self.assertIs(source.slug_menace_opening_journal_stages('other', other), other)
        from ankiscape.data import quest_data
        self.assertFalse(hasattr(quest_data, 'SLUG_MENACE_OPENING_ITEMS'))


class TestSlugMenaceTransaction(unittest.TestCase):
    def test_unstarted_prerequisite_and_skill_boundaries(self):
        for missing in ('sea_slug', 'wanted', 'recruitment_drive'):
            data = player(started=False)
            data['quests'][missing]['completed'] = False
            result, ok = start_quest_pure(data, QUEST_ID, QUEST_DATA)
            self.assertFalse(ok, missing)
            self.assertEqual(result, data)
        for skill in ('crafting', 'runecrafting', 'slayer', 'thieving'):
            data = player(started=False)
            data[skill + '_level'] = 29
            self.assertIn(skill.title() + ' 30', quest_locked_reasons_pure(data, QUEST_ID, QUEST_DATA))
            self.assertFalse(start_quest_pure(data, QUEST_ID, QUEST_DATA)[1])
        self.assertTrue(start_quest_pure(player(started=False), QUEST_ID, QUEST_DATA)[1])

    def test_start_journal_and_load_are_not_deeds(self):
        data = player(started=False)
        owned = copy.deepcopy(data['inventory'])
        for _ in range(3):
            data, ok = start_quest_pure(data, QUEST_ID, QUEST_DATA)
            self.assertTrue(ok)
            journal(data)
            data = migrate_loaded_data(json.loads(json.dumps(data)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual({k: v for k, v in data['inventory'].items() if v}, owned)
        self.assertEqual(data['quest_action_proofs'], [])

    def test_unstarted_card_previews_only_opening_without_earning_it(self):
        data = player(started=False)
        before = copy.deepcopy(data)
        self.assertEqual(quest_journal_view_rows_pure(data, QUEST_ID, QUEST_DATA), (
            dict(stage=1, lines=LINES, completed=False, current=False),
        ))
        self.assertEqual(journal(data), ())
        for quest_id in ('murder_mystery', 'cooks_assistant', 'missing_quest'):
            self.assertEqual(quest_journal_view_rows_pure(data, quest_id, QUEST_DATA), ())
        self.assertEqual(quest_journal_view_rows_pure(data, QUEST_ID, {}), ())
        self.assertEqual(data, before)

    def test_owned_custody_and_all_carried_view_deltas(self):
        cases = [({}, {}, {}, {'Commorb v2': 1}),
                 ({'Commorb': 1}, {}, {}, {'Commorb': 0, 'Commorb v2': 1}),
                 ({'Commorb': 1}, {'a': {'Commorb': 1}}, {}, {'Commorb': 0, 'Commorb v2': 1}),
                 ({'Commorb': 1}, {'a': {'Commorb': 1}, 'b': {'Commorb': 1}}, {}, {'Commorb': 0, 'Commorb v2': 1}),
                 ({}, {'stale': {'Commorb': 1}}, {}, {'Commorb v2': 1}),
                 ({'Commorb v2': 1}, {}, {}, {'Commorb v2': 1}),
                 ({'Commorb': 3}, {'a': {'Commorb': 3}}, {'a': {'Commorb': 2}}, {'Commorb': 2, 'Commorb v2': 1}),
                 ({'Commorb': 3, 'Commorb v2': 4}, {'a': {'Commorb': 3, 'Commorb v2': 4}},
                  {'a': {'Commorb': 3, 'Commorb v2': 4}}, {'Commorb': 3, 'Commorb v2': 4})]
        for stock, views, expected_views, expected_stock in cases:
            with self.subTest(stock=stock, views=views):
                data = player()
                data['inventory'].update(stock)
                full = {f'Unrelated {i}': 1 for i in range(28)}
                data['inventory'].update(full)
                data['carried_inventory'] = dict(views, full=full.copy())
                self.assertTrue(transaction.apply_slug_menace_opening_pure(data))
                self.assertEqual(data['inventory'], dict(full, Coins=37, **expected_stock))
                self.assertEqual(data['carried_inventory'], dict(expected_views, full=full))

    def test_invalid_orb_counts_refuse_without_any_mutation(self):
        for name in ('Commorb', 'Commorb v2'):
            for count in (-1, True, False, 1.5, '1', None):
                with self.subTest(name=name, count=count):
                    data = player()
                    data['inventory'].update({'Commorb': 2, 'Commorb v2': 1, name: count})
                    before = copy.deepcopy(data)
                    self.assertFalse(transaction.apply_slug_menace_opening_pure(data))
                    self.assertEqual(data, before)
                    self.assertEqual(advance(data), (before, False, False))

    def test_order_execution_and_prefilled_proofs_never_bypass_scan(self):
        for proofs in ([], list(ACTIONS[:3]), [ACTIONS[3]], list(ACTIONS)):
            data = player()
            data['inventory']['Commorb v2'] = 1
            data['quest_action_proofs'] = proofs
            observed = []

            def observe(name, real):
                def call(candidate, prefix):
                    observed.append((name, tuple(prefix)))
                    return real(candidate, prefix)
                return call
            from contextlib import ExitStack
            with ExitStack() as stack:
                for name in DEEDS:
                    stack.enter_context(patch.object(transaction, name, side_effect=observe(name, getattr(transaction, name))))
                result, ok, completed = advance(data)
            self.assertTrue(ok)
            self.assertFalse(completed)
            self.assertEqual(observed, [(name, ACTIONS[:i]) for i, name in enumerate(DEEDS)])
            self.assertEqual(result['quests'][QUEST_ID]['progress'], 2)

    def test_possession_and_all_saved_proofs_cannot_supply_local_deeds(self):
        data = player()
        data['inventory']['Commorb v2'] = 1
        data['quest_action_proofs'] = list(ACTIONS)
        before = copy.deepcopy(data)
        with patch.object(transaction, '_perform_commission_pure', return_value=True), \
             patch.object(transaction, '_perform_referral_pure', return_value=True), \
             patch.object(transaction, '_perform_mayor_conversation_pure', return_value=True), \
             patch.object(transaction, '_perform_mayor_scan_pure', wraps=transaction._perform_mayor_scan_pure) as scan:
            self.assertEqual(advance(data), (before, False, False))
            scan.assert_called_once()
        self.assertEqual(data, before)

    def test_scan_prefix_and_owned_orb_required(self):
        for prefix in ([], list(ACTIONS[:1]), list(ACTIONS[:2]), list(ACTIONS), list(reversed(ACTIONS[:3]))):
            data = player()
            data['inventory']['Commorb v2'] = 1
            before = copy.deepcopy(data)
            self.assertFalse(transaction._perform_mayor_scan_pure(data, prefix))
            self.assertEqual(data, before)
        self.assertFalse(transaction._perform_mayor_scan_pure(player(), list(ACTIONS[:3])))
        data = player()
        data['inventory']['Commorb v2'] = 1
        self.assertEqual(transaction._perform_mayor_scan_pure(data, list(ACTIONS[:3])), 'two life forms')

    def test_each_deed_refusal_rolls_back_items_views_and_proofs(self):
        for name in DEEDS:
            for proofs in ([], list(ACTIONS)):
                data = player()
                data['inventory']['Commorb'] = 1
                data['carried_inventory'] = {'a': {'Commorb': 1}}
                data['quest_action_proofs'] = proofs
                before = copy.deepcopy(data)
                with patch.object(transaction, name, return_value=False):
                    self.assertFalse(transaction.apply_slug_menace_opening_pure(data))
                    self.assertEqual(advance(data), (before, False, False))
                self.assertEqual(data, before)

    def test_only_performed_opening_changes_on_success(self):
        for progress in (0, 1):
            data = player(progress)
            data['quest_action_proofs'] = ['unrelated.proof']
            before = copy.deepcopy(data)
            result, ok, completed = advance(data)
            self.assertEqual((ok, completed), (True, False))
            expected = copy.deepcopy(before)
            expected['inventory']['Commorb v2'] = 1
            expected['quest_action_proofs'] = sorted([*ACTIONS, 'unrelated.proof'])
            expected['quests'][QUEST_ID]['progress'] = 2
            self.assertEqual(result, expected)
            self.assertEqual(data, before)
            self.assertTrue(journal(result)[0]['completed'])
            self.assertFalse(journal(result)[1]['completed'])
            self.assertEqual(advance(result), (result, False, False))

    def test_legacy_progress_completed_and_repeated_opening_no_regrant(self):
        for progress, completed in [(2, False), (6, False), (8, True)]:
            data = player(progress, completed=completed)
            data['inventory']['Commorb'] = 2
            before = copy.deepcopy(data)
            self.assertFalse(transaction.apply_slug_menace_opening_pure(data))
            row = journal(data)[0]
            self.assertEqual(row, dict(stage=1, completed=False, current=False, lines=source.LEGACY_OPENING_JOURNAL))
            self.assertEqual(data, before)
        self.assertFalse(transaction.apply_slug_menace_opening_pure(player(started=False)))

    def test_later_supply_shortages_and_generic_deed_blockers_remain(self):
        self.assertEqual(quest_current_stage_blockers_pure(player(), QUEST_ID, QUEST_DATA), ())
        for stage, shortage in [(5, 'Swamp paste'), (6, 'Rune essence')]:
            data = player(stage)
            blockers = str(quest_current_stage_blockers_pure(data, QUEST_ID, QUEST_DATA))
            self.assertIn(shortage, blockers)
            data['inventory'].update({'Swamp paste': 1, 'Chisel': 1, 'Pure essence': 5, 'Omni-talisman': 1})
            blockers = str(quest_current_stage_blockers_pure(data, QUEST_ID, QUEST_DATA))
            self.assertIn(f'Complete The Slug Menace stage {stage} objective', blockers)
            self.assertEqual(advance(data), (data, False, False))
