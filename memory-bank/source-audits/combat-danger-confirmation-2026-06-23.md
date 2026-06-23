# Combat Dangerous Target Confirmation Audit - 2026-06-23

## Scope

This slice implements the Combat grill decision that targets rated `Death
possible` should require explicit confirmation before activation, without adding
a persistent confirmation flag to the flat save model.

## Implemented Contract

- `combat_target_rows()` now maps the existing `combat_target_preview_pure()`
  risk band into UI row metadata.
- Rows with `risk_band == "Death possible"` stay enabled, but carry:
  - `requires_confirmation = True`
  - `confirmation_title = "Confirm dangerous combat"`
  - a target-specific confirmation message
  - a tooltip line saying confirmation is required before selecting the target
- The grouped target-tree builder accepts an optional confirmation callback.
- The Combat target tree passes a `QMessageBox.question` callback for rows that
  require confirmation.
- Choosing `No` leaves the previous target unchanged.
- Choosing `Yes` calls the existing `on_set_combat(target_id)` callback.
- The confirmation is intentionally non-persistent: selecting the target is the
  accepted action, and no new saved `player_data` flag is introduced.

## Tests

- `tests.test_target_metadata.TargetMetadataTest.test_combat_rows_mark_death_possible_targets_for_confirmation`
- `tests.test_main_menu_widget.MainMenuWidgetTest.test_combat_death_possible_target_requires_confirmation`

## Deferred

- Wilderness risk opt-in still needs a separate kept/lost equipment surface
  because its risk set can change materially.
- Richer risk previews, including time-to-kill and equipment-risk detail, remain
  future Combat UI work.
