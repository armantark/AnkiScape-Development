#!/usr/bin/env python3
"""Render one real Shop-provider panel for repeatable visual review."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QListWidget, Qt  # type: ignore

from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _make_player_data,
    _open_shop_tab,
)
from tools.render_skill_panel_ui import _dark_palette


def render(args: argparse.Namespace) -> Path:
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName="test_shop_service_providers_browse_as_their_own_selector_entries"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    player_data = _make_player_data()
    player_data["inventory"].update(
        {
            "Coins": args.coins,
            "Long kebbit spike": args.spikes,
        }
    )
    dialog = case._open(player_data)
    _open_shop_tab(dialog)

    selector = dialog.findChild(QListWidget, "shopSelectionList")
    if selector is None:
        raise RuntimeError("Shop selector was not found")
    provider_item = next(
        (
            selector.item(index)
            for index in range(selector.count())
            if (
                isinstance(
                    selector.item(index).data(Qt.ItemDataRole.UserRole),
                    dict,
                )
                and selector.item(index)
                .data(Qt.ItemDataRole.UserRole)
                .get("kind")
                == "provider"
                and selector.item(index)
                .data(Qt.ItemDataRole.UserRole)
                .get("provider")
                == args.provider
            )
        ),
        None,
    )
    if provider_item is None:
        raise RuntimeError(f"Provider {args.provider!r} was not found")
    selector.setCurrentItem(provider_item)
    app.processEvents()

    dialog.show()
    dialog.resize(args.width, args.height)
    for _ in range(8):
        app.processEvents()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not dialog.grab().save(str(args.output)):
        raise RuntimeError(f"Could not save {args.output}")
    dialog.close()
    case.tearDown()
    return args.output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="Leon")
    parser.add_argument("--coins", type=int, default=400)
    parser.add_argument("--spikes", type=int, default=5)
    parser.add_argument("--width", type=int, default=1040)
    parser.add_argument("--height", type=int, default=560)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(render(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
