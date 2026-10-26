from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_scraped_sprites_are_pretrimmed_on_disk(self) -> None:
        # Sprites are trimmed to their opaque box at build time (tools/trim_icons.py)
        # so the UI can use a plain QIcon(path) with no runtime cropping. Verify the
        # asset itself is tight: a padded 64x64 sprite would defeat that contract.
        import os as _os
        from aqt.qt import QImage
        flax = _os.path.join(self._ui.current_dir, "crafteditems", "flax.png")
        if not _os.path.exists(flax):
            self.skipTest("flax sprite not present")
        img = QImage(flax)
        self.assertFalse(img.isNull())
        self.assertLess(max(img.width(), img.height()), 64,
                        "flax sprite is not pre-trimmed; run tools/trim_icons.py")
