"""Witch's House: real earned deeds, custody, combat and qualified identities."""

import ast
import copy
import hashlib
import json
from pathlib import Path
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA, QUEST_ITEM_IMAGES, EXP_TABLE,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest.witchs_house import (
    QUEST_ID, DIARY, DOOR_KEY, MAGNET, BACKROOM_KEY, BALL, LEATHER_GLOVES,
    CHEESE, TAKE_DIARY, READ_DIARY, ENTER_BASEMENT, TAKE_GLOVES, PASS_GATE,
    TAKE_MAGNET, TAKE_KEY, TAKE_BALL, INSULATING_GLOVES, EXPERIMENTS, RESUME_KEY,
)
from ankiscape.data.quest_data import quest_reward_items_as_dict
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic.shop_logic import apply_shop_buy_pure
from ankiscape.logic_pure.logic_pure_equipment import equip_item_pure
from ankiscape.logic_pure.logic_pure_quest import (
    start_quest_pure, apply_quest_progress_pure, apply_quest_combat_encounter_pure,
    quest_current_stage_blockers_pure, quest_journal_rows_pure,
)
from ankiscape.logic_pure.quest.witchs_house import (
    witchs_house_stage_rows_pure, witchs_house_extra_blockers_pure,
    witchs_house_worn_insulation_pure,
)
from ankiscape.logic_pure.quest.review_services import (
    quest_review_service_phase_pure, quest_review_service_ready_pure,
    apply_quest_review_service_pure,
)

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'data/quest/evidence/witchs_house'
ENTER = "Enter the Witch's house with the door key"
MOUSE = "Use cheese on the mouse hole and attach the magnet to the mouse"
PATROL = "Avoid the witch's patrol through the house"
SHED = "Unlock the Witch's shed door with the backroom key"
RETURN = "Return the ball to Harvey"
ACTION_ORDER = (ENTER, TAKE_DIARY, READ_DIARY, ENTER_BASEMENT, TAKE_GLOVES,
                PASS_GATE, TAKE_MAGNET, MOUSE, PATROL, TAKE_KEY, SHED, TAKE_BALL, RETURN)


def player_at(stage=None, proofs=()):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player['current_quest'] = QUEST_ID
    if stage is not None:
        player['quests'][QUEST_ID] = dict(started=True, completed=False, progress=stage)
    player['quest_action_proofs'] = list(proofs)
    return player


def progress(player, quest_data=QUEST_DATA):
    return apply_quest_progress_pure(player, QUEST_ID, quest_data)


def blockers(player, quest_data=QUEST_DATA):
    return quest_current_stage_blockers_pure(player, QUEST_ID, quest_data)


def wear_leather(player):
    inventory, equipment, ok = equip_item_pure(
        LEATHER_GLOVES, player['inventory'], player['equipment'], EQUIPMENT_DATA,
    )
    if not ok:
        raise AssertionError('Basement gloves must be available to equip')
    player.update(inventory=inventory, equipment=equipment)
    return player


def buy_cheese(player):
    player['inventory']['Coins'] = 8
    player, result = apply_shop_buy_pure(player, 'wydins_food_store', 'wydins_food_store:3:1985')
    if not result['allowed']:
        raise AssertionError(result)
    return player


def train_for_experiments(player):
    for skill in ('attack', 'strength', 'defense', 'constitution'):
        player[f'{skill}_level'] = 60
        player[f'{skill}_exp'] = EXP_TABLE[59]
    return player


def fight_to_completion(player, encounter_id):
    for _ in range(300):
        player, ok, result = apply_quest_combat_encounter_pure(
            player, QUEST_ID, QUEST_DATA, encounter_id, rng=lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
        )
        if not ok:
            raise AssertionError(result)
        if result.get('quest_combat_completed'):
            return player
    raise AssertionError(f'Encounter failed to complete: {encounter_id}')


