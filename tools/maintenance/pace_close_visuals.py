"""Capture the approved pace dialog and Settings page without native Anki."""

import argparse
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from aqt.qt import QApplication, QCheckBox, QComboBox, QLabel, QPushButton, QSpinBox, QWidget
from tests import test_main_menu_widget as menu
from tests.pace.test_pace_settings_qt import _cut_off, _dark_palette
from ankiscape.logic.pace.onboarding import pace_onboarding_plan_pure
from ankiscape.ui.ui_pace_settings import PaceDialog


def settle():
    for _ in range(8):
        QApplication.processEvents()


def control_clipped(control, text):
    if control.height() < control.minimumSizeHint().height():
        return True
    if isinstance(control, (QCheckBox, QPushButton, QSpinBox, QComboBox)):
        return control.width() < control.minimumSizeHint().width()
    if not isinstance(control, QLabel) or not text:
        return False
    if control.wordWrap():
        return control.height() < control.heightForWidth(control.width())
    return control.fontMetrics().horizontalAdvance(text) > control.width()


def control_geometry(page):
    rows = []
    for control in page.findChildren(QWidget):
        if not control.isVisible() or not isinstance(control, (QLabel, QCheckBox, QPushButton, QSpinBox, QComboBox)):
            continue
        text = getattr(control, "text", lambda: "")()
        rows.append({"name": control.objectName() or text, "text": text,
                     "size": [control.width(), control.height()],
                     "minimum_height": control.minimumSizeHint().height(),
                     "clipped": control_clipped(control, text)})
    return rows


def capture_settings(output, theme, height):
    case = menu.MainMenuWidgetTest()
    case.setUp()
    try:
        dialog = case._open(menu._make_player_data())
        dialog.show()
        dialog.resize(720, height or dialog.height())
        tabs = menu._find_main_tabs(dialog)
        tabs.setCurrentIndex(next(i for i in range(tabs.count()) if tabs.tabText(i) == "Settings"))
        scroll = tabs.currentWidget()
        page = scroll.widget()
        page.findChild(QCheckBox, "settingsWorldDayFollowToggle").setChecked(False)
        developer = next(box for box in page.findChildren(QCheckBox) if box.text().startswith("Enable developer mode"))
        with patch("ankiscape.core.debug.set_debug_enabled"):
            developer.setChecked(True)
        settle()
        tag = f"settings-{theme}-{height or 'default'}"
        rows = control_geometry(page)
        report = {"dialog": [dialog.width(), dialog.height()],
                  "viewport": [scroll.viewport().width(), scroll.viewport().height()],
                  "page": [page.width(), page.height()],
                  "vertical_range": scroll.verticalScrollBar().maximum(),
                  "horizontal_range": scroll.horizontalScrollBar().maximum(),
                  "frame_shape": scroll.frameShape().name,
                  "vertical_policy": scroll.verticalScrollBarPolicy().name,
                  "controls": rows, "clipped": [row["name"] for row in rows if row["clipped"]]}
        for position, value in (("top", 0), ("bottom", scroll.verticalScrollBar().maximum())):
            scroll.verticalScrollBar().setValue(value)
            settle()
            scroll.grab().save(str(output / f"{tag}-{position}.png"))
        dialog.resize(720, 900)
        settle()
        report["tall_canary"] = {"range": scroll.verticalScrollBar().maximum(),
                                  "bar_visible": scroll.verticalScrollBar().isVisible()}
        dialog.close()
        return tag, report
    finally:
        case.tearDown()


def capture_dialog(output, theme, existing):
    plan = pace_onboarding_plan_pure(existing_player=existing, speed=None,
                                    legacy_speed=4 if existing else None,
                                    follow_study_volume=None, world_day_cards=None, suggestion=300)
    dialog = PaceDialog(plan, 300)
    dialog.show()
    dialog.resize(dialog.width(), dialog.height())
    settle()
    tag = f"dialog-{theme}-{'existing' if existing else 'new'}"
    clipped = _cut_off(dialog)
    dialog.grab().save(str(output / f"{tag}.png"))
    dialog.close()
    dialog.deleteLater()
    return tag, {"clipped": clipped}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output
    output.mkdir(parents=True, exist_ok=False)
    menu.MainMenuWidgetTest.setUpClass()
    app = QApplication.instance()
    app.setStyle("Fusion")
    reports = {}
    for theme in ("light", "dark"):
        app.setPalette(_dark_palette() if theme == "dark" else app.style().standardPalette())
        for height in (None, 560):
            tag, report = capture_settings(output, theme, height)
            reports[tag] = report
        for existing in (False, True):
            tag, report = capture_dialog(output, theme, existing)
            reports[tag] = report
    (output / "geometry.json").write_text(json.dumps(reports, indent=2) + "\n")
    failures = {key: value["clipped"] for key, value in reports.items() if value["clipped"]}
    print(json.dumps({"surfaces": len(reports), "clipped": failures}, indent=2))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
