# Achievement Semantics Contract — 2026-07-16

## Status

Implemented on `codex/achievement-semantics`. This contract repairs the current
achievement catalog and establishes the history substrate that a later
achievement-diary reward system may consume. It does not choose or grant diary
gear.

## Predicate Semantics

- Action verbs such as Mine, Cut, Collect, Craft, Smelt, Catch, Mix, Earn, and
  Burn are cumulative. Spending, selling, dropping, drinking, or redeeming the
  produced item never erases that progress.
- Explicit Hold and Own wording reads live Bank/equipment state. A player who no
  longer holds the threshold no longer satisfies the predicate unless the
  achievement has already been completed, because completed achievement names
  remain sticky.
- Level, quest, claim, lap, activity, and established skill-counter predicates
  retain their existing authoritative state.

## Durable Ledger

`player_data["achievement_progress"]` is a versioned owner-scoped ledger:

```python
{
    "version": 1,
    "skills": {
        "mining": {
            "actions": {"iron_rock": 25},
            "outputs": {"Iron ore": 27},
        }
    },
}
```

The central runtime action recorder is the only live writer. Successful actions
increment the owning action and its semantic output quantities; failures do not.
The ledger deliberately does not duplicate a skill-wide success total because
that total is derivable from `actions`.

## Ownership Rule

Production belongs to the explicit action surface, not every skill that receives
XP:

- Superheat outputs are Magic-owned and do not satisfy Smithing production.
- Construction tablets are Construction-owned even though they award Magic XP.
- Inferno-adze cuts are Woodcutting-owned even though they award Firemaking XP.
- Fishing double catches are Fishing-owned and count their actual item quantity.

The factual action-telemetry output remains distinct from semantic achievement
output. Inferno-adze logs and Brimhaven tickets use that override so the ledger
can record earned credit without fabricating or double-adding inventory.

## Catalog Rules

- Mining bonus ores and Fishing double catches count their actual quantities.
- Failed iron smelts, burns, dry gathers, and other failures add no cumulative
  production.
- Rune Stockpile includes standard and combination runes only; tiaras are real
  Runecrafting outputs but are not runes.
- First Potion counts every finished Herblore target, including non-drinkable
  finished products such as weapon poison.
- Potion Collector and Potion Hoarder remain live holdings but measure conserved
  doses: 400 and 4,000 finished doses, equivalent to 100 and 1,000 four-dose
  potions. Vials, mixes, and six-dose flasks contribute their real doses, so Bob
  Barter decanting cannot change achievement eligibility by rearranging the same
  liquid.
- Arena Ticket is cumulative earned progress. Arena Regular remains a live Hold
  predicate.

## Save Migration

Config v37 seeds the new ledger once for older saves:

1. Aggregate available action-telemetry successes and output quantities by
   owning skill.
2. For achievement-relevant items, merge the current Bank quantity with
   `max(telemetry_total, held_quantity)`, never addition.
3. Do not count carried-inventory overlays separately because they are another
   view of the same Bank.
4. Preserve `completed_achievements` unchanged.
5. On later loads, sanitize only; never reseed from holdings.

Pre-ledger history cannot be reconstructed exactly after items were spent or
sold. The migration is a conservative minimum, while already completed
achievement names remain authoritative.

## Undo and Atomicity

The ledger is ordinary player data and therefore participates in the existing
review snapshot. One Anki undo restores inventory, XP, ledger progress, and
newly completed achievement names together. Instant non-review actions do not
write production progress unless they are the owning production surface.

## Achievement Diary Foundation

Future diary gear must consume sticky completion/history state, not current Bank
quantities and not a recalculated percentage whose denominator moves whenever
new achievements are added. The reward cadence, category/tier mapping, player
choice, retroactive grants, upgrade flow, and exact diary-item roster remain a
separate owner grill.

