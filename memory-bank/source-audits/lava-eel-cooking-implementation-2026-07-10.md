# Lava Eel Cooking Implementation Audit

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Evidence

- `Lava eel` oldid 5850408, 2012-06-28: level 53 Cooking, 30 Cooking XP,
  Raw lava eel input, Lava eel output, fire or range, and explicit never-burn
  behavior.
- `Raw lava eel` oldid 5850448, 2012-06-28: item identity, Heroes' Quest
  context, oily-rod Fishing acquisition, and non-tradeable status.
- Darkan `Cooking.java` independently binds item 2148 to item 2149 at level 53
  for 30 XP with no burnt item. Darkan is used only as reconciled runtime
  corroboration; the pinned pages establish the period values.
- Existing AnkiScape Heroes' Quest data and assets already register both item
  identities and the quest-stage catch/cook chain.

## Implementation

- Added `cook_lava_eel` to the ordinary `eels` Cooking family.
- One successful review consumes one Raw lava eel, produces one Lava eel, and
  awards 30 base Cooking XP. The action always succeeds and has no burnt output.
- Reused the existing period-sourced quest item icons rather than downloading
  duplicate assets.
- Added data, pure-logic, runtime, registry/asset, undo-integration, and
  offscreen Qt coverage.

## Remaining family boundary

Karambwan and karambwanji levels, outputs, XP, and quest teaching gates are
pinned, but their intermediate burn curves are not. Darkan's current karambwan
rows are internally inconsistent about input/output identity and burn levels.
Those actions remain source-blocked rather than borrowing an unrelated fish
curve. Wine and gnome recipes remain separate later sub-slices.
