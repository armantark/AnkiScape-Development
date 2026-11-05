"""Capture the settled ammo and queue states using fresh offscreen menu fixtures."""

import argparse
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from aqt.qt import QApplication, QColor, QListWidget, QPalette, QPushButton  # noqa: E402
from tests.action_queue.test_queue_plan_rows import PlanRowClickTest, _ARROWTIPS  # noqa: E402
from tests.test_main_menu_widget import _open_equipment_tab  # noqa: E402


def set_theme(app, dark):
    app.setStyle("Fusion")
    palette = app.style().standardPalette()
    if dark:
        for role, colour in (("Window", "#252525"), ("Base", "#181818"), ("AlternateBase", "#292929"),
                             ("Text", "#eeeeee"), ("WindowText", "#eeeeee"),
                             ("Button", "#333333"), ("ButtonText", "#eeeeee")):
            palette.setColor(getattr(QPalette.ColorRole, role), QColor(colour))
    app.setPalette(palette)


def make_state(case, state):
    if state == "manual":
        addon = case._plan_addon("evidence_manual", equipment={"weapon": "Shortbow"}, inventory={"Bronze arrows": 840})
        addon.on_equip_item("Bronze arrows")
        dialog = case._menu(addon, "Crafting")
        _open_equipment_tab(dialog)
        worn = dialog.findChild(QListWidget, "equipmentList")
        row = next(worn.item(i) for i in range(worn.count()) if "Manual" in worn.item(i).text())
        width = worn.fontMetrics().horizontalAdvance(row.text()) + worn.iconSize().width() + 12
        assert width < worn.viewport().width(), (width, worn.viewport().width())
        return dialog, {"slot": row.text(), "text_width": width, "viewport_width": worn.viewport().width()}
    if state == "funded":
        addon = case._plan_addon("evidence_funded", (_ARROWTIPS, 60), fletching_level=10,
                                 inventory={"Bronze bar": 4, "Headless arrows": 35})
        dialog = case._menu(addon, "Fletching")
        case._click_row(dialog, "bronze_arrows")
    else:
        addon = case._plan_addon("evidence_gray", crafting_level=20, current_craft="cut_sapphire",
                                 inventory={"Uncut sapphire": 20})
        dialog = case._menu(addon, "Crafting")
        case._click_row(dialog, "form_bowl_unfired")
    return dialog, {"count": case._count(dialog).value(), "maximum": case._count(dialog).maximum(),
                    "add": case._visible(dialog, QPushButton, "queueAddButton").isEnabled(),
                    "start": case._header(dialog).isEnabled(), "suffix": case._count(dialog).suffix()}


def capture(output, theme, state):
    case = PlanRowClickTest("test_a_row_without_inputs_keeps_the_saved_target_when_nothing_runs_it")
    case.setUp()
    set_theme(case.app, theme == "dark")
    try:
        dialog, probe = make_state(case, state)
        for size in ("default", "560"):
            if size == "default":
                dialog.resize(dialog.sizeHint())
            else:
                dialog.resize(900, 560)
            case._settle()
            if state == "manual":
                worn = dialog.findChild(QListWidget, "equipmentList")
                row = next(worn.item(i) for i in range(worn.count()) if "Manual" in worn.item(i).text())
                assert worn.visualItemRect(row).height() >= worn.sizeHintForIndex(worn.indexFromItem(row)).height()
                assert worn.horizontalScrollBar().maximum() == 0
            path = output / f"{theme}-{state}-{size}.png"
            assert dialog.grab().save(str(path))
        return {"theme": theme, "state": state, **probe}
    finally:
        for window in QApplication.topLevelWidgets():
            window.close()
        case.doCleanups()
        case.tearDown()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    probes = [capture(args.output, theme, state) for theme in ("light", "dark") for state in ("manual", "gray", "funded")]
    (args.output / "probes.json").write_text(json.dumps(probes, indent=2) + "\n")
    print(json.dumps(probes, indent=2))
    app.processEvents()


if __name__ == "__main__":
    main()
