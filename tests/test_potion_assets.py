import json
import os
import unittest
from pathlib import Path

from constants import ITEM_DEFINITIONS
from potion_data import (
    EMPTY_FLASK_ITEM,
    POTION_FAMILIES,
    VIAL_ITEM,
    potion_dose_name,
    potion_flask_name,
    potion_item_names,
)
from tools.fetch_potion_assets import asset_manifest


ROOT = Path(__file__).resolve().parents[1]


class PotionAssetTest(unittest.TestCase):
    def test_manifest_covers_every_potion_container_state_needing_new_art(self):
        manifest = asset_manifest()
        expected = set(potion_item_names()) - {VIAL_ITEM[0]}

        self.assertEqual({request.item_name for request in manifest}, expected)
        self.assertEqual(len(manifest), 1 + (len(POTION_FAMILIES) * 10))
        self.assertTrue(
            all(request.output_path.is_relative_to(ROOT) for request in manifest)
        )
        manifest_by_item = {request.item_name: request for request in manifest}
        self.assertEqual(
            manifest_by_item[EMPTY_FLASK_ITEM[0]].wiki_title,
            "Potion flask.png",
        )
        self.assertEqual(
            manifest_by_item[potion_flask_name("Attack potion", 6)].wiki_title,
            "Attack flask (6).png",
        )

    def test_every_registered_potion_state_has_existing_provenanced_art(self):
        definitions = {
            definition.storage_key: definition
            for definition in ITEM_DEFINITIONS
        }
        provenance = json.loads(
            (ROOT / "assets_provenance.json").read_text(encoding="utf-8")
        )

        for item_name in potion_item_names():
            with self.subTest(item_name=item_name):
                definition = definitions[item_name]
                self.assertIsNotNone(definition.asset_path)
                self.assertTrue(os.path.isfile(definition.asset_path))
                relative_path = str(
                    Path(definition.asset_path).resolve().relative_to(ROOT)
                )
                self.assertIn(relative_path, provenance)

    def test_flask_dose_art_uses_the_registered_family_names(self):
        manifest_by_item = {
            request.item_name: request
            for request in asset_manifest()
        }

        for base, spec in POTION_FAMILIES.items():
            for dose in spec["doses"]:  # type: ignore[union-attr]
                item_name = potion_dose_name(base, dose)
                self.assertEqual(
                    manifest_by_item[item_name].wiki_title,
                    f"{item_name}.png",
                )
            for dose in spec["flask_doses"]:  # type: ignore[union-attr]
                item_name = potion_flask_name(base, dose)
                self.assertEqual(
                    manifest_by_item[item_name].wiki_title,
                    f"{item_name}.png",
                )


if __name__ == "__main__":
    unittest.main()
