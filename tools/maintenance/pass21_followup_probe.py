"""Replay the native seed and capture the shown HUD's geometry, without saves.

Run with QT_QPA_PLATFORM=offscreen .venv-qt/bin/python
tools/maintenance/pass21_followup_probe.py --output /tmp/pass21-followup-evidence.
"""

import argparse
from itertools import product
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pkg_alias  # noqa: F401

from ankiscape.logic_pure import logic_pure_combat_supplies as supplies
from ankiscape.logic_pure.combat.ammunition import equipped_ammo
from ankiscape.runtime.runtime_actions_combat import handle_combat_answer
from tests.test_combat_logic import _player
from tests.test_runtime_actions import _context
from tests.test_review_strip import ReviewStripTest


def replay_bank_runs(lobsters):
    player = _player(
        equipment={"weapon": "Shortbow"},
        inventory={"Bronze arrows": 500, "Iron arrows": 200, "Lobster": lobsters},
        combat_auto_eat_food=["Lobster"], combat_lifepoints=450,
        **{skill + "_level": 45 for skill in ("attack", "strength", "defense", "ranged", "magic", "constitution")},
    )
    triggers, cards = [], []
    bank_needed = supplies._combat_bank_run_needed

    def record_trigger(data, target, *args, **kwargs):
        needed = bank_needed(data, target, *args, **kwargs)
        if needed:
            carried_slots, loot_slots = supplies._combat_carried_slot_counts(data, target)
            triggers.append({
                "card": card, "ammo": equipped_ammo(data),
                "loaded_food": supplies._combat_loaded_food_count(data),
                "banked_food": supplies._combat_banked_auto_food_count(data),
                "supply_slots": supplies._combat_supply_slots_used(data),
                "carried_slots": carried_slots, "loot_slots": loot_slots,
                "carried": (data.get("carried_inventory") or {}).get(target, {}),
            })
        return needed

    with patch.object(supplies, "_combat_bank_run_needed", side_effect=record_trigger):
        for card in range(1, 11):
            ctx = _context(player, random_values=(0.5,) * 1000, review_action_multiplier=10)
            ctx.cadence_live_enabled = True
            assert handle_combat_answer(ctx), player.get("combat_last_result")
            result = player["combat_last_result"]
            cards.append({"card": card, "reason": result["reason"], "ammo_used": result["ammo_used"],
                          "bank_run": player["combat_bank_run"]})
    return {"bank_lobsters": lobsters, "rng": "constant 0.5", "triggers": triggers, "cards": cards}


def capture_hud(output):
    from aqt.qt import QApplication, QColor, QFont, QPalette

    ReviewStripTest.setUpClass()
    app = ReviewStripTest.app
    app.setStyle("Fusion")
    app.setFont(QFont("Helvetica Neue", 13))
    rows = []
    themes = (("light", "#f0f0f0", "#101010"), ("dark", "#202020", "#f0f0f0"))
    sizes = ((1000, 700), (667, 602), (720, 560))
    for (theme, background, text), (width, height), weapon in product(themes, sizes, ("Shortbow", "Iron sword")):
        palette = app.style().standardPalette()
        for role in (QPalette.ColorRole.Window, QPalette.ColorRole.Base, QPalette.ColorRole.Button):
            palette.setColor(role, QColor(background))
        for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText):
            palette.setColor(role, QColor(text))
        app.setPalette(palette)
        fixture = ReviewStripTest()
        fixture.setUp()
        try:
            state = fixture._state()
            for skill in ("attack", "strength", "defense", "ranged", "magic", "constitution"):
                state[skill + "_level"] = 45
            state.update(combat_lifepoints=450, current_combat_target="chicken")
            state["equipment"] = {"weapon": weapon}
            fixture.ui.update_review_hud(state, "Combat")
            fixture.ui.update_review_bank_run_button(state, "combat", ammo_pickup_action=lambda: None)
            fixture.parent.resize(width, height)
            for _ in range(5):
                QApplication.processEvents()
            hud = fixture.ui._REVIEW_HUD
            widgets = {"title": hud.title_lbl, "pickup": hud.ammo_pickup_button,
                       "player_bar": hud.progress, "resources": hud.combat_resources,
                       "target": hud.target_lbl, "enemy_bar": hud.enemy_progress, "chips": hud.chips_lbl}
            name = f"{theme}-{width}x{height}-{'pickup' if weapon == 'Shortbow' else 'no-pickup'}"
            assert hud.grab().save(str(output / (name + ".png")))
            assert fixture.parent.grab().save(str(output / (name + "-window.png")))
            rows.append({"case": name, "window_size": [fixture.parent.width(), fixture.parent.height()],
                         "hud_size": [hud.width(), hud.height()],
                         "title_text": hud.title_lbl.text(),
                         "title_required_height": hud.title_lbl.sizeHint().height(),
                         "title_font_height": hud.title_lbl.fontMetrics().height(),
                         "geometry": {key: list(widget.geometry().getRect()) for key, widget in widgets.items()}})
        finally:
            fixture.tearDown()
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    evidence = {"bank_replays": [replay_bank_runs(60), replay_bank_runs(0)], "hud": capture_hud(args.output)}
    (args.output / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
