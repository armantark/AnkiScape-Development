# Ranging Guild horizontal MVP, 2026-08-10

## Outcome

The Ranging Guild archery competition and ticket exchange are live on the
Activities surface. One review fires one supplied Bronze arrow. Ten shots
produce a persisted score, one replay-safe ticket claim, and access to the
complete six-row cutoff reward exchange. The first reward closes the existing
Barb bolttip to Barbed-bolt Fletching route.

## Reused frozen evidence

- RuneScape Wiki Ranging Guild oldid `6372385`, timestamp
  `2012-10-09T03:01:36Z`.
- Competition Judge oldid `6454773`, 2012-10-22.
- Ticket Merchant oldid `6226065`, 2012-09-09.
- Archery ticket oldid `6534408`, timestamp
  `2012-11-04T20:38:51Z`.
- Darkan frozen contract:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/ranging-guild-target-contract.json`.
- Darkan restoration tree `28b377b417e1999c131b49f00b5fce782d5a90ff`
  and canonical commit `6e9bf37f85caf9c47f877d571fddc308ceffbaf4`.
- Rev-742 identities: Barb bolttips `47`, Adamant javelin `829`, Bronze
  arrows `882`, Rune arrows `892`, Studded body `1133`, Green d'hide body
  `1135`, Coif `1169`, and Archery ticket `1464`.

No web or cache harvest was repeated. This slice reused the shared Darkan
record exactly.

## Exact live contract

- Effective level 40 Ranged is required; temporary combat boosts count.
- Entry costs 200 Coins and supplies 10 Bronze arrows for exactly 10 shots.
- A shot requires a bow compatible with Bronze arrows and Bronze arrows in the
  ammunition slot. The add-on's equipment model stores the ammo identity while
  inventory stores its count, so each review consumes one inventory arrow.
- Outcomes are Missed `0/0 XP`, Black `10/5 XP`, Blue `20/10 XP`, Red
  `30/15 XP`, Yellow `50/25 XP`, and Bull's-eye `100/50 XP`.
- Hati paws double only that exact activity Ranged XP. No Constitution XP or
  global multiplier enters the result.
- The tenth shot creates a pending claim worth `floor(score / 10)` Archery
  tickets. Claiming is direct-action undo-safe and cannot replay.
- The exchange sells 30 Barb bolttips for 114 tickets, Studded body for 51,
  50 Rune arrows for 1,020, Coif for 12, Green d'hide body for 856, and 20
  Adamant javelins for 292.
- Logging out preserves both active progress and a pending claim. Leaving an
  unfinished competition forfeits its partial score through the established
  activity-switch confirmation.
- The global review multiplier never repeats this activity: one answered card
  remains one shot. The review strip reports Ranged only.
- `Arch Archer` now requires holding 1,001 Archery tickets, while `What, No
  Cuddly Toy?` requires a recorded ticket-exchange purchase; level 40 alone no
  longer completes either Seers task.

## Registered source block

`ranging_guild.hit_quality_resolver` is a declared breadth placeholder. The
period record fixes consequences but not target probability. The live resolver
is Darkan's frozen bounded equation and thresholds. It is not presented as a
recovered 2012 server formula.

Hati paws item acquisition remains data-depth debt. The exact modifier is live
when that equipment identity is present, but this slice does not invent a new
acquisition route.

## Assets and UI

`activityicons/ranging_guild.png` is the normalized pre-cutoff Archery-ticket
bitmap and is reused for the ticket item and activity identity. The exchange
reuses existing normalized reward art. `assets_provenance.json` records the
2011-11-29 source revision. The panel is a compact no-scroll Activities detail
with ready, active, claim-ready, and exchange states.

## Verification

Focused pure/runtime/direct-undo coverage passes 120 tests with one expected Qt
skip. Focused real offscreen Qt passes 16 tests. Full plain discovery passes
4,053 tests with 494 expected skips. These checks cover atomic entry, boosts,
equipment gates, all six bands and rewards, arrow consumption, ten-shot
persistence, Hati paws, one-time claim, cadence, the Barb-bolt bridge, diary
conditions, panel state changes, selector icons, and the actual Activities page.

The first full offscreen Qt lane found two stale Activities inventory assertions:
one expected 29 Minigames, and one exact ID set omitted `ranging_guild`. Both
passed after a test-only correction. Full offscreen Qt then passed all 4,053
tests with three expected skips. Documentation passes across 558 Markdown and
431 HTML files. Test quality reports 4,018 tests in 183 files with zero hard
issues. Compilation, 26 tracked JSON files, placeholder, asset normalization,
diff, reachability, and worktree checks pass. Reachability is now 1,556 actions,
2,573 reachable items, 102 known orphan inputs, and 101 blocked actions.

Native Anki opened one current AnkiScape menu and reached Activities, but
Computer Use returned `AXError.notImplemented` on the non-AX Minigames row.
Native Ranging Guild detail is therefore not claimed.
