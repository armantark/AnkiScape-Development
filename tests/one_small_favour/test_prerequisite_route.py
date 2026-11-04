"""An earned route from a fresh save, separate from declared refusal fixtures."""

import copy
import math
import random
import unittest
from unittest.mock import patch

from tests.one_small_favour.test_opening_transactions import player
from tests.test_runtime_actions import _context
from ankiscape.core import constants as c
from ankiscape.core.logic import level_up_check
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest.one_small_favour import QUEST_ID, BLUNT_HATCHET, OPENING_PROOFS
from ankiscape.data.shop_data import SHOP_DATA
from ankiscape.logic.shop_logic import apply_shop_buy_pure, apply_shop_sell_pure, preview_shop_buy_pure
from ankiscape.logic_pure.logic_pure import (
    apply_safe_combat_recovery_pure, combat_max_lifepoints_pure, equip_item_pure, can_equip_item_pure,
    set_combat_auto_eat_food_pure,
)
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, start_quest_pure, quest_locked_reasons_pure,
)
from ankiscape.runtime import runtime_actions as actions


class EarnedRoute:
    """Selections and ordinary owners only: no level, victory, item or proof seeding."""
    def __init__(self, case):
        self.case = case
        self.data = default_player_data(c.ORE_DATA, c.ITEM_DEFINITIONS)
        self.calls = {'xp': [], 'saves': 0, 'errors': []}
        self.ctx = _context(self.data, self.calls, review_action_multiplier=10)
        self.ctx.level_up_check = level_up_check
        self.rng = random.Random(1430)
        self.ctx.random_random = self.rng.random

    def answer(self, handler, key=None, target=None):
        if key:
            self.data[key] = target
        self.case.assertTrue(handler(self.ctx), (target, self.calls['errors'][-1:]))

    def until(self, condition, action, limit=20000):
        for _ in range(limit):
            if condition():
                return
            action()
        self.case.fail(str({key: self.data.get(key) for key in ('attack_level', 'strength_level', 'defense_level', 'combat_last_result')}))

    def utility(self, target):
        self.answer(actions.handle_utility_answer, 'current_utility', target)

    def mine(self, target):
        self.answer(actions.handle_mining_answer, 'current_ore', target)

    def ensure_ore(self, target, quantity):
        output = c.ORE_DATA[target]['output_item']
        self.until(lambda: self.data['inventory'].get(output, 0) >= quantity, lambda: self.mine(target))

    def replace(self, updated):
        self.data.clear()
        self.data.update(updated)

    def sell(self, item):
        updated, result = apply_shop_sell_pure(self.data, 'general_store', item, self.data['inventory'][item])
        self.case.assertTrue(result['allowed'], result)
        self.replace(updated)

    def buy(self, shop_id, item, quantity=1):
        row = next(row for row in SHOP_DATA[shop_id]['stock'] if row['item_name'] == item)
        preview = preview_shop_buy_pure(self.data, shop_id, row['id'], quantity)
        self.case.assertTrue(preview['allowed'], preview)
        coins = self.data['inventory']['Coins']
        updated, result = apply_shop_buy_pure(self.data, shop_id, row['id'], quantity)
        self.case.assertTrue(result['allowed'], result)
        self.case.assertEqual(updated['inventory']['Coins'], coins - result['total_price'])
        self.replace(updated)

    def train_crafting(self, level):
        self.until(lambda: self.data['crafting_level'] >= level, self._craft_one)

    def _craft_one(self):
        high = self.data['crafting_level'] >= c.CRAFTING_DATA['spin_flax_to_bow_string']['level']
        target = 'spin_flax_to_bow_string' if high else 'spin_wool_to_ball_of_wool'
        item = next(iter(c.CRAFTING_DATA[target]['requirements']))
        if not self.data['inventory'].get(item):
            self.utility('gather_flax' if high else 'gather_wool')
        self.answer(actions.handle_crafting_answer, 'current_craft', target)

    def smith(self, target):
        requirements = c.SMITHING_DATA[target]['requirements']
        if 'Bronze bar' in requirements:
            self.until(lambda: self.data['inventory']['Bronze bar'] >= requirements['Bronze bar'],
                       lambda: self.smith('smelt_bronze_bar'))
        else:
            for ore in ('copper', 'tin'):
                self.ensure_ore(ore, requirements[c.ORE_DATA[ore]['output_item']])
        self.answer(actions.handle_smithing_answer, 'current_smith', target)

    def train_and_buy_supplies(self):
        self.ensure_ore('clay', 200)
        self.sell('Clay')
        for item in ('Tinderbox', 'Candle', 'Rope', 'Spade', 'Chisel'):
            self.buy('jiminuas_jungle_store', item)
        self.buy('gerrants_fishy_business', 'Fishing rod')
        self.buy('general_store', 'Hammer')
        level = next(r['level'] for r in c.QUEST_DATA[QUEST_ID]['required_skills'] if r['skill_id'] == 'smithing')
        self.until(lambda: self.data['smithing_level'] >= level, lambda: self.smith('forge_bronze_dagger'))
        self.sell('Bronze dagger')
        self.smith('forge_bronze_wire')
        self.utility('light_candle')
        gates = {r['skill_id']: r['level'] for r in c.QUEST_DATA[QUEST_ID]['required_skills']}
        self.train_crafting(gates['crafting'])
        self.until(lambda: self.data['agility_level'] >= gates['agility'],
                   lambda: self.answer(actions.handle_agility_answer, 'current_agility', 'burthorpe_course'))

    def quest(self, quest_id):
        self.data['current_quest'] = quest_id
        self.answer(actions.handle_quest_answer)
        for skill in ('Herblore', 'Crafting'):
            level_up_check(skill, self.data)

    def finish(self, quest_id):
        self.until(lambda: self.data['quests'][quest_id]['completed'], lambda: self.quest(quest_id), limit=200)

    def jungle_potion(self):
        self.data['current_quest'] = 'jungle_potion'
        self.finish('jungle_potion')
        # The quest cleans its own herbs; train the later prerequisite with its unlocked search.
        target = c.HERBLORE_DATA['clean_snake_weed']
        quantity = math.ceil(c.EXP_TABLE[17] / target['exp']) + 2
        self.until(lambda: self.data['inventory']['Grimy snake weed'] >= quantity,
                   lambda: self.utility('search_marshy_jungle_vines'))
        self.until(lambda: not self.data['inventory']['Grimy snake weed'],
                   lambda: self.answer(actions.handle_herblore_answer, 'current_herblore', 'clean_snake_weed'))
        self.case.assertTrue(self.data['quests']['jungle_potion']['completed'])

    def equip(self, item):
        allowed, reasons = can_equip_item_pure(item, c.EQUIPMENT_DATA, self.data)
        self.case.assertTrue(allowed, reasons)
        inventory, equipment, ok = equip_item_pure(item, self.data['inventory'], self.data['equipment'], c.EQUIPMENT_DATA)
        self.case.assertTrue(ok)
        self.data.update(inventory=inventory, equipment=equipment)

    def rest(self):
        # The reviewer heals after each skilling review (_spend_card_on_action);
        # direct handler calls skip that hook, so earlier knocks would otherwise
        # reach the chickens.
        self.until(lambda: self.data['combat_lifepoints'] >= combat_max_lifepoints_pure(self.data),
                   lambda: self.replace(apply_safe_combat_recovery_pure(self.data, c.EQUIPMENT_DATA)))

    def train_combat(self):
        self.buy('varrock_sword_shop', 'Bronze sword')
        self.equip('Bronze sword')
        self.rest()
        self.ctx.random_random = lambda: 0.75
        self.until(lambda: self.data['inventory']['Raw chicken'] >= 400,
                   lambda: self.answer(actions.handle_combat_answer, 'current_combat_target', 'chicken'))
        self.prepare_combat_food()
        self.ctx.random_random = lambda: 0.75
        for style, skill in (('accurate', 'attack'), ('aggressive', 'strength'), ('defensive', 'defense')):
            self.data['combat_attack_style'] = style
            self.until(lambda: self.data[skill + '_level'] >= 40,
                       lambda: self.answer(actions.handle_combat_answer, 'current_combat_target', 'chicken'))
        self.case.assertGreaterEqual(self.data['inventory']['Bones'], 3)
        self.ctx.random_random = self.rng.random

    def prepare_combat_food(self):
        self.ctx.random_random = self.rng.random
        self.until(lambda: self.data['inventory']['Cooked chicken'] >= 100,
                   lambda: self.answer(actions.handle_cooking_answer, 'current_cooking', 'cook_chicken'))
        updated, ok, reason = set_combat_auto_eat_food_pure(self.data, 'Cooked chicken')
        self.case.assertTrue(ok, reason)
        self.replace(updated)

    def armour_for_shilo(self):
        for shop, item in (('horviks_armour_shop', 'Iron chainbody'),
                           ('horviks_armour_shop', 'Iron platelegs'),
                           ('horviks_armour_shop', 'Iron full helm'),
                           ('cassies_shield_shop', 'Iron kiteshield'),
                           ('varrock_sword_shop', 'Steel sword')):
            self.buy(shop, item)
            self.equip(item)


