import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from tools import trim_icons
from tools.trim_icons import ADDON_ROOT, DEFAULT_DIRS, MAX_DIM, _iter_pngs, _select_backend


class UIAssetNormalizationTest(unittest.TestCase):
    def test_invalid_trim_target_prevents_changes_to_every_selected_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            valid = root / "valid"
            valid.mkdir()
            image = valid / "image.png"
            image.write_bytes(b"keep this image")
            for invalid in (root / "missing", image):
                with self.subTest(invalid=invalid), redirect_stderr(StringIO()) as errors:
                    with patch.object(
                        trim_icons, "_select_backend"
                    ) as backend:
                        with self.assertRaises(SystemExit) as failure:
                            trim_icons.main([str(valid), str(invalid)])
                    self.assertEqual(failure.exception.code, 2)
                    self.assertIn(f"Not a directory: {invalid}", errors.getvalue())
                    backend.assert_not_called()
                    self.assertEqual(image.read_bytes(), b"keep this image")

    def test_trim_dry_run_preserves_bytes_and_live_run_trims(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            image = Path(tmp_dir) / "image.png"
            image.write_bytes(b"padded")
            backend = (
                "canary",
                lambda _path: ((4, 4), (1, 1, 3, 3)),
                lambda path, _box: Path(path).write_bytes(b"trimmed"),
            )
            with patch.object(trim_icons, "_select_backend", return_value=backend):
                with redirect_stdout(StringIO()):
                    self.assertEqual(trim_icons.main(["--dry-run", tmp_dir]), 0)
                    self.assertEqual(image.read_bytes(), b"padded")
                    self.assertEqual(trim_icons.main([tmp_dir]), 0)
            self.assertEqual(image.read_bytes(), b"trimmed")

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
