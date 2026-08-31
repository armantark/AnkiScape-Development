# Vinesweeper flattened activity contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period structure pinned and owner design closed; the board puzzle is
deliberately omitted.**

## Pinned period evidence

`Vinesweeper`, oldid `6288368` (`2012-09-24T04:55:21Z`), establishes:

- a safe members Farming/Hunter minigame at Winkin's Farm;
- a spade requirement satisfied by the tool belt;
- ten free starting flags, a maximum of ten, and replacement flags costing
  either 500 coins or 50 Vinesweeper points;
- a grid whose uncovered numbers identify adjacent seeds;
- one point per empty square uncovered, a ten-point penalty for digging up a
  seed, and a lost flag for an incorrect placement;
- correct seed flags paying a variable reward described as level-related,
  apparently random, commonly in the 100–200 range and reaching the 300s;
- rabbits racing farmers to flagged seeds, with a lost flag and no points when
  a rabbit wins;
- Ogleroots bought for 10 coins or found while digging, with each successful
  rabbit repulsion granting 30 Hunter XP and a random point award;
- Farming XP coming only from point redemption, at one point per XP from level
  40 and a level-scaled cost reaching 7.75 points per XP below level 40;
- a persistent point balance and an exact point shop containing Farming seeds,
  compost potion (4), flags, and direct Farming XP; and
- familiars and pets being barred from entry.

Source:

- <https://runescape.wiki/w/Vinesweeper?oldid=6288368>

The revision itself says the correct-flag and Ogleroot point awards appear
random and does not publish their distribution. It also does not provide
probabilities for safe digs, destroyed seeds, correct flags, rabbit threats, or
found Ogleroots.

The final local implementation search on `2026-07-20` was negative for server
mechanics:

- Darkan's
  `src/main/java/com/rs/game/content/minigames/vinesweeper/Vinesweeper.java`
  is an empty interface-ID stub; its Tool Leprechaun handler explicitly says
  Vinesweeper is not available yet. Its item configs prove only the period
  Ogleroot identity, item `12624`.
- the local 2011Scape baseline contains only generated `Items.kt`/`Npcs.kt`
  identity constants for the searched terms and no Vinesweeper handler.
- the period client caches can prove interfaces, sprites, and item identity,
  but not the missing server-side outcome probabilities.

Those weights therefore remain `source_blocked`. The owner-approved breadth
slice uses one labeled bounded roll: 45% safe uncover, 35% correct flag, 10%
mistaken dig, 5% mistaken flag, and 5% rabbit pressure. The first five
percentage points of the safe-uncover band also find one activity-local
Ogleroot. Correct-flag and defended-rabbit awards use a level-related 100-325
point band derived from that same roll. This keeps the period outcome set and
one-roll atomicity without pretending the hidden distribution is recovered.

Below level 40, the exact point-per-XP curve is likewise absent from the pinned
revision. The implementation linearly interpolates the two sourced endpoints:
`7.75` points/XP at level 1 and `1` point/XP at level 40, clamping to `1` at
level 40+. This is a labeled bounded pacing abstraction, not a period formula.

## Cutoff reward shop

The literal `Farming Seeds (and other items)` table in oldid `6288368` pins the
executable shop rows and prices:

- Flag 50; cabbage 10; tomato 10; sweetcorn 150; strawberry 165; watermelon
  680; guam 10; marrentill 10; tarromin 10;
- avantoe 1,250; wergali 3,800; ranarr 4,000; kwuarm 1,000; cadantine 1,000;
  snapdragon 16,000; lantadyme 7,500; dwarf weed 9,000; torstol 45,000;
- rosemary 10; nasturtium 10; woad 30; limpwurt 70; cactus 1,200; bittercap
  mushroom spore 800; belladonna 300;
- asgarnian 5; jute 50; yanillian 60; krandorian 20; wildblood 100;
- redberry 5; cadavaberry 5; dwellberry 5; jangerberry 10; whiteberry 25;
  poison ivy 30;
- acorn 100; willow 1,800; maple 12,000; yew 29,000; pineapple 10,000;
  papaya tree 20,000; palm tree 35,000; calquat tree 35,000; spirit tree
  55,000; and compost potion (4) 5,000.

The same revision's later `Making money` comparison table mentions Fellstalk
and Morchella, but the literal shop interface table does not. They are excluded
from the cutoff shop rather than promoted from commentary into executable stock.

### Compost-potion reward seam

Making the 5,000-point reward reachable exposed one downstream item chain that
the shop table alone did not settle. `Compost potion`, oldid `6357928`
(`2012-10-06T19:39:59Z`), pins that the potion cannot be made through Herblore,
one dose converts one bucket of Compost into Supercompost, and the four-dose
version is bought from Vinesweeper for 5,000 points. OpenRS2 revision 742 pins
the four non-stackable item identities: `6470` (4), `6472` (3), `6474` (2), and
`6476` (1). The executable utility therefore consumes exactly one dose,
preserves the next lower-dose potion or an empty Vial, and grants no XP.

