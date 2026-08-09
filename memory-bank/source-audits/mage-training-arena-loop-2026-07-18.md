# Mage Training Arena review-native contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-design loop closed; period room and reward structure,
goal-driven routing, checkpoint switching, Arena-wide approach, and Graveyard
death boundary are settled; final source/cadence rates remain implementation
work.**

Implementation note `2026-08-08`: the complete 25-row reward catalog is live
with exact prices, canonical outputs, equipment integration, source sprites,
and direct-purchase coverage. See
`mage-training-arena-reward-catalog-2026-08-08.md`. The mechanic contract below
is unchanged.

## Pinned period evidence

`Mage Training Arena`, oldid `6491109`
(`2012-10-28T20:51:43Z`), establishes:

- level 7 Magic permits the first Enchantment spell, while level 33 Magic
  permits participation in all four rooms;
- four distinct rooms and point wallets: Telekinetic, Alchemist,
  Enchantment, and Graveyard;
- room-specific spells, runes, Magic XP, point rules, bonuses, outputs, hazards,
  and point caps;
- most rewards require points from all four wallets;
- the complete cutoff reward shop, including Infinity equipment, the wand
  ladder, Mage's book, combination runes, and the Bones to Peaches unlock; and
- the period room restrictions on coins, fruit, familiars, clue scrolls, and
  caskets.

Source:

- <https://runescape.wiki/w/Mage_Training_Arena?oldid=6491109>

The literal historical wikitext owns the room tables and reward costs.
Rendered modern templates or current-game rates do not.

## Four rooms remain real

AnkiScape removes spatial puzzles and repetitive target selection, not the
Arena's economy. The implementation keeps:

- four separate point balances and their period caps;
- each room's exact eligible spells, rune costs, Magic XP, rewards, and
  hazards;
- source bonuses and residual thresholds;
- the complete four-column reward costs; and
- ordinary inventory, equipment, Constitution, death, and undo consequences.

It does not create a blended Arena currency or award representative points
from rooms the player did not train.

## Owner-settled goal router

The primary control is a **Reward goal** selector containing the exact reward
catalog. `Auto — selected reward` is the default room policy. The same control
also offers direct Telekinetic, Alchemist, Enchantment, and Graveyard overrides
for players who want a specific point balance or Magic-training method. There
is no Casual/Advanced split.

For each room required by the selected reward:

```text
point deficit = max(0, reward cost - current wallet)
remaining review-equivalents =
    point deficit / source-calibrated expected points per successful review
```

Auto works on the largest remaining review-equivalent workload. It never
compares the four raw point deficits because their currencies have deliberately
different scales and period earning rates. Room throughput must be calibrated
through the live cadence kernel from period action rates and action units; one
review is not naively one completed maze, one point, or one arbitrary room
batch.

If the preferred room lacks required runes, equipment, food, or LP safety, Auto
may work another still-needed runnable room while visibly listing the blocked
requirement. It pauses when no still-needed room is runnable. It never buys or
pulls supplies, changes the reward goal, spends points, or silently chooses an
unneeded room.

Reaching the complete four-wallet price pauses the goal and surfaces the
ordinary direct purchase command. The player still decides whether to spend
the points. Purchasing consumes no review and is atomic with the reward; undo
uses the existing direct-command transaction contract.

## Natural switching checkpoints

Auto may change rooms only after the current room reaches its next source
checkpoint:

| Room | Switching checkpoint |
|---|---|
| Telekinetic | Completed maze |
| Alchemist | 100 coins deposited for one point |
| Enchantment | Ten-shape bonus resolved |
| Graveyard | Sixteen fruit deposited for one point and rune reward |

This prevents review-to-review room jitter and makes every result line
understandable. A reward goal may become affordable inside the final
checkpoint; any legitimate excess points remain in their separate wallets.

## Automated room microplay

Each successful review admits the cadence-calibrated count of the room's
ordinary source actions. Only bounded residual counters persist; AnkiScape does
not simulate maze coordinates, cupboard positions, loose shapes, bone piles, or
NPC actors.

- **Telekinetic:** follow a competent valid route automatically. Track only
  admitted Telekinetic Grab moves, Law-rune costs, moves remaining in the
  current seven-to-ten-move maze, two-point completion, and the five-maze bonus
  of eight points, ten Law runes, and 1,000 Magic XP.
- **Alchemist:** select the current strategy's eligible cupboard value, cast
  the applicable Alchemy spell, accumulate coins, and deposit at each 100-coin
  point checkpoint. Preserve Nature-rune use, two Magic XP per deposited coin,
  and ten banked coins per point.
- **Enchantment:** select the current bonus shape, use the chosen eligible
  enchantment spell, and deposit automatically. Preserve one base point per
  correct shape, 75% ordinary spell XP, the enchantment-level bonus on every
  tenth shape, and the rune reward on every twentieth orb. The world-hopping
  dragonstone-respawn exploit is excluded.
