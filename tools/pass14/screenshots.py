"""Capture Pass 14 Slayer UI evidence with real offscreen Qt widgets."""
from __future__ import annotations

import argparse
import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from aqt.qt import (
    QApplication,
    QColor,
    QLabel,
    QMainWindow,
    QPalette,
    QPoint,
    QPushButton,
    QRect,
    QTimer,
    QVBoxLayout,
    QWidget,
    Qt,
)
from tests import allow_modal_dialogs

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.ui import ui


PARENT_SIZES = {
    "default": (1000, 700),
    "parent-900x560": (900, 560),
}


def _apply_fusion_dark(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    for role, color in (
        (QPalette.ColorRole.Window, QColor(45, 45, 45)),
        (QPalette.ColorRole.WindowText, QColor(238, 238, 238)),
        (QPalette.ColorRole.Base, QColor(30, 30, 30)),
        (QPalette.ColorRole.AlternateBase, QColor(45, 45, 45)),
        (QPalette.ColorRole.Text, QColor(238, 238, 238)),
        (QPalette.ColorRole.Button, QColor(55, 55, 55)),
        (QPalette.ColorRole.ButtonText, QColor(238, 238, 238)),
        (QPalette.ColorRole.Highlight, QColor(55, 130, 70)),
        (QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)),
    ):
        palette.setColor(role, color)
    app.setPalette(palette)


def _mapped_rect(widget: QWidget, ancestor: QWidget) -> QRect:
    origin = widget.mapTo(ancestor, QPoint(0, 0))
    return QRect(origin, widget.size())


def _rect_record(rect: QRect) -> dict:
    return {
        "x": rect.x(),
        "y": rect.y(),
        "width": rect.width(),
        "height": rect.height(),
    }


def _label_probe(label: QLabel, ancestor: QWidget) -> dict:
    rect = _mapped_rect(label, ancestor)
    contents = label.contentsRect()
    metrics = label.fontMetrics()
    if label.wordWrap():
        measured = metrics.boundingRect(
            QRect(0, 0, max(1, contents.width()), 10_000),
            int(Qt.TextFlag.TextWordWrap),
            label.text(),
        )
        measured_width = measured.width()
        measured_height = measured.height()
    else:
        lines = label.text().splitlines() or [""]
        measured_width = max(metrics.horizontalAdvance(line) for line in lines)
        measured_height = metrics.lineSpacing() * len(lines)
    return {
        "kind": "QLabel",
        "object_name": label.objectName(),
        "text": label.text(),
        "visible": label.isVisibleTo(ancestor),
        "word_wrap": label.wordWrap(),
        "geometry": _rect_record(rect),
        "contents_size": [contents.width(), contents.height()],
        "measured_text_size": [measured_width, measured_height],
        "size_hint": [label.sizeHint().width(), label.sizeHint().height()],
        "minimum_size_hint": [
            label.minimumSizeHint().width(),
            label.minimumSizeHint().height(),
        ],
        "contained": ancestor.rect().contains(rect),
        "text_fits": (
            measured_width <= contents.width()
            and measured_height <= contents.height()
        ),
    }


def _button_probe(button: QPushButton, ancestor: QWidget) -> dict:
    rect = _mapped_rect(button, ancestor)
    return {
        "kind": "QPushButton",
        "object_name": button.objectName(),
        "text": button.text(),
        "visible": button.isVisibleTo(ancestor),
        "geometry": _rect_record(rect),
        "size_hint": [button.sizeHint().width(), button.sizeHint().height()],
        "minimum_size_hint": [
            button.minimumSizeHint().width(),
            button.minimumSizeHint().height(),
        ],
        "contained": ancestor.rect().contains(rect),
        "text_fits": button.sizeHint().width() <= button.width(),
    }


