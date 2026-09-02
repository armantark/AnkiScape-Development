from __future__ import annotations

from .leather_dragons import (
    ENEMIES as _leather_dragons_enemies,
    BLACK_DRAGON_DROPS,
    BLUE_DRAGON_DROPS,
    RED_DRAGON_DROPS,
)

from .metal_dragons import (
    ENEMIES as _metal_dragons_enemies,
    BRONZE_DRAGON_DROPS,
    IRON_DRAGON_DROPS,
    STEEL_DRAGON_DROPS,
)

ENEMIES = {}
for _family_enemies in (
    _leather_dragons_enemies,
    _metal_dragons_enemies,
):
    ENEMIES.update(_family_enemies)

del _family_enemies
del _leather_dragons_enemies
del _metal_dragons_enemies

__all__ = (
    "ENEMIES",
    'BLACK_DRAGON_DROPS',
    'BLUE_DRAGON_DROPS',
    'BRONZE_DRAGON_DROPS',
    'IRON_DRAGON_DROPS',
    'RED_DRAGON_DROPS',
    'STEEL_DRAGON_DROPS',
)