The generated cutoff Exchange records also close their ordinary market edge:
all four doses have a four-hour buy limit of `1,000`; their pinned guide prices
are `1,858`, `3,447`, `7,174`, and `12,282` coins from one through four doses.
The four-dose record is `Exchange:Compost potion (4)` oldid `6561561`
(`2012-11-16T03:00:21Z`). The other three exact oldids and timestamps remain in
`grand_exchange_period_generated.py` beside the executable rows.

Source:

- <https://runescape.wiki/w/Compost_potion?oldid=6357928>

## Deliberate flattening

AnkiScape does not reproduce Minesweeper. There is no grid, tile selection,
number inspection, confidence control, path state, farmer actor, rabbit actor,
or invisible board simulation.

Each successful review resolves exactly one automatic, narrated
Vinesweeper operation from the source-shaped outcome set:

- uncover safe ground and gain its point;
- identify and correctly flag a seed, temporarily spending and then recovering
  one flag while receiving the bounded point award;
- make a mistaken dig or flag and apply the matching point or flag loss; or
- repel a rabbit with an Ogleroot, preserving the flagged-seed reward and
  granting 30 Hunter XP.

This is a single bounded outcome roll and a few scalar deltas, not a backend
simulation of a field. The result line reports the operation, point change,
flag change, coin change, and Hunter XP when applicable. There is no strategy
selector: without a visible board, cautious/aggressive modes would be fake
agency.

`Again` performs no Vinesweeper operation, grants no points or XP, and loses no
flag. It advances only the ordinary answered-card world systems. There is no
wall-clock timer, daily limit, session expiry, or offline catch-up.

Cadence class is `source_blocked_activity` until the outcome weights are
resolved. At multiplier `M`, resolve up to `M` complete operations, stopping
when the activity cannot afford a required flag or when the player leaves. One
undo restores the complete review batch, including every point, flag, coin,
Ogleroot, and XP delta.

## Automatic supplies

The player receives the source ten free flags once. Flags are an
activity-local charge meter capped at ten; they do not clutter the ordinary
inventory.

When a replacement is required, automation:

1. spends 500 coins;
2. if coins are unavailable, spends 50 Vinesweeper points; and
3. pauses the activity only when neither payment is possible.

The status line shows the current flag count and the payment used. There is no
trip to Mrs Winkin and no refill toggle.

Rabbit handling is equally automatic. A found Ogleroot is used first. If a
rabbit threatens and no root is held, the activity buys one for 10 coins and
uses it immediately. If neither a root nor 10 coins is available, the rabbit
wins and the source flag/no-points consequence applies. Any excess roots are
refunded on leaving, matching the source without making them a general
inventory-management chore.

## Rewards and persistence

Vinesweeper points persist across visits. Leaving clears only the discarded
field abstraction and refunds excess Ogleroots; there is no board to save or
resume.

Mrs Winkin's complete cutoff shop is one bespoke point-shop surface backed by
the shared activity wallet:

- direct Farming XP uses the source level-scaled point cost and is a
  `direct_command`;
- every period seed row and compost potion (4) remains available at the exact
  point price in the pinned revision;
- bought items enter the ordinary inventory/bank transaction and retain their
  real downstream Farming or Herblore uses; and
- buying flags uses the same 50-point source price as automatic replenishment.

Reward redemption consumes no review and is never cadence-multiplied.

## Entry and follower boundary

Entry requires the tool-belt spade or an ordinary carried spade. The
Tool-Leprechaun teleport is flattened into the Activity's direct location
transition and consumes no review.

An active familiar or pet cannot enter. The shared follower-dismissal
confirmation appears before the transition; AnkiScape does not silently dismiss
one. After confirmation, the follower uses its ordinary dismissal state and
the activity opens.

## Implementation acceptance

The implementation pass must prove:

1. no board, tile, NPC, or timer state exists;
2. one successful review mutates only the bounded source-shaped outcome;
3. `Again`, multiplier, terminal, save/load, and undo behavior follow this
   contract;
4. flag replacement uses coins, then points, then a visible pause;
5. rabbit defense uses found or automatically purchased Ogleroots before
   applying the source failure;
6. Farming XP can arise only from point redemption and Hunter XP only from
   rabbit repulsion;
7. the complete cutoff shop uses exact prices and real item outputs; and
8. familiar/pet entry invokes the shared confirmation rather than creating a
   Vinesweeper-only follower rule.

## Implementation closure — 2026-07-20

All eight acceptance points are implemented. The saved state contains only
scalar activity state and no board, tile, actor, or timer simulation. Review
and direct mutations use their established independent undo paths; schema 57
migrates and sanitizes the new state. The complete literal shop is registered,
and every item reward resolves through the ordinary item graph.

