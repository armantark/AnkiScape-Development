import unittest
from pathlib import Path

from tools.trim_icons import ADDON_ROOT, DEFAULT_DIRS, MAX_DIM, _iter_pngs, _select_backend


class UIAssetNormalizationTest(unittest.TestCase):
    def test_every_top_level_visual_asset_family_is_in_the_normalization_manifest(self):
        root = Path(ADDON_ROOT)
        asset_directories = {
            directory.name
            for directory in root.iterdir()
            if directory.is_dir() and any(directory.glob("*.png"))
        }
        self.assertEqual(asset_directories, set(DEFAULT_DIRS))

    def test_every_small_ui_asset_is_tight_cropped(self):
        backend_name, bbox_fn, _crop_fn = _select_backend()
        padded = []
        for directory_name in DEFAULT_DIRS:
            for path in _iter_pngs(str(Path(ADDON_ROOT) / directory_name)):
                result = bbox_fn(path)
                if result is None:
                    continue
                (width, height), box = result
                if max(width, height) > MAX_DIM:
                    continue
                if box != (0, 0, width, height):
                    padded.append(str(Path(path).relative_to(ADDON_ROOT)))

        preview = "\n".join(f"- {path}" for path in padded[:20])
        self.assertEqual(
            padded,
            [],
            f"{len(padded)} padded small UI asset(s) found. "
            f"Run tools/trim_icons.py after adding assets ({backend_name} audit).\n"
            f"{preview}",
        )


if __name__ == "__main__":
    unittest.main()