def _text_geometry(widget: QWidget) -> dict:
    rows = [
        _label_probe(label, widget)
        for label in widget.findChildren(QLabel)
        if label.text() and label.isVisibleTo(widget)
    ]
    rows.extend(
        _button_probe(button, widget)
        for button in widget.findChildren(QPushButton)
        if button.text() and button.isVisibleTo(widget)
    )
    overlaps = []
    for index, left in enumerate(rows):
        left_geometry = left["geometry"]
        left_rect = QRect(
            left_geometry["x"],
            left_geometry["y"],
            left_geometry["width"],
            left_geometry["height"],
        )
        for right in rows[index + 1 :]:
            right_geometry = right["geometry"]
            right_rect = QRect(
                right_geometry["x"],
                right_geometry["y"],
                right_geometry["width"],
                right_geometry["height"],
            )
            if left_rect.intersects(right_rect):
                overlaps.append([left["text"], right["text"]])
    return {
        "labels_and_buttons": rows,
        "overlaps": overlaps,
        "all_contained": all(row["contained"] for row in rows),
        "all_text_fits": all(row["text_fits"] for row in rows),
    }


def _save_grab(widget: QWidget, path: Path) -> dict:
    image = widget.grab()
    assert not image.isNull(), f"empty grab for {path}"
    assert image.save(str(path), "PNG"), f"could not save {path}"
    return {
        "path": str(path),
        "logical_size": [widget.width(), widget.height()],
        "pixel_size": [image.width(), image.height()],
        "device_pixel_ratio": image.devicePixelRatio(),
    }


def _dialog_capture(output_dir: Path, label: str, parent_size: tuple[int, int]) -> dict:
    parent = QMainWindow()
    parent.show()
    parent.resize(*parent_size)
    for _ in range(4):
        QApplication.processEvents()
    old_mw = ui.mw
    ui.mw = parent
    captured = {}

    def _capture_and_accept() -> None:
        modal = QApplication.activeModalWidget()
        assert modal is not None, "Slayer completion did not open a modal QDialog"
        modal.show()
        natural_size = modal.sizeHint().expandedTo(modal.minimumSizeHint())
        minimum = modal.minimumSize()
        maximum = modal.maximumSize()
        capture_width = min(
            max(natural_size.width(), minimum.width()), maximum.width()
        )
        capture_height = min(
            max(natural_size.height(), minimum.height()), maximum.height()
        )
        modal.resize(capture_width, capture_height)
        for _ in range(4):
            QApplication.processEvents()
        captured.update(
            {
                "window_title": modal.windowTitle(),
                "parent_requested_size": list(parent_size),
                "parent_actual_size": [parent.width(), parent.height()],
                "dialog_natural_size": [natural_size.width(), natural_size.height()],
                "dialog_minimum_size": [minimum.width(), minimum.height()],
                "dialog_maximum_size": [maximum.width(), maximum.height()],
                "dialog_capture_size": [modal.width(), modal.height()],
                "geometry": _text_geometry(modal),
                "image": _save_grab(
                    modal, output_dir / f"slayer-dialog-{label}.png"
                ),
            }
        )
        modal.accept()

    try:
        QTimer.singleShot(0, _capture_and_accept)
        with allow_modal_dialogs():
            ui.show_slayer_completion_dialog(17, "bears")
        for _ in range(4):
            QApplication.processEvents()
    finally:
        ui.mw = old_mw
        parent.close()
        parent.deleteLater()
        for _ in range(4):
            QApplication.processEvents()
    assert captured, "Slayer completion dialog returned without a capture"
    return captured


def _review_parent(size: tuple[int, int]) -> QMainWindow:
    parent = QMainWindow()
    central = QWidget(parent)
    parent.setCentralWidget(central)
    parent.form = types.SimpleNamespace(centralwidget=central)
    parent.mainLayout = QVBoxLayout()
    parent.mainLayout.setContentsMargins(0, 0, 0, 0)
    parent.mainLayout.setSpacing(0)
    card_web = QWidget(parent)
    card_web.setObjectName("reviewCardWeb")
    bottom_web = QWidget(parent)
    bottom_web.setObjectName("bottomWeb")
    bottom_web.setFixedHeight(72)
    parent.mainLayout.addWidget(card_web, 1)
    parent.mainLayout.addWidget(bottom_web, 0)
    central.setLayout(parent.mainLayout)
    parent.bottomWeb = bottom_web
    parent.reviewer = types.SimpleNamespace(web=card_web)
    parent.show()
    parent.resize(*size)
    for _ in range(4):
        QApplication.processEvents()
    return parent


