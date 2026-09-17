from __future__ import annotations

from .mogres import ENEMIES as _mogres_enemies

from .skeletal_wyverns import (
    ENEMIES as _skeletal_wyverns_enemies,
)

from .slayer_caves import (
    ENEMIES as _slayer_caves_enemies,
    CAVE_HORROR_DROPS,
)

from .slayer_coastal import (
    ENEMIES as _slayer_coastal_enemies,
    BRINE_RAT_DROPS,
    JUNGLE_HORROR_DROPS,
    MOLANISK_DROPS,
    SEA_SNAKE_HATCHLING_DROPS,
    SEA_SNAKE_YOUNG_DROPS,
)

from .slayer_creatures import (
    ENEMIES as _slayer_creatures_enemies,
    TUROTH_DROPS,
)

from .slayer_dark import (
    ENEMIES as _slayer_dark_enemies,
)

from .slayer_desert import (
    ENEMIES as _slayer_desert_enemies,
    DUST_DEVIL_DROPS,
    OGRE_DROPS,
)

from .slayer_elemental import (
    ENEMIES as _slayer_elemental_enemies,
    SHADOW_WARRIOR_DROPS,
)

from .slayer_finishers import (
    ENEMIES as _slayer_finishers_enemies,
    DESERT_LIZARD_DROPS,
    GARGOYLE_DROPS,
    MUTATED_ZYGOMITE_DROPS,
    MUTATED_ZYGOMITE_FINISHER,
    ROCKSLUG_DROPS,
)

ENEMIES = {}
for _family_enemies in (
    _mogres_enemies,
    _skeletal_wyverns_enemies,
    _slayer_caves_enemies,
    _slayer_coastal_enemies,
    _slayer_creatures_enemies,
    _slayer_dark_enemies,
    _slayer_desert_enemies,
    _slayer_elemental_enemies,
    _slayer_finishers_enemies,
):
    ENEMIES.update(_family_enemies)

del _family_enemies
del _mogres_enemies
del _skeletal_wyverns_enemies
del _slayer_caves_enemies
del _slayer_coastal_enemies
del _slayer_creatures_enemies
del _slayer_dark_enemies
del _slayer_desert_enemies
del _slayer_elemental_enemies
del _slayer_finishers_enemies

__all__ = (
    "ENEMIES",
    'BRINE_RAT_DROPS',
    'CAVE_HORROR_DROPS',
    'DESERT_LIZARD_DROPS',
    'DUST_DEVIL_DROPS',
    'GARGOYLE_DROPS',
    'JUNGLE_HORROR_DROPS',
    'MOLANISK_DROPS',
    'MUTATED_ZYGOMITE_DROPS',
    'MUTATED_ZYGOMITE_FINISHER',
    'OGRE_DROPS',
    'ROCKSLUG_DROPS',
    'SEA_SNAKE_HATCHLING_DROPS',
    'SEA_SNAKE_YOUNG_DROPS',
    'SHADOW_WARRIOR_DROPS',
    'TUROTH_DROPS',
)
