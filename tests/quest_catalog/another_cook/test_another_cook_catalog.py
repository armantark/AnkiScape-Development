"""Opening-only source overlay, distinct cache identities, and retained art."""

import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import COOKING_DATA, COOKING_ITEM_IMAGES, ITEM_DEFINITIONS, QUEST_DATA
from ankiscape.data.quest import another_cook as source
from ankiscape.data.quest.catalog import _quest_from_catalog, _quest_with_stage_requirements
from ankiscape.data.quest import serializers
from ankiscape.data.quest_action_proof_data import ANOTHER_COOK_DIRTY_BLAST_PROOF
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG

ROOT = Path(__file__).resolve().parents[3]


class AnotherCookCatalogTest(unittest.TestCase):
    def test_only_first_requirement_journal_and_qualified_source_change(self):
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row['id'] == source.QUEST_ID)
        original = _quest_with_stage_requirements(_quest_from_catalog(generated), generated)
        assembled = source.apply_another_cook_opening(original)
        self.assertEqual(assembled.stages, 4)
        for field in original.__dataclass_fields__:
            if field not in ('stage_requirements', 'journal_stages', 'source'):
                self.assertEqual(getattr(assembled, field), getattr(original, field), field)
        self.assertEqual(assembled.stage_requirements[1:], original.stage_requirements[1:])
        self.assertEqual(assembled.journal_stages[1:], original.journal_stages[1:])
        self.assertEqual(assembled.journal_stages[0].journal, source.STATIC_JOURNAL)
        self.assertEqual(assembled.source, f'Opening only: {source.OPENING_SOURCE}; later fields retain: {original.source}')
        self.assertIn('oldid=36823822', assembled.source)
        with patch.object(serializers, 'QUESTS', (assembled,)):
            self.assertEqual(QUEST_DATA[source.QUEST_ID], serializers.quests_as_dict()[source.QUEST_ID])
        unrelated = _quest_from_catalog(PRE_EOC_QUEST_CATALOG[0])
        self.assertIs(source.apply_another_cook_opening(unrelated), unrelated)

    def test_no_generated_bundle_or_generic_sentinel_in_live_opening(self):
        row = QUEST_DATA[source.QUEST_ID]['stage_requirements'][0]
        self.assertEqual(row['stage'], 1)
        self.assertEqual(row['description'], 'Prepare a Dirty blast for the Cook')
        self.assertEqual(row['required_skills'], (dict(skill_id='cooking', display_name='Cooking', level=10),))
        self.assertEqual(row['required_actions'], (ANOTHER_COOK_DIRTY_BLAST_PROOF,))
        for field in ('required_inventory', 'required_inventory_options', 'consumed_inventory',
                      'consumed_inventory_options', 'produced_inventory', 'required_tools',
                      'required_routes', 'auto_actions', 'combat_encounters'):
            self.assertFalse(row[field], field)
        self.assertEqual(row['source'], source.OPENING_SOURCE)
        self.assertEqual(hashlib.sha256((ROOT / 'generated/quest_catalog_generated.py').read_bytes()).hexdigest(),
                         '33d1c8294cff9b808732aab3cce756727fd79573cedef153d24c170fec3e78d2')

    def test_distinct_registered_identities_and_metadata(self):
        items = {item.storage_key: item for item in ITEM_DEFINITIONS}
        self.assertEqual(source.STORAGE_IDENTITIES, {'Ashes': 592, 'Fruit blast': 2084,
                         'Fruit blast (9514)': 9514, "Premade fr' blast": 2034, 'Dirty blast': 7497})
        for name, item_id in source.STORAGE_IDENTITIES.items():
            self.assertEqual(items[name].source_item_id, item_id)
        for name in source.OPENING_ITEM_DATA:
            self.assertEqual(items[name].category, 'material')
            self.assertFalse(items[name].tradeable)
            self.assertFalse(items[name].stackable)
            self.assertNotIn(name, QUEST_DATA[source.QUEST_ID]['rewards'])
        self.assertNotIn('Fruit Blast', source.STORAGE_IDENTITIES)
        self.assertEqual(len({items[name].id for name in source.STORAGE_IDENTITIES}), 5)
        self.assertIn('storage compatibility', ' '.join(source.SOURCE_LIMITATIONS))

    def test_bundled_dirty_blast_exact_bytes_and_provenance(self):
        path = ROOT / 'data/quest/assets/dirty_blast.png'
        self.assertEqual(Path(COOKING_ITEM_IMAGES['Dirty blast']), path)
        self.assertEqual(COOKING_ITEM_IMAGES['Fruit blast (9514)'], COOKING_ITEM_IMAGES['Fruit blast'])
        self.assertEqual(len(path.read_bytes()), 877)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), '19f6993fdede8346b17e19626893fe879fe8f6b0c3e9b24a7d295ca29e78bc68')
        self.assertEqual(tuple(int.from_bytes(path.read_bytes()[i:i + 4], 'big') for i in (16, 20)), (25, 32))
        record = json.loads((path.parent / 'assets_provenance.json').read_text())['data/quest/assets/dirty_blast.png']
        self.assertEqual(record, dict(file_page_url='https://runescape.wiki/w/File:Dirty_blast.png',
            file_title='Dirty blast.png', image_url='https://runescape.wiki/images/archive/20140502063922%21Dirty_blast.png?13056',
            license_string='unknown', mediatype='BITMAP', mime='image/png', sha1='fd93be6e0566c2140a174872f10333a64a185190',
            size=877, source_wiki='rs3', timestamp='2011-11-20T02:17:11Z'))

    def test_placeholder_conflict_and_period_source_metadata_retained(self):
        self.assertEqual(source.DIRTY_BLAST_BASE_XP, 5.0)
        register = (ROOT / 'memory-bank/placeholder-values.md').read_text()
        row = next(line for line in register.splitlines() if '| `quests.another_cook.dirty_blast_xp`' in line)
        for text in ('5.0', '6084510', 'Darkan', 'Independent pre-cutoff numeric'):
            self.assertIn(text, row)
        self.assertEqual(source.PERIOD_SOURCES[0]['sha256'], 'c583ca6b47a69d622bf73851315e67c02468bc2f2939e90085696defe219d1e5')
        self.assertEqual(source.PERIOD_SOURCES[0]['timestamp'], '2012-11-06T06:20:48Z')
        self.assertIn('not checked-negative', ' '.join(source.SOURCE_LIMITATIONS))

    def test_normal_mixing_keeps_2084_level6_50xp_and_consumed_glass(self):
        recipe = COOKING_DATA['mix_fruit_blast']
        self.assertEqual((recipe['cooked_item'], recipe['cooked_item_id']), ('Fruit blast', 2084))
        self.assertEqual((recipe['level'], recipe['exp']), (6, 50.0))
        self.assertEqual(recipe['requirements'], {'Cocktail glass': 1, 'Pineapple': 1, 'Lemon': 1,
                         'Orange': 1, 'Lemon slices': 1, 'Cocktail shaker': 1})
        self.assertEqual(recipe['byproducts'], {'Cocktail shaker': 1})


