"""Period route supplies play on quest cards without changing activities."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.logic_pure.logic_pure_quest import quest_current_stage_pure
from tests.quests.test_clear_item_supplies import answer, player_for


SUPPLIES = {
    'pirates_treasure': {'Coins': 30},
    'dragon_slayer': {'Coins': 12000, "Wizard's mind bomb": 1, 'Silk': 1,
                      'Bowl (unfired)': 1, 'Crayfish cage': 1, 'Steel bar': 6},
    'heroes_quest': {'Coins': 8, 'Harralander potion (unf)': 1},
    'monks_friend': {'Coins': 1},
    'clock_tower': {},
    'tree_gnome_village': {},
    'shilo_village': {'Spade': 1, 'Rope': 1, 'Lit torch': 1, 'Coins': 14, 'Bronze wire': 1, 'Bones': 3},
    'gertrudes_cat': {'Coins': 100, 'Bucket': 1, 'Raw sardine': 1},
    'tai_bwo_wannai_trio': {'Karambwan vessel': 1},
    'the_fremennik_trials': {'Coins': 2, 'Raw shark': 1, 'Potato': 1, 'Cabbage': 1, 'Onion': 1},
    'the_tale_of_the_muspah': {'Cosmic rune': 8},
}
# Supply reviews plus the original stage review; existing fights remain on their own cards.
ROW_CARDS = {
    'pirates_treasure': {3: 2}, 'dragon_slayer': {11: 10},
    'heroes_quest': {4: 2, 5: 2}, 'monks_friend': {4: 3, 5: 2},
    'clock_tower': {4: 2}, 'tree_gnome_village': {2: 7}, 'shilo_village': {7: 2},
    'gertrudes_cat': {4: 2}, 'tai_bwo_wannai_trio': {2: 5},
    'the_fremennik_trials': {2: 2}, 'the_tale_of_the_muspah': {4: 9},
}


def route_player(quest_id):
    return player_for(quest_id, SUPPLIES[quest_id])


class RouteItemSupplyReviewTest(unittest.TestCase):
    def test_each_folded_row_plays_from_the_start_at_both_speeds(self):
        for quest_id, stages in ROW_CARDS.items():
            for speed in (1, 10):
                with self.subTest(quest=quest_id, speed=speed):
                    self.assert_route(quest_id, stages, speed)

    def assert_route(self, quest_id, stages, speed):
        player = route_player(quest_id)
        counts = dict.fromkeys(stages, 0)
        for _ in range(2000):
            stage = quest_current_stage_pure(player, quest_id, QUEST_DATA)
            if stage > max(stages) or player['quests'][quest_id]['completed']:
                break
            handled, calls = answer(player, speed)
            self.assertTrue(handled, (stage, calls))
            self.assertEqual(calls['saves'], 1)
            self.assertEqual(player['current_skill'], 'Quests')
            if stage in counts:
                counts[stage] += 1
        self.assertEqual(counts, stages)
        self.assertGreater(quest_current_stage_pure(player, quest_id, QUEST_DATA), max(stages))

    def test_held_products_skip_prices_tools_and_levels(self):
        cases = (
            ('dragon_slayer', 11, {'Plank': 3, 'Steel nails': 90}),
            ('clock_tower', 4, {'Ice gloves': 1, 'White cog': 1, 'Black cog': 1, 'Blue cog': 1, 'Red cog': 1}),
            ('tai_bwo_wannai_trio', 2, {'Raw karambwan': 2}),
            ('monks_friend', 5, {'Logs': 1}),
        )
        for quest_id, stage, inventory in cases:
            with self.subTest(quest=quest_id):
                player = route_player(quest_id)
                player['quests'][quest_id]['progress'] = stage
                player['inventory'] = inventory
                player['fishing_level'] = player['smithing_level'] = 1
                before = (player['fishing_exp'], player['smithing_exp'], player['woodcutting_exp'])
                handled, calls = answer(player)
                self.assertTrue(handled, calls)
                self.assertEqual(quest_current_stage_pure(player, quest_id, QUEST_DATA), stage + 1)
                self.assertEqual((player['fishing_exp'], player['smithing_exp'], player['woodcutting_exp']), before)

    def test_started_quest_names_missing_level_coins_equipment_and_material(self):
        cases = (
            ('tai_bwo_wannai_trio', 2, 'fishing_level', 64, 'Fishing 65'),
            ('tai_bwo_wannai_trio', 2, 'Karambwan vessel', None, 'Needs Karambwan vessel'),
            ('dragon_slayer', 11, 'smithing_level', 33, 'Smithing 34'),
            ('dragon_slayer', 11, 'Steel bar', None, 'Needs Steel bar'),
            ('monks_friend', 4, 'Coins', None, 'Needs Coins x1'),
            ('monks_friend', 5, 'woodcutting', [], 'Needs Hatchet'),
            ('shilo_village', 7, 'Coins', None, 'Needs Coins x14'),
            ('the_tale_of_the_muspah', 4, 'mining_level', 7, 'Mining 8'),
        )
        for quest_id, stage, key, value, reason in cases:
            with self.subTest(quest=quest_id, missing=key):
                player = route_player(quest_id)
                player['quests'][quest_id]['progress'] = stage
                if key.endswith('_level'):
                    player[key] = value
                elif key == 'woodcutting':
                    player['toolbelt'][key] = value
                else:
                    player['inventory'].pop(key, None)
                if quest_id == 'shilo_village':
                    player['inventory'].update({'Bervirius notes': 1, 'Bone shard': 1, 'Sword pommel': 1})
                before = copy.deepcopy(player)
                handled, calls = answer(player)
                self.assertFalse(handled)
                self.assertEqual(player, before)
                self.assertTrue(calls['deactivated'])
                self.assertIn(reason, calls['errors'][0][1])
                self.assertEqual(calls['errors'][0][1].count(reason), 1)

    def test_smithing_preserves_surplus_and_pays_one_bar_xp(self):
        player = route_player('dragon_slayer')
        player['quests']['dragon_slayer']['progress'] = 11
        player['inventory'] = {'Plank': 3, 'Steel nails': 75, 'Steel bar': 28}
        xp = player['smithing_exp']
        handled, calls = answer(player)
        self.assertTrue(handled, calls)
        self.assertEqual(player['inventory']['Steel bar'], 27)
        self.assertEqual(player['inventory']['Steel nails'], 90)
        self.assertEqual(player['smithing_exp'] - xp, 37.5)
        self.assertEqual(calls['activity'], ['+15 Steel nails'])

    def test_gathering_pays_period_xp_once_per_product(self):
        cases = (('monks_friend', 5, 'woodcutting_exp', 25),
                 ('tree_gnome_village', 2, 'woodcutting_exp', 150),
                 ('tai_bwo_wannai_trio', 2, 'fishing_exp', 220))
        for quest_id, stage, key, xp in cases:
            with self.subTest(quest=quest_id):
                player = route_player(quest_id)
                player['quests'][quest_id]['progress'] = stage
                before = player[key]
                for _ in range(ROW_CARDS[quest_id][stage]):
                    handled, calls = answer(player, 10)
                    self.assertTrue(handled, calls)
                self.assertEqual(player[key] - before, xp)
