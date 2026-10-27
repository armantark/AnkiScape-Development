"""Adversarial catalog obligations must also gate explicit opening actions."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.hazeel_opening import ACTIONS, BRANCH_ROUTES, QUEST_ID
from ankiscape.logic_pure.logic_pure_quest import (
    can_attempt_quest_review_pure, quest_eligibility_reasons_pure,
)
from ankiscape.logic_pure.quest.hazeel import apply_hazeel_opening_action_pure
from tests.quest_catalog.hazeel_helpers import (
    before_valves, branch_player, review, started_player,
)


OBLIGATIONS = (
    ('required_inventory', {'Feather': 999}),
    ('consumed_inventory', {'Feather': 999}),
    ('required_inventory_options', ((('Feather', 999), ('Coins', 999)),)),
    ('consumed_inventory_options', ((('Feather', 999), ('Coins', 999)),)),
    ('required_actions', ('External stage deed',)),
    ('required_routes', ('External stage route',)),
    ('required_skills', ({'skill_id': 'mining', 'level': 99},)),
    ('required_tools', {'Hammer': 2}),
    ('combat_encounters', ({'encounter_id': 'external_fight', 'quantity': 2},)),
)


def injected_catalog(key, value, variant=None, mandatory=False):
    catalog = copy.deepcopy(QUEST_DATA)
    rows = catalog[QUEST_ID]['stage_requirements']
    if mandatory:
        catalog[QUEST_ID]['stage_requirements'] = (*rows, {'stage': 1, key: value})
        return catalog
    for row in rows:
        if row['stage'] == 1 and (variant is None or row['variant'] == variant):
            # Retain every real opening obligation alongside the injected one.
            existing = row.get(key, ())
            row[key] = (*existing, *value) if key in ('required_actions', 'required_routes') else value
    return catalog


def explicit_action(player, action_id, catalog, evaluator=quest_eligibility_reasons_pure):
    action = ACTIONS[action_id]
    return apply_hazeel_opening_action_pure(
        player, action_id, action.target, action.option,
        quest_data=catalog, eligibility_reasons=evaluator,
    )


def action_states():
    yield 'unselected', started_player(), 'ceril_commission'
    yield 'unselected', review(started_player()), 'clivet_briefing'
    for branch, action_ids in (
        ('carnillean', ('carnillean_refusal',)),
        ('hazeel', ('cult_acceptance', 'poison_range', 'family_confirmation', 'clivet_mark')),
    ):
        player = branch_player(branch)
        for action_id in action_ids:
            yield branch, player, action_id
            player = review(player)
        yield branch, before_valves(branch), 'valve_2848_right'


class HazeelStageEligibilityTest(unittest.TestCase):
    def assert_atomic_refusal(self, player, action_id, catalog, evaluator=quest_eligibility_reasons_pure):
        before = copy.deepcopy(player)
        data, ok, result = explicit_action(player, action_id, catalog, evaluator)
        self.assertFalse(ok)
        self.assertIs(data, player)
        self.assertEqual(result, {'action_id': action_id, 'status': 'unchanged'})
        self.assertEqual(player, before)

    def test_explicit_actions_refuse_every_unmet_stage_obligation(self):
        for branch, player, action_id in action_states():
            for key, value in OBLIGATIONS:
                with self.subTest(branch=branch, action=action_id, obligation=key):
                    variant = None if branch == 'unselected' else branch
                    catalog = injected_catalog(key, value, variant)
                    self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, catalog))
                    self.assert_atomic_refusal(player, action_id, catalog)

    def test_mandatory_rows_and_legacy_selected_shared_deeds_are_checked(self):
        for branch in BRANCH_ROUTES:
            # Legacy saved selection still owes the two real shared deeds.
            player = started_player()
            player['quest_route_states'][QUEST_ID] = [BRANCH_ROUTES[branch]]
            for key, value in OBLIGATIONS:
                with self.subTest(branch=branch, obligation=key):
                    catalog = injected_catalog(key, value, mandatory=True)
                    self.assert_atomic_refusal(player, 'ceril_commission', catalog)

    def test_catalog_without_evaluator_still_enforces_stage_obligations(self):
        player = branch_player('hazeel')
        for key, value in OBLIGATIONS:
            with self.subTest(obligation=key):
                catalog = injected_catalog(key, value, 'hazeel')
                self.assert_atomic_refusal(player, 'cult_acceptance', catalog, evaluator=None)

    def test_unselected_rows_cannot_hide_an_external_obligation(self):
        player = started_player()
        for branch in BRANCH_ROUTES:
            catalog = injected_catalog('required_inventory', {'Feather': 999}, branch)
            self.assert_atomic_refusal(player, 'ceril_commission', catalog)

    def test_satisfied_external_obligations_allow_only_the_requested_deed(self):
        # Explicit adversarial fixtures satisfy only the added obligations.
        for branch, player, action_id in action_states():
            player['inventory'].update({'Feather': 999, 'Hammer': 2})
            player['mining_level'] = 99
            player['quest_action_proofs'].append('External stage deed')
            player['quest_route_states'].setdefault(QUEST_ID, []).append('External stage route')
            player['quest_combat_encounter_counts'][QUEST_ID] = {'external_fight': 2}
            for key, value in OBLIGATIONS:
                with self.subTest(branch=branch, action=action_id, obligation=key):
                    variant = None if branch == 'unselected' else branch
                    catalog = injected_catalog(key, value, variant)
                    before = copy.deepcopy(player)
                    expected, expected_ok, expected_result = explicit_action(player, action_id, QUEST_DATA)
                    self.assertTrue(expected_ok)
                    data, ok, result = explicit_action(player, action_id, catalog)
                    self.assertTrue(ok)
                    self.assertEqual(data, expected)
                    self.assertEqual(result, expected_result)
                    self.assertEqual(player, before)

    def test_other_branch_obligations_do_not_gate_selected_route(self):
        for branch in BRANCH_ROUTES:
            player = branch_player(branch)
            action_id = 'cult_acceptance' if branch == 'hazeel' else 'carnillean_refusal'
            other = 'carnillean' if branch == 'hazeel' else 'hazeel'
            for key, value in OBLIGATIONS:
                with self.subTest(branch=branch, obligation=key):
                    catalog = injected_catalog(key, value, other)
                    data, ok, _ = explicit_action(player, action_id, catalog)
                    self.assertTrue(ok)
                    self.assertIn(ACTIONS[action_id].proof, data['quest_action_proofs'])
