# Combat UI, Bank Runs, and Enemy Images - 2026-06-24

## Scope

Owner feedback on the first Combat UI required a follow-up implementation pass:

- Keep Combat as the playable Skills-hub row and hide Attack, Constitution,
  Defence, Magic, Ranged, and Strength from the hub list.
- Derive the active combat style from equipped gear instead of presenting a
  free global style dropdown.
- Move combat setup state to the Equipment tab.
- Remove the global food dropdown and stop advertising unowned food.
- Treat banked supplies as automatic bank runs with a short review-turn delay
  once loaded supplies run out. This is intended to balance future Summoning
  supply extension without turning refill into manual micromanagement.
- Use actual enemy sprites from the wiki for Combat target rows instead of
  falling back to Bones/drop-item icons.

## Implementation Notes

- `skill_registry.py` now keeps the individual combat stats in storage/XP logic
  while setting `visible_in_skill_hub=False` for Attack, Constitution, Defence,
  Magic, Ranged, and Strength.
- `combat_attack_style_for_equipment_pure` resolves Ranged from supported bows,
  Magic from staves, and otherwise preserves valid melee styles. Combat preview,
  lock checks, refill logic, and burst simulation now use that resolved style.
- `combat_bank_run` state stores the remaining automatic bank-run review delay.
  A bank run costs two no-combat reviews: the first starts/decrements the run,
  and the second completes the refill. Loaded supplies are consumed first.
- Food refill no longer caps at 28. Banked supplies now represent repeatable
  farm-run supplies with time cost rather than an inventory-sized pouch.
- The Combat tab target panel no longer renders style or food controls. The
  Equipment tab now renders the combat mode label, spell selector, auto-eat
  threshold, supply summary, bank-run status, and refill/unload actions.
- `COMBAT_ENEMY_IMAGES` maps Combat target ids to local `combatenemies/*.png`
  files. `target_metadata.combat_target_rows` uses that map for row icons and
  no longer falls back to `Bones`.
- `tools/fetch_combat_enemy_assets.py` fetches normalized 48px target sprites
  from the OSRS/RS3 wikis and records provenance in `assets_provenance.json`.

## Verification

- `python3 -m unittest tests.test_combat_logic tests.test_main_menu_widget tests.test_skill_hub tests.test_target_metadata`
  passed with 294 tests, 133 skipped.
- A direct file audit found `missing 0 []` for `COMBAT_ENEMY_DATA` target ids
  under `combatenemies/`.
