from __future__ import annotations

from .canifis import (
    ENEMIES as _canifis_enemies,
)

from .undead import (
    ENEMIES as _undead_enemies,
    GHOST_DROPS,
    SKELETON_HIGH_DROPS,
    SKELETON_LOW_DROPS,
    ZOMBIE_DROPS,
    ZOMBIE_LEVEL_25_DROPS,
)

ENEMIES = {}
for _family_enemies in (
    _canifis_enemies,
    _undead_enemies,
):
    ENEMIES.update(_family_enemies)

del _family_enemies
del _canifis_enemies
del _undead_enemies

__all__ = (
    "ENEMIES",
    'GHOST_DROPS',
    'SKELETON_HIGH_DROPS',
    'SKELETON_LOW_DROPS',
    'ZOMBIE_DROPS',
    'ZOMBIE_LEVEL_25_DROPS',
)
