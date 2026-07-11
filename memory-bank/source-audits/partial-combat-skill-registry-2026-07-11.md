# Partial Combat Skill Registry Closure — 2026-07-11

## Verdict

The skill ledger now distinguishes a complete skill surface, a partial but trainable skill, and a planned skill. Attack, Strength, Defence, Constitution, Ranged, and Magic are recorded as partial skills trained through unified Combat; they are no longer falsely represented as wholly planned stats.

## Runtime contract

- `implemented` continues to mean that a skill owns a complete selectable review surface.
- `surface_state` is `complete`, `partial`, or `planned`.
- `trainable` is true for complete and partial skills.
- `training_source` records the owning surface for partial skills; all six use `Combat`.
- Partial Combat skills stay out of the standalone review-skill selector. Magic may still appear as a developer-facing partial row because it will eventually own noncombat targets.
- Quest requirements accept live partial Combat levels.
- Quest and action XP rewards apply directly to trainable partial skills instead of being parked as pending future-skill XP.
- Existing pending Combat-stat XP migrates into the live stat once and is removed from the pending ledger.

The stable persistence id remains `defense`; the player-facing registry spelling is now the period-appropriate `Defence`.

## Remaining scope

This closes status truthfulness only. It does not claim full Attack, Strength, Defence, Constitution, Ranged, or Magic parity. Enemy, equipment, ammo, spell, special-attack, boss, and activity breadth remains governed by `memory-bank/combat-design-grill-2026-06-23.md` and the completion kanban.

