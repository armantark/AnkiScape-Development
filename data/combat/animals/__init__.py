from __future__ import annotations

from .animals import (
    ENEMIES as _animals_enemies,
    BLACK_BEAR_DROPS,
    GIANT_BAT_DROPS,
    UNICORN_DROPS,
    WHITE_WOLF_DROPS,
    WOLF_LEVEL_11_DROPS,
)

from .birds import (
    ENEMIES as _birds_enemies,
    DUCK_LAND_DROPS,
    DUCK_WATER_DROPS,
)

from .lumbridge import (
    ENEMIES as _lumbridge_enemies,
)

from .rats import (
    ENEMIES as _rats_enemies,
    GIANT_RAT_DROPS,
)

from .scorpions import (
    ENEMIES as _scorpions_enemies,
    SCORPION_CHARM_DROPS,
)

from .spiders import (
    ENEMIES as _spiders_enemies,
)

from .training_staples import (
    ENEMIES as _training_staples_enemies,
)

ENEMIES = {}
for _family_enemies in (
    _animals_enemies,
    _birds_enemies,
    _lumbridge_enemies,
    _rats_enemies,
    _scorpions_enemies,
    _spiders_enemies,
    _training_staples_enemies,
):
    ENEMIES.update(_family_enemies)

del _family_enemies
del _animals_enemies
del _birds_enemies
del _lumbridge_enemies
del _rats_enemies
del _scorpions_enemies
del _spiders_enemies
del _training_staples_enemies

__all__ = (
    "ENEMIES",
    'BLACK_BEAR_DROPS',
    'DUCK_LAND_DROPS',
    'DUCK_WATER_DROPS',
    'GIANT_BAT_DROPS',
    'GIANT_RAT_DROPS',
    'SCORPION_CHARM_DROPS',
    'UNICORN_DROPS',
    'WHITE_WOLF_DROPS',
    'WOLF_LEVEL_11_DROPS',
)
