#!/usr/bin/env python3
"""Render the real ammo HUD in both palettes and probe button text geometry."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from aqt.qt import QApplication, QStyle, QStyleOptionButton
from tests.test_review_strip import ReviewStripTest
from tools.render_skill_panel_ui import _dark_palette, _light_palette


def render(output: Path) -> None:
    ReviewStripTest.setUpClass()
    app = QApplication.instance()
    app.setStyle("Fusion")
    output.mkdir(parents=True, exist_ok=True)
    probes = []
    for theme, palette in (("dark", _dark_palette()), ("light", _light_palette())):
        app.setPalette(palette)
        case = ReviewStripTest()
        case.setUp()
        try:
            state = case._state()
            state.update(equipment={"weapon": "Shortbow", "ammunition": "Bronze arrows"},
                         equipment_ammunition_count=840, combat_prayers_enabled=False,
                         ground_ammunition=[{"name": "Bronze arrows", "count": 840, "expires_at": 350}])
            case.ui.update_review_hud(state, "Combat")
            case.ui.update_review_bank_run_button(state, "combat", lambda: None)
            case.ui.update_review_bank_run_button(state, "combat", ammo_pickup_action=lambda: None)
            for width, height in ((1000, 700), (740, 560)):
                case.parent.show()
                case.parent.resize(width, height)
                for _ in range(8):
                    app.processEvents()
                button = case.ui._REVIEW_HUD.ammo_pickup_button
                option = QStyleOptionButton()
                button.initStyleOption(option)
                contents = button.style().subElementRect(QStyle.SubElement.SE_PushButtonContents, option, button)
                text_width = button.fontMetrics().horizontalAdvance(button.text())
                path = output / f"ammo-{theme}-{width}x{height}.png"
                if not case.parent.grab().save(str(path)):
                    raise RuntimeError(f"Could not save {path}")
                probe = {"theme": theme, "size": [width, height], "text": button.text(),
                         "button_width": button.width(), "text_width": text_width,
                         "contents_width": contents.width(), "cut_text": text_width > contents.width(),
                         "hud_width": case.ui._REVIEW_HUD.width(), "image": str(path)}
                probes.append(probe)
        finally:
            case.tearDown()
    (output / "geometry.json").write_text(json.dumps(probes, indent=2) + "\n")
    print(json.dumps(probes, indent=2))
    if any(row["cut_text"] for row in probes):
        raise RuntimeError("Pickup button text is cut")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    render(parser.parse_args().output)
