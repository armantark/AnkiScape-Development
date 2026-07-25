"""Process-local confirmations for dangerous Combat targets."""

from __future__ import annotations

from typing import Mapping

from ..logic_pure.logic_pure import combat_wilderness_equipment_risk_pure


_CONFIRMED_WILDERNESS_RISKS: set[str] = set()


def wilderness_combat_risk_fingerprint(
    player_data: Mapping[str, object],
    target_id: str,
    enemy: Mapping[str, object],
) -> str:
    risk = enemy.get("wilderness_risk")
    if not isinstance(risk, Mapping):
        return ""
    equipment_risk = combat_wilderness_equipment_risk_pure(player_data, enemy)
    return repr(
        (
            target_id,
            float(risk.get("ambush_chance", 0.0) or 0.0),
            int(risk.get("max_hit", 0) or 0),
            bool(equipment_risk.get("skulled")),
            bool(equipment_risk.get("protect_item")),
            tuple(equipment_risk.get("kept_slots", {}).items()),
            tuple(equipment_risk.get("lost_slots", {}).items()),
        )
    )


def confirm_wilderness_combat_risk(fingerprint: str) -> None:
    if fingerprint:
        _CONFIRMED_WILDERNESS_RISKS.add(fingerprint)


def wilderness_combat_risk_confirmed(fingerprint: str) -> bool:
    return bool(fingerprint and fingerprint in _CONFIRMED_WILDERNESS_RISKS)


def reset_wilderness_combat_confirmations() -> None:
    _CONFIRMED_WILDERNESS_RISKS.clear()
