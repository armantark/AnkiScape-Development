# Ranked design gaps from the overnight audit — 2026-07-16

This file is reserved for genuine creative-direction decisions that existing
source evidence, product contracts, and established AnkiScape patterns do not
settle. Routine bugs, parity facts, and implementation choices do not belong
here.

## Status

All four owner-facing design questions were resolved on 2026-07-16. Their
implementation is still pending on `main`. This file now preserves the
overnight escalation ledger rather than advertising open owner decisions or
claiming that the approved mechanics already ship.

## Owner resolutions

1. **Agility carried risk:** Agility will use the shared target-specific Auto/Custom
   28-slot pack. Auto carries course requirements and real food when damage is
   possible; fatal failures grave the actual pack and equipment. The Wilderness
   course also uses the documented bounded PKer abstraction. See the
   post-closure amendment in `agility-skill-contract-2026-07-15.md`.
2. **Charge duration:** Charge will use the global review-driven temporary-effect
   clock: 50 game ticks per successful review at 1x, scaling with Actions per
   Review. It dissipates during safe non-combat activity and never reads wall
   time. See the duration amendment in `magic-skill-contract-2026-07-11.md`.
3. **Farming replacement and presets:** `Dig up` will be an explicit one-review verb
   for mature regrowth crops. Whole-farm presets snapshot user-selected patch
   plans; selecting is inert, applying copies plans, and `Queue full run`
   performs the work. See the replacement and preset amendment in
   `farming-skill-contract-2026-07-11.md`.
4. **Bank destructive and carried-quantity actions:** Bank will use `Discard X`
   with direct-action undo. `Set carried quantity...` distinguishes stackable
   and non-stackable slot use, while Custom-pack entries retain insertion order
   as the bank-run packing queue. See the Bank Direct-Action Contract in
   `gap-grill-decisions-2026-07-10.md`.

## Resolved without owner input during the audit

- The Pit's existing invitation gate now remains satisfied while its six-review
  challenge session is active.
- Fatal Agility failures use the established Thieving/Combat death presentation
  and deactivate training.
- Farming's settled watering multiplier, Magic's existing Farming-patch
  selector pattern, canonical Crafting item identities, Thieving's source
  denominator, and tooltip damage ranges required no new creative direction.
