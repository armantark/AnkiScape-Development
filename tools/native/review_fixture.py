"""Explicit fixture preparation inside an already-open disposable Anki profile."""

from pathlib import Path
import tempfile


def prepare_state_fixture(mw, *, disposable_base: str) -> dict:
    """Seed a fresh collection, then require a normal profile reopen before use.

    Import this module through the installed add-on package. This function does
    not launch Anki, load a profile, or replace the add-on's in-memory state.
    """
    base = Path(disposable_base)
    if not base.is_absolute():
        raise ValueError("The disposable base must be an absolute path")
    base = base.resolve(strict=True)
    temp_roots = (Path(tempfile.gettempdir()).resolve(), Path("/tmp").resolve())
    if not base.is_dir() or not any(
        base != root and base.is_relative_to(root) for root in temp_roots
    ):
        raise ValueError("The disposable base must be a directory below a temporary root")

    collection = mw.col
    collection_path = Path(collection.path).resolve(strict=True)
    if not collection_path.is_file() or not collection_path.is_relative_to(base):
        raise ValueError("The actual collection file is outside the disposable base")

    # Only path metadata is read before the boundary above succeeds.
    if collection.note_count():
        raise ValueError("The fixture requires a collection with no existing notes")
    notetype = collection.models.by_name("Basic")
    if notetype is None or [field["name"] for field in notetype["flds"]] != ["Front", "Back"]:
        raise ValueError("The fixture requires the standard Basic note type")

    from ...core.constants import ITEM_DEFINITIONS, ORE_DATA
    from ...core.storage_pure import migrate_loaded_data

    from .player_data import merge_player_data

    # These values define the scenario independently of future player defaults.
    seed = merge_player_data({
        "inventory": {"Logs": 1, "Ashes": 0},
        "firemaking_level": 1,
        "firemaking_exp": 0,
        "current_firemaking": "logs",
    })
    # Persist the same values that the normal profile load will expose.
    seed = migrate_loaded_data(seed, ORE_DATA, ITEM_DEFINITIONS)

    deck_id = collection.decks.id("AnkiScape native state acceptance")
    note_ids = []
    for number in range(1, 21):
        note = collection.new_note(notetype)
        note["Front"] = f"AnkiScape state acceptance {number:02d}"
        note["Back"] = "Use Good for the native review check."
        collection.add_note(note, deck_id)
        note_ids.append(note.id)
    collection.set_config("ankiscape_player_data", seed)
    collection.set_config("ankiscape_current_skill", "None")
    return {
        "collection_path": str(collection_path),
        "deck_id": deck_id,
        "note_ids": note_ids,
        "config_version": seed["config_version"],
        "next_step": "Close and reopen this isolated profile before any AnkiScape action",
    }
