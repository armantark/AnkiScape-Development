# Pass 19 owner notes: run record

The owner's Pass 19 notes, word for word (2026-10-29 22:57):

> Pass 19 (10/28/26 start)
> Make it so that the sort and tickboxes for quests sorting/filtering gets saved
> Make quest progress colorcoded like the real game. Red = not started, bright green = completed, yellow = in progress, cyan = selected/current
> I had selected nettles and also added it to the queue and it sat doing nothing for several cards before I noticed.
> When I add to a queue, it means I want it to start. I queued it to gather 1 doogle leaves and I thought the queue was going, but it was just running the activity I had selected and I gathered 140 of them before I realized. Wtf.
>
> Here's pass 19 for you. fix pls
> Also yeah you could check all those in the tsv idc

The last line answers the Pass 18 offer to check the 50 icons whose wiki files
moved (`/Users/armantarkhanian/Code/ankiscape-pass18/evidence/slot-icons/sweep-rows-with-wiki-moves.tsv`).
During the build the owner added, on the first Quests screenshot: "Those
outlines are ugly tbh" and "I also don't think you should literally use ffff00
etc for the colors, they're too bright and saturated".

## Route

The owner did not ask for `/ask-matt`, and the notes name their fixes, so no
grill ran. Each open choice took the default under "Defaults offered back".
No plan artifact: "fix pls" asks for the build, and the results page offers
the defaults back, as Pass 18's did.

## What changed

1. **Every add starts the queue (notes 3 and 4).** Cause: the Pass 17 rule "A
   new plan never replaces an action the player started by hand" made an add
   wait behind the running action, and a free pickup never stops by itself.
   Reproduced through the real review handler at 10x before the fix: one card
   gave 20 Doogle leaves and 10 nettles for a 1-count entry. An add now starts
   the queue at once, in place of whatever runs, unless the queue already runs
   its first entry; a paused queue, and a queue set aside by a hand-started
   action, restart from entry 1. The waiting state, its "Starts when … stops."
   hint and "Start now" are gone. An add whose entry cannot start says
   "<entry> could not start.".
2. **The Quests tab keeps its sort and filters (note 1)**: the sort, both
   tickboxes and the four filter lists, in Anki's profile config under
   `ankiscape_quest_list_view`. The search text is not kept.
3. **Quest names show their progress (note 2)**: red not started, yellow
   started, green completed, cyan for the quest that runs now, in the game's
   hues at a lower saturation; the light theme uses darker shades.
4. **Quest cards lose the inner boxes.** The card's border style reached
   every label and button in it; it now frames the card alone, and the card's
   buttons take the "Add to queue" frame.
5. **Icons with moved wiki files.** `tools/reresearch_period_art.py` now
   follows the wiki's move log (the first move after the cutoff, then each
   later move of the new title) and retries an uncached URL before it counts
   a SHA-1 mismatch. 30 of the 50 icons now show their 2012 art. Not used: 6
   goblins (the 2012 file is one Port Sarim goblin), the swamp lizard (a
   standing human), adamant armour (worn, where the hall shows a stand) and the
   bullseye lantern (lit, where the game shows the unfinished lantern). 10 have
   no revision before the cutoff, and Torag's hammers fail the SHA-1 check.
   Contact sheet: `/Users/armantarkhanian/Code/ankiscape-pass18/evidence/renamed-icons/contact-sheet.png`.

## Defaults offered back

- An add to a paused queue starts the queue again from its first entry.
- Cyan marks the quest that runs now, not a quest picked earlier while
  another action runs.
- Only the quest name takes the colour; the status text stays dim.
- The search text is not saved.

## Review

An Opus review of the queue and Quests commits found three defects, all fixed
with regression tests in the last queue commit: a silent add that could not
start, the session-leave question asked before the count check, and a stale
cyan after an add started one quest over another. Not changed: a save from the
old code with `"waiting": true` shows its entry as "Now" until the next card,
which then pauses the queue.

## Second level, surfaced and not fixed

- The Shop and Achievements tabs do not keep their filters either; the owner asked for Quests.
- Cloudflare recompresses cached wiki images, so some of the sweep's 35
  "persistent SHA-1 mismatch" rows may now succeed, and `tools/fetch_assets.py`
  downloads have the same exposure.
- The six goblin provenance records name the Old School `Goblin.png`, but the
  PNGs are six period-style goblins from 495b48af9; their source is unrecorded.
- `fetch_shop_assets.py`, `fetch_construction_assets.py`,
  `fetch_fletching_assets.py`, `fetch_crafting_assets.py` and
  `fetch_smithing_assets.py` download the current revision, so a forced
  re-fetch replaces the pinned 2012 art.

## Checks

GATE RESULTS FILLED AT LANDING.
