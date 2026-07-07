# 28-Slot Carried Inventory — Design (owner-grilled 2026-07-07)

Status: **designed, not implemented.** Grilled decisions locked; no code yet.
This is a substantial slice that touches the flat inventory, so it wants its
own implementation pass with its own status artifacts.

## The problem it solves

The number 28 already recurs everywhere as a shadow of the same missing
primitive: combat food loadout capacity (28), batch-28 utilities, the
"inventory-bounded bank run" rationale for tanning/sawmill, and the Wilderness
ambush's 28-slot accounting. A real 28-slot carried inventory is the model
those five constants are all approximating.

## Core decisions

1. **Teeth, for everyone (option A).** The 28-slot carry limit is a real
   constraint, not cosmetic — because a coal/gem/rune bag is worth *exactly*
   the cost of a bank run, and bags are content the owner wants. Without teeth,
   the whole system (and every bag) is inert.

2. **Overlay, not replacement.** The flat name-keyed inventory stays the source
   of truth (the bank = unlimited storage; zero risk to the parity price
   tables and the ~20 modules that read `inventory[name]`). The 28-slot grid is
   a *carried subset* — an ordering + capacity layer over the flat bank. This
   generalizes the existing `combat_supply_loadout` into one model used
   everywhere.

3. **Shared execution, swappable policy (this is the whole UX answer).** Bank
   runs *always auto-execute* — the player never opens a menu when the
   inventory empties (that would be "playing a game with learning on the
   side"). Default and advanced run identical machinery; they differ only in
   who decides the packing:
   - **Default (casual):** a **mode dropdown** of named preset packing
     strategies (e.g. balanced / max-food / max-materials) — not one opaque
     auto-manager, so each preset is individually inspectable and sane. The
     eat-queue is subsumed here (owner 2026-07-07): consume order falls out of
     the chosen mode. Transparency: the player sees e.g. "banked: 20 food /
     8 coal, +1 review."
   - **Advanced (opt-in):** the player sets the 4×7 layout / packing policy
     *once*; the system auto-executes it at every bank run. No per-depletion
     micromanagement. A smart layout (bags, food-vs-supply split, order) beats
     the dumb default.
   This mirrors how **combat already works today**: teeth exist for everyone
   (running out of food → bank run costs 2 reviews), auto-eat manages them at a
   decent-but-not-perfect default, and advanced players tune food priority /
   loadout. Advanced mode here is just *exposing the manual controls combat
   already half-hides*, extended to skilling — not a new concept.

4. **Advanced genuinely yields more XP/review.** The default auto-manager is
   deliberately modest (not optimal). An optimizer beats it — but by a **small
   gap** (target ~10-20% fewer bank-run reviews, never a 2x gulf that punishes
   casuals for not "doing homework").

5. **Input + output teeth (option B), unified.** Every session both draws from
   *and* deposits to the same 28 carried slots. Processing/combat drain it
   (food, supplies, materials); gathering fills it and banks when full. One
   model everywhere — and the canonical coal bag (mining) and gem bag finally
   have their home.

6. **Stackable rule (source-authentic, non-negotiable for bags to matter).**
   Stackables (runes, ammo, coins) occupy one slot regardless of count;
   unstackables occupy one slot each. Bags pack an otherwise-unstackable
   material (coal, gems) into a single slot — that is the entire value of a
   bag, and it only exists because of this rule. (The Wilderness ambush already
   reads the cache `stackable` flag; reuse it.)

7. **Every bank run costs a review (owner correction 2026-07-07 — no free
   banking).** A bank run costs review-answers everywhere, gathering included
   (combat keeps its existing 2; skilling starts at 1; tunable). This *sharpens*
   the Keep/Drop toggle below: Drop = never bank = never pay = fastest XP;
   Keep = pay bank-run reviews for materials. Bags reduce the number of bank
   runs, so they buy back reviews in every skill — which is exactly why gem
   bags (mining), coal bags (mining/smithing), and rune pouches all earn their
   keep.

8. **Gathering Keep/Drop toggle (per target).** Power-gathering vs collecting:
   - **Keep** (default): product goes to the carried grid, auto-bank when full
     (costs a bank-run review, per decision 7). You get materials.
   - **Drop:** no product, no banking, maximum XP/action. Bypasses the
     inventory entirely. This is the authentic power-mining / power-chopping
     choice and the real reason "some skills you bank, others you drop."

## Held-item requirements meet the toggle (the cannonball-mould rule)

Many actions require a *held item to be present* — the cannonball mould for
cannonball smithing, a chisel for gem cutting, a needle for leather, a
tinderbox for firemaking, etc. The carried-inventory toggle resolves "present"
cleanly:

- **Inventory management ON (advanced):** the required item must be in your 28
  carried slots — it occupies space, a real cost (bringing a mould means one
  fewer slot of coal).
- **Inventory management OFF (default):** "present" means "owned" — satisfied
  if the item is anywhere in the bank. No carry cost; the requirement is just
  a possession gate.

The toolbelt shrinks this: any belt-able tool (hammer, chisel, needle, knife,
tinderbox, gathering tools — the 2011 belt) needs no slot; only non-belt tools
(moulds, glassblowing pipe) are carried requirements. So the carried-tool
residual is tiny. Full map:
`memory-bank/source-audits/held-item-interactions-audit-2026-07-07.md`.

## Johari pass (2026-07-07) — the focused pre-code grill agenda

A one-round known/unknown pass surfaced four items beyond the original
"not-yet-decided" list. The implementation grill must cover, in priority order:

1. **Death + carried inventory (load-bearing).** RS drops carried inventory on
   death (except protected). AnkiScape's grave/death-office covers *equipment*
   only. Does the carried grid also drop on death, into the grave? Biggest open
   interaction.
2. **Undo snapshot for a bank run inside a review.** Bank runs mutate state and
   cost reviews *during* a card answer; Anki-undo must roll it all back. Known
   constraint, unsurfaced design.
3. **Unify (or separate) the carried-slot counter with the Wilderness ambush's
   existing 28 purchase-slot counter** — same number, different meaning; check
   for conflict.
4. **Quest items competing for carried slots** (RS quest-inventory pressure).

Plus the original known-unknowns: which preset modes exist; v1 bag roster +
capacities (source-audit each); exact skilling bank-run cost; grid UI
drag-vs-list; how it subsumes `combat_supply_loadout`; storage migration.

### Surfaced tacit assumptions (now explicit)

- **The carried inventory is skill-agnostic and persists across skill
  switches** — "combat loadout" and "skilling materials" are the *same* 28
  slots. This is the RS loop falling out for free (mine coal → switch to
  Smithing → forge from carried → bank when dry).
- Bank = infinite; only the carried grid is limited.
- Coins/currency are exempt from carried slots.
- Worn equipment is already outside the 28 (separate Equipment tab).

## Scope note

This is the flat-inventory-adjacent change the parity ledger flags as a
"standing adaptation" (flat name-keyed inventory). The overlay approach keeps
that adaptation intact — the grid is a view over the flat bank, so the price
tables and every module reading `inventory[name]` are untouched. That is the
whole reason overlay beats replacement.
