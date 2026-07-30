# Breadth-first: the next tranche

Status: **rewritten 2026-07-26, after nine families landed.** The previous version
of this file planned batches A, B and C. Batch A is finished, batch B is two
families in, so the ordering below is what actually remains.

## Where the programme stands

`main` is clean at 3,017 tests and green in both lanes. No worktree is open and
nothing is interrupted.

Nine families reached breadth one on 2026-07-26: Skeletal Horror, Duel Arena,
Clan Wars, Daily Challenges, Treasure Trails (Easy), Tears of Guthix, Enchanted
Key, The Crucible, and Goblin Raids. All nine survived an independent Sol
verification, which found four real bugs that three earlier Claude passes had
cleared. Those are fixed and merged.

## What remains

| family | estimate | source state |
| --- | --- | --- |
| ~~Shattered Heart~~ | done 2026-07-27 | breadth one; commit `eeff3738` |
| ~~Troll Invasion~~ | done 2026-07-27 | breadth one; see `source-audits/troll-invasion-horizontal-implementation-2026-07-27.md` |
| ~~Mage Training Arena~~ | done 2026-07-27 | breadth one; the placeholder rule unblocked the Enchantment rate; commits `c9fbc163`/`62d60965` |
| ~~Temple Trekking~~ | done 2026-07-27 | breadth one; see `source-audits/temple-trekking-trek-model-2026-07-18.md`; commit `0abb8c33` |
| ~~Dominion Tower~~ | done 2026-07-28 | breadth one; see `source-audits/dominion-tower-harvest-2026-07-28.md` and design forks 3.22-3.24 |
| ~~Gnome Restaurant~~ | done 2026-07-28 | breadth one; see `source-audits/gnome-restaurant-harvest-2026-07-28.md` and design fork 3.19 |
| ~~Mobilising Armies~~ | done 2026-07-28 | breadth one; see `source-audits/mobilising-armies-breadth-one-2026-07-28.md` |
| ~~Achievement Diaries~~ | done 2026-07-26 | breadth one; see `source-audits/achievement-diary-harvest-2026-07-26.json` and design forks 3.8/3.9 |
| ~~Dungeoneering~~ | DONE 2026-07-30 | breadth one complete: skill + floors (`0ac64a57`) and phase C kinship/trader/Coal bag (`d0cac104`), execution-verified clean |
| ~~Conquest~~ | DONE 2026-07-30 | breadth one merged (`10e342dc`) after three Sol verify rounds; schema 102 |

The Sol cross-lineage verification pass over Temple Trekking, Mobilising
Armies, Gnome Restaurant, and Dominion Tower is running as of 2026-07-28; its
findings gate calling those four settled.

**Do not plan from these estimates.** They come from a frontier audit that
predates both the placeholder rule and the parallel-agent workflow, and they are
solo human-hours. Measured against how families actually land now, they are off by
roughly an order of magnitude: nine families reached breadth one on 2026-07-26 in
a single day, several of them carrying estimates of 14-20 hours each. The owner's
own read is that Achievement Diaries is "at most an overnight run, maybe 2-4
hours". Treat the column as a rough ordering of relative size and nothing more.

**Bork is half-unblocked.** It needed the `Hunt for Surok` miniquest and the
regional Achievement Diary substrate. The diary substrate now exists — eight
families, real tiers, real reward equipment, a claim flow and a durable ledger in
`player_data["achievement_diaries"]` — so only the miniquest still blocks it. See
`source-audits/bork-loop-2026-07-18.md`.

**Gnome Restaurant reached breadth one on 2026-07-28.** Gnome cooking is live as
twenty real Cooking targets with exact levels, XP and ingredients; the delivery
loop runs one order per productive review with the source point, token and tip
tables; and the long-deferred presentation fork is queued as design decision 3.19
with both layouts drawn and the recommended one implemented. See
`source-audits/gnome-restaurant-harvest-2026-07-28.md`.

**The catalog is closed (2026-07-30).** Bork merged with the minimal
miniquest ledger (`f69bb751`): Hunt for Surok and The Lair of Tarn Razorlor
are playable miniquest rows, Bork runs his daily loop, and the Dominion Tarn
fight gates on Haunted Mine per its pinned source. Every family in the
pre-EOC catalog is at breadth one. Remaining programme work is depth, the
384-diary-task clause, and the parked 3.25 guardian-drop reshape.

## What every brief must carry

The failure modes below are not hypothetical. Each one shipped this week, and the
last four were caught only by execution after three review passes had cleared them.

1. **An invented mechanic advertised as settled.** Skeletal Horror banked two
   weekly entries, written into the UI, the memory bank and a test name.
2. **Tests that prove nothing.** Stubbing the system under test makes a green
   suite compatible with a feature that cannot work at all. One Skeletal Horror
   test asserted item and grave behaviour it could never observe, because it
   stubbed the reducer that produces both.
3. **An inert row.** A reward gated on a state no player reaches. The Crucible's
   Supreme helm was one until rank-point persistence was corrected.
4. **The panel re-deriving a rule the logic layer owns.** Found in Duel Arena and
   then in Skeletal Horror. The `*_view_pure` owns every enable and visibility
   decision.
5. **An unlabelled reconstruction.** The placeholder register test can only see
   values that carry a `PLACEHOLDER(...)` marker, so an invented value with no
   marker is invisible to it. Three reached a merged family this way.

## Model routing for the next run

Verify Claude-authored families with Sol, not with another Claude model. One Sol
pass found four shipped defects that three Claude passes had missed, and the
difference was lineage rather than effort.
