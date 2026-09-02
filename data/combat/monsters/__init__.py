from __future__ import annotations

from .dagannoths import (
    ENEMIES as _dagannoths_enemies,
    DAGANNOTH_DROPS,
)

from .demons import (
    ENEMIES as _demons_enemies,
    IMP_DROPS,
)

from .giants import (
    ENEMIES as _giants_enemies,
    FIRE_GIANT_DROPS,
    HILL_GIANT_DROPS,
    ICE_GIANT_DROPS,
    MOSS_GIANT_DROPS,
)

from .stronghold_of_security import (
    ENEMIES as _stronghold_of_security_enemies,
)

from .wilderness_bosses import (
    ENEMIES as _wilderness_bosses_enemies,
)

ENEMIES = {}
for _family_enemies in (
    _dagannoths_enemies,
    _demons_enemies,
    _giants_enemies,
    _stronghold_of_security_enemies,
    _wilderness_bosses_enemies,
):
    ENEMIES.update(_family_enemies)

del _family_enemies
del _dagannoths_enemies
del _demons_enemies
del _giants_enemies
del _stronghold_of_security_enemies
del _wilderness_bosses_enemies

__all__ = (
    "ENEMIES",
    'DAGANNOTH_DROPS',
    'FIRE_GIANT_DROPS',
    'HILL_GIANT_DROPS',
    'ICE_GIANT_DROPS',
    'IMP_DROPS',
    'MOSS_GIANT_DROPS',
)
