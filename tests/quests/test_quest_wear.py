"""Played quest wear: physical moves, bank/end/Stop return, hand edits and Undo.

Failures to cover: the carried item leaves Start disabled; a swap costs a card;
released wear returns too early or never; empty slots or two-handed weapons lose
items; hand changes get overwritten; review Undo loses the remembered return.
"""

import copy
import random

from tests.integration_smoke.fixtures import ReviewedProfile


class QuestWearTests(ReviewedProfile):
    def _quest(self, quest_id='witchs_house', *, banking=True):
        addon = self._addon('ankiscape_quest_wear')
        self._new_save(
            addon, current_quest=quest_id, inventory={
                'Cheese': 1, 'Coins': 1, 'Bucket of water': 1, 'Bones': 25,
                'Lobster': 1000, 'White gloves': 1,
            }, equipment={'weapon': 'Rune scimitar', 'hands': 'Barrows gloves', 'shield': 'Rune kiteshield'},
            combat_auto_eat_food=['Lobster'] if banking else [],
            combat_auto_flee=False, combat_prayers_enabled=False,
        )
        data = addon._state.player_data
        for skill in ('attack', 'strength', 'defense', 'constitution'):
            data[f'{skill}_level'] = 99
            data[f'{skill}_exp'] = 13034431.0
        data['combat_lifepoints'] = 990
        random.seed(20261104)
        self.assertTrue(addon.on_set_quest(quest_id))
        addon._select_review_action('Quests')
        return addon

    def _until_stage(self, addon, stage):
        data = addon._state.player_data
        for _ in range(500):
            if data['quests'][data['current_quest']]['progress'] >= stage:
                return
            self._answer(addon)
            self.assertEqual(self.errors, [])
        self.fail(f'Quest did not reach stage {stage}')

    def _finish(self, addon):
        data = addon._state.player_data
        for _ in range(800):
            if data['quests'][data['current_quest']]['completed']:
                return
            self._answer(addon)
            self.assertFalse(data.get('combat_grave'))
        self.fail('Quest did not finish')

    def _pass_gate(self, addon):
        self._until_stage(addon, 6)
        self.assertEqual(addon._state.player_data['equipment']['hands'], 'Barrows gloves')
        self._answer(addon)
        data = addon._state.player_data
        self.assertEqual(data['quests']['witchs_house']['progress'], 7)
        self.assertEqual(data['equipment']['hands'], 'Leather gloves')
        self.assertEqual(data['inventory']['Barrows gloves'], 1)
        self.assertFalse(data['quest_equipment_swap']['needed'])

    def test_witch_gloves_return_at_first_combat_bank_arrival_after_release(self):
        addon = self._quest()
        self._pass_gate(addon)
        self._until_stage(addon, 12)
        data = addon._state.player_data
        self.assertEqual(data['equipment']['hands'], 'Leather gloves')
        for _ in range(20):
            self._answer(addon)
            if data['equipment']['hands'] == 'Barrows gloves':
                break
        self.assertEqual(data['equipment']['hands'], 'Barrows gloves')
        self.assertFalse(data['quest_equipment_swap'])
        self.assertFalse(data['quests']['witchs_house']['completed'])
        self.assertFalse(data['combat_bank_run'])

    def test_no_trip_returns_gloves_at_end_and_stop_returns_at_once(self):
        addon = self._quest(banking=False)
        self._pass_gate(addon)
        self._finish(addon)
        self.assertEqual(addon._state.player_data['equipment']['hands'], 'Barrows gloves')
        self.assertFalse(addon._state.player_data['quest_equipment_swap'])
        addon = self._quest(banking=False)
        self._pass_gate(addon)
        addon.stop_action(addon)
        self.assertEqual(addon._state.player_data['equipment']['hands'], 'Barrows gloves')
        self.assertFalse(addon._state.player_data['quest_equipment_swap'])

    def test_demon_slayer_wields_silverlight_and_restores_weapon_and_shield(self):
        addon = self._quest('demon_slayer')
        self._until_stage(addon, 7)
        before = dict(addon._state.player_data['equipment'])
        self._answer(addon)
        self.assertEqual(addon._state.player_data['equipment']['weapon'], 'Silverlight')
        self._finish(addon)
        self.assertEqual(addon._state.player_data['equipment'], before)
        self.assertFalse(addon._state.player_data['quest_equipment_swap'])

    def test_hand_change_cancels_even_when_player_equips_quest_gloves_again(self):
        addon = self._quest(banking=False)
        self._pass_gate(addon)
        self.assertTrue(addon.on_equip_item('White gloves'))
        self.assertFalse(addon._state.player_data['quest_equipment_swap'])
        self.assertTrue(addon.on_equip_item('Leather gloves'))
        self._finish(addon)
        self.assertEqual(addon._state.player_data['equipment']['hands'], 'Leather gloves')
        self.assertEqual(addon._state.player_data['inventory']['Barrows gloves'], 1)

    def test_review_undo_restores_slot_bank_and_swap_then_replay_matches(self):
        addon = self._quest(banking=False)
        self._until_stage(addon, 6)
        before = copy.deepcopy(addon._state.player_data)
        self._answer(addon)
        after = copy.deepcopy(addon._state.player_data)
        addon._on_state_did_undo(type('Undo', (), {'operation': 'Answer Card'})())
        self.assertEqual(addon._state.player_data, before)
        self._answer(addon)
        self.assertEqual(addon._state.player_data, after)

    def test_missing_gloves_or_silverlight_stops_and_names_the_item(self):
        for quest_id, stage, missing, item in (
            ('witchs_house', 6, 'gloves', 'Leather gloves'),
            ('demon_slayer', 7, 'Silverlight', 'Silverlight'),
        ):
            with self.subTest(quest=quest_id):
                addon = self._quest(quest_id)
                self._until_stage(addon, stage)
                addon._state.player_data['inventory'][item] = 0
                self._answer(addon)
                self.assertEqual(addon._state.current_skill, 'Utilities')
                self.assertIn(missing, self.errors[-1][1])

    def test_skilling_arrival_returns_released_gloves_after_json_reload(self):
        addon = self._quest(banking=False)
        self._pass_gate(addon)
        data = addon._state.player_data
        addon.save_player_data()
        addon.load_player_data()
        data = addon._state.player_data
        self.assertFalse(data['quest_equipment_swap']['needed'])
        data.update(current_ore='iron', mining_level=99, mining_exp=13034431.0,
                    toolbelt={'mining': ['rune_pickaxe']})
        addon._state.current_skill = 'Mining'
        self.assertTrue(addon.on_request_review_bank_run())
        for _ in range(100):
            self._answer(addon)
            if not data.get('quest_equipment_swap'):
                break
        self.assertEqual(data['equipment']['hands'], 'Barrows gloves')
        self.assertFalse(data['quest_equipment_swap'])

    def test_each_accepted_pair_can_be_worn_and_already_worn_pair_needs_no_return(self):
        from ankiscape.data.quest.witchs_house import INSULATING_GLOVES

        for item in INSULATING_GLOVES:
            with self.subTest(item=item):
                addon = self._quest(banking=False)
                self._until_stage(addon, 6)
                data = addon._state.player_data
                data['inventory']['Leather gloves'] = 0
                data['inventory'][item] = 1
                self._answer(addon)
                self.assertEqual(data['quests']['witchs_house']['progress'], 7)
                self.assertEqual(data['equipment']['hands'], item)
                addon.stop_action(addon)
                self.assertEqual(data['equipment']['hands'], 'Barrows gloves')
        addon = self._quest(banking=False)
        self._until_stage(addon, 6)
        data = addon._state.player_data
        data['equipment']['hands'] = 'Leather gloves'
        before = dict(data['inventory'])
        self._answer(addon)
        self.assertFalse(data.get('quest_equipment_swap'))
        self.assertEqual(data['inventory'], before)

    def test_empty_slot_returns_to_empty_and_other_slot_change_preserves_return(self):
        addon = self._quest(banking=False)
        self._until_stage(addon, 6)
        data = addon._state.player_data
        data['equipment'].pop('hands')
        self._answer(addon)
        self.assertTrue(addon.on_unequip_slot('shield'))
        self.assertTrue(data['quest_equipment_swap'])
        addon.stop_action(addon)
        self.assertNotIn('hands', data['equipment'])
        self.assertEqual(data['inventory']['Leather gloves'], 1)
        self.assertNotIn('shield', data['equipment'])

    def test_two_handed_weapon_returns_without_introducing_a_shield(self):
        addon = self._quest('demon_slayer')
        self._until_stage(addon, 7)
        data = addon._state.player_data
        data['equipment'].pop('shield')
        data['equipment']['weapon'] = 'Bronze 2h sword'
        self._answer(addon)
        self.assertEqual(data['equipment']['weapon'], 'Silverlight')
        self._finish(addon)
        self.assertEqual(data['equipment']['weapon'], 'Bronze 2h sword')
        self.assertNotIn('shield', data['equipment'])

    def test_returning_two_handed_weapon_banks_a_shield_equipped_during_swap(self):
        addon = self._quest('demon_slayer')
        self._until_stage(addon, 7)
        data = addon._state.player_data
        self.assertTrue(addon.on_unequip_slot('shield'))
        data['equipment']['weapon'] = 'Bronze 2h sword'
        data['inventory']['Silverlight'] = 1
        before = {item: data['inventory'].get(item, 0) + list(data['equipment'].values()).count(item)
                  for item in ('Bronze 2h sword', 'Silverlight', 'Rune kiteshield')}
        self._answer(addon)
        self.assertEqual(data['equipment']['weapon'], 'Silverlight')
        self.assertTrue(addon.on_equip_item('Rune kiteshield'))
        addon.stop_action(addon)
        self.assertEqual(data['equipment']['weapon'], 'Bronze 2h sword')
        self.assertNotIn('shield', data['equipment'])
        self.assertEqual(data['inventory']['Rune kiteshield'], 1)
        self.assertFalse(data['quest_equipment_swap'])
        self.assertEqual({item: data['inventory'].get(item, 0) + list(data['equipment'].values()).count(item)
                          for item in before}, before)
