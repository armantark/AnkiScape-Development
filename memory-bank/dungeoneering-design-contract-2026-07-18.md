# Dungeoneering design contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-ratified 2026-07-18 (via the proposals and choice-architecture
artifacts). Design closed; every ~number is harvest work.**

Artifacts: `status-updates/dungeoneering-proposals-2026-07-18.html`,
`status-updates/dungeoneering-choice-architecture-2026-07-18.html`. Numbers
shown there are illustrative shapes, never historical claims.

## The model: Roguelike Floor, fresh-start tuned

A floor is a seeded room graph compiled at entry with only the reachable
frontier revealed. One successful review resolves one room-scale beat. Floor
**size is the authentic small/medium/large source choice**, so early floors
run small (the "fresh account in miniature" feel) and grow with prestige and
levels. The packet's six forks close as recommended:

| Fork | Resolution |
|---|---|
| 13 Floor unit | Seeded room graph; one room beat per successful review |
| 14 Solo/party | Authentic solo canonical; party simulation parked |
| 15 Persistence/death | Floors persist indefinitely; death respawns at floor start and shrinks the completion payout; never erases the floor |
| 16 Skill XP | Ordinary skill XP inside Daemonheim is authentic, cadence-calibrated |
| 17 Complexity/binds | Authentic Complexity 1–6 and bind caps; Casual automates, Advanced selects; critical path always level-feasible |
| 18 Reward staging | Token shop opens only fully functional rows; Coal bag is the proof purchase |

## Three-tier choice architecture (the babysitting answer)

1. **Entry — strategic, once per floor:** theme/floor by unlock, size,
   complexity, Ring of Kinship class, bind loadout review, saved policies
   (auto-route, eat threshold, and similar).
2. **Checkpoints — rare, mid-floor, never modal:** frontier routing (Casual
   auto-routes toward the boss, Advanced picks among revealed doors), and
   bind offers through the shared contextual action row (`Bind / Replace /
   Skip`, remembered choice, conservative default `Skip`) — rare by nature
   because bind caps are authentic and drops are rolls.
3. **Never per-review:** eating, potions, door solving, gathering, cooking —
   automated microplay under saved policies, MTA-style, reported in the
   result line and reversed atomically by review undo.

## Faithfulness commitments (owner-stated)

- Authentic bind caps and the ammo bind, on the source DG-level ladder.
- Ring of Kinship class customisation with authentic token-tier upgrades as
  outside metaprogression; class tier shapes in-floor automation quality.
- Prestige, floor-completion marks, and the authentic XP/token payout model.
- The closed economy: nothing found inside reaches the Bank; the 54
  quarantined Herblore targets live only inside floors
  (this closes the questions in
  `dungeoneering-product-decision-deferred-2026-07-13.md`).
- The roguelike feeling survives as fog-of-war frontier, keys, branches, and
  scarcity — not a map screen.
- Skilling loops and interconnections inside floors are real: skill doors,
  resource rooms, session crafting chains feeding combat and survival.

## Starter expedition (unchanged from the packet)

Frozen theme, one small solo floor band, complexities 1 and 6 audited, six
room families, session inventory/equipment, one bind slot, one resource
chain, one quarantined Herblore chain, resume/abandon/death/prestige/tokens,
and a reward trader whose first purchase is the Coal bag.

## Harvest work

Pin from the period record: floor/size/complexity tables, bind-cap ladder,
kinship classes and tier costs, room and boss rosters per theme, door types,
prestige/XP/token formulas, death penalty magnitude, the full reward catalog
with staging order, and per-floor review budgets (`provisional/<source>`
where unattested).