def finished_fights(player):
    """Adversarial fixture only; ordinary route uses the actual combat engine."""
    player['quest_combat_encounters'][QUEST_ID] = [eid for eid, _ in EXPERIMENTS]
    return player


class WitchsHouseRouteTest(unittest.TestCase):
    def test_ordinary_route_separates_pickup_read_wearing_combat_and_single_reward(self):
        player = buy_cheese(player_at())
        self.assertFalse(any(player['inventory'].get(name) for name in (DIARY, DOOR_KEY, MAGNET, BALL, LEATHER_GLOVES)))
        player, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player['quests'][QUEST_ID]['progress'], 0)
        self.assertEqual(player['quest_action_proofs'], [])
        seen = []
        for stage in range(1, 12):
            if stage == 6:
                wear_leather(player)
            prior = set(player['quest_action_proofs'])
            player, ok, complete = progress(player)
            self.assertTrue(ok, stage)
            self.assertFalse(complete)
            self.assertEqual(player['quests'][QUEST_ID]['progress'], stage + 1)
            added = set(player['quest_action_proofs']) - prior
            seen.extend(action for action in ACTION_ORDER if action in added)
            self.assert_stage_custody(player, stage)
        self.assertEqual(seen, list(ACTION_ORDER[:-2]))
        self.assertEqual(player['inventory'][MAGNET], 1)
        self.assertEqual(player['equipment']['hands'], LEATHER_GLOVES)
        self.assertEqual(player['inventory'][DOOR_KEY], 1)
        self.assertEqual(player['inventory'][BACKROOM_KEY], 1)
        train_for_experiments(player)
        self.assert_refused(player)
        for remaining, (eid, _) in zip((3, 2, 1, 0), EXPERIMENTS):
            player = fight_to_completion(player, eid)
            self.assertEqual(player['quests'][QUEST_ID]['progress'], 12)
            self.assertEqual(len(blockers(player)), remaining)
        player, ok, complete = progress(player)
        self.assertTrue(ok)
        self.assertEqual(player['quests'][QUEST_ID]['progress'], 13)
        self.assertFalse(player['inventory'].get(BALL))
        player, ok, complete = progress(player)
        self.assertTrue(ok)
        self.assertEqual(player['inventory'][BALL], 1)
        self.assertIn(TAKE_BALL, player['quest_action_proofs'])
        xp, points = player['constitution_exp'], player['quest_points']
        player, ok, complete = progress(player)
        self.assertTrue(ok and complete)
        self.assertEqual(player['quests'][QUEST_ID]['progress'], 15)
        self.assertEqual(player['inventory'][BALL], 0)
        self.assertEqual(player['constitution_exp'] - xp, 6325)
        self.assertEqual(player['quest_points'] - points, 4)
        self.assertEqual(player['pending_skill_exp_rewards'], {})
        self.assertEqual(set(player['quest_action_proofs']), set(ACTION_ORDER))
        self.assert_refused(player)

    def assert_stage_custody(self, player, stage):
        if stage == 3:
            self.assertEqual(player['inventory'][DIARY], 1)
            self.assertNotIn(READ_DIARY, player['quest_action_proofs'])
        if stage == 4:
            self.assertEqual(player['inventory'][DIARY], 1)
        if stage == 6:
            self.assertFalse(player['inventory'].get(MAGNET))
        if stage == 8:
            self.assertEqual(player['inventory'][CHEESE], 0)

    def assert_refused(self, player, quest_data=QUEST_DATA):
        original = copy.deepcopy(player)
        data, ok, completed = progress(player, quest_data)
        self.assertFalse(ok or completed)
        self.assertEqual(data, original)
        self.assertEqual(player, original)

    def test_inventory_diary_only_nonconsuming_read_and_proof_survives_removal(self):
        for location in ('none', 'equipment', 'toolbelt', 'carried_inventory'):
            player = player_at(4)
            if location != 'none':
                player[location] = {'hands': DIARY} if location == 'equipment' else {DIARY: 1}
            self.assert_refused(player)
        player = player_at(4)
        player['inventory'][DIARY] = 1
        player, ok, _ = progress(player)
        self.assertTrue(ok)
        self.assertEqual(player['inventory'][DIARY], 1)
        del player['inventory'][DIARY]
        player['quests'][QUEST_ID]['progress'] = 10
        player, ok, _ = progress(player)
        self.assertTrue(ok)
        self.assertEqual(player['inventory'][BACKROOM_KEY], 1)

    def test_fountain_requires_prior_read_never_same_step_or_possession_credit(self):
        for proofs in ((), (TAKE_DIARY,), (PASS_GATE,), ('Read a diary',)):
            player = player_at(10, proofs)
            player['inventory'][DIARY] = 1
            self.assert_refused(player)
        custom = copy.deepcopy(QUEST_DATA)
        row = next(r for r in custom[QUEST_ID]['stage_requirements'] if r['stage'] == 10)
        row['auto_actions'] = (READ_DIARY, TAKE_KEY)
        self.assert_refused(player_at(10), custom)
        self.assertNotIn(READ_DIARY, next(r for r in QUEST_DATA[QUEST_ID]['stage_requirements'] if r['stage'] == 10)['auto_actions'])

    def test_conditional_acquisition_suppresses_items_and_proofs_without_mutating_catalog(self):
        original = copy.deepcopy(QUEST_DATA)
        for stage, item, action, proofs in ((3, DIARY, TAKE_DIARY, ()),
                (5, LEATHER_GLOVES, TAKE_GLOVES, (READ_DIARY,)),
                (7, MAGNET, TAKE_MAGNET, (PASS_GATE,)),
                (10, BACKROOM_KEY, TAKE_KEY, (READ_DIARY,)), (13, BALL, TAKE_BALL, ())):
            with self.subTest(stage=stage):
                player = player_at(stage, proofs)
                if stage == 13:
                    finished_fights(player)
                player['inventory'][item] = 1
                player, ok, _ = progress(player)
                self.assertTrue(ok)
                self.assertEqual(player['inventory'][item], 1)
                self.assertNotIn(action, player['quest_action_proofs'])
        self.assertEqual(QUEST_DATA, original)
        rows = QUEST_DATA[QUEST_ID]['stage_requirements']
        self.assertIs(witchs_house_stage_rows_pure({}, 'other', rows), rows)

    def test_basement_leather_custody_only_and_gloves_need_not_remain_after_gate(self):
        for location, produces in (('inventory', False), ('hands', False), ('toolbelt', True), ('feet', True)):
            with self.subTest(location=location):
                player = player_at(5, (READ_DIARY,))
                if location in ('hands', 'feet'):
                    player['equipment'][location] = LEATHER_GLOVES
                else:
                    player[location][LEATHER_GLOVES] = 1
                player, ok, _ = progress(player)
                self.assertTrue(ok)
                self.assertEqual(TAKE_GLOVES in player['quest_action_proofs'], produces)
                self.assertIn(ENTER_BASEMENT, player['quest_action_proofs'])
        player = wear_leather(progress(player_at(5, (READ_DIARY,)))[0])
        player, ok, _ = progress(player)
        self.assertTrue(ok)
        player['equipment'].pop('hands')
        player, ok, _ = progress(player)
        self.assertTrue(ok)
        self.assertEqual(player['inventory'][MAGNET], 1)
        self.assertIn(TAKE_MAGNET, player['quest_action_proofs'])

    def test_exact_worn_whitelist_and_missing_read_or_gate_refuse(self):
        for name in INSULATING_GLOVES:
            player = player_at(6, (READ_DIARY,))
            player['equipment']['hands'] = name
            self.assertTrue(witchs_house_worn_insulation_pure(player))
            self.assertEqual(blockers(player), ())
            self.assertTrue(progress(player)[1])
        for location, name in (('carried_inventory', LEATHER_GLOVES),
                ('toolbelt', LEATHER_GLOVES), ('feet', LEATHER_GLOVES), ('hands', 'Ice gloves'), ('hands', 'Bronze gloves')):
            player = player_at(6, (READ_DIARY,))
            if location in ('hands', 'feet'):
                player['equipment'][location] = name
            elif location == 'carried_inventory':
                player[location] = {'quest:witchs_house': {name: 1}}
            else:
                player.setdefault(location, {})[name] = 1
            self.assert_refused(player)
            self.assertEqual(blockers(player)[0]['reason'], 'Wear insulating gloves to pass the electric gate')
            self.assertTrue(blockers(player)[0]['source'])
        player = player_at(6)
        player['equipment']['hands'] = LEATHER_GLOVES
        self.assert_refused(player)
        self.assert_refused(player_at(7, (READ_DIARY,)))
        self.assert_refused(player_at(5))

    def test_each_missing_fight_blocks_even_an_already_held_ball_and_explicit_bypass(self):
        for missing, name in EXPERIMENTS:
            player = finished_fights(player_at(13))
            player['quest_combat_encounters'][QUEST_ID].remove(missing)
            player['inventory'][BALL] = 1
            self.assert_refused(player)
            self.assertEqual(blockers(player)[0]['action_id'], missing)
            self.assertEqual(blockers(player)[0]['display_name'], name)
        player = train_for_experiments(player_at(12))
        for eid, _ in EXPERIMENTS[1:]:
            before = copy.deepcopy(player)
            result, ok, _ = apply_quest_combat_encounter_pure(player, QUEST_ID, QUEST_DATA, eid)
            self.assertFalse(ok)
            self.assertEqual(result, before)
        self.assertEqual(witchs_house_extra_blockers_pure(player, 'other', {'stage': 6}), ())

    def test_journal_is_repeatedly_observational_and_corrects_unearned_claims(self):
        player = player_at(13)
        player[RESUME_KEY] = 0
        before = copy.deepcopy(player)
        rows = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
        by_stage = {r['stage']: r for r in rows}
        for stage, text in ((5, "Read the Witch's diary before searching the fountain."),
                (7, 'Wear insulating gloves to pass the electric gate before searching the cupboard.'),
                (13, "Defeat all four forms of the Witch's experiment before taking the Ball.")):
            self.assertEqual(by_stage[stage]['lines'], (text,))
            self.assertFalse(by_stage[stage]['completed'])
        for _ in range(3):
            self.assertEqual(quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA), rows)
        self.assertEqual(player, before)
        player['quests'][QUEST_ID]['progress'] = 3
        player[RESUME_KEY] = 12
        self.assertIn('Your earlier quest progress is preserved.', quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)[-1]['lines'][-1])

    def test_recovery_contexts_require_only_the_matching_missing_item(self):
        for stage, phase, item, action in ((11, 'recover_key', BACKROOM_KEY, TAKE_KEY), (14, 'recover_ball', BALL, TAKE_BALL)):
            player = player_at(stage, (READ_DIARY,))
            if stage == 14:
                finished_fights(player)
            original = copy.deepcopy(player)
            reasons = blockers(player)
            self.assertTrue(quest_review_service_ready_pure(player, QUEST_ID, reasons))
            self.assertEqual(quest_review_service_phase_pure(player, QUEST_ID, reasons), phase)
            recovered, result = apply_quest_review_service_pure(player, QUEST_ID, reasons)
            self.assertEqual(result, 'deed_only')
            self.assertEqual(player, original)
            self.assertEqual(recovered['quests'], original['quests'])
            self.assertEqual(recovered['inventory'][item], 1)
            self.assertIn(action, recovered['quest_action_proofs'])
            self.assertEqual(recovered['constitution_exp'], player['constitution_exp'])
            self.assertEqual(recovered['quest_points'], 0)
            self.assertEqual(recovered['quest_combat_encounters'], player['quest_combat_encounters'])
            self.assertFalse(quest_review_service_ready_pure(recovered, QUEST_ID, blockers(recovered)))
            self.assertTrue(progress(recovered)[1])
            extra = reasons + ({'kind': 'required_action', 'action_id': 'other'},)
            self.assertFalse(quest_review_service_ready_pure(player, QUEST_ID, extra))
        self.assertFalse(quest_review_service_ready_pure(player_at(11), QUEST_ID, blockers(player_at(11))))
        incomplete = player_at(14)
        self.assertFalse(quest_review_service_ready_pure(incomplete, QUEST_ID, blockers(incomplete)))
        unrelated = player_at(11)
        self.assertEqual(apply_quest_review_service_pure(unrelated, 'other', ()), (unrelated, 'unchanged'))