The shop-discovered Compost potion edge is also closed rather than left as an
inert reward. All four doses are registered with exact cache IDs, normalized
period sprites, dose preservation, a zero-XP Compost-to-Supercompost Utility
action, and cutoff Grand Exchange price/limit rows.

Fable and Kimi K3 independently reviewed the new card. Confirmed defects in
effective flag pricing, hierarchy, compact-height clipping, pause disclosure,
numeric copy, accessible names, and catalog keyboard behavior were reproduced
and fixed. A fully quit and freshly relaunched native Anki process then proved
one launcher, one menu, the paginated Minigames catalog, and the unclipped
Vinesweeper card without entering the activity or mutating the player save.
The exact closure passes all 2,024 non-Qt tests (266 expected environment
skips) and all 2,024 real offscreen-Qt tests (one intentional skip).

## Reachability point-economy closure — 2026-08-31

The live runtime chain was re-established before changing the instrument. The
Activities catalog registers Vinesweeper, entry accepts an inventory or tool-belt
Spade, review answers execute the activity operation, point state persists, and
`buy_reward` delivers every non-Flag shop row into inventory. The Flag row is a
capped activity-state purchase and never creates an inventory item.

Vinesweeper point state has no maximum. Safe uncovers award one point and
correct flags or defended rabbits award up to 325 points. The attainability probe
seeded all 170 operations into a maximum-award band, accumulated the 55,250-point
ceiling for that sequence, bought the highest-priced 55,000-point Spirit tree seed,
and kept 250 points. This is not an expected earning rate: ordinary play averages
about 130.45 points per operation and needs roughly 424 operations to reproduce
that balance, while the forced ceiling proves that every listed price is reachable.

The checked `93197a3d` table has 46 reward rows, not 16:

- `Wergali seed` and `Compost potion (4)` had no baseline route and gain their
  direct Vinesweeper buy routes.
- `Flag` is state-only and is deliberately absent from the item graph.
- The other 43 item rewards already had a route. Cabbage, tomato, and sweetcorn
  seeds came from Black knights; strawberry, watermelon, marrentill, tarromin,
  ranarr, limpwurt, wildblood, jangerberry, and whiteberry seeds from level-75
  Ankous; guam, nasturtium, redberry, cadavaberry, and dwellberry seeds from
  Master Farmers; avantoe, kwuarm, cadantine, snapdragon, lantadyme, dwarf weed,
  torstol, cactus, belladonna, and poison ivy seeds from Aberrant spectres;
  rosemary and krandorian seeds from Draynor Seed Market; woad, asgarnian, and
  jute seeds from Mutated zygomites; bittercap mushroom spores and yanillian
  seeds from Cyclopes; and acorns plus willow, maple, yew, pineapple, papaya,
  palm, calquat, and spirit seeds from seed nests.
- Of the 44 seed/spore rewards, 42 feed a live Farming or sapling action.
  `Bittercap mushroom spore` has no crop consumer, and `Spirit seed` is attached
  to a source-blocked, non-runnable Spirit tree crop. Both were already
  reachable and remain separate downstream implementation gaps.

The audit now follows the Fist of Guthix point-economy shape while retaining the
runtime gates that make the route executable. A Spade-gated operation produces
a repeatable synthetic `Vinesweeper point`; 45 buy nodes cover every
inventory-delivered reward and exclude Flag. Four dose-specific Compost potion
uses require both Compost and the current dose and preserve the exact next dose
or Vial plus Supercompost. The point shop also changes the preferred route for
nine already-reachable nest rewards: Acorn, Willow seed, Maple seed, Yew seed,
Pineapple seed, Papaya tree seed, Palm tree seed, Calquat tree seed, and Spirit
seed.

Measured report changes on this tree are:

| Audit value | Before | After |
| --- | ---: | ---: |
| `action_count` | 1,609 | 1,659 |
| `reachable_item_count` | 2,257 | 2,270 |
| `orphan_input_count` | 179 | 167 |
| `root_orphan_count` | 37 | 32 |
| `cascade_orphan_count` | 142 | 135 |
| `unresolved_action_count` | 266 | 256 |
| `seed_item_count` | 1,182 | 1,182 |
| blocked quest-stage rows | 143 | 143 |

The 13 new graph routes are the synthetic Vinesweeper point plus Wergali seed,
Grimy wergali, Clean wergali, Wergali potion (unf), Crafting potion (1) through
(4), and Compost potion (1) through (4). This removes five root orphans and
seven cascade orphans without changing quest-stage blocking.

Focused runtime and instrument coverage passes 74 tests. Complete discovery
passes 4,567 tests in both lanes: plain skips 515 and real offscreen Qt skips
three. The oversized audit and existing audit-test files do not grow; the
extracted Vinesweeper builder has cyclomatic and cognitive complexity 4, while
`build_reachability_report` remains at its baseline cyclomatic complexity 161.
