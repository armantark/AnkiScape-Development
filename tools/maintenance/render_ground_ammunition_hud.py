#!/usr/bin/env python3
"""Capture the shown ammo HUD and prove title/button geometry in both palettes."""

from __future__ import annotations

import argparse
from itertools import product
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from aqt.qt import QApplication, QFont, QStyle, QStyleOptionButton
from tests.test_review_strip import ReviewStripTest
from tools.render_skill_panel_ui import _dark_palette, _light_palette


def capture_hud(case, output: Path, theme: str, width: int, height: int, count: int) -> dict:
    case.parent.show()
    case.parent.resize(width, height)
    for _ in range(8):
        QApplication.processEvents()
    hud = case.ui._REVIEW_HUD
    title, button = hud.title_lbl, hud.ammo_pickup_button
    option = QStyleOptionButton()
    button.initStyleOption(option)
    contents = button.style().subElementRect(QStyle.SubElement.SE_PushButtonContents, option, button)
    text_width = button.fontMetrics().horizontalAdvance(button.text())
    path = output / f"hud-fix-{theme}-{width}x{height}-ammo-{count}.png"
    window_path = path.with_stem(path.stem + "-window")
    for widget, image_path in ((hud, path), (case.parent, window_path)):
        if not widget.grab().save(str(image_path)):
            raise RuntimeError(f"Could not save {image_path}")
    assert title.text() == "Combat — Lv 51", title.text()
    assert title.width() >= title.sizeHint().width(), title.geometry()
    assert title.height() >= title.sizeHint().height(), title.geometry()
    assert title.geometry().bottom() < hud.progress.y()
    assert hud.combat_resources.height() >= hud.combat_resources.sizeHint().height()
    assert hud.chips_lbl.width() >= hud.chips_lbl.sizeHint().width()
    assert not title.geometry().intersects(button.geometry())
    assert hud.rect().contains(button.geometry()), button.geometry()
    assert hud.rect().contains(case.ui._BANK_RUN_BUTTON.geometry())
    assert not button.geometry().intersects(case.ui._BANK_RUN_BUTTON.geometry())
    probe = {"theme": theme, "size": [width, height], "text": button.text(),
             "device_pixel_ratio": hud.devicePixelRatioF(),
             "title": title.text(), "title_hint": [title.sizeHint().width(), title.sizeHint().height()],
             "title_rect": list(title.geometry().getRect()),
             "pickup_rect": list(button.geometry().getRect()),
             "bank_rect": list(case.ui._BANK_RUN_BUTTON.geometry().getRect()),
             "title_pickup_intersect": title.geometry().intersects(button.geometry()),
             "button_width": button.width(), "text_width": text_width,
             "contents_width": contents.width(), "cut_text": text_width > contents.width(),
             "hud_width": hud.width(), "image": str(path), "window_image": str(window_path)}
    return probe


def render(output: Path) -> None:
    ReviewStripTest.setUpClass()
    app = QApplication.instance()
    app.setStyle("Fusion")
    app.setFont(QFont("Helvetica Neue", 13))
    output.mkdir(parents=True, exist_ok=True)
    probes = []
    for theme, palette in (("dark", _dark_palette()), ("light", _light_palette())):
        app.setPalette(palette)
        case = ReviewStripTest()
        case.setUp()
        try:
            state = case._state()
            for skill in ("attack", "strength", "defense", "ranged", "magic", "constitution"):
                state[skill + "_level"] = 45
            state.update(equipment={"weapon": "Shortbow", "ammunition": "Bronze arrows"},
                         equipment_ammunition_count=840, combat_prayers_enabled=False,
                         combat_lifepoints=450, current_combat_target="chicken")
            for (width, height), count in product(((1000, 700), (720, 560)), (0, 42)):
                state["ground_ammunition"] = [{"name": "Bronze arrows", "count": count, "expires_at": 350}]
                case.ui.update_review_hud(state, "Combat")
                case.ui.update_review_status_badge(state)
                case.ui.update_review_bank_run_button(state, "combat", lambda: None, ammo_pickup_action=lambda: None)
                probes.append(capture_hud(case, output, theme, width, height, count))
        finally:
            case.tearDown()
    (output / "hud-fix-geometry.json").write_text(json.dumps(probes, indent=2) + "\n")
    print(json.dumps(probes, indent=2))
    if any(row["cut_text"] for row in probes):
        raise RuntimeError("Pickup button text is cut")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    render(parser.parse_args().output)
