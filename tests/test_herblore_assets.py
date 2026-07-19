import json
import os
import struct
import unittest
from pathlib import Path

from constants import HERBLORE_DATA, HERBLORE_ITEM_IMAGES
from herblore_data import (
    CLEAN_TARGETS,
    DUNGEONEERING_CLEAN_TARGETS,
    DUNGEONEERING_FINISHED_TARGETS,
    DUNGEONEERING_UNF_TARGETS,
    FINISHED_TARGETS,
    UNF_TARGETS,
)
from target_metadata import herblore_target_rows
from tools.fetch_herblore_assets import asset_manifest


ROOT = Path(__file__).resolve().parents[1]


class HerbloreAssetTest(unittest.TestCase):
    def test_shrink_me_quick_assets_are_normalized_to_their_visible_bounds(self):
        expected_dimensions = {
            "shrink_me_quick.png": (20, 29),
            "shrunk_ogleroot.png": (23, 29),
        }
        for filename, dimensions in expected_dimensions.items():
            with self.subTest(filename=filename):
                data = (ROOT / "herbloreitems" / filename).read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", data[16:24]), dimensions)

    def test_manifest_is_skill_icon_plus_every_live_herblore_output(self):
        manifest = asset_manifest()
        live_targets = CLEAN_TARGETS + UNF_TARGETS + FINISHED_TARGETS
        deferred_targets = (
            DUNGEONEERING_CLEAN_TARGETS
            + DUNGEONEERING_UNF_TARGETS
            + DUNGEONEERING_FINISHED_TARGETS
        )
        expected_items = {
            "Herblore skill icon",
            "Shrunk ogleroot",
            *(target.output_item for target in live_targets),
        }
        live_items = {target.output_item for target in live_targets}
        deferred_only_items = {target.output_item for target in deferred_targets} - live_items

        self.assertEqual({request.item_name for request in manifest}, expected_items)
        self.assertTrue(deferred_only_items.isdisjoint(request.item_name for request in manifest))
        self.assertEqual(len(manifest), len(live_targets) + 2)
        self.assertTrue(all(request.output_path.is_relative_to(ROOT) for request in manifest))
        manifest_by_item = {request.item_name: request for request in manifest}
        self.assertEqual(
            manifest_by_item["Guam potion (unf)"].wiki_title,
            "Guam potion (unfinished).png",
        )
        self.assertEqual(
            manifest_by_item["Anti-p supermix (2)"].wiki_title,
            "Super antipoison mix (2).png",
        )
        self.assertEqual(
            manifest_by_item["Shrunk ogleroot"].wiki_title,
            "Shrunk ogleroot.png",
        )

    def test_every_live_row_has_an_existing_provenanced_icon(self):
        rows = herblore_target_rows(
            {"herblore_level": 99, "inventory": {}},
            HERBLORE_DATA,
            HERBLORE_ITEM_IMAGES,
        )
        rows_by_id = {row.target_id: row for row in rows}
        provenance = json.loads((ROOT / "assets_provenance.json").read_text(encoding="utf-8"))

        for target in CLEAN_TARGETS + UNF_TARGETS + FINISHED_TARGETS:
            row = rows_by_id[target.id]
            self.assertIsNotNone(row.icon_path, target.id)
            self.assertTrue(os.path.isfile(row.icon_path), target.id)
            key = str(Path(row.icon_path).resolve().relative_to(ROOT))
            self.assertEqual(provenance[key]["source_wiki"], "rs3", target.id)

        for target in (
            DUNGEONEERING_CLEAN_TARGETS
            + DUNGEONEERING_UNF_TARGETS
            + DUNGEONEERING_FINISHED_TARGETS
        ):
            self.assertNotIn(target.id, rows_by_id)

        root_path = ROOT / "herbloreitems" / "shrunk_ogleroot.png"
        self.assertTrue(root_path.is_file())
        self.assertEqual(
            provenance[str(root_path.relative_to(ROOT))]["source_wiki"],
            "rs3",
        )

    def test_herblore_skill_icon_is_real_and_provenanced(self):
        icon_path = ROOT / "icon" / "herblore_icon.png"
        provenance = json.loads((ROOT / "assets_provenance.json").read_text(encoding="utf-8"))

        self.assertTrue(icon_path.is_file())
        self.assertEqual(provenance["icon/herblore_icon.png"]["source_wiki"], "osrs")
        self.assertEqual(
            provenance["icon/herblore_icon.png"]["file_title"],
            "Herblore icon (detail).png",
        )
        self.assertNotEqual(icon_path.read_bytes(), (ROOT / "icon" / "achievement_icon.png").read_bytes())

    def test_juju_farming_dose_family_is_registered_and_provenanced(self):
        provenance = json.loads((ROOT / "assets_provenance.json").read_text(encoding="utf-8"))
        for dose in range(1, 5):
            with self.subTest(dose=dose):
                path = ROOT / "herbloreitems" / f"juju_farming_potion_{dose}.png"
                self.assertTrue(path.is_file())
                self.assertEqual(provenance[str(path.relative_to(ROOT))]["source_wiki"], "rs3")


if __name__ == "__main__":
    unittest.main()