- **Graveyard:** advance the exact repeating bone-value sequence, cast Bones to
  Bananas or an unlocked Bones to Peaches, eat only according to the selected
  survival strategy, and deposit automatically. Preserve one point and one
  source reward rune per sixteen deposited fruit, falling-bone damage, fruit
  sacrificed to healing, and the source death consequence of returning to the
  lobby and losing ten Graveyard points.

`Again` emits no room action, rune consumption, XP, points, healing choice, or
hazard roll. It advances only established world consumers. One review undo
restores all admitted actions, residuals, point wallets, runes, XP, outputs,
damage, routing state, and checkpoint state.

## Concrete routing example

Bones to Peaches costs:

| Wallet | Cost |
|---|---:|
| Telekinetic | 200 |
| Alchemist | 300 |
| Enchantment | 2,000 |
| Graveyard | 200 |

At balances `80 / 250 / 600 / 150`, the raw deficits are
`120 / 50 / 1,400 / 50`. Auto does not assume Enchantment is furthest behind.
The source workloads behind those deficits include:

- 120 Telekinetic points: 35 completed mazes when the five-maze bonus is
  preserved;
- 50 Alchemist points: 5,000 deposited coins;
- 1,400 Enchantment points: at level-87 Enchant Level 6, approximately 880
  correct shape casts when ten-shape bonuses are preserved and dragonstone
  world hopping is excluded; and
- 50 Graveyard points: 800 deposited fruit.

The cadence audit converts those unequal workloads into expected successful
reviews. Auto finishes the largest normalized workload until its next natural
checkpoint, recalculates all four, and continues until the four exact costs are
present. This routing changes order and convenience, never the total source
work, resources, XP, hazards, or reward price.

## Arena-wide approach

One saved **Approach** dropdown applies wherever the source offers a genuine
cost-versus-throughput choice:

1. **Fast rewards** (default)
2. **Conserve runes**

Fast rewards uses the highest-value eligible Alchemist target and the
highest-throughput eligible Enchantment spell supported by the player's Magic
level, carried runes, and equipment. Conserve runes takes free Alchemist casts
when the source-shaped opportunity is present and otherwise continues useful
goal routing; it selects the lowest actual consumable-rune cost per expected
Enchantment point after staff substitution. It never turns a successful review
into an inert wait merely to save a rune.

The dropdown does not change Telekinetic solving, point prices, spell XP,
hazards, or reward outputs. Graveyard survival remains owned by the shared
auto-eat/LP policy rather than being smuggled into a vague “cheap versus fast”
setting. There is no third Balanced value, per-room checkbox matrix, or
Casual/Advanced split.

## Graveyard death boundary

The source hazard remains real. Shared auto-eat consumes eligible carried or
converted food at the ordinary LP threshold. If no food can restore the player,
automation does not grant a free pre-hazard exit: falling-bone damage continues
through its source-shaped hidden roll.

Death atomically:

- returns the player to the Arena lobby;
- removes exactly ten Graveyard Pizazz points without going below zero;
- preserves equipment and the other three Pizazz wallets;
- clears only the room-local fruit/bone residuals that the source discards; and
- stops Arena training instead of automatically re-entering.

This preserves the Graveyard's only meaningful danger without requiring the
player to watch LP between reviews. A manual Leave command remains available
before answering another card, but no new safety toggle or free auto-retreat is
added.

## Wand upgrade chain

The wand rows are not four independent purchases. Period item revisions close
the exact upgrade chain:

| Wand | Period item oldid | Points (Telekinetic / Alchemist / Enchantment / Graveyard) | Required input |
|---|---:|---:|---|
| Beginner wand | `6021040` (`2012-07-31`) | `30 / 30 / 300 / 30` | none |
| Apprentice wand | `5825592` (`2012-06-25`) | `60 / 60 / 600 / 60` | Beginner wand |
| Teacher wand | `5832254` (`2012-06-25`) | `150 / 200 / 1,500 / 150` | Apprentice wand |
| Master wand | `6291896` (`2012-09-24`) | `240 / 240 / 2,400 / 240` | Teacher wand |

Buying an upgrade atomically consumes its predecessor and the four point costs.
Selecting a higher wand as the reward goal automatically expands the goal into
the missing predecessor purchases before calculating remaining room workloads.
It never pretends the displayed Master-wand row can be bought directly without
the Teacher wand. Already owning the required predecessor removes only that
earlier material requirement, not the listed point price of the selected
upgrade.

Sources:

- <https://runescape.wiki/w/Beginner_wand?oldid=6021040>
- <https://runescape.wiki/w/Apprentice_wand?oldid=5825592>
- <https://runescape.wiki/w/Teacher_wand?oldid=5832254>
- <https://runescape.wiki/w/Master_wand?oldid=6291896>

## Implementation source work

Before implementation:

1. harvest the full four-column reward catalog from oldid `6491109`;
2. reconcile each room's period action rate and hidden rolls through the source
   hierarchy;
3. derive cadence emissions without treating answered-card world time as
   literal activity duration;
4. record the exact room caps, restrictions, outputs, death handling, wand
   upgrade requirements, and equipment stats; and
5. leave any unsupported hidden rate `source_blocked` or use only a compliant
   provisional hidden-roll calibration.
