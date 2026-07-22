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
- absent Bork, Ork-legion, and mystery-box consumers retain their explicit
  triple-charm exclusions; and
- the entire session and reward claim must remain undo-safe without duplicate claims.

## Settled AnkiScape translation

The owner delegated this unfamiliar D&D's product shape. AnkiScape uses a four-answer
session with three abstract focus pips. A successful answer collects 15 shards; Again
collects none and removes one focus pip. The session ends at 60 shards, zero focus, or
four segments, then exposes the period ingredient-box/triple-charm choice as a free
direct command. These discrete magnitudes are labeled balance abstractions rather than
period claims. Cooldown starts at entry, partial sessions persist without wall-clock
resolution, and every review/reward mutation is undo-safe.

## Horizontal reward and session correction — 2026-07-22

The period `Box of summoning ingredients` revision, oldid `6469202`, timestamp
`2012-10-25T06:01:45Z`, states that the non-bankable box immediately yields two
noted pouch ingredients and that both item identity and quantity depend on raw
shards plus Summoning level. Its table is observational rather than a complete
server formula. Two literal rows supply the smallest honest horizontal ladder:

- level `1`, `40` shards: `27` Raw rabbit and `42` Raw beef; and
- level `48`, `60` shards: `19` Raw shark and `22` Goat horn dust.

AnkiScape selects the highest of those two level bands and scales both observed
quantities proportionally by `collected shards / source-row shards`, flooring
each positive quantity and preserving both items. The anchor rows are exact;
intermediate shard totals are a labeled `abstraction/oldid-6469202`, not a
claimed historical formula. This replaces the old one-item-per-15-shards
round-robin across every pouch tertiary, which had no period source and
materially understated the reward.

The same pass makes Familiarisation a real shared activity session. Start
refuses another activity owner, claims `activity_session`, preserves ownership
through all four reviews and the pending reward, and releases it only when the
direct reward claim succeeds. Legacy active state repairs a missing empty
session on its next review without overwriting another live activity.

Oldid `6544727` also explicitly includes ordinary, Obsidian, and Abyssal charms
in the triple reward while excluding Talon beast charms, Bork/Ork Legion drops,
and mystery-box rewards. The ordinary-only combat multiplier is therefore a
known implementation defect pending the shared `logic_pure.py` writer boundary;
the consumer exclusions remain inert until those reward sources exist.
