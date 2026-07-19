# Slayer Desert lizard Combat and finisher audit — 2026-07-17

Status: **target, finisher, water context, asset, and review mapping
implemented**. Exact period desert-heat timing and damage remain
`source_blocked`; the live supply cost is an explicit bounded abstraction.
Cutoff: `2012-11-20T00:00:00Z`.

## Period target and finisher

RuneScape Wiki, `Desert lizard`, oldid `6548273`, timestamp
`2012-11-11T18:54:08Z`:
<https://runescape.wiki/w/Desert_lizard?oldid=6548273>.

The cutoff page supplies the live family facts:

- Combat level 24;
- 250 lifepoints;
- level 22 Slayer;
- 25 Slayer XP;
- melee combat with a maximum hit of 40 LP;
- an Ice cooler is consumed to finish the target at 1–30 LP;
- using the cooler above the threshold consumes it without effect in the
  period game; and
- a water source is advised because the target is in the desert-heat area.

The owner-approved no-misclick rule intentionally disables the manual action
above 30 LP. That is the only deviation from the period finisher interaction.

## Emulator reconciliation

Pinned Darkan sources:

- `data/npcs/combatdefs/uncategorized/desert_lizard.json:1-30` supplies 250 LP,
  maximum hit 40, melee/crush combat, Attack 20, Strength 22, Defence 20,
  Magic/Ranged 1, and respawn delay 59.
- `data/npcs/drops/desert_lizard.json:1-390` supplies guaranteed Bones and 31
  weighted ordinary rows. Each AnkiScape selector entry retains its original
  `7009/100000`, `1401/100000`, or `207/100000` chance and source quantity.
- `src/main/java/com/rs/game/content/skills/slayer/npcs/ConditionalDeath.java:47-84`
  holds an otherwise lethal target at 1 LP until the required item succeeds.
- `ConditionalDeath.java:91-100` maps all six Desert lizard NPC IDs to item
  `6696`, consumes it, and shares the quick-finisher path.
- `data/items/config.json:75729-75738` identifies item `6696` as
  `ice_cooler`.
- `data/items/shops/turaels_slayer_equipment.json:73-83` stocks 1,000 Ice
  coolers.

The period page wins for the exact 1–30 LP manual threshold. Darkan's generic
conditional-death implementation uses its shared below-ten-percent check, which
would resolve this target below 25 LP and is therefore only corroboration for
the item, consumption, death hold, and quick-finisher shape.

## Drop-table mapping

`dropOne: false` controls whether every item inside a selected row drops; it
does not make sibling rows independent. Darkan's executable `DropList` assigns
all 31 nonzero rows adjacent intervals under one random draw. AnkiScape now
uses the resulting exact 100,000-slot selector: 99,981 occupied slots and 19
empty. Guaranteed Bones remain outside that selector. The earlier independent
mapping is superseded by
`slayer-darkan-drop-selector-correction-2026-07-18.md`.

## Review-native finisher

Before the 400-point quick-finisher unlock:

1. ordinary damage may reduce the lizard only to 1 LP;
2. the action selector becomes available at 1–30 LP only when an Ice cooler is
   loaded;
3. the next correct review atomically spends one cooler, awards one kill and
   its drops, clears the encounter, and returns the selector to Attack; and
4. an invalid or stale selection spends nothing and does not disable Combat.

After the unlock, any lethal player-side damage source checks the loaded cooler,
spends exactly one, and completes the same kill in the damaging review. Without
the item, the target still remains at 1 LP. Damage effects that run after the
enemy has already died cannot spend a second cooler. Death-prayer damage does
not auto-spend a finisher because the current death-prayer path does not award
that simultaneous kill atomically.

## Desert-heat context

RuneScape Wiki, `Desert heat`, oldid `6520962`:
<https://runescape.wiki/w/Desert_heat?oldid=6520962>.

The period material proves that filled Waterskins protect the player, each
automatic drink consumes one dose, and dose remainders are retained. It did not
yield a sufficiently stable cutoff damage/interval formula for this audit.
Those exact values remain `source_blocked`.

AnkiScape does not use wall-clock timers. The live mapping is the following
owner-authorized bounded abstraction:

- each damaging Desert lizard Combat review consumes one Waterskin dose;
- `(4) -> (3) -> (2) -> (1) -> (0)` is preserved exactly;
- up to eight filled skins load into the Combat pack, with each skin consuming
  one carried slot;
- required hazard supplies take priority at the 28-slot boundary, returning
  only excess food to the bank rather than overfilling the pack;
- a depleted pack uses the existing two-review bank run when filled skins
  remain banked; and
- without either a loaded or banked filled skin, the target is visibly locked.

The manual finisher review neither consumes nor requires a second heat dose
once the target is already in the valid finisher window. The one-dose cost
belongs to the damaging Combat burst, which keeps the flattened context
legible, prevents the separate finisher review from paying twice for one
encounter step, and lets a player use the finisher after the preceding attack
consumed the last filled dose. Slayer level and finisher-item gates still apply.

Enchanted-water-tiara charges, desert-clothing timing modifiers, Tome of frost
damage reduction, and exact unwatered damage remain source/dependency debt.
They do not make the target unreachable because the cutoff Waterskin route is
fully executable.

## Asset

`combatenemies/desert_lizard.png` is the normalized 48-pixel target sprite from
RuneScape Wiki file `Desert lizard (green).png`. Its URL, SHA-1, timestamp, and
source wiki are retained in `assets_provenance.json`. The Combat asset fetcher
contains the stable title override, and real offscreen Qt coverage proves the
row renders a non-null icon.

## Verification contract

Coverage pins:

- exact target stats, level gate, drop-table shape, finisher schema, and asset
  provenance;
- manual success, early/missing-item rejection, lethal hold, quick completion,
  one-item spend, and dose preservation;
- automatic bank refill of both coolers and Waterskins;
- the shared 28-slot boundary under max-safety packing;
- runtime telemetry/save/UI feedback;
- tooltip legibility for finisher and Desert heat;
- persisted default and migrated Combat action/loadout state; and
- the real Qt selector hidden for ordinary enemies, disabled above 30 LP, and
  enabled at the valid threshold.

Final closure ran 1,497 core methods (1,293 ordinary passes and 204 expected
environment skips) and 1,497 real offscreen Qt methods with no skips, expected
failures, or failures. The test-quality audit reports zero hard issues.