# Pins from packet sources/assets/verification.json. Local hashes bind normalized
# art; raw hashes bind the downloaded source bytes. Pixel equality is a separate
# observation and does not establish source-byte identity or resolve limitations.
RETAINED_ASSET_VERIFICATION = (('cookingitems/fruit_blast.png', 'c371186a47f56d067538e875f6e57b613e4b4d33d3bf4a4be4d0143eb86eafde', 'a0c94458db1f4c2bea367c5e1940f1a37dc10688472bd5fd89aad7525bdb4520', '90cc8c3c84d7ae59db9ab19b32c008eaf7a1b02a164436b07a8aa0183ebdb1c4', False, False), ('firemakingitems/ashes.png', '0b121e7b90bc56d022be164d3473dfd3cc1a6be674a6de65b99b30162b04d962', 'ee671c82daa2a6ee597dc7492a73dafda58db92e818873069c495373cd9097d4', '2ae2e275cb4d645911c99aba3d3a5922533d338db461d0154f1c39f81abdaba2', True, True), ('cookingitems/cocktail_shaker.png', 'd489d4cda9caeae639c4da5039436167bebe48bb6d3af08749278ec16e566123', '7ed4a5bf69c8cddfc8e1f4ddb55459f60037135f013f28fd8e626db006109123', '3dc94a799c354180e179f7b4a67675cc0ecfdb4b9944e7e2e67c43ba1a6f8879', True, False), ('cookingitems/cocktail_glass.png', '63aca0009cc5ca68debafab9dc1fa7a9a083b989c103cd0dbc39a1a9f927b8ed', '5117443fd3abfeb3d0bfcec5f01aca7e201e22babd7e980e3968147db7888bde', 'fd8a354de91c6483dec33ac9183fe633caaa80691c635054eadb2e4eb9c4a0bb', True, True), ('cookingitems/lemon.png', 'ae2a8153a60f80153a96e0ac71b26edc416721bfe070b23656660b250dce2936', '2b7126debb982aaa07d5f8d646b9ba062d6c4396749162ba0a97224e49b583e6', '24802dba032d7f97d49fc90e5cae8f0cd00796f74b9035b0f37e3f148bdf7089', True, False), ('cookingitems/lemon_slices.png', '8f2d3c848707bd3e259a83489245f46d0a49e0a6a397608d9c9bdd2f90c6b459', '95ed1e031254352ec8ab91e63a18a82f4b47685b04cb4f5e5299e97f392ae430', '9241ff9e6313fd20a6eb7cc83cc8df0d3b0086b61ffde2ddfebb3b90fb3d5104', True, False), ('cookingitems/orange.png', 'eaebc5bb924e8173d331a0f9059db6e675fea31e51a54b1be7121b0f07c99b95', 'be01acd3cc009938ae973bd93894166f71a9f5c558969c893a735b929e417104', '97aec31133a8b913e076777bc35e924c59f30e0c6cea99dc3bac152bc74716ae', True, False), ('cookingitems/pineapple.png', 'a25a62ba5fac3fe432b466736a946b31260902e70b2f04579621af86c6dda4ad', '7179454f70a9159dd433c58840930efdba1355d414a021563e23fb4b433c128a', '01431c9cd397f76ffa2681dbf28a6192f6552879252f8dbab38985f79ee6ed0d', True, True), ('shopitems/knife.png', '24a3f1783252884b8e09dea76730159d7ed307b9ddd320809d8244902132dba9', 'f6cf8d65b6d2709ece6cbfcd23f173ebe8080a667adeb474bb35a875608ef674', '75f4eafe7a835429b0452571aceea863527d8a8c92ff9e43a37ee2ca3b79977f', False, True), ('combatitems/coins.png', '0a5fbe34ac3c164eeaa882f16d841b8f6b9a58e222bebf3b14d487301d8a41ac', '7dcdc7d7b9dc7237d5c15260ff7525cbac21a5c18f05864d22e0f6192dd4fb72', '457677bc9532f65c3c7b5abd45e804178443f375332cc3142e4aac453673a426', False, True))


