# Legacy README (Migration Compatibility)

This folder exists to document legacy support kept around after the major data/model restructure. It is here to ensure that users upgrading from older builds have their data migrated seamlessly without manual steps.

## Why this exists

Older versions stored different keys and shapes (for example a single `total_exp`, missing/None inventories, or pre-menu config). The app now maintains per-skill fields and additional settings. We preserve older data by migrating it on load.

## Where the migration happens

- Code: `storage_pure.py` (pure migration helpers) and `storage.py` (I/O + integration)
- Entry point: `storage.load_player_data()` calls a migration that normalizes the loaded dict before use

## What is migrated (non-exhaustive)

- Missing or `None` inventory -> an empty dict
- Old schemas with `total_exp` and partial per-skill fields -> preserved totals; per-skill values are populated with safe defaults
- Unknown/extra keys -> left intact (forward-compatible)
- Type normalization for numeric fields (ints/floats)
- Config keys introduced after restructure (e.g., `ankiscape_current_skill`, floating button settings) -> loaded with defaults if absent
- Settings consolidation: legacy `ankiscape_hud_progress_enabled` is migrated to `ankiscape_review_hud_enabled` (Experience HUD) when the new key is unset

## Guarantees

- Idempotent: running migration multiple times produces the same result
- Non-destructive: data is only added/normalized; unknown keys are not dropped
- Backward-safe: if per-skill exp already exists, prior aggregates like `total_exp` are preserved (not recomputed)

## Tests covering migrations

- `tests/test_storage_pure.py`
- `tests/test_storage_migration_extra.py`

These verify defaults, idempotency, inventory normalization, and preservation behavior.

## Developer guidance

- When adding new fields, update the migration to set a sensible default and keep it idempotent
- Extend the tests above to cover the new field and any legacy shapes
- Do not remove this folder or migration logic until you are certain users have upgraded past legacy versions

## User impact

No action required. Upgrades should keep progress, inventory, and settings intact automatically.
