# Design gaps for morning review — 2026-07-17

This file contains only genuine owner-level creative direction discovered while
source harvesting or implementing the settled queue. Missing historical values,
ordinary dependency gaps, and implementation details with an established
AnkiScape pattern do not belong here.

## Priority guide

- **P0:** blocks an otherwise source-ready implementation batch.
- **P1:** materially changes a major player-facing loop but does not block other
  independent work.
- **P2:** meaningful polish or scope choice that can wait.

## Open questions

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

Owner decision needed: approve this collapsed attunement/alignment loop or
choose a different representation. A smaller source conflict can be settled at
the same time: retain the approved refresh-on-recast abstraction, or enforce
the corrected page's no-recast-while-active rule.

Evidence:

- `memory-bank/source-audits/magic-charge-reconciliation-2026-07-17.md`

### P2 — Farming preset cure policy beyond the existing Cure item

The approved preset editor needs a compact cure choice for every patch. The
current Farming owner already has an item-backed Cure action, while Magic owns
a separate Cure Plant spell with its own rune, level, and target-selection
requirements. Making presets choose between them, automatically fall back
between them, or reserve runes would materially couple two otherwise separate
automation policies.

Recommended design:

1. Ship a simple per-patch `Auto-cure` toggle now, backed by the existing Cure
   item path and only queued when the patch is diseased.
2. Keep Cure Plant as an explicit Magic action until Farming presets gain a
   general cross-skill resource policy.
3. If cross-skill preset policies are later approved, add an ordered
   `Cure item → Cure Plant` preference rather than an opaque automatic choice.

Owner decision needed later: whether presets should ever cast Cure Plant
automatically, and if so whether the user chooses an ordered fallback or one
exclusive cure method.
