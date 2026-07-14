import json
import os
import unittest
from pathlib import Path

from constants import HERBLORE_DATA, HERBLORE_ITEM_IMAGES
from herblore_data import CLEAN_TARGETS, DUNGEONEERING_CLEAN_TARGETS
from target_metadata import herblore_target_rows
from tools.fetch_herblore_assets import asset_manifest


ROOT = Path(__file__).resolve().parents[1]


class HerbloreAssetTest(unittest.TestCase):
    def test_manifest_is_skill_icon_plus_live_clean_herb_outputs(self):
        manifest = asset_manifest()
        expected_items = {"Herblore skill icon", *(target.output_item for target in CLEAN_TARGETS)}
        deferred_items = {target.output_item for target in DUNGEONEERING_CLEAN_TARGETS}

        self.assertEqual({request.item_name for request in manifest}, expected_items)
        self.assertTrue(deferred_items.isdisjoint(request.item_name for request in manifest))
        self.assertEqual(len(manifest), len(CLEAN_TARGETS) + 1)
        self.assertTrue(all(request.output_path.is_relative_to(ROOT) for request in manifest))

    def test_live_clean_rows_have_existing_rs3_provenanced_icons(self):
        rows = herblore_target_rows(
            {"herblore_level": 99, "inventory": {}},
            HERBLORE_DATA,
            HERBLORE_ITEM_IMAGES,
        )
        rows_by_id = {row.target_id: row for row in rows}
        provenance = json.loads((ROOT / "assets_provenance.json").read_text(encoding="utf-8"))

        for target in CLEAN_TARGETS:
            row = rows_by_id[target.id]
            self.assertIsNotNone(row.icon_path, target.id)
            self.assertTrue(os.path.isfile(row.icon_path), target.id)
            key = str(Path(row.icon_path).resolve().relative_to(ROOT))
            self.assertEqual(provenance[key]["source_wiki"], "rs3", target.id)

        for target in DUNGEONEERING_CLEAN_TARGETS:
            self.assertNotIn(target.id, rows_by_id)

    def test_herblore_skill_icon_is_real_and_provenanced(self):
        icon_path = ROOT / "icon" / "herblore_icon.png"
        provenance = json.loads((ROOT / "assets_provenance.json").read_text(encoding="utf-8"))

        self.assertTrue(icon_path.is_file())
        self.assertEqual(provenance["icon/herblore_icon.png"]["source_wiki"], "rs3")
        self.assertNotEqual(icon_path.read_bytes(), (ROOT / "icon" / "achievement_icon.png").read_bytes())


if __name__ == "__main__":
    unittest.main()
