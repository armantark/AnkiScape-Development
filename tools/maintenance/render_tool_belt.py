#!/usr/bin/env python3
"""Capture the real Bank tool belt and item menu before and after a UI change."""

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from aqt.qt import QApplication, QScrollArea, QWidget

from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data, _open_bank_tab
from tests.ui_flows.qt_text_fit import text_fit_defects
from tools.render_skill_panel_ui import _dark_palette, _light_palette


def capture(output_dir: Path, label: str, theme: str) -> dict:
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(methodName="runTest")
    case.setUp()
    app = QApplication.instance()
    app.setStyle("Fusion")
    app.setPalette(_dark_palette() if theme == "dark" else _light_palette())
    try:
        data = _make_player_data()
        data["inventory"] = {"Tiara mould": 1, "Chain link mould": 1, "Logs": 3}
        dialog = case._open(data)
        dialog.show()
        dialog.resize(720, 560)
        _open_bank_tab(dialog)
        for _ in range(8):
            app.processEvents()
        panel = dialog.findChild(QWidget, "toolbeltPanel")
        page = dialog.findChild(QScrollArea, "bankTabScroll")
        page.ensureWidgetVisible(panel)
        for _ in range(4):
            app.processEvents()
        defects = text_fit_defects(page.widget())
        menu = dialog._ankiscape_equip_menu_for("Tiara mould")
        menu.popup(dialog.mapToGlobal(dialog.rect().center()))
        for _ in range(4):
            app.processEvents()
        defects.extend(text_fit_defects(menu))
        for action in menu.actions():
            if action.isSeparator():
                continue
            if menu.fontMetrics().horizontalAdvance(action.text()) > menu.actionGeometry(action).width():
                defects.append(f"Menu text clipped: {action.text()}")
        for name, widget in (("bank", dialog), ("menu", menu), ("toolbelt", panel)):
            path = output_dir / f"{label}-{theme}-{name}.png"
            if not widget.grab().save(str(path)):
                raise RuntimeError(f"Could not save {path}")
        return {"theme": theme, "size": [dialog.width(), dialog.height()], "text_fit_defects": defects}
    finally:
        case.tearDown()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = [capture(args.output_dir, args.label, theme) for theme in ("light", "dark")]
    print(json.dumps(results, indent=2))
    if any(result["text_fit_defects"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