class PrerequisiteRouteTest(unittest.TestCase):
    def test_each_composed_prerequisite_and_skill_gate_still_refuses_atomically(self):
        quest = c.QUEST_DATA[QUEST_ID]
        self.assertEqual(tuple(r['quest_id'] for r in quest['required_quests']),
                         ('shilo_village', 'jungle_potion', 'rune_mysteries'))
        self.assertIn('Rune Mysteries', quest['requirements'])
        for requirement in quest['required_quests']:
            data = player(started=False)
            data['quests'][requirement['quest_id']]['completed'] = False
            self._refusal(data, requirement['display_name'])
        for requirement in quest['required_skills']:
            data = player(started=False)
            data[requirement['skill_id'] + '_level'] = requirement['level'] - 1
            self._refusal(data, requirement['display_name'])

    def _refusal(self, data, expected):
        before = copy.deepcopy(data)
        self.assertTrue(any(expected in reason for reason in quest_locked_reasons_pure(data, QUEST_ID, c.QUEST_DATA)))
        after, ok = start_quest_pure(data, QUEST_ID, c.QUEST_DATA)
        self.assertFalse(ok)
        self.assertEqual(after, before)
        after, ok, _ = apply_quest_progress_pure(data, QUEST_ID, c.QUEST_DATA)
        self.assertFalse(ok)
        self.assertIs(after, data)
        self.assertEqual(data, before)

    def test_fresh_player_earns_prerequisites_supplies_and_all_seven_contacts(self):
        route = EarnedRoute(self)
        self.assertFalse(any(q['completed'] for q in route.data['quests'].values()))
        self.assertFalse(any(route.data['inventory'].values()))
        self.assertFalse(route.data['quest_action_proofs'])
        with patch('ankiscape.core.logic.show_level_up_dialog'):
            route.finish('rune_mysteries')
            self.assertEqual(route.data['inventory']['Air talisman'], 1)  # completion returns it
            self.assertEqual(route.data['inventory']['Research package'], 0)
            self.assertEqual(route.data['inventory']['Research notes'], 0)
            route.train_and_buy_supplies()
            route.finish('druidic_ritual')
            route.jungle_potion()
            route.train_combat()
            route.armour_for_shilo()
            route.ctx.random_random = lambda: 0.5
            route.finish('shilo_village')
            self._assert_shilo(route.data)
            route.data['current_quest'] = QUEST_ID
            for index, proof in enumerate(OPENING_PROOFS):
                route.quest(QUEST_ID)
                self.assertIn(proof, route.data['quest_action_proofs'])
                self.assertEqual(route.data['inventory'][BLUNT_HATCHET], int(index in (1, 2)))
                self.assertEqual(route.data['quests'][QUEST_ID]['progress'], 2 if index == 6 else 1)
            self.assertFalse(route.data['quests'][QUEST_ID]['completed'])

    def _assert_shilo(self, data):
        self.assertTrue(data['quests']['shilo_village']['completed'])
        self.assertEqual(data['inventory']['Rashiliyia corpse'], 0)
        expected = ('shilo_village_nazastarool_zombie_91', 'shilo_village_nazastarool_skeleton_68',
                    'shilo_village_nazastarool_ghost_93')
        self.assertEqual(set(data['quest_combat_encounters']['shilo_village']), set(expected))
