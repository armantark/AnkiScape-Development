"""storage.py - Persistence helpers for AnkiScape.

- player_data persists a 'config_version' which is updated to the
    CURRENT_CONFIG_VERSION on load via storage_pure.migrate_loaded_data.
- current_skill is stored separately under the 'ankiscape_current_skill' key.
"""
from aqt import mw
from .constants import ITEM_DEFINITIONS, ORE_DATA
from .storage_pure import default_player_data, migrate_loaded_data


_PLAYER_DATA_KEY = "ankiscape_player_data"
_PLAYER_DATA_RECOVERY_KEY = "ankiscape_player_data_recovery"


def _is_legacy_config_type_error(exc: Exception) -> bool:
    """Return whether Anki rejected an older TEXT-backed config row."""
    return exc.__class__.__name__ == "DBError" and "InvalidColumnType" in str(exc)


def _save_player_data_config(player_data: dict) -> None:
    """Persist player data, repairing legacy TEXT rows without risking the save."""
    try:
        mw.col.set_config(_PLAYER_DATA_KEY, player_data)
    except Exception as exc:
        if not _is_legacy_config_type_error(exc):
            raise
        # Some older installs stored the JSON value as SQLite TEXT. Current Anki
        # expects a BLOB and cannot update or remove that row through the config
        # API. Keep a valid backup until the canonical row has been recreated.
        mw.col.set_config(_PLAYER_DATA_RECOVERY_KEY, player_data)
        mw.col.db.execute("DELETE FROM config WHERE key = ?", _PLAYER_DATA_KEY)
        mw.col.set_config(_PLAYER_DATA_KEY, player_data)
    if mw.col.get_config(_PLAYER_DATA_RECOVERY_KEY, default=None) is not None:
        mw.col.remove_config(_PLAYER_DATA_RECOVERY_KEY)


def load_player_data():
    """Load player data and current skill from Anki config."""
    loaded = mw.col.get_config(_PLAYER_DATA_KEY)
    if not loaded:
        loaded = mw.col.get_config(_PLAYER_DATA_RECOVERY_KEY)
    if loaded:
        player_data = migrate_loaded_data(dict(loaded), ORE_DATA, ITEM_DEFINITIONS)
    else:
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    current_skill = mw.col.get_config("ankiscape_current_skill", default="None")
    return player_data, current_skill


def save_player_data(player_data: dict, current_skill: str) -> None:
    """Persist player data and current skill to Anki config."""
    _save_player_data_config(player_data)
    mw.col.set_config("ankiscape_current_skill", current_skill)