class WitchsHouseCatalogTest(unittest.TestCase):
    def test_live_fifteen_stage_catalog_preserves_rewards_and_qualified_combat(self):
        witch = QUEST_DATA[QUEST_ID]
        rows = {r['stage']: r for r in witch['stage_requirements']}
        self.assertEqual(witch['stages'], 15)
        self.assertEqual(witch['required_items'], {})
        self.assertEqual(witch['rewards'], {})
        self.assertEqual(witch['point_reward'], 4)
        self.assertEqual(witch['xp_rewards'], ({'skill_id': 'constitution', 'amount': 6325},))
        self.assertEqual(rows[1]['produced_inventory'], {DOOR_KEY: 1})
        self.assertEqual(rows[2]['required_tools'], {DOOR_KEY: 1})
        self.assertEqual(rows[2]['auto_actions'], (ENTER,))
        self.assertEqual(rows[3]['produced_inventory'], {DIARY: 1})
        self.assertEqual(rows[4]['required_inventory'], {DIARY: 1})
        self.assertEqual(rows[4]['required_tools'], {})
        self.assertEqual(rows[6]['required_tools'], {})
        self.assertEqual(rows[8]['consumed_inventory'], {CHEESE: 1})
        self.assertEqual(rows[8]['required_tools'], {MAGNET: 1})
        self.assertEqual(rows[8]['auto_actions'], (MOUSE,))
        self.assertEqual(rows[9]['required_routes'], ())
        self.assertEqual(rows[9]['auto_actions'], (PATROL,))
        self.assertEqual(rows[10]['required_actions'], (READ_DIARY,))
        self.assertEqual(rows[11]['required_tools'], {BACKROOM_KEY: 1})
        self.assertEqual(rows[11]['auto_actions'], (SHED,))
        self.assertEqual(rows[13]['produced_inventory'], {BALL: 1})
        self.assertEqual(rows[14]['consumed_inventory'], {BALL: 1})
        self.assertEqual(rows[14]['auto_actions'], (RETURN,))
        forms = rows[12]['combat_encounters']
        self.assertEqual([e['display_name'] for e in forms], [name for _, name in EXPERIMENTS])
        self.assertEqual([e['level'] for e in forms], [19, 30, 42, 53])
        self.assertEqual([e['npc_stats']['hitpoints'] for e in forms], [1130, 1225, 1325, 1425])
        self.assertEqual([forms[0]['npc_stats'][k] for k in ('attack', 'strength', 'defence')], [18, 10, 19])
        self.assertEqual(forms[-1]['npc_configs']['max_hit'], 150)
        self.assertIn("Witch's_House?oldid=6474931", forms[0]['source'])
        self.assertTrue(forms[0]['npc_stats_source'].endswith("witch's_experiment_(19) (noanims).json"))
        self.assertEqual([e['required_encounters'] for e in forms], [(), *( (eid,) for eid, _ in EXPERIMENTS[:-1])])

    def test_four_encounter_statistics_configs_and_source_qualifications_are_unchanged(self):
        retained = EVIDENCE / 'sources/ankiscape-data__quest__definitions__members__witchs_house.py.txt'
        calls = [n for n in ast.walk(ast.parse(retained.read_text()))
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == '_combat']
        live = next(row for row in QUEST_DATA[QUEST_ID]['stage_requirements'] if row['stage'] == 12)['combat_encounters']
        self.assertEqual(len(calls), 4)
        for original, current in zip(calls, live):
            self.assertEqual(current['source_text'], ast.literal_eval(original.args[5]))
            for keyword in original.keywords:
                if keyword.arg in ('npc_stats', 'npc_configs', 'npc_bonuses'):
                    self.assertEqual(current[keyword.arg], dict(ast.literal_eval(keyword.value)))

    def test_encounter_counts_alone_satisfy_the_four_fight_ball_predicate(self):
        player = player_at(13)
        player['quest_combat_encounter_counts'][QUEST_ID] = {eid: 1 for eid, _ in EXPERIMENTS}
        self.assertEqual(blockers(player), ())
        player, ok, _ = progress(player)
        self.assertTrue(ok)
        self.assertEqual(player['inventory'][BALL], 1)

    def test_diary_registry_and_retained_icon_preserve_existing_assets(self):
        diary = next(i for i in ITEM_DEFINITIONS if i.storage_key == DIARY)
        self.assertEqual(diary.source_item_id, 2408)
        self.assertEqual(diary.category, 'tool')
        self.assertFalse(diary.stackable or diary.tradeable)
        self.assertIn('5849371', diary.source)
        self.assertIn('cache-727-items.txt', diary.source)
        self.assertIn(DIARY, quest_reward_items_as_dict())
        asset = EVIDENCE / 'sources/diary-20111205.png'
        self.assertEqual(Path(QUEST_ITEM_IMAGES[DIARY]), asset)
        raw = asset.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), '433dfc455d1b6a436a8513f7ce353c72e010df39f6df00bcacd9a3fd38d6482a')
        self.assertEqual((int.from_bytes(raw[16:20], 'big'), int.from_bytes(raw[20:24], 'big')), (31, 29))
        for item in (DOOR_KEY, BACKROOM_KEY, MAGNET, BALL):
            self.assertTrue(Path(QUEST_ITEM_IMAGES[item]).is_file())
        self.assertTrue(Path(next(i for i in ITEM_DEFINITIONS if i.storage_key == LEATHER_GLOVES).asset_path).is_file())

    def test_retained_evidence_hashes_and_unchanged_generated_scaffold(self):
        pinned = {'witchs-house-6474931.txt': 'b89036019923a1922f60068293aa7e334358a1631b54155f29863c5a5be9ffe1',
                  'supplying-handler.txt': '930edd5e77d25c9e0d8d9bbb016c197286c88c40db63c236d339281d2cba3413'}
        for name, expected in pinned.items():
            self.assertEqual(hashlib.sha256((EVIDENCE / 'sources' / name).read_bytes()).hexdigest(), expected)
        for excluded in ('parse_archives.py', 'finalize_packet.py', 'OpenRs2CacheItemSearch.java'):
            self.assertFalse((EVIDENCE / 'sources' / excluded).exists())
        self.assertTrue(json.loads((EVIDENCE / 'source-index.json').read_text()))
        self.assertTrue(json.loads((EVIDENCE / 'sources/exact-source-lines.json').read_text()))
        self.assertEqual(hashlib.sha256((ROOT / 'generated/quest_catalog_generated.py').read_bytes()).hexdigest(),
                         '33d1c8294cff9b808732aab3cce756727fd79573cedef153d24c170fec3e78d2')
        generated = next(q for q in PRE_EOC_QUEST_CATALOG if q['id'] == QUEST_ID)
        self.assertEqual(generated['stages'], 3)
