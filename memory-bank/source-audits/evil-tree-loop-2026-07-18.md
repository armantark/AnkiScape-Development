# Evil Tree Review-Native Source Pin

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period source pinned; three-phase loop and review-clock discovery
owner-settled; partial-participation gate under grill.**

## Pinned period evidence

`Evil Tree`, oldid `6569638` (`2012-11-17T22:22:59Z`), establishes:

- the activity may be completed twice per source day;
- merely inspecting a tree does not consume an interaction, but nurturing or
  otherwise interacting with it does;
- the tree has five sapling growth stages followed by the fully grown tree;
- nurturing advances sapling growth and awards Farming XP;
- the grown-tree loop consists of chopping roots for Woodcutting XP and
  kindling, lighting up to eight sections for Firemaking XP and tree damage,
  and chopping the tree itself for Woodcutting XP and tree damage;
- contribution raises the player's reward percentage, while the shared tree
  health is reduced by chopping and fire;
- the fallen tree pays noted logs, coins, and item-table rolls, with reward
  magnitude affected by contribution;
- finishing grants a temporary ordinary-tree Woodcutting benefit whose maximum
  source duration varies from 6 to 30 minutes by tree tier; and
- the event has seven tree tiers with distinct Farming, Woodcutting, and
  Firemaking requirements and XP tables.

Source:

- <https://runescape.wiki/w/Evil_Tree?oldid=6569638>

The exact reward-distribution formula, participation curve, post-event bonus
conversion to AnkiScape review opportunities, and active-window length remain
implementation-source work. They must not use the wall clock or simulate
worlds, clans, scouts, or individual other players.

## Settled phase compression

The source contains six growth stages, four recurring root positions, eight
fire positions, shared health, and a contribution percentage. Reproducing
those objects literally would add state without adding a meaningful review
decision.

The recommended AnkiScape boundary is one explicit finite activity session with
three consequential phases:

1. **Nurture** — compress the five sapling stages into one Farming review beat;
2. **Prepare** — chop roots to obtain and spend kindling, preserving the
   Woodcutting-to-Firemaking dependency; and
3. **Fell** — combined chopping and burning progress defeats the grown tree and
   determines the player's reward share.

The HUD exposes the current phase and one bounded progress meter; each answered
review performs one source-shaped phase action and emits one result line. No
hidden tree population, root-position, fire-position, or multiplayer
simulation runs behind that line.

The owner accepted this three-phase boundary. The event must not flatten into
one generic `Tend Evil Tree` action, because that would erase the sourced
Farming-to-Woodcutting-to-Firemaking chain.

## Discovery and availability

Discovery reuses the settled Shooting Stars world-event pattern:

- the global answered-card clock generates Evil Tree opportunities at the
  source approximately two-hour cadence, or about twenty answered cards;
- a generated tree appears directly in the D&D UI while active, without a
  scouting, hint-solving, world-hopping, or travel minigame;
- its tier is drawn from the seven source tiers without scaling or filtering
  the skill requirement to the player;
- the UI exposes the drawn tier, location label, requirements, remaining event
  availability, and twice-per-simulated-day participation allowance before the
  player interacts;
- locations that require inaccessible quest areas are excluded from the draw,
  representing the source player's ability to find another world's tree
  without simulating worlds or adding a location system; and
- completing or missing the event schedules the next opportunity from the
  shared review clock, never the computer clock.

The exact historical tier distribution is currently `source_blocked`. Until a
period distribution is recovered, implementation may use a labeled random
abstraction across the seven real tiers; it must not quietly favor the player's
current level.

## Next owner fork: partial participation

The source permits a player who meets the Farming requirement to nurture a tree
even when they cannot later meet its equal Woodcutting and Firemaking
requirements. Nurturing grants Farming XP and consumes one of the two daily
interactions.

The recommended authentic behavior is to allow that partial entry. The
pre-interaction panel clearly shows `Nurture only — cannot fell`, and selecting
it starts the ordinary Nurture phase without a separate confirmation dialog.
After the nurture beat, the session ends with the earned Farming XP but without
the fallen-tree reward. Requiring all three skill gates would be tidier, but it
would delete a legal source action and make the random tier less meaningful.
