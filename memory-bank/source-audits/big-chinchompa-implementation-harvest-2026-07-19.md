# Big Chinchompa implementation harvest

Date: `2026-07-19`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **source-ready contract implemented; Polar-kebbit quota-ticket use
remains dependency-blocked on the ordinary target restoration.**

## Period evidence reused

The implementation follows the closed contract in
`memory-bank/source-audits/big-chinchompa-loop-2026-07-18.md`. Its primary
literal-wikitext source is `Big Chinchompa`, oldid `6538836`
(`2012-11-06T10:56:45Z`):

- safe twice-daily Hunter D&D;
- random Hunter-area discovery and direct portal;
- twenty-minute maximum duration, late entry, and early communal completion;
- one fifteen-moth Moth jar and Protea-flower attraction;
- the eight exact moth level, XP, and point rows;
- the 1,500 personal event-point cap and 20,000 Competence-point cap; and
- the complete reward shop, including five quota tickets and direct Hunter XP.

Independent period pages:

- `Moth jar`, oldid `6484579` (`2012-10-27T10:13:33Z`);
- `Protea flower`, oldid `6552181` (`2012-11-13T11:13:53Z`);
- `Competence points`, oldid `6241664`
  (`2012-09-13T10:20:35Z`).

Sources:

- <https://runescape.wiki/w/Big_Chinchompa?oldid=6538836>
- <https://runescape.wiki/w/Moth_jar?oldid=6484579>
- <https://runescape.wiki/w/Protea_flower?oldid=6552181>
- <https://runescape.wiki/w/Competence_points?oldid=6241664>

## Cache corroboration

The extracted OpenRS2 rev-736 (`2012-10-09`) and rev-742 (`2012-11-07`)
caches corroborate the following period client identities:

| ID | Name | client options |
|---:|---|---|
| 24948 | Protea flower | `Wield`, `Drop` |
| 24949 | Moth jar | `Check`, `Destroy` |
| 24950 | Carnivorous chinchompa quota ticket | `Read`, `Destroy` |
| 24951 | Pawya quota ticket | `Read`, `Destroy` |
| 24952 | Grenwall quota ticket | `Read`, `Destroy` |
| 24953 | Polar kebbit quota ticket | `Read`, `Destroy` |
| 24954 | Swamp lizard quota ticket | `Read`, `Destroy` |

Cache roots:

- `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/736-2012-10-09/cache`
- `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache`

The cache proves client identity and options, not reward cost, XP, event timing,
or server rolls.

## Period assets

`tools/fetch_big_chinchompa_assets.py` pins the latest file revision at or
before the cutoff and writes transparent PNGs through the shared asset
normalizer. Resolved file timestamps:

- Moth jar: `2012-08-28T18:20:27Z`;
- Protea flower: `2012-08-28T15:34:55Z`;
- green-salamander quota-ticket art used for the period cache's swamp-lizard
  ticket: `2012-08-28T18:36:30Z`;
- carnivorous chinchompa ticket: `2012-08-28T18:20:26Z`;
- Pawya ticket: `2012-08-28T23:04:00Z`;
- Polar kebbit ticket: `2012-08-28T19:01:22Z`; and
- Grenwall ticket: `2012-08-28T19:01:23Z`.

No period Big-Chinchompa-specific badge file was available. The activity row
therefore uses the period Moth-jar art rather than a modern or invented badge.
All display surfaces scale it into the standard `28 × 28` UI box.

## Explicit AnkiScape abstractions

The owner-approved contract supplies the following values because the period
sources do not expose server formulas:

- event slots at answered cards `60` and `180` in each 240-card world day;
- six source minutes per answered review;
- quiet/normal/busy aggregate crowd ceilings `0.72/0.92/1.12`;
- one percentage point of communal fullness per completed player jar;
- seeded `±20%` crowd-ceiling variation, `±10%` midpoint variation,
  `±15%` steepness variation, `±10%` smooth phase jitter, and the shared
  `0.75–1.25` world-day envelope; and