def _reset_review_globals() -> None:
    for name in (
        "_REVIEW_HUD",
        "_REVIEW_STRIP",
        "_BANK_RUN_BUTTON",
        "_MAIN_MENU_BUTTON",
        "_REVIEW_CONTEXT_STRIP",
        "_SHOOTING_STAR_NOTICE_BAND",
        "_DND_BADGE",
        "_FARMING_BADGE",
        "_STATUS_POPOVER",
        "_STATUS_POPOVER_BADGE",
        "_FILL_DRAWER",
        "_EVENT_LOG_DRAWER",
    ):
        setattr(ui, name, None)


def _hud_capture(output_dir: Path, label: str, parent_size: tuple[int, int]) -> dict:
    parent = _review_parent(parent_size)
    old_mw = ui.mw
    old_config = ui.get_config_bool
    ui.mw = parent
    ui.get_config_bool = lambda _key, default=True: default
    _reset_review_globals()
    state = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    state.update(
        {
            "current_combat_target": "black_bear",
            "combat_action": "attack",
            "combat_attack_style": "aggressive",
            "combat_attack_style_type": "crush",
            "attack_level": 31,
            "strength_level": 26,
            "defense_level": 21,
            "constitution_level": 28,
            "combat_lifepoints": 280,
            "combat_kill_counts": {"black_bear": 13},
            "slayer_assignment": {
                "master_id": "turael_spria",
                "family_id": "bears",
                "initial_count": 17,
                "remaining": 4,
            },
        }
    )
    try:
        ui.update_review_hud(state, "Combat")
        hud = ui._REVIEW_HUD
        assert hud is not None, "ReviewHUD was not created"
        hud.show()
        hud.resize(hud.size())
        for _ in range(4):
            QApplication.processEvents()
        hud_in_parent = _mapped_rect(hud, parent)
        hud_in_strip = _mapped_rect(hud, ui._REVIEW_STRIP)
        assert parent.rect().contains(hud_in_parent), hud_in_parent
        assert ui._REVIEW_STRIP.rect().contains(hud_in_strip), hud_in_strip
        result = {
            "parent_requested_size": list(parent_size),
            "parent_actual_size": [parent.width(), parent.height()],
            "hud_geometry_in_parent": _rect_record(hud_in_parent),
            "hud_contained_in_parent": True,
            "hud_contained_in_strip": True,
            "geometry": _text_geometry(hud),
            "image": _save_grab(hud, output_dir / f"slayer-hud-{label}.png"),
        }
        texts = [
            row["text"] for row in result["geometry"]["labels_and_buttons"]
        ]
        assert "Slayer: 4 of 17 left" in texts, texts
        return result
    finally:
        for widget in (ui._REVIEW_STRIP, ui._REVIEW_CONTEXT_STRIP):
            if widget is not None:
                widget.close()
                widget.deleteLater()
        _reset_review_globals()
        ui.mw = old_mw
        ui.get_config_bool = old_config
        parent.close()
        parent.deleteLater()
        for _ in range(4):
            QApplication.processEvents()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    _apply_fusion_dark(app)
    assert app.platformName() == "offscreen", app.platformName()
    assert hasattr(ui, "show_slayer_completion_dialog"), (
        "S2 production UI is not present: missing show_slayer_completion_dialog"
    )

    report = {
        "qt_platform": app.platformName(),
        "style": app.style().objectName(),
        "interpretation": {
            "default_parent_logical_size": list(PARENT_SIZES["default"]),
            "compact_parent_logical_size": list(PARENT_SIZES["parent-900x560"]),
            "dialog_resize": (
                "Each real modal was shown and resized to its own natural size hint. "
                "The 560 logical-point requirement applies to the parent window height, "
                "not to the dialog."
            ),
            "grab_order": "show -> resize -> four processEvents passes -> grab",
        },
        "dialog": {},
        "hud": {},
    }
    for label, size in PARENT_SIZES.items():
        report["dialog"][label] = _dialog_capture(args.output_dir, label, size)
        report["hud"][label] = _hud_capture(args.output_dir, label, size)

    for surface in ("dialog", "hud"):
        for capture in report[surface].values():
            geometry = capture["geometry"]
            assert geometry["all_contained"], capture
            assert geometry["all_text_fits"], capture
            assert not geometry["overlaps"], capture
    output = args.output_dir / "probes.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
