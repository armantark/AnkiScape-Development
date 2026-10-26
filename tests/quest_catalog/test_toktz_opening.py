"""Ordered TokTz opening, source boundaries and atomic inventory custody."""

import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA, QUEST_ITEM_IMAGES, QUEST_REWARD_ITEM_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest import catalog, serializers
from ankiscape.data.quest.contract import QuestStageRequirementCleanup
from ankiscape.data.quest import toktz_opening as source
from ankiscape.data.quest.toktz_opening import (
    QUEST_ID, TABLET, GUIDE, PROOFS, SERVICES, INTERACTIONS, COMPLETED_LINES,
    PENDING_LINES, RECOVERY, INVALID, LEGACY_LINE, RECOVERY_INSTRUCTION, RECOVERY_MESSAGE,
)
from ankiscape.data.quest_action_proof_data import QUEST_ACTION_PROOF_RULES, QUEST_ACTION_PROOF_AUDIT_SOURCES
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, can_start_quest_pure, can_attempt_quest_review_pure,
    quest_current_stage_pure, quest_current_stage_blockers_pure, quest_journal_rows_pure,
)
from ankiscape.logic_pure.quest import toktz_opening as opening
from ankiscape.logic_pure.quest import journal as journal_projection

GATES = {'attack': 40, 'mining': 41, 'crafting': 43, 'strength': 45, 'construction': 50}


def player(prefix=0, progress=0, started=True, completed=False):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data['inventory'] = {'Coins': 37}
    data['toolbelt'] = {}
    for skill, level in GATES.items():
        data[skill + '_level'] = level
        data[skill + '_exp'] = EXP_TABLE[level]
    data['quests'][QUEST_ID] = dict(started=started, progress=progress, completed=completed)
    data['current_quest'] = QUEST_ID
    data['quest_action_proofs'] = sorted(PROOFS[:prefix])
    if prefix >= 2:
        data['inventory'][TABLET] = 1
    return data


def advance(data, **kwargs):
    return apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA, **kwargs)


def journal(data):
    return quest_journal_rows_pure(data, QUEST_ID, QUEST_DATA)


def reload_player(data):
    return migrate_loaded_data(json.loads(json.dumps(data)), ORE_DATA, ITEM_DEFINITIONS)


def blockers(data):
    return quest_current_stage_blockers_pure(data, QUEST_ID, QUEST_DATA)


def apply_event(data, event):
    return opening.apply_toktz_opening_review_pure(data, QUEST_ID, blockers(data), event)


def opening_snapshot(data):
    return {key: copy.deepcopy(data.get(key)) for key in (
        'inventory', 'quest_action_proofs', 'quests', 'quest_points', 'pending_skill_exp_rewards',
    )}, journal(data)


