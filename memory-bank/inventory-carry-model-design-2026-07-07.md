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
   - **Default (casual):** a dumb-but-transparent auto-manager packs the grid
     and refills. Frictionless — you just answer cards. Transparency is
     required: the player sees e.g. "banked: packed 20 food / 8 coal, +1
     review," which is both honest feedback and the breadcrumb that tells an
     optimizer there is headroom.
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

## Not yet decided (for the implementation grill or judgment)

- Exact default auto-manager heuristic (proportional fill? food-to-threshold
  then supplies?). Judgment, but must be *competent* — a dumb default that
  makes casual players silently worse is the one unacceptable outcome.
- Transparency surface wording / where it shows (review HUD toast vs a small
  banked-log panel).
- Which bags exist v1 (coal bag, gem bag, rune pouch?) and their capacities —
  source-audit each.
- Whether the 4×7 grid is drag-arrangeable in advanced mode or list-ordered.
- Interaction with the existing `combat_supply_loadout` (this model should
  subsume it, not sit beside it).

## Scope note

This is the flat-inventory-adjacent change the parity ledger flags as a
"standing adaptation" (flat name-keyed inventory). The overlay approach keeps
that adaptation intact — the grid is a view over the flat bank, so the price
tables and every module reading `inventory[name]` are untouched. That is the
whole reason overlay beats replacement.
