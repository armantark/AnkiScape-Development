"""Six bedroom identities; advanced families are recognition keys only."""

from ..equipment_data import EquipmentBonuses, EquipmentItem

SILVER_SEARCHES = (
    {
        'owner': 'Anna',
        'barrel_id': 2656,
        'name': 'Silver necklace',
        'clean_id': 1796,
        'dusted_name': 'Silver necklace (dusted)',
        'dusted_id': 1797,
        'print_name': "Anna's print",
        'print_id': 1816,
        'proof_id': 'murder_mystery.search_anna_barrel',
    },
    {
        'owner': 'Bob',
        'barrel_id': 2657,
        'name': 'Silver cup',
        'clean_id': 1798,
        'dusted_name': 'Silver cup (dusted)',
        'dusted_id': 1799,
        'print_name': "Bob's print",
        'print_id': 1817,
        'proof_id': 'murder_mystery.search_bob_barrel',
    },
    {
        'owner': 'Carol',
        'barrel_id': 2658,
        'name': 'Silver bottle',
        'clean_id': 1800,
        'dusted_name': 'Silver bottle (dusted)',
        'dusted_id': 1801,
        'print_name': "Carol's print",
        'print_id': 1818,
        'proof_id': 'murder_mystery.search_carol_barrel',
    },
    {
        'owner': 'David',
        'barrel_id': 2659,
        'name': 'Silver book',
        'clean_id': 1802,
        'dusted_name': 'Silver book (dusted)',
        'dusted_id': 1803,
        'print_name': "David's print",
        'print_id': 1819,
        'proof_id': 'murder_mystery.search_david_barrel',
    },
    {
        'owner': 'Elizabeth',
        'barrel_id': 2660,
        'name': 'Silver needle',
        'clean_id': 1804,
        'dusted_name': 'Silver needle (dusted)',
        'dusted_id': 1805,
        'print_name': "Elizabeth's print",
        'print_id': 1820,
        'proof_id': 'murder_mystery.search_elizabeth_barrel',
    },
    {
        'owner': 'Frank',
        'barrel_id': 2661,
        'name': 'Silver pot',
        'clean_id': 1806,
        'dusted_name': 'Silver pot (dusted)',
        'dusted_id': 1807,
        'print_name': "Frank's print",
        'print_id': 1821,
        'proof_id': 'murder_mystery.search_frank_barrel',
    },
)

MURDER_MYSTERY_SILVER_ITEMS = {
    'Silver necklace': {
        'category': 'equipment',
        'item_id': 1796,
        'stackable': False,
        'tradeable': False,
        'source': (
            'https://runescape.wiki/w/index.php?title=Silver+necklace&oldid=5144754&action=raw; '
            'sources/silver-necklace-5144754.txt:20; '
            'data/quest/murder_mystery_silver.sources.json (W1/W2/A2, D1:64-69; '
            'configuration identities, not original server transactions)'
        ),
        'members': 'Yes',
        'quest': 'Yes',
        'store': 'No',
        'value': 1,
        'equipable': 'Yes',
        'high': 0,
        'low': 0,
        'weight': 1,
    },
    'Silver cup': {
        'category': 'material',
        'item_id': 1798,
        'stackable': False,
        'tradeable': False,
        'source': (
            'https://runescape.wiki/w/index.php?title=Silver+cup&oldid=5144752&action=raw; '
            'sources/silver-cup-5144752.txt:20; '
            'data/quest/murder_mystery_silver.sources.json (W1/W2/A2, D1:64-69; '
            'configuration identities, not original server transactions)'
        ),
        'members': 'Yes',
        'quest': 'Yes',
        'store': 'No',
        'value': 1,
        'equipable': 'No',
        'high': 'No',
        'low': 'No',
    },
    'Silver bottle': {
        'category': 'material',
        'item_id': 1800,
        'stackable': False,
        'tradeable': False,
        'source': (
            'https://runescape.wiki/w/index.php?title=Silver+bottle&oldid=5144751&action=raw; '
            'sources/silver-bottle-5144751.txt:20; '
            'data/quest/murder_mystery_silver.sources.json (W1/W2/A2, D1:64-69; '
            'configuration identities, not original server transactions)'
        ),
        'members': 'Yes',
        'quest': 'Yes',
        'store': 'No',
        'value': 1,
        'equipable': 'No',
        'high': 'No',
        'low': 'No',
    },
    'Silver book': {
        'category': 'material',
        'item_id': 1802,
        'stackable': False,
        'tradeable': False,
        'source': (
            'https://runescape.wiki/w/index.php?title=Silver+book&oldid=6391161&action=raw; '
            'sources/silver-book-6391161.txt:20; '
            'data/quest/murder_mystery_silver.sources.json (W1/W2/A2, D1:64-69; '
            'configuration identities, not original server transactions)'
        ),
        'members': 'Yes',
        'quest': 'Yes',
        'store': 'No',
        'value': 1,
        'equipable': 'No',
        'high': 'No',
        'low': 'No',
    },
    'Silver needle': {
        'category': 'material',
        'item_id': 1804,
        'stackable': False,
        'tradeable': False,
        'source': (
            'https://runescape.wiki/w/index.php?title=Silver+needle&oldid=5144755&action=raw; '
            'sources/silver-needle-5144755.txt:21; '
            'data/quest/murder_mystery_silver.sources.json (W1/W2/A2, D1:64-69; '
            'configuration identities, not original server transactions)'
        ),
        'members': 'Yes',
        'quest': 'Yes',
        'store': 'No',
        'value': 1,
        'equipable': 'No',
        'high': 'No',
        'low': 'No',
        'weight': 0,
    },
    'Silver pot': {
        'category': 'material',
        'item_id': 1806,
        'stackable': False,
        'tradeable': False,
        'source': (
            'https://runescape.wiki/w/index.php?title=Silver+pot&oldid=5144756&action=raw; '
            'sources/silver-pot-5144756.txt:21; '
            'data/quest/murder_mystery_silver.sources.json (W1/W2/A2, D1:64-69; '
            'configuration identities, not original server transactions)'
        ),
        'members': 'Yes',
        'quest': 'Yes',
        'store': 'No',
        'value': 1,
        'equipable': 'No',
        'high': 'No',
        'low': 'No',
    },
}


def murder_mystery_silver_equipment_data_as_dict():
    # Neck/zero bonuses: non-beta necklace oldid 5144754:24,30,32-49.
    # Wear identity: retained cache row 1796. Other fields encode a nonweapon.
    return {'Silver necklace': EquipmentItem(
        item_name='Silver necklace', slot='neck', source_item_id=1796,
        combat_skill=None, required_level=1, two_handed=False,
        equipment_type='neck', bonuses=EquipmentBonuses(), attack_speed=0,
        skill_requirements=(), weapon_type=-1,
        source=MURDER_MYSTERY_SILVER_ITEMS['Silver necklace']['source'],
        source_status='period wiki and retained cache equipment identity',
    )}
