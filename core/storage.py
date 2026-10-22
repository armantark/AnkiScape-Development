"""storage.py - Persistence helpers for AnkiScape.

- player_data persists a 'config_version' which is updated to the
    CURRENT_CONFIG_VERSION on load via storage_pure.migrate_loaded_data.
- current_skill is stored separately under the 'ankiscape_current_skill' key.
"""
from copy import deepcopy

from aqt import mw
from .constants import ITEM_DEFINITIONS, ORE_DATA
from .storage_pure import default_player_data, migrate_loaded_data
from ..logic.inventory_pure import clamp_carried_view_to_bank
from ..data.quest.cold_war import COLD_WAR_SUIT_BACKFILL_KEY, COLD_WAR_SUIT_NAME


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


def saved_player_record(collection):
    """The stored save, else the backup a TEXT-row repair keeps; empty for a new player."""
    return collection.get_config(_PLAYER_DATA_KEY, None) or collection.get_config(_PLAYER_DATA_RECOVERY_KEY, None)


def _persist_quest_repairs(loaded, player_data):
    """Save greeting and suit repairs together without unrelated normalization."""
    patch = {}
    greeting = player_data["cold_war_greeting"]
    if greeting and greeting != loaded.get("cold_war_greeting"):
        patch["cold_war_greeting"] = list(greeting)
    if player_data[COLD_WAR_SUIT_BACKFILL_KEY] and loaded.get(COLD_WAR_SUIT_BACKFILL_KEY) is not True:
        patch[COLD_WAR_SUIT_BACKFILL_KEY] = True
    raw_inventory = loaded.get("inventory")
    raw_inventory = raw_inventory if isinstance(raw_inventory, dict) else {}
    suit_quantity = player_data["inventory"].get(COLD_WAR_SUIT_NAME, 0)
    raw_quantity = raw_inventory.get(COLD_WAR_SUIT_NAME, 0)
    if suit_quantity != raw_quantity or type(suit_quantity) is not type(raw_quantity):
        patch["inventory"] = deepcopy(raw_inventory)
        patch["inventory"][COLD_WAR_SUIT_NAME] = suit_quantity
    if not patch:
        return
    backfill = deepcopy(loaded)
    backfill.update(patch)
    _save_player_data_config(backfill)


def load_player_data():
    """Load player data and current skill from Anki config."""
    loaded = saved_player_record(mw.col)
    if loaded:
        player_data = migrate_loaded_data(deepcopy(loaded), ORE_DATA, ITEM_DEFINITIONS)
        _persist_quest_repairs(loaded, player_data)
    else:
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    current_skill = mw.col.get_config("ankiscape_current_skill", default="None")
    return player_data, current_skill


def save_player_data(player_data: dict, current_skill: str) -> None:
    """Persist player data and current skill to Anki config."""
    if carried := player_data.get("carried_inventory"):
        player_data["carried_inventory"] = {
            target_id: clamped
            for target_id, view in carried.items()
            if (clamped := clamp_carried_view_to_bank(view, player_data.get("inventory")))
        }
    _save_player_data_config(player_data)
    mw.col.set_config("ankiscape_current_skill", current_skill)