class ToktzCatalogTest(unittest.TestCase):
    def test_current_stage_projection_preserves_progression_import_and_boundaries(self):
        self.assertIs(quest_current_stage_pure, journal_projection.quest_current_stage_pure)
        final_stage = QUEST_DATA[QUEST_ID]['stages']
        cases = (
            (False, False, 0, 0), (True, False, 0, 1),
            (True, False, 1, 1), (True, False, 2, 2),
            (True, False, 99, final_stage), (True, True, 2, final_stage),
        )
        for started, completed, progress, expected in cases:
            with self.subTest(started=started, completed=completed, progress=progress):
                data = player(started=started, completed=completed, progress=progress)
                before = copy.deepcopy(data)
                self.assertEqual(quest_current_stage_pure(data, QUEST_ID, QUEST_DATA), expected)
                self.assertEqual(data, before)
        self.assertEqual(quest_current_stage_pure(player(), 'absent_quest', QUEST_DATA), 0)

    def test_source_pins_excerpts_and_qualifications(self):
        packet = json.loads(Path(source.__file__).with_name('toktz_opening_sources.json').read_text())
        rows = packet['sources']
        self.assertEqual(set(rows), set('W S G R T RT RG D DS DI C SK II FG FS'.split()))
        self.assertEqual(rows['W']['sha256'], '188d9842e6260fac9e122047e980c7ffc6d533ecd342e46244110e92a314279c')
        pins = {
            'W': ('6493266', '2012-10-29T18:11:47Z', '188d9842e6260fac9e122047e980c7ffc6d533ecd342e46244110e92a314279c'),
            'S': ('5512319', '2012-04-19T12:30:49Z', 'ac63f7a1268dd4f87e51f65b1883957f5866870f0a02d393e5f741d8874a72f2'),
            'G': ('6154887', '2012-08-28T02:30:28Z', '0661accf376fead8941093803df33d0c3fea3ac96564e2e2bc7f60ee33b7f10c'),
            'R': ('Wayback 20121103195426', '2012-11-03T19:54:26Z', 'a7afd02516aaccea71c8f11ca04842265f7f946c6fa94c44e95c38b3726fc9fa'),
            'T': ('Wayback 20120425170926', '2012-04-25T17:09:26Z', '8f0127e949cbcc205f4657716d07eed252cd976622bc4bb15eb2a943acb00ad8'),
            'RT': ('Wayback 20090418134630', '2009-04-18T13:46:30Z', 'a5fecbfd5de5a00ab4ac4910fdfdc0c9723eb9d59a7566406e24494a73996f4d'),
            'RG': ('Wayback 20090418084844', '2009-04-18T08:48:44Z', 'c08eea28dcd439e4cb5e8bae1afca294bca04acdbf73f38765e18879e8585e54'),
            'D': ('ba45bbc92399fe303bc1c054a72040311b52ed77 (supplying commit); inspected HEAD 517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed', '2026-07-18T09:07:18Z supply; modern reconstruction', '03b02b3633d19bf8bd124a8171fc737eea426245219fdd0fe7cbb2a4a27e376f'),
            'DS': ('ba45bbc92399fe303bc1c054a72040311b52ed77 (supplying commit); inspected HEAD 517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed', '2026-07-18T09:07:18Z supply; modern reconstruction', 'b5c91be57394ba233c1d9510f8359cfe040927fc09ba0d77a35baa10e88e7c80'),
            'DI': ('ba45bbc92399fe303bc1c054a72040311b52ed77 (supplying commit); inspected HEAD 517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed', '2026-07-18T09:07:18Z supply; modern reconstruction', 'c8c25fb707789614d3f7244b83e0d2c93da704d3d6f17d0c0b5aa32ad1622bed'),
            'C': ('727/728/729/736/741/742; OpenRS2 309/310/311/313/1468/544', '2012-07-24 / 2012-08-01 / 2012-08-11 / 2012-10-09 / 2012-11-04 / 2012-11-07; UTC times not stated', '8c6aa436c213208962b291a530822d716349b2a31d82498e927d927f351f0444'),
            'SK': ('6555554', '2012-11-14T19:46:20Z', '6776376d2c748749f0b1643aa789e33cd938d9d7099d7a43b26985f29b45686e'),
            'II': ('6550327', '2012-11-12T23:11:13Z', 'd7e9b9ebbd5094deddb74bd82aff1fb72fd7f8de0ef8973d75b9ee1f91b745c8'),
            'FG': ('6420572', '2012-10-15T12:28:17Z', '8c417118fdf8f0a63597613bb0cb9eaae2318a6b63690b757e43ff34c7c1e73c'),
            'FS': ('6419415', '2012-10-15T11:17:37Z', '9b0d1ccb86a18f8d0bc9e0f3eff29409c4f666bbf4c7bca8c63bbca8a86d2730'),
        }
        for key, row in rows.items():
            self.assertTrue(all(row.get(field) for field in ('title', 'url', 'saved_body', 'original_numbered_excerpts')))
            self.assertEqual((row['revision'], row['timestamp'], row['sha256']), pins[key])
        self.assertIn('second bookcase from the south', rows['W']['original_numbered_excerpts']['63'])
        self.assertIn('modern restoration', packet['qualifications']['restoration'])
        self.assertIn('No tablet weight selected', packet['qualifications']['weight'])
        self.assertIn('350–351', packet['qualifications']['retention'])
        self.assertEqual(set(packet['checked_not_stated']), {'original_dialogue', 'proof_timing', 'duplicate_policy', 'replacement_policy', 'bank_routing', 'transaction_internals'})

    def test_item_identities_icons_and_saved_binary_hashes(self):
        expected = ((TABLET, 13243, 'stone_tablet.png', '1036d1a48f8d02496ee9c710255cf8a8675ed5f002c8ce30462fca555bbd8f90'),
                    (GUIDE, 13244, 'tourist_guide.png', 'c94c91d990f3f50f77b151060780b5f126244539cfdfdc1178900f95b09ec693'))
        definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for name, item_id, filename, digest in expected:
            item = definitions[name]
            self.assertEqual((item.display_name, item.source_item_id, item.stackable, item.tradeable, item.equipment_slot), (name, item_id, False, False, None))
            path = Path(item.asset_path)
            self.assertEqual(path.name, filename)
            self.assertTrue(path.is_absolute())
            self.assertEqual(str(path), QUEST_ITEM_IMAGES[name])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
            self.assertIsNot(QUEST_REWARD_ITEM_DATA[name], source.OPENING_ITEMS[name])
            self.assertNotIn('weight', source.OPENING_ITEMS[name])
        aliases = [item.storage_key for item in definitions.values() if item.source_item_id == 13243]
        self.assertEqual(aliases, [TABLET])
        assets = json.loads(Path(source.OPENING_IMAGES[TABLET]).with_name('provenance.json').read_text())
        self.assertEqual({r['asset_candidate']['timestamp'] for r in assets}, {'2011-11-29T06:02:58Z', '2011-11-30T03:45:58Z'})
        for record in assets:
            self.assertEqual(record['file_description']['original_numbered_excerpts']['1'].split('|')[0], '{{Inventory license')
            self.assertEqual(hashlib.sha256(Path(record['destination']).read_bytes()).hexdigest(), record['asset_candidate']['sha256'])

    def test_baseline_assembly_preserves_every_later_field(self):
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row['id'] == QUEST_ID)
        original_cleanup = (QuestStageRequirementCleanup(stage=1, remove_required_inventory=('A crush weapon',)),)
        journals = dict(catalog.QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID)
        journals.pop(QUEST_ID)
        with patch.dict(catalog.QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID, {QUEST_ID: original_cleanup}), patch.object(catalog, 'QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID', journals):
            baseline = catalog._quest_with_stage_requirements(catalog._quest_from_catalog(generated), generated)
        with patch.object(serializers, 'QUESTS', (baseline,)):
            before = serializers.quests_as_dict()[QUEST_ID]
        actual = copy.deepcopy(QUEST_DATA[QUEST_ID])
        self.assertEqual(actual['stage_requirements'][1:], before['stage_requirements'][1:])
        self.assertEqual({k: v for k, v in actual['journal_stages'].items() if k > 1}, {k: v for k, v in before['journal_stages'].items() if k > 1})
        actual['stage_requirements'] = before['stage_requirements']
        actual['journal_stages'] = before['journal_stages']
        self.assertEqual(actual, before)
        self.assertEqual(len(before['journal_stages']), 7)
        self.assertEqual(actual['stages'], before['stages'])

    def test_exact_cleanup_and_ordered_bindings(self):
        row = QUEST_DATA[QUEST_ID]['stage_requirements'][0]
        self.assertEqual(row['required_actions'], (PROOFS[-1],))
        for key in ('required_inventory', 'required_tools', 'consumed_inventory', 'produced_inventory'):
            self.assertEqual(row[key], {})
        for key in ('auto_actions', 'required_routes', 'combat_encounters', 'required_skills'):
            self.assertEqual(row[key], ())
        self.assertEqual(QUEST_DATA[QUEST_ID]['start_inventory'], {})
        for index, service in enumerate(SERVICES):
            self.assertEqual(QUEST_ACTION_PROOF_RULES['quest_service', service], (PROOFS[:index], (PROOFS[index],)))
            self.assertNotIn(('quest_service', service), QUEST_ACTION_PROOF_AUDIT_SOURCES)
        self.assertNotIn('npc_id', INTERACTIONS[3])
        self.assertEqual(INTERACTIONS[0]['npc_ids'], (7746, 7747, 7748))

    def test_earned_base_level_boundaries_and_no_prerequisites(self):
        quest = QUEST_DATA[QUEST_ID]
        self.assertEqual(quest['required_quests'], ())
        self.assertEqual({row['skill_id']: row['level'] for row in quest['required_skills']}, GATES)
        self.assertTrue(can_start_quest_pure(player(started=False), QUEST_ID, QUEST_DATA))
        for skill, level in GATES.items():
            data = player(started=False)
            data[skill + '_level'] = level - 1
            data['skilling_current_levels'][skill] = level
            data['combat_current_levels'][skill] = level
            before = copy.deepcopy(data)
            self.assertFalse(can_start_quest_pure(data, QUEST_ID, QUEST_DATA), skill)
            self.assertEqual(advance(data), (data, False, False))
            self.assertEqual(data, before)