class AnotherCookExistingAssetsTest(unittest.TestCase):
    def test_existing_ingredient_tool_art_and_retained_provenance_are_unchanged(self):
        provenance = json.loads((ROOT / 'assets_provenance.json').read_text())
        for relative, local_hash, metadata_hash, raw_hash, pixels_equal, source_sha1_matches in RETAINED_ASSET_VERIFICATION:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file())
                self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), local_hash)
                self.assertEqual(hashlib.sha256(json.dumps(provenance[relative], sort_keys=True).encode()).hexdigest(), metadata_hash)
                self.assertNotEqual(local_hash, raw_hash)
                self.assertEqual(pixels_equal, relative not in ('cookingitems/fruit_blast.png', 'shopitems/knife.png', 'combatitems/coins.png'))
                self.assertEqual(source_sha1_matches, relative in ('firemakingitems/ashes.png', 'cookingitems/cocktail_glass.png', 'cookingitems/pineapple.png', 'shopitems/knife.png', 'combatitems/coins.png'))
        items = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for name in ('Ashes', 'Fruit blast', "Premade fr' blast", 'Knife', 'Coins', 'Cocktail glass',
                     'Cocktail shaker', 'Lemon', 'Lemon slices', 'Pineapple', 'Orange'):
            self.assertTrue(Path(items[name].asset_path).is_file(), name)
