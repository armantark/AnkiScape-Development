"""Drop-defined equipment reaches Bank, wearing and the period exchange catalog."""

import json
from pathlib import Path
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.equipment_data import EQUIPMENT_DATA
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
from ankiscape.logic.grand_exchange_logic import apply_ge_frontend_action_pure
from ankiscape.logic_pure.logic_pure_equipment import equip_item_pure, unequip_item_pure
from ankiscape.runtime.runtime_actions_combat import handle_combat_answer
from tests.test_runtime_actions import _context


ITEMS = (
    'Abyssal whip', 'Adamant boots', 'Adamant dart (p)', 'Adamant spear',
    'Black knife', 'Black mask (10)', 'Black robe', 'Bronze boots',
    'Dragon chainbody', 'Dragon med helm', 'Dragon platelegs', 'Dragon plateskirt',
    'Granite maul', 'Iron boots', 'Mystic fire staff', 'Ogre arrows', 'Rune boots',
    'Rune dart', 'Rune dart (p)', 'Shade robe', 'Steel arrow (p)',
)
ROOT = Path(__file__).resolve().parents[2]


class MissingEquipmentItemsTest(unittest.TestCase):
    def test_every_base_equipment_definition_has_an_item_registration(self):
        registered = {item.storage_key for item in ITEM_DEFINITIONS}
        self.assertEqual(sorted(set(EQUIPMENT_DATA) - registered), [])

    def test_period_tradeable_items_enter_the_exchange_but_shade_robe_does_not(self):
        registered = {item.storage_key: item for item in ITEM_DEFINITIONS}
        player = default_player_data({}, ITEM_DEFINITIONS)
        for name in ITEMS:
            with self.subTest(item=name):
                item = registered[name]
                self.assertEqual(item.source_item_id, EQUIPMENT_DATA[name].source_item_id)
                self.assertIn(name, player['inventory'])
                self.assertEqual(item.tradeable, name != 'Shade robe')
                self.assertEqual(name in GE_ITEM_CATALOG, name != 'Shade robe')
                if item.tradeable:
                    market = GE_ITEM_CATALOG[name]
                    _data, preview = apply_ge_frontend_action_pure(
                        {'inventory': {'Coins': 10000000}}, 'preview_offer',
                        {'side': 'buy', 'item_name': name, 'quantity': 1,
                         'unit_price': market['guide_price']},
                        item_catalog=GE_ITEM_CATALOG,
                    )
                    self.assertTrue(preview['ok'], preview)
        self.assertEqual(GE_ITEM_CATALOG['Adamant boots']['guide_price'], 1920)
        self.assertEqual(GE_ITEM_CATALOG['Black robe']['cache_value'], 13)

    def test_registered_art_is_backed_by_a_pre_cutoff_file(self):
        registered = {item.storage_key: item for item in ITEM_DEFINITIONS}
        provenance = json.loads((ROOT / 'assets_provenance.json').read_text())
        for name in ITEMS:
            with self.subTest(item=name):
                # These exact poisoned variants have no retained period file.
                if name in {'Adamant dart (p)', 'Steel arrow (p)'}:
                    self.assertIsNone(registered[name].asset_path)
                    continue
                path = Path(registered[name].asset_path)
                self.assertTrue(path.is_file(), name)
                source = provenance[path.relative_to(ROOT).as_posix()]
                self.assertLess(source['timestamp'], '2012-11-20T00:00:00Z')
                self.assertEqual(source['source_wiki'], 'rs3')

    def test_gargoyle_boots_can_be_held_worn_banked_and_offered_for_sale(self):
        player = {
            'inventory': {}, 'equipment': {}, 'current_combat_target': 'gargoyle',
            'combat_action': 'finisher', 'slayer_level': 75, 'defense_level': 30,
            'combat_lifepoints': 100, 'constitution_level': 10,
            'combat_encounter': {'target_id': 'gargoyle', 'enemy_lifepoints': 1},
            'combat_supply_loadout': {'finishers': {'Rock hammer': 1}},
        }
        ctx = _context(player, random_values=(0.932, 1.0, 1.0))
        ctx.cadence_live_enabled = True
        self.assertTrue(handle_combat_answer(ctx))
        self.assertEqual(player['combat_last_result']['drops'], {'Adamant boots': 1})
        self.assertEqual(player['inventory']['Adamant boots'], 1)
        inventory, equipment, ok = equip_item_pure(
            'Adamant boots', player['inventory'], player['equipment'], EQUIPMENT_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(equipment['feet'], 'Adamant boots')
        self.assertEqual(inventory['Adamant boots'], 0)
        player['inventory'], player['equipment'], ok = unequip_item_pure('feet', inventory, equipment)
        self.assertTrue(ok)
        self.assertEqual(player['inventory']['Adamant boots'], 1)
        offered, result = apply_ge_frontend_action_pure(
            player, 'place_offer',
            {'side': 'sell', 'item_name': 'Adamant boots', 'quantity': 1, 'unit_price': 1920},
            item_catalog=GE_ITEM_CATALOG,
        )
        self.assertTrue(result['ok'], result)
        self.assertEqual(offered['inventory']['Adamant boots'], 0)
        self.assertEqual(offered['ge_player_orders'][0]['item_name'], 'Adamant boots')