class ToktzTransactionTest(unittest.TestCase):
    def assert_refuses(self, data, event):
        before = copy.deepcopy(data)
        result, success = apply_event(data, event)
        self.assertIs(result, data)
        self.assertFalse(success)
        self.assertEqual(data, before)

    def test_five_real_reviews_reload_and_exact_deltas(self):
        data = reload_player(player(started=False))
        for index in range(5):
            data = reload_player(data)
            before = copy.deepcopy(data)
            self.assertTrue(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
            result, success, completed, refusal = advance(data, include_clue_refusal=True)
            self.assertEqual((success, completed, refusal), (True, False, ''))
            self.assertEqual(data, before)
            expected = dict(before['inventory'])
            if index == 1:
                expected[TABLET] = 1
            if index == 4:
                expected[GUIDE] = 1
            self.assertEqual(result['inventory'], expected)
            self.assertEqual(result['quest_action_proofs'], sorted(PROOFS[:index + 1]))
            self.assertEqual(result['quests'][QUEST_ID], dict(started=True, progress=2 if index == 4 else 1, completed=False))
            self.assert_unchanged_rewards(before, result)
            snap = opening_snapshot(result)
            data = reload_player(result)
            self.assertEqual(opening_snapshot(data), snap)
        self.assertEqual(advance(data), (data, False, False))

    def assert_unchanged_rewards(self, before, after):
        for key in before:
            if key.endswith('_exp') or key in ('quest_points', 'pending_skill_exp_rewards', 'quest_route_states', 'quest_combat_encounters', 'quest_unlocks'):
                self.assertEqual(after.get(key), before[key], key)

    def test_order_incomplete_events_and_preparation_are_inert(self):
        for index in range(5):
            data = player(index)
            before = copy.deepcopy(data)
            event = opening.toktz_opening_next_event_pure(data, QUEST_ID)
            self.assertEqual(data, before)
            self.assert_refuses(data, None)
            self.assert_refuses(data, {})
            self.assert_refuses(data, dict(event, completed=False))
            self.assert_refuses(data, dict(event, service_id=SERVICES[(index + 1) % 5]))
            result, ok = apply_event(data, event)
            self.assertTrue(ok)
            self.assert_refuses(result, event)
        data = player(4)
        event = opening.toktz_opening_next_event_pure(data, QUEST_ID)
        self.assert_refuses(data, dict(event, object_id=31208))
        self.assert_refuses(data, dict(event, option='Read'))

    def test_any_one_guard_suffices_and_each_interaction_records_once(self):
        for npc_id in (7746, 7747, 7748):
            data = player()
            event = opening.toktz_opening_next_event_pure(data, QUEST_ID)
            event['npc_id'] = npc_id
            result, ok = apply_event(data, event)
            self.assertTrue(ok)
            self.assertEqual(result['quest_action_proofs'], [PROOFS[0]])
            self.assertEqual(result['quests'][QUEST_ID]['progress'], 1)
        data = player()
        recorder = opening.record_runtime_quest_action_proofs_pure
        with patch.object(opening, 'record_runtime_quest_action_proofs_pure', wraps=recorder) as record:
            for index in range(5):
                data, ok, _ = advance(data)
                self.assertTrue(ok)
                self.assertEqual(record.call_count, index + 1)

    def test_nonprefix_and_all_proofs_stage_one_refuse(self):
        for proofs in ((PROOFS[1],), (PROOFS[0], PROOFS[3]), PROOFS):
            data = player()
            data['quest_action_proofs'] = list(proofs)
            self.assertEqual(opening.toktz_opening_phase_pure(data, QUEST_ID), INVALID)
            self.assertFalse(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
            self.assertFalse(opening.toktz_opening_review_ready_pure(data, QUEST_ID, blockers(data)))
            self.assert_refuses(data, dict(INTERACTIONS[-1], completed=True))
            self.assertEqual(advance(data), (data, False, False))
            self.assertEqual(journal(data)[0]['lines'], (LEGACY_LINE,))

    def test_possession_never_invents_deeds_and_preowned_copies_never_multiply(self):
        for quantity in (1, 3):
            data = player()
            data['inventory'].update({TABLET: quantity, GUIDE: quantity, 'Stone tablet': 7})
            inventory = dict(data['inventory'])
            for index in range(5):
                data, ok, done = advance(data)
                self.assertEqual((ok, done), (True, False))
                self.assertEqual(data['inventory'], inventory)
                self.assertEqual(data['quest_action_proofs'], sorted(PROOFS[:index + 1]))
            self.assert_unchanged_rewards(player(), data)

    def test_unique_grant_rejects_malformed_quantities(self):
        for item, prefix in ((TABLET, 1), (GUIDE, 4)):
            for value in (-1, True, False, 1.0, '1', None, [], {}):
                data = player(prefix)
                data['inventory'][item] = value
                before = copy.deepcopy(data)
                self.assertEqual(advance(data), (data, False, False))
                self.assertEqual(data, before)
            data = player(prefix)
            data['inventory'][item] = 0
            result, ok, _ = advance(data)
            self.assertTrue(ok)
            self.assertEqual(result['inventory'][item], 1)

    def test_grant_failures_and_bad_postconditions_never_leak(self):
        for prefix in (1, 4):
            for mode in ('refuse', 'mutate_refuse', 'wrong', 'boolean', 'side_effect'):
                self.check_failed_grant(player(prefix), mode)
        data = player(2)
        del data['inventory'][TABLET]
        self.check_failed_grant(data, 'mutate_refuse')
        data = player(started=False)
        before = copy.deepcopy(data)
        with patch.object(opening, 'record_runtime_quest_action_proofs_pure', return_value=True):
            self.assertEqual(advance(data), (data, False, False))
        self.assertEqual(data, before)

    def check_failed_grant(self, data, mode):
        before = copy.deepcopy(data)

        def grant(inventory, name):
            if mode == 'refuse':
                return False
            inventory[name] = True if mode == 'boolean' else 2
            if mode == 'side_effect':
                inventory['Coins'] = 0
                inventory[name] = 1
            return mode != 'mutate_refuse'
        with patch.object(opening, '_grant_unique_opening_item_pure', side_effect=grant):
            result = advance(data)
            self.assertIs(result[0], data)
            self.assertEqual(result[1:], (False, False))
        self.assertEqual(data, before)

    def test_full_carried_packs_and_generic_tablet_do_not_block_delivery(self):
        for mode in ('casual', 'advanced'):
            data = player(1)
            data['carried_advanced_targets'] = {'mining': True} if mode == 'advanced' else {}
            data['carried_layout'] = {'mining': {'Iron ore': 28}} if mode == 'advanced' else {}
            data['inventory']['Stone tablet'] = 1
            data['inventory']['Iron ore'] = 28
            data['carried_inventory'] = {'mining': {'Iron ore': 28}}
            carried = copy.deepcopy(data['carried_inventory'])
            result, success, _ = advance(data)
            self.assertTrue(success)
            self.assertEqual(result['inventory'][TABLET], 1)
            self.assertEqual(result['inventory']['Stone tablet'], 1)
            self.assertEqual(result['carried_inventory'], carried)

    def test_unrelated_blockers_are_never_bypassed(self):
        data = player(1)
        event = opening.toktz_opening_next_event_pure(data, QUEST_ID)
        for kind in ('required_inventory', 'required_skill', 'choice', 'route', 'combat', 'required_action'):
            bad = dict(kind=kind, action_id='unrelated')
            self.assertFalse(opening.toktz_opening_review_ready_pure(data, QUEST_ID, (*blockers(data), bad)))
            result, success = opening.apply_toktz_opening_review_pure(data, QUEST_ID, (*blockers(data), bad), event)
            self.assertIs(result, data)
            self.assertFalse(success)

    def test_recovery_is_one_review_no_proof_then_librarian_retains_tablet(self):
        data = player(2, progress=1)
        del data['inventory'][TABLET]
        data = reload_player(data)
        self.assertNotIn(TABLET, {k: v for k, v in data['inventory'].items() if v})
        self.assertEqual(opening.toktz_opening_phase_pure(data, QUEST_ID), RECOVERY)
        self.assertEqual(opening.toktz_opening_message_pure(data, QUEST_ID), RECOVERY_MESSAGE)
        self.assertEqual(journal(data)[0]['lines'], COMPLETED_LINES[:2] + (RECOVERY_INSTRUCTION,))
        before = copy.deepcopy(data)
        result, ok, done = advance(data)
        self.assertEqual((ok, done), (True, False))
        self.assertEqual(result['quest_action_proofs'], before['quest_action_proofs'])
        self.assertEqual(result['quests'], before['quests'])
        self.assertEqual(result['inventory'][TABLET], 1)
        data = reload_player(result)
        self.assertEqual(opening_snapshot(data), opening_snapshot(result))
        result, ok, _ = advance(data)
        self.assertTrue(ok)
        self.assertEqual(result['quest_action_proofs'], sorted(PROOFS[:3]))
        self.assertEqual(result['inventory'][TABLET], 1)

    def test_journal_every_phase_endpoint_and_past_custody(self):
        data = player()
        for index in range(5):
            self.assertEqual(journal(data)[0]['lines'], COMPLETED_LINES[:index] + (PENDING_LINES[index],))
            self.assertEqual(opening.toktz_opening_message_pure(data, QUEST_ID), COMPLETED_LINES[index])
            before = copy.deepcopy(data)
            journal(data)
            self.assertEqual(data, before)
            data, ok, _ = advance(data)
            self.assertTrue(ok)
        self.assertEqual(journal(data)[0]['lines'], COMPLETED_LINES)
        self.assertTrue(journal(data)[0]['completed'])
        self.assertFalse(journal(data)[0]['current'])
        data['inventory'].pop(GUIDE)
        data['inventory'].pop(TABLET)
        self.assertEqual(journal(reload_player(data))[0]['lines'], COMPLETED_LINES)
        self.assertIsNone(opening.toktz_opening_phase_pure(data, QUEST_ID))
        self.assertEqual(opening.toktz_opening_message_pure(data, QUEST_ID), '')

    def test_legacy_progress_items_proofs_preserved_on_load(self):
        for completed, progress in ((False, 2), (False, 5), (True, 8)):
            for prefix in (0, 1, 3, 4):
                data = player(prefix, progress=progress, completed=completed)
                data['inventory'].update({GUIDE: 2, TABLET: 3})
                data = reload_player(data)
                before = opening_snapshot(data)
                loaded = reload_player(data)
                self.assertEqual(opening_snapshot(loaded), before)
                self.assertEqual(journal(loaded)[0], dict(stage=1, lines=(LEGACY_LINE,), current=False, completed=False))
                self.assertIsNone(opening.toktz_opening_phase_pure(loaded, QUEST_ID))
                self.assertEqual(advance(loaded), (loaded, False, False))

    def test_no_post_library_recovery_or_load_grants_and_outside_identity(self):
        for prefix in (3, 4):
            data = player(prefix)
            del data['inventory'][TABLET]
            loaded = reload_player(data)
            self.assertEqual(loaded['inventory'].get(TABLET, 0), 0)
            self.assertEqual(opening.toktz_opening_phase_pure(loaded, QUEST_ID), SERVICES[prefix])
        for stage in (0, 1):
            self.assertEqual(opening.toktz_opening_phase_pure(player(progress=stage), QUEST_ID), SERVICES[0])
        data = player()
        row = dict(stage=1, lines=('unchanged',))
        self.assertIs(opening.toktz_opening_journal_row_pure(data, 'other', row), row)
        self.assertIsNone(opening.toktz_opening_phase_pure(data, 'other'))
