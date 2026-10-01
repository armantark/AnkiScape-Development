"""Capture the sourced bone-quest journal without touching a live Anki profile."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from aqt.qt import QApplication, QColor, QLabel, QLineEdit, QPalette
from tests.test_main_menu_widget import MainMenuWidgetTest, _expand_quest_card, _open_quests_tab
from tests.test_combat_quest_gate import _maxed_player_for_quest


def dark_palette():
    palette = QPalette()
    for role, color in (
        (QPalette.ColorRole.Window, "#242424"),
        (QPalette.ColorRole.WindowText, "#eeeeee"),
        (QPalette.ColorRole.Base, "#191919"),
        (QPalette.ColorRole.AlternateBase, "#303030"),
        (QPalette.ColorRole.Text, "#eeeeee"),
        (QPalette.ColorRole.Button, "#303030"),
        (QPalette.ColorRole.ButtonText, "#eeeeee"),
    ):
        palette.setColor(role, QColor(color))
    return palette


def capture_theme(output, theme):
    app = QApplication.instance()
    app.setPalette(dark_palette() if theme == "dark" else app.style().standardPalette())
    case = MainMenuWidgetTest(methodName="runTest")
    case.setUp()
    try:
        player = _maxed_player_for_quest("rag_and_bone_man")
        player["current_quest"] = "rag_and_bone_man"
        player["quests"]["rag_and_bone_man"] = {"started": True, "progress": 4, "completed": False}
        player["inventory"] = {"Logs": 8}
        player["quest_combat_encounters"] = {"rag_and_bone_man": [
            f"rag_and_bone_man_{suffix}" for suffix in (
                "goblin_1", "bear_2", "big_frog_3", "ram_4", "unicorn_5", "monkey_6",
            )
        ]}
        dialog = case._open(player, current_skill="Quests")
        dialog.show()
        _open_quests_tab(dialog)
        dialog.findChild(QLineEdit, "questSearchInput").setText("Rag and Bone Man")
        _expand_quest_card(dialog, "rag_and_bone_man")
        default_size = dialog.size()
        captures = []
        for label, height in (("default", default_size.height()), ("560", 560)):
            dialog.resize(default_size.width(), height)
            for _ in range(5):
                app.processEvents()
            filename = f"quest-stats-{theme}-{label}.png"
            if not dialog.grab().save(str(output / filename)):
                raise RuntimeError(f"Could not save {filename}")
            captures.append({"file": filename, "width": dialog.width(), "height": dialog.height()})
        texts = [label.text() for label in dialog.findChildren(QLabel) if label.isVisible()]
        assert any("Giant rat level 6" in text for text in texts), texts
        return {"theme": theme, "captures": captures, "visible_labels": texts}
    finally:
        case.tearDown()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    MainMenuWidgetTest.app.setStyle("Fusion")
    evidence = [capture_theme(args.output, theme) for theme in ("light", "dark")]
    (args.output / "visual-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    images = "".join(
        f'<h2>{row["theme"]} — {capture["width"]} × {capture["height"]}</h2>'
        f'<img src="{capture["file"]}" alt="Rag and Bone Man quest journal">'
        for row in evidence for capture in row["captures"]
    )
    (args.output / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Quest stat visual proof</title>'
        '<style>body{margin:20px;font:16px sans-serif}img{max-width:100%;display:block}</style>'
        '<h1>Quest stat visual proof</h1>' + images
    )
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
