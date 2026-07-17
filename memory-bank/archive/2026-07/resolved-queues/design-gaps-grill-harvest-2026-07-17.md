# Resolved grill-harvest design gaps — 2026-07-17

Both questions were resolved by the owner on 2026-07-17 and implemented in the
same follow-up batch. This archived record preserves the alternatives and final
direction without leaving a stale open-work queue in the live Memory Bank.

## Priority guide

- **P0:** blocks an otherwise source-ready implementation batch.
- **P1:** materially changes a major player-facing loop but does not block other
  independent work.
- **P2:** meaningful polish or scope choice that can wait.

## Resolved questions

### P1 — Mage Arena alignment, god capes, and Charge's actual effect

The corrected Charge spell revision requires a worn god cape for the boost.
The Mage Arena and god-cape revisions also require one chosen cape at a time, a
matching first staff, 100 arena casts per god spell before external use, and
statue-based cape replacement/reclaim. The current five-review landmark simply
unlocks all three god spells and Charge, grants no equipment, and has no
alignment state. There is therefore no honest condition under which the live
duration flag can increase god-spell damage.

Recommended design:

1. Keep the five-review Kolodion landmark.
2. Its final step asks for one god alignment and grants exactly that cape plus
   the matching first staff.
3. Represent each source-required 100-cast unlock as one explicit review-native
   `Attune <god spell> in the arena` line, rather than 100 repetitive reviews.
   The initial alignment can include its first attunement; other spells require
   the existing 80,000-coin staff purchase and their own one-line attunement.
4. Make statue alignment/reclaim an instantaneous Mage Arena action. Switching
   destroys/replaces the current cape so the player still owns only one.
5. Apply Charge's +100 old-life-point maximum-hit boost only to the three god
   spells, only while Charge remains active, and only with the appropriate cape
   and valid casting weapon equipped.

Owner decision: approved the recommended collapsed alignment and attunement
loop. The existing review-driven refresh-on-recast abstraction remains in
force. Implementation adds final-form alignment, the first matching cape and
staff, per-spell one-review attunement, instantaneous direct-undoable statue
replacement/reclaim, one-cape and matching-loadout enforcement, and Charge's
conditional +100 LP maximum-hit effect.

Evidence:

- `memory-bank/source-audits/magic-charge-reconciliation-2026-07-17.md`

### P2 — Farming preset cure policy beyond the existing Cure item

The approved preset editor needs a compact cure choice for every patch. The
current Farming owner already has an item-backed Cure action, while Magic owns
a separate Cure Plant spell with its own rune, level, and target-selection
requirements. Making presets choose between them, automatically fall back
between them, or reserve runes would materially couple two otherwise separate
automation policies.

Alternatives considered:

1. Keep auto-cure item-only.
2. Make the two routes mutually exclusive.
3. Save an ordered preference and fall back to the other route when the first
   is unavailable.

Owner decision: use the third option as a compact two-choice toggle:
`Plant cure first` or `Cure Plant first`. The choice is stored per patch and in
presets, snapshotted into queued cure steps, and resolved atomically at
execution time through the existing item and Magic transactions.
