from __future__ import annotations

from .barbarians import (
    ENEMIES as _barbarians_enemies,
)

from .elves import (
    ENEMIES as _elves_enemies,
    ELF_WARRIOR_DROPS,
)

from .goblins import (
    ENEMIES as _goblins_enemies,
    GOBLIN_HIGHER_LEVEL_DROPS,
    GOBLIN_LEVEL_2_DROPS,
)

from .hobgoblins import (
    ENEMIES as _hobgoblins_enemies,
    HOBGOBLIN_ARMED_DROPS,
    HOBGOBLIN_UNARMED_DROPS,
)

from .humanoid_criminals import (
    ENEMIES as _humanoid_criminals_enemies,
    CHAOS_DWARF_DROPS,
    HAAKON_DROPS,
    HAM_GUARD_DROPS,
    OUTLAW_DROPS,
)

from .humanoid_guards import (
    ENEMIES as _humanoid_guards_enemies,
    GUARD_DROPS,
    WHITE_KNIGHT_LEVEL_36_DROPS,
    WHITE_KNIGHT_LEVEL_38_DROPS,
    WHITE_KNIGHT_LEVEL_39_DROPS,
    WHITE_KNIGHT_LEVEL_42_DROPS,
)

from .humanoid_villagers import (
    ENEMIES as _humanoid_villagers_enemies,
    CHAOS_DRUID_DROPS,
    DWARF_DROPS,
    FARMER_DROPS,
    LOW_LEVEL_HUMANOID_DROPS,
    MONK_OF_ZAMORAK_LEVEL_45_DROPS,
    PIRATE_DROPS,
)

from .tzhaar import (
    ENEMIES as _tzhaar_enemies,
    TZHAAR_KET_DROPS,
)

from .warriors import (
    ENEMIES as _warriors_enemies,
)

from .warriors_guild import (
    ENEMIES as _warriors_guild_enemies,
    CYCLOPS_WARRIORS_GUILD_DROPS,
    CYCLOSSUS_WARRIORS_GUILD_DROPS,
)

ENEMIES = {}
for _family_enemies in (
    _barbarians_enemies,
    _elves_enemies,
    _goblins_enemies,
    _hobgoblins_enemies,
    _humanoid_criminals_enemies,
    _humanoid_guards_enemies,
    _humanoid_villagers_enemies,
    _tzhaar_enemies,
    _warriors_enemies,
    _warriors_guild_enemies,
):
    ENEMIES.update(_family_enemies)

del _family_enemies
del _barbarians_enemies
del _elves_enemies
del _goblins_enemies
del _hobgoblins_enemies
del _humanoid_criminals_enemies
del _humanoid_guards_enemies
del _humanoid_villagers_enemies
del _tzhaar_enemies
del _warriors_enemies
del _warriors_guild_enemies

__all__ = (
    "ENEMIES",
    'CHAOS_DRUID_DROPS',
    'CHAOS_DWARF_DROPS',
    'CYCLOPS_WARRIORS_GUILD_DROPS',
    'CYCLOSSUS_WARRIORS_GUILD_DROPS',
    'DWARF_DROPS',
    'ELF_WARRIOR_DROPS',
    'FARMER_DROPS',
    'GOBLIN_HIGHER_LEVEL_DROPS',
    'GOBLIN_LEVEL_2_DROPS',
    'GUARD_DROPS',
    'HAAKON_DROPS',
    'HAM_GUARD_DROPS',
    'HOBGOBLIN_ARMED_DROPS',
    'HOBGOBLIN_UNARMED_DROPS',
    'LOW_LEVEL_HUMANOID_DROPS',
    'MONK_OF_ZAMORAK_LEVEL_45_DROPS',
    'OUTLAW_DROPS',
    'PIRATE_DROPS',
    'TZHAAR_KET_DROPS',
    'WHITE_KNIGHT_LEVEL_36_DROPS',
    'WHITE_KNIGHT_LEVEL_38_DROPS',
    'WHITE_KNIGHT_LEVEL_39_DROPS',
    'WHITE_KNIGHT_LEVEL_42_DROPS',
)
