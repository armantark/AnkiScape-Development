# Summoning Familiarisation source audit (2026-07-16)

Scope: establish the period activity loop and isolate the AnkiScape session-shape choice.
Cutoff: 2012-11-20.

## Pinned period source

- RuneScape Wiki, `Familiarisation`, oldid `6544727`, timestamp
  `2012-11-09T06:31:59Z`. Revision ID and timestamp came from the MediaWiki revisions
  API; findings below were checked against the literal revision wikitext.

## Period findings

- Familiarisation is a once-per-week Distraction and Diversion released on 2010-02-16.
  It has no quest or skill requirement, including no Wolf Whistle requirement.
- The fiction is explicit: find the currently active small obelisk, project into the
  spirit plane as a random familiar, collect raw-shard piles, and avoid native familiars
  that drain mental focus.
- A run ends at 60 raw shards, zero mental focus, or 20 minutes. The active obelisk moves
  on a multi-hour cadence. Those real-time windows cannot use the wall clock in
  AnkiScape.
- After the run, the player chooses one of two rewards:
  - a box of Summoning ingredients scaled by collected raw shards; or
  - triple eligible charm drops for 40 seconds per raw shard, rounded to the nearest
    minute, up to 40 minutes at 60 shards.
- The triple-charm reward excludes Talon beast charms, Bork/Ork Legion charms, and
  mystery-box charm rewards. The activity becomes available again one week after the
  last participation.

## AnkiScape boundary

The source fixes the fiction, stop conditions, shard cap, reward alternatives, and reward
scaling. It cannot decide how many answered cards should represent one 20-minute run or
how avoiding hunters maps onto review input. That session length is a labeled product
abstraction.

Standing project rules settle the outer shell without owner input:

- availability returns 1,680 answered-card world ticks after participation, preserving
  the source's rolling week through the global simulation clock and never the wall clock;
- obelisk searching/travel is folded into the activity rather than creating location
  state or a transport system;
- the reward choice is an immediate UI command after the run, not another review;
- the triple-charm duration uses the settled short-duration answered-card conversion;
- charm exclusions and ingredient-box contents remain catalog/source data; and
- the entire session and reward claim must remain undo-safe without duplicate claims.

The remaining owner fork is whether the spirit-plane run is one flattened successful
review with a narrative result line or a short multi-review session whose segments can
lose focus and collect partial shards.
