"""Source-audited item actions for filled impling jars."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ImplingJarReward:
    item: str
    minimum: int
    maximum: int
    weight: int


# Wiki oldid 6151109 is the period enumeration. Darkan's original
# dragon_impling.json at c6fbe036 supplies the ranges and probabilities.
# Rows absent from the live item registry stay out, as do defective finished-
# ammunition rows 11212/11230; the empty row preserves their probability share.
IMPLING_JAR_DATA: Dict[str, Tuple[ImplingJarReward, ...]] = {
    "Dragon impling jar": (
        ImplingJarReward("Dragon longsword", 1, 1, 803_531),
        ImplingJarReward("Dragon bolt tips", 10, 49, 803_531),
        ImplingJarReward("Dragon bolts", 3, 49, 803_531),
        ImplingJarReward("Dragon dart tip", 105, 350, 803_531),
        ImplingJarReward("Dragon arrowtips", 100, 500, 803_531),
        ImplingJarReward("Dragon bones", 52, 99, 187_466),
        ImplingJarReward("Dragonstone", 3, 6, 187_466),
        ImplingJarReward("Magic seed", 1, 1, 187_466),
        ImplingJarReward("Dragonstone ammy", 2, 3, 25_000),
        ImplingJarReward("Amulet of glory", 2, 3, 25_000),
        ImplingJarReward("Snapdragon seed", 6, 6, 25_000),
        ImplingJarReward("Summer pie", 5, 15, 25_000),
        ImplingJarReward("Death tiara", 1, 1, 12_500),
        ImplingJarReward("", 0, 0, 2_007_447),
    ),
}

