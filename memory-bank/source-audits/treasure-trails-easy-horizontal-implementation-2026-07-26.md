# Easy Treasure Trails horizontal implementation

Date: `2026-07-26`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **breadth level one for the Easy tier.** Medium, hard and elite trails
are not built; a clue of those tiers now reports why instead of doing nothing.

This supersedes the implementation boundary in
`treasure-trails-easy-source-boundary-2026-07-19.md`. Its three blockers are
closed: the owner settled ownership in `design-thread-queue.md` 4.5, and the
Darkan working tree on disk supplied the selection and reward rolls the audit
could not reach at the time.

## Sources used

| what | source | pinned id |
| --- | --- | --- |
| one clue across every tier; 1-to-5 easy trail length; reward decided at the casket; easy and any-level reward families | RuneScape Wiki `Treasure Trails` | oldid `6473708`, 2012-10-26T00:01:09Z |
| easy trails use simple, emote, map and cryptic steps | RuneScape Wiki `Clue scroll (easy)` | oldid `6333359`, 2012-10-02T09:39:55Z |
| simple clue text and tier labels | RuneScape Wiki `Treasure Trails/Guide/Simple clues` | oldid `6579176`, 2012-11-18T16:48:49Z |
| emote clue text and equipment lists | RuneScape Wiki `Treasure Trails/Guide/Emotes` | oldid `6538968`, 2012-11-06T15:34:10Z |
| map clue destinations | RuneScape Wiki `Treasure Trails/Guide/Maps` | oldid `6362741`, 2012-10-07T05:35:23Z |
| uniform step selection; 2-to-4 casket reward spots; 1/12 rare against 11/12 standard; easy standard quantities | Darkan `TreasureTrailsManager.java` (`generateClueDetails`, `generateRewards`) and `data/npcs/drops/treasure_trails/easy_casket.json`, `easy_standard.json`, `easy_rare.json` | working tree at `~/Documents/2012scape with bots/darkan-world-server` |

Where the two disagree the period page wins, per the standing rule. Darkan rolls
`1 + Utils.random(3)` for easy trail length, which cannot reach the five the page
states, so the range is the page's.

The trimmed black armour ids in Darkan's `easy_rare.json` (2583, 2587, …) match
the wiki's easy-reward item ids exactly, which is how we know the two records
describe the same table rather than two different ones.

## What ships

Nine real easy steps across three kinds:

- four **simple** steps, each tagged level 1 on the guide page;
- two **map** steps, taken from the maps guide's crate destinations; and
- three **emote** steps, two with equipment lists and one that demands nothing
  worn at all.

Emote steps keep their gear gate under the settled flattening. Every listed item
is reachable: Coif, Leather chaps and Leather gloves are craftable, Iron
chainbody and Steel plateskirt are smithable, and Sapphire necklace is
craftable, so no emote step is an unreachable wall.

Cryptic steps are **not** shipped. The easy-clue page names them as an easy step
kind, but no pinned source tags an individual cryptic row as easy, and under the
settled flattening a cryptic resolves exactly as a simple clue does. Shipping one
would add a guessed tier assignment and no mechanic.

## Decisions honoured

`design-thread-queue.md` 4.5. One clue across every tier, checked against the
inventory and against a trail already in progress. Caskets sit outside the check,
so a finished trail opens normally even while a fresh clue is held. The
one-per-tier rule does not ship.

The rule lives only in `clue_ownership_reason_pure`. The combat drop path, the
thieving grant path, the activity panel and the activity handler all ask it
rather than deciding for themselves.

Consequence recorded honestly: `tests/test_combat_logic.py`'s black dragon
tertiary test previously asserted that a single kill could yield both a hard and
an elite clue. Under the period rule it cannot, so that assertion now expects one
clue and a second assertion covers the already-holding case. The change is noted
inline at the assertion.

## Rewards, and how a player reaches each one

`tests/test_treasure_trails.py::test_every_casket_reward_is_reachable_through_a_real_trail`
walks every row of both tables. For each one it reads a clue, follows the trail
to its end, and opens the casket that trail produced — the reward is never
injected into a hand-built state.

## Failure modes

- An emote step stalls, with the missing gear named, until the equipment is
  worn; the stall is recorded as a failed action rather than counted as progress.
- The bare-emote step stalls while anything is worn.
- Abandoning a trail keeps the scroll, so the trail can be picked up again.
- Reading a medium, hard or elite clue is refused with a reason and the scroll is
  kept, rather than the click doing nothing.

## Item registration

`Clue scroll (hard)` was awarded by three combat drop tables while easy, medium
and elite were registered items and it was not. Treasure Trails owns clue
scrolls, so it registers that row, together with `Casket (easy)`, through
`treasure_trails_extra_items_as_dict()`. No generated table was hand-edited.

The reward items are deliberately **not** registered: they already carry item
identities and exchange rows elsewhere, and a second registration would overwrite
their owning system's metadata. Their art is keyed separately.

## Placeholders

One, registered in `memory-bank/placeholder-values.md`:
`treasure_trails.easy_step_count_distribution`.

## Deliberate deferrals

The full easy rare table is 64 slots and the standard table 32. Six and six
ship. Widening them adds rows, not mechanics, and the exact per-row rate is the
"rare-roll precision" the breadth programme defers.
