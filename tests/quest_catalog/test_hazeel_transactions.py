"""Exact action traces and atomic adversarial Hazeel transactions."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.hazeel_opening import (
    ACTIONS, PROOFS, SHARED, BRANCH_DEEDS, BRANCH_ROUTES, CORRECT_VALVE_ACTIONS,
    ENDPOINTS, VALVES, VALVE_KEY, POISON, MARK, POISON_RECEIPT, POISON_OWNED, MARK_RECEIPT, MARK_OWNED,
)
from ankiscape.logic_pure.quest.hazeel import (
    apply_hazeel_opening_action_pure, hazeel_opening_next_action_pure, hazeel_opening_review_ready_pure,
)
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, can_attempt_quest_review_pure, quest_current_stage_blockers_pure,
)
from tests.quest_catalog.hazeel_helpers import (
    fresh_player, started_player, review, choose, shared_player, branch_player, before_valves,
)

QUEST_ID = 'hazeel_cult'


def perform(player, action_id, **kwargs):
    action = ACTIONS[action_id]
    return apply_hazeel_opening_action_pure(player, action_id, action.target, action.option, **kwargs)


def expected_after(player, action, branch, final):
    expected = copy.deepcopy(player)
    proofs = {action.proof}
    if action.action_id == 'cult_acceptance':
        expected['inventory'][POISON] = 1
        proofs.add(POISON_RECEIPT)
    if action.action_id == 'poison_range':
        expected['inventory'][POISON] = 0
    if action.action_id == 'clivet_mark':
        expected['inventory'][MARK] = 1
        proofs.add(MARK_RECEIPT)
    if action.direction:
        expected[VALVE_KEY][str(action.target)] = action.direction
    if final:
        proofs.add(PROOFS[ENDPOINTS[branch]])
        expected['quests'][QUEST_ID]['progress'] = 2
    expected['quest_action_proofs'] = sorted(set(expected['quest_action_proofs']) | proofs)
    return expected


class HazeelTransactionsTest(unittest.TestCase):
    def assertRefused(self, player, action_id, target=None, option=None):
        before = copy.deepcopy(player)
        data, ok, result = apply_hazeel_opening_action_pure(player, action_id, target, option)
        self.assertFalse(ok, result)
        self.assertEqual(result, {'action_id': action_id, 'status': 'unchanged'})
        self.assertIs(data, player)
        self.assertEqual(player, before)

    def _assert_trace(self, branch, legacy_progress=None):
        player = started_player()
        if legacy_progress is not None:
            # Explicit stage-1 legacy fixture; no deed history is seeded.
            player['quests'][QUEST_ID]['progress'] = legacy_progress
        actions = (*BRANCH_DEEDS[branch], *CORRECT_VALVE_ACTIONS)
        seen = []
        for index, action_id in enumerate(actions):
            if index == 2:
                player = choose(player, branch)
            self.assertEqual(hazeel_opening_next_action_pure(player).action_id, action_id)
            self.assertTrue(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))
            action = ACTIONS[action_id]
            expected = expected_after(player, action, branch, index == len(actions)-1)
            before = copy.deepcopy(player)
            updated = review(player)
            self.assertEqual(player, before)
            self.assertEqual(updated, expected, action_id)
            seen.append(action_id)
            player = updated
        self.assertFalse(player['quests'][QUEST_ID]['completed'])
        self.assertEqual(player['quests'][QUEST_ID]['progress'], 2)
        self.assertEqual(len(seen), 8 if branch == 'carnillean' else 11)
        if branch == 'carnillean':
            self.assertEqual(player['inventory'].get(POISON, 0), 0)
            self.assertEqual(player['inventory'].get(MARK, 0), 0)
            self.assertFalse(any(PROOFS[key] in player['quest_action_proofs'] for key in BRANCH_DEEDS['hazeel'][2:]))
        else:
            self.assertEqual(player['inventory'][MARK], 1)

    def test_ordinary_carnillean_eight_action_trace(self):
        self._assert_trace('carnillean')
        self._assert_trace('carnillean', legacy_progress=1)

    def test_ordinary_cult_eleven_action_trace(self):
        self._assert_trace('hazeel')
        self._assert_trace('hazeel', legacy_progress=1)

    def test_branch_and_order_refusals_are_atomic(self):
        for player in (fresh_player(), started_player(), review(started_player()), shared_player()):
            for key in ('carnillean_refusal', 'cult_acceptance', 'poison_range', 'family_confirmation', 'clivet_mark', 'valve_2844_right'):
                action = ACTIONS[key]
                self.assertRefused(player, key, action.target, action.option)
        player = branch_player('hazeel')
        for key in ('carnillean_refusal', 'poison_range', 'family_confirmation', 'clivet_mark', 'valve_2844_right'):
            action = ACTIONS[key]
            self.assertRefused(player, key, action.target, action.option)
        player = review(player)
        self.assertRefused(player, 'cult_acceptance')
        self.assertRefused(player, 'family_confirmation')
        self.assertRefused(player, 'clivet_mark')
        for target, option in ((0,'use'), (2859,'Inspect'), (2844,'use'), (True,'use')):
            self.assertRefused(player, 'poison_range', target, option)
        for key in ('bogus', 'cult_endpoint', 'carnillean_endpoint'):
            self.assertRefused(player, key)
        player = before_valves('carnillean')
        for target, option in ((2845,'Turn-right'), (2844,'Turn-left'), ('2844','Turn-right')):
            self.assertRefused(player, 'valve_2844_right', target, option)
        for key in BRANCH_DEEDS['carnillean']:
            self.assertRefused(player, key)
        self.assertRefused(player, 'cult_acceptance')
        for stage, completed in ((2,False), (3,False), (4,True)):
            legacy = copy.deepcopy(player)
            legacy['quests'][QUEST_ID].update(progress=stage, completed=completed)
            self.assertRefused(legacy, 'valve_2844_right', 2844, 'Turn-right')

    def test_missing_or_wrong_poison_is_atomic(self):
        accepted = review(branch_player('hazeel'))
        for replacement in ('missing', 'weapon', 'consumable', 'equipment', 'carried'):
            player = copy.deepcopy(accepted)
            player['inventory'].pop(POISON, None)
            if replacement == 'weapon':
                player['inventory']['Weapon poison'] = 7
            if replacement == 'consumable':
                player['inventory']['Antipoison (4)'] = 5
            if replacement == 'equipment':
                player['equipment']['weapon'] = POISON
            if replacement == 'carried':
                player['combat_supply_loadouts'] = {'other_target': {'carried': {POISON: 3}}}
            self.assertRefused(player, 'poison_range', 2859, 'use')
            blockers = quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA)
            self.assertIn('Needs Poison x1', [b['reason'] for b in blockers])
            before = copy.deepcopy(player)
            self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))
            data, ok, _ = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
            self.assertFalse(ok)
            self.assertIs(data, player)
            self.assertEqual(player, before)
        for invalid in (-1, True, False, 1.0, '1', None, [], {}):
            for key, item, base in (('cult_acceptance', POISON, branch_player('hazeel')),
                                    ('clivet_mark', MARK, review(review(accepted)))):
                base['inventory'][item] = invalid
                self.assertRefused(base, key)

    def test_owned_items_preserve_quantities_without_creating_receipts(self):
        for quantity in (1, 4):
            player = branch_player('hazeel')
            player['inventory'][POISON] = quantity
            before = copy.deepcopy(player)
            self.assertNotIn(PROOFS['cult_acceptance'], player['quest_action_proofs'])
            self.assertEqual(player, before)
            player = review(player)
            self.assertEqual(player['inventory'][POISON], quantity)
            self.assertIn(POISON_OWNED, player['quest_action_proofs'])
            self.assertNotIn(POISON_RECEIPT, player['quest_action_proofs'])
            self.assertRefused(player, 'cult_acceptance')
            player = review(player)
            self.assertEqual(player['inventory'][POISON], quantity-1)
        for inventory_count, equipped in ((1,False), (4,False), (0,True), (3,True)):
            player = branch_player('hazeel')
            player['inventory'][MARK] = inventory_count
            if equipped:
                player['equipment']['neck'] = MARK
            self.assertRefused(player, 'clivet_mark')
            for _ in range(3):
                player = review(player)
            self.assertNotIn(PROOFS['clivet_mark'], player['quest_action_proofs'])
            before = copy.deepcopy(player)
            player = review(player)
            self.assertEqual(player['inventory'][MARK], inventory_count)
            self.assertEqual(player['equipment'], before['equipment'])
            self.assertIn(MARK_OWNED, player['quest_action_proofs'])
            self.assertNotIn(MARK_RECEIPT, player['quest_action_proofs'])
            self.assertRefused(player, 'clivet_mark')
            for _ in range(5):
                player = review(player)
            self.assertEqual(player['inventory'][MARK], inventory_count)

    def test_wrong_valve_state_overrides_historical_turn_proof(self):
        for valve in VALVES:
            player = before_valves('carnillean')
            for other in VALVES:
                if other != valve:
                    player, ok, _ = perform(player, f'valve_{other.object_id}_{other.correct}')
                    self.assertTrue(ok)
            correct = f'valve_{valve.object_id}_{valve.correct}'
            wrong = f"valve_{valve.object_id}_{'left' if valve.correct == 'right' else 'right'}"
            player, ok, result = perform(player, correct)
            self.assertTrue(ok)
            self.assertEqual(result['status'], 'ready')
            self.assertRefused(player, correct, valve.object_id, f'Turn-{valve.correct}')
            # Displaying/inspecting the opposite option performs nothing.
            before = copy.deepcopy(player)
            self.assertEqual(ACTIONS[wrong].option, valve.opposite_option)
            self.assertRefused(player, wrong, valve.object_id, 'Inspect')
            self.assertEqual(player, before)
            player, ok, result = perform(player, wrong)
            self.assertTrue(ok)
            self.assertEqual(result['status'], 'pending')
            self.assertIn(PROOFS[correct], player['quest_action_proofs'])
            self.assertIn(PROOFS[wrong], player['quest_action_proofs'])
            self.assertTrue(quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA))
            self.assertEqual(player['quests'][QUEST_ID]['progress'], 0)
            player = review(player)
            self.assertEqual(player[VALVE_KEY][str(valve.object_id)], valve.correct)
            self.assertEqual(player['quests'][QUEST_ID]['progress'], 2)

    def test_valves_accept_any_order_and_skip_earned_correct_states(self):
        player = before_valves('hazeel')
        for object_id in (2848, 2846, 2844, 2847, 2845):
            valve = next(v for v in VALVES if v.object_id == object_id)
            player, ok, result = perform(player, f'valve_{object_id}_{valve.correct}')
            self.assertTrue(ok)
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(len(player[VALVE_KEY]), 5)
        # No sixth turn or timer: the derived endpoint satisfies ordinary transition.
        player = review(player)
        self.assertEqual(player['quests'][QUEST_ID]['progress'], 2)
        player = before_valves('carnillean')
        player, ok, _ = perform(player, 'valve_2845_right')
        self.assertTrue(ok)
        self.assertEqual(hazeel_opening_next_action_pure(player).action_id, 'valve_2844_right')
        player = review(player)
        self.assertEqual(hazeel_opening_next_action_pure(player).action_id, 'valve_2846_left')
        # Explicit adversarial states: a direction alone does not earn a deed.
        player = before_valves('carnillean')
        player[VALVE_KEY] = {str(v.object_id): v.correct for v in VALVES}
        self.assertRefused(player, 'valve_2844_right', 2844, 'Turn-right')
        self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))
        self.assertNotIn(PROOFS['carnillean_endpoint'], player['quest_action_proofs'])
        for valve in VALVES:
            wrong = 'left' if valve.correct == 'right' else 'right'
            player, ok, _ = perform(player, f'valve_{valve.object_id}_{wrong}')
            self.assertTrue(ok)
            player, ok, _ = perform(player, f'valve_{valve.object_id}_{valve.correct}')
            self.assertTrue(ok)
        self.assertIn(PROOFS['carnillean_endpoint'], player['quest_action_proofs'])
        # Proof without the current state also remains pending.
        player[VALVE_KEY].pop('2844')
        self.assertTrue(quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA))
        player = review(player)
        self.assertEqual(player['quests'][QUEST_ID]['progress'], 2)

    def test_generated_objective_cannot_finish_opening(self):
        # Explicit adversarial retired-objective injection, never an ordinary helper.
        player = started_player()
        player['quest_action_proofs'].append('Complete Hazeel Cult stage 1 objective')
        for index in range(2):
            player = review(player)
            self.assertEqual(player['quests'][QUEST_ID]['progress'], 0)
            self.assertIn(PROOFS[SHARED[index]], player['quest_action_proofs'])
        player = choose(player, 'carnillean')
        for _ in range(5):
            player = review(player)
            self.assertEqual(player['quests'][QUEST_ID]['progress'], 0)
        player = review(player)
        self.assertEqual(player['quests'][QUEST_ID]['progress'], 2)

    def test_legacy_selected_routes_owe_shared_deeds_and_conflicts_refuse(self):
        for branch in BRANCH_DEEDS:
            # Explicit legacy selected-route fixture with no performed opening.
            player = started_player()
            player['quest_route_states'][QUEST_ID] = [BRANCH_ROUTES[branch]]
            for key in SHARED:
                self.assertEqual(hazeel_opening_next_action_pure(player).action_id, key)
                self.assertRefused(player, BRANCH_DEEDS[branch][2])
                player = review(player)
            self.assertEqual(hazeel_opening_next_action_pure(player).action_id, BRANCH_DEEDS[branch][2])
            self.assertEqual(player['inventory'].get(MARK, 0), 0)
        player = started_player()
        player['quest_route_states'][QUEST_ID] = list(BRANCH_ROUTES.values())
        self.assertRefused(player, 'ceril_commission')
        self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))

    def test_readiness_never_waives_external_obligations(self):
        for key, value in (('required_actions', ('Arbitrary deed',)), ('required_inventory', {'Feather': 999}),
                           ('required_skills', ({'skill_id':'mining','level':99},)),
                           ('required_routes', ('Other route',))):
            catalog = copy.deepcopy(QUEST_DATA)
            row = next(row for row in catalog[QUEST_ID]['stage_requirements'] if row['stage'] == 1)
            row[key] = value
            player = started_player()
            self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, catalog))
        for key, value in (('required_quest_points', 999), ('required_items', {'Feather': 999}),
                           ('required_skills', ({'skill_id':'mining','level':99},)),
                           ('required_quests', ({'quest_id':'cooks_assistant'},))):
            catalog = copy.deepcopy(QUEST_DATA)
            catalog[QUEST_ID][key] = value
            player = started_player()
            self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, catalog))
            self.assertFalse(hazeel_opening_review_ready_pure(player, QUEST_ID, catalog, ()))
            data, ok, _ = perform(player, 'ceril_commission', quest_data=catalog)
            self.assertFalse(ok)
            self.assertIs(data, player)
