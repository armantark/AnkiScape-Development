"""storage.py - Persistence helpers for AnkiScape.

- player_data persists a 'config_version' which is updated to the
    CURRENT_CONFIG_VERSION on load via storage_pure.migrate_loaded_data.
- current_skill is stored separately under the 'ankiscape_current_skill' key.
"""
from aqt import mw
from .constants import ITEM_DEFINITIONS, ORE_DATA
from .storage_pure import default_player_data, migrate_loaded_data


def load_player_data():
    """Load player data and current skill from Anki config."""
    loaded = mw.col.get_config("ankiscape_player_data")
    if loaded:
        player_data = migrate_loaded_data(dict(loaded), ORE_DATA, ITEM_DEFINITIONS)
    else:
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    current_skill = mw.col.get_config("ankiscape_current_skill", default="None")
    return player_data, current_skill


def save_player_data(player_data: dict, current_skill: str) -> None:
    """Persist player data and current skill to Anki config."""
    mw.col.set_config("ankiscape_player_data", player_data)
    mw.col.set_config("ankiscape_current_skill", current_skill)
