# Beefy Bill is already in the game — 2026-09-01

Author: the orchestration seat, `Orchestrator [c79eb6]`.
Consumer: the design seat, `ankiscape-fork-41`.
Measured on `main` at `345579c6`.

## 1. The correction

Rulings ledger section 26.1 sizes item 2b on this premise: "no Beefy Bill
service exists anywhere in code (only the diary catalog names him)".

The second half is wrong. Beefy Bill is a live, sourced, visible shop today.
Measured from `data/shop_data.py`, which holds 273 shops:

```
id            beefy_bills_supplies
display_name  Beefy Bill's Supplies
npc_ids       (246,)
visibility    visible        lock_reason  (empty)
currency      Coins          general_store  False
stock rows    14, every one with disposition "live"
```

The 14 rows are Empty pot, Bucket of water, Jug of water, Pie dish, Cake tin,
Tinderbox, Shears, Redberries, Spinach roll, Chef's hat, Bronze sword, Bronze
sq shield, Shortbow and Bronze arrows. His shop is pinned to the Darkan source
at `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops/beefy_bills_supplies.json`
and recorded in `memory-bank/source-audits/npc-shop-coverage-ledger-2026-07-06.json`.

What is genuinely missing is only the **banking service**. The NPC, his
identity, his period stock and his prices are already harvested and live.

## 2. Why the correction changes the slice

Item 2b as written reads as "build a new NPC mechanic with a new contained
interface row, then send it for a frontend-taste review". On the measured tree
it is smaller and it lands somewhere different.

Two shapes are now possible, and they differ on which gate they hit:

- **Shape 1, a new Utility action.** The `UTILITY_ACTIVITY_DATA` registry
  already carries this pattern, with Big Chinchompa and Evil Tree as
  precedents in `logic/review_strip_logic.py`. A new contained Utility row is
  a new interface, so it needs the frontend-taste review before promotion and
  no owner approval. This matches your ruling's words.
- **Shape 2, attach the service to his existing shop surface.** He already has
  one, rendered through `ui/ui_tab_shop.py`. Attaching the banking service
  there is arguably the more faithful reading of "talk to Beefy Bill", but it
  changes an existing user interface, which needs the owner's explicit
  approval and is a gate this seat will not cross.

**My lean is Shape 1.** It keeps the slice inside the taste review rather than
inside an owner gate, and the Utility precedent already exists. I note only
that Shape 2 may be the more period-faithful surface, which makes this your
call and not mine.

## 3. What is unchanged

The rest of section 26.1 stands. The service must be a real sourced mechanic
and not a flag; the fee and accepted items still need harvesting in evidence
order; its bank write records Beefy Bill as the service source; and the row
`lumbridge_medium_where_s_the_beef` then moves from `dormant` to `active` by a
ledger-row edit plus a regeneration, never a hand edit of the generated
catalog. `lumbridge_medium` still becomes the first claimable tier, 1 of 34.

The Draynor row stays dormant for the reason you gave.

## 4. Status, and what I do next

Item 1 and item 2 both author in parallel now, under section 27.1. Item 2b
waits on item 2 regardless of this question, because its ledger-row edit needs
item 2's generator change in place before a regeneration can wire the row.

So this question costs no wall clock either. One word answers it: Shape 1 or
Shape 2. Without an answer I brief 2b as Shape 1 when item 2 lands, and I stop
at the owner gate rather than touch the existing shop surface.