- one event point converts to one Competence point at resolution.

These are disclosed review-native abstractions. They are not represented as
recovered RuneScape server constants.

The slot-boundary review discovers the event after that review's selected
action has run. A fresh twenty-source-minute window therefore contains exactly
three complete six-minute future review opportunities. The fourth review would
finish after the source window and is not advertised or admitted.

## Deliberate boundary and remaining dependency

Four ticket routes reuse already implemented ordinary Hunter targets and
consume one carried ticket only after a successful catch:

- swamp lizard;
- carnivorous/red chinchompa;
- Pawya; and
- Grenwall.

The Polar-kebbit ticket is registered and purchasable because the period
reward exists. Its use remains dependency-blocked: the newer tracking/pitfall
Hunter audit marks the ordinary Polar-kebbit target `source_blocked` while its
tracking-roll sequence is unresolved. This is source debt, not an open design
question, and no substitute target was invented.

## Verification map

- `tests/test_big_chinchompa_logic.py`: slots, event window, naturalized crowd,
  moth tiers, grouped jars, caps, reward table, tickets, and sanitization.
- `tests/test_runtime_actions.py`: grouped Hunter XP and successful-catch-only
  carried-ticket consumption.
- `tests/test_storage_pure.py`: default state and migration repair.
- `tests/test_cadence_live.py`: declared `activity_group` and world boundary.
- `tests/test_integration_smoke.py`: shared review clock and complete undo.
- `tests/test_main_menu_widget.py`: activity card, reward shop, population
  preference, private-ground toggle, and Review HUD.

## Workflow note

Readiness workflow run `b63a1a08-a3a0-4ea8-b399-443a2d171fc9` was cancelled
after two Sol-high leaves remained pre-session with no `thread.started`, no
session ID, zero telemetry, and no tool activity. The root independently
reproduced the readiness audit and selected Big Chinchompa. This failure did
not supply or validate any implementation claim.

## Verification

- Focused pure/runtime/storage/cadence/integration verification: `282` tests,
  all passing.
- Focused real offscreen Qt behavior: four Big Chinchompa/Hunter/HUD/geometry
  tests, all passing.
- Complete non-Qt runner: `1,874` methods, all passing with `243` expected
  environment skips.
- Documentation audit: `406` Markdown and `374` HTML files, passing.
- Test-quality audit: `1,874` tests across `80` files, zero hard issues.
- Compilation, diff whitespace, guarded-worktree layout, and normalized-asset
  checks pass.
- The repository-wide reachability audit retains its known baseline of `284`
  orphan inputs and exits non-zero; none of the seven Big Chinchompa items is
  in that orphan set.
- A fully restarted native macOS Anki process opened exactly one AnkiScape
  dialog and verified the dark-mode card and scroll behavior at the real
  application size without changing the user's save before the last reviewer
  polish. The post-review native recheck was unavailable because the Mac was
  locked; focused Qt and a fresh final render cover the accepted tooltip,
  sibling-refresh, carried-ticket, renderer, and icon changes.

## UI review

Fable and Kimi K3 independently reviewed the Utility card, Hunter control, and
Review HUD. Confirmed issues were fixed before closure:

- native progress-bar text and light/dark status contrast;
- wallet and reward-row grammar;
- configured private-ground removal at zero tickets;
- stale Big Chinchompa selection after choosing Evil Tree;
- backend/UI agreement that quota tickets must be in the target's carried pack;
- explicit disabled-purchase reasons;
- a scroll-safe 1,000 × 560 layout with no clipped card rows;
- correct show → resize → process → grab renderer ordering; and
- a restrained 28-pixel backdrop that keeps the dark period Moth-jar sprite
  legible without replacing or modernizing it.

Kimi's open-dialog live-refresh concern was not changed: the shared Review HUD
is the established per-answer live surface, while an already-open main menu
remains a configuration snapshot. Its light-mode progress-text concern was
screenshot-only uncertainty and not reproduced. The root independently
verified every accepted finding against the final tree.
