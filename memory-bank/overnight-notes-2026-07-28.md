# Overnight running notes — 2026-07-28

Compiled into the morning results artifact; delete after.

## Landed
- **Gravestone rework** merged, both lanes green on main at 3,251 (was 3,247).
  Owner's design end to end: clickable banner, walk-back on the travel clock,
  expiry timer ticks on every answered card (open encounters can no longer
  freeze it), expiry destroys per the sourced period answer, auto-stop option
  default-on, every dangerous death announces itself. Two tests that pinned the
  invented auto-reclaim corrected. Fork queued: Death's Office bridge (agent
  filed it as 4.12 in the queue — renumber to a 3.x open slot when next edited).
- Silent-Agility-death finding (2026-07-15 review, item 1) marked FIXED in the
  session memory.
- Second Ayn Rand deletion: the deployed user_files copy this time; zero copies
  remain anywhere under Anki2.
- Owner's dead-save incident closed: items restored by running the real recovery
  function against his collection (backup taken first at
  User 1/ankiscape_backups/collection-before-grave-restore-20260727-233644.anki2).

## Running
- HUD strip (Opus, worktree hud-strip): pass-3 strip contract — live XP bars,
  D&D+Farming badge with popover navigation, favourites affordance, GE drawer
  under the XP box.
- families-f re-land (Sol): rebase onto main with the full conflict map; gates on
  green lanes plus a clean trial merge. First attempt was botched in resolution,
  reverted from main after the owner's Anki failed to load against it.
- Selection-highlight fix (Sol): ::item:selected rules for every target tree.

## Queued
- Proxy swap to v7.2.103 once the Sol agents land (binary verified, config
  tested on port 8318).
- Dominion Tower, Mobilising Armies, Gnome Restaurant data surface — staggered
  launches on Claude as slots free.
- Art sweep tranche 2 + re-research of the ~200 endpoint-failure assets: waits
  for the codex daily line to reset.

## For the owner's eyes in the artifact
- Four stacked defects produced his equipment scare: silent death, invisible
  grave, auto-deactivated skill, frozen countdown. All four now dead.
- Kimi crossed its daily line again overnight-adjacent; nothing routed to it.

## Update — all five tracked landings closed
- MTA + Temple Trekking re-landed (3,300 both lanes), then the selection
  highlight (3,301), then the HUD strip (3,333 both lanes). Clicked targets are
  now unmistakably blue in both themes, distinct from the green current marker.
- The strip: live XP bars, merged D&D+Farming badge with navigating popover,
  favourites star on the shared control row (schema 95, undoable), GE drawer
  under the XP box with the pass-2 colour rules. Its offscreen probe caught a
  real drawer-position bug the tests missed.
- Proxy v7.2.103 swapped and serving; old binary backed up.
- Strip gap recorded honestly: the XP-bar table covers 12 verified families;
  exhaustiveness sweep died on a provider error and is queued.
- Schema map now: 95 strip (merged), 96 mobilising, 97 gnome-rest, 98 dominion
  (renumbered from 95 by steer).
- Still building: Dominion Tower, Mobilising Armies, Gnome Restaurant (+ its
  concrete presentation fork for the owner).
