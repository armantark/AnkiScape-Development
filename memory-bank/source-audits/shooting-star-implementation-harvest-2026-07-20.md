# Shooting Stars implementation harvest

Date: `2026-07-20`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **mechanic-complete horizontal slice implemented with a compact,
period-qualified location set; exhaustive landing locations and hidden server
distributions remain data-depth work.**

## Period evidence

The primary source is the final pre-cutoff RuneScape Wiki revision of
`Shooting Star`, oldid `6556329`, timestamp
`2012-11-15T09:20:35Z`:

- Shooting Stars are members-only Distractions and Diversions that fall about
  every two hours;
- the current layer requires Mining level `size × 10`, down to level 10;
- the first player to attempt a star receives `75 × Mining level` XP and does
  not need the layer level or a pickaxe for that tag;
- the nine exact layer rows are:

| size | level | XP per stardust | layer stardust |
|---:|---:|---:|---:|
| 9 | 90 | 210 | 15 |
| 8 | 80 | 145 | 25 |
| 7 | 70 | 114 | 40 |
| 6 | 60 | 71 | 80 |
| 5 | 50 | 47 | 175 |
| 4 | 40 | 32 | 250 |
| 3 | 30 | 29 | 439 |
| 2 | 20 | 25 | 700 |
| 1 | 10 | 14 | 1,200 |

- stardust is capped at 200 across inventory and bank, while Mining XP
  continues after the cap;
- fully depleting the star exposes the Star sprite, and saved dust survives
  between stars;
- one exchange per day can pay, at 200 dust, 152 Cosmic runes, 52 Astral runes,
  20 noted Gold ore, and 50,002 coins;
- the exchange also grants a 25% chance of an additional ore for up to fifteen
  in-game minutes; and
- sapphire-through-diamond gem rolls can occur while mining and the Amulet of
  glory improves the chance.

Source:
<https://runescape.wiki/w/Shooting_Star?oldid=6556329>

The period page establishes that sub-200 rewards scale with the submitted dust,
but it does not expose the server's exact rounding rule. It also does not expose
the initial-size distribution, first-finder probability, crowd-arrival
distribution, or exact incidental-gem probability.

## Item identity

The period cache item table identifies Stardust as item ID `13727`. The cache
proves identity, not exchange arithmetic or server rolls.

## Period assets

`tools/fetch_shooting_star_assets.py` requests the newest file revisions at or
before `2012-11-20T23:59:59Z`, records central provenance, trims transparent
padding, and normalizes the visible UI art:

- Star sprite: timestamp `2011-01-15T23:07:03Z`, SHA-1
  `1bdefad053accf87649f1ba12bd67baef164914b`;
- Stardust: timestamp `2010-01-27T02:46:04Z`, SHA-1
  `88eeba3e73081088138f5d87f9aaec15920e6d8a`.

The archive URL can contain the later date on which a period upload was
superseded. The file timestamp and SHA-1 above identify the selected period
revision. Runtime surfaces scale the Star sprite into the standard `28 × 28`
box and use the normalized Stardust inventory icon.

## Owner-settled AnkiScape translation

The closed Mining/activity contract supplies these review-native mappings:

- a new communal star slot every 20 answered cards;
- one sprite reward allowance per 240 answered cards;
- one successful selected review mines one stardust and awards the exact
  current-layer XP;
- other simulated miners deplete the finite shared layers through the shared,
  monotonic naturalized-population curve;
- Casual joins the natural star and waits visibly through inaccessible layers;
- Advanced saves a preferred contiguous starting-size range and the shared
  Quiet / Normal / Busy population profile;
- selection joins the active layer directly, with no map, telescope, travel,
  or scouting phase;
- the first-attempt tag remains possible without a usable pickaxe or layer
  level;
- exchange is a manual direct action with its own undo boundary; and
- no gameplay mechanic reads wall-clock time.

The Star sprite's source ten-minute availability maps to two answered reviews,
the smallest whole-review window that does not shorten it under the established
six-source-minute world-review model.

## Disclosed bounded abstractions

Values unavailable from the period source are represented without claiming
server recovery:

- deterministic seeded initial-size selection;
- first-finder chances of `0.30 / 0.16 / 0.08` for Quiet / Normal / Busy;
- the existing naturalized-population S-curve for crowd discovery and
  depletion;
- floor-proportional sub-200 exchange rewards; and
- the already implemented ordinary Mining gem roll and Amulet-of-glory bonus.

These are data-depth debts, not missing mechanics. A later source harvest may
replace the parameters without changing the event state machine, UI, storage,
undo, or activity dispatch.

The fifteen-minute extra-ore effect is no longer timing-blocked. The live
cadence kernel supplies RuneScape ticks, so the source duration is exactly
`1,500` ticks. It decrements through the same review-driven temporary-effect
clock as other timed effects and never through elapsed real time. Its 25% roll
stacks with existing Mining extra-output effects.

## Deliberate data boundary and dependencies

The implementation uses six unrestricted period-flavor landing locations.
Completing every restricted location and its quest/area eligibility is deferred
catalog depth because the owner-settled product removes map travel and scouting;
the compact set exercises no additional mechanic less honestly.

The source's D&D token and Squeal ticket can grant an additional exchange.
Their acquisition systems are not part of the current reachable core and are
therefore dependency-deferred. They must be added through those systems rather
than invented as Shooting Stars buttons.

## Verification map

- `tests/test_shooting_star_logic.py`: slot spawning, preferences, first tag,
  inaccessible-layer waiting, communal layers, dust cap, persistent dust,
  sprite expiry, exchange scaling, corrupt-state repair, and tick duration.
- `tests/test_runtime_actions.py`: selected-review mining, telemetry, and
  extra-ore stacking.
- `tests/test_storage_pure.py`: versioned default and migration repair.
- `tests/test_cadence_live.py`: explicit activity-group cadence declaration.
- `tests/test_integration_smoke.py`: review undo and manual exchange undo.
- `tests/test_main_menu_widget.py`: Activities-only card, policies, selection,
  exchange, Review HUD, and real offscreen Qt behavior.
- `tests/test_skill_and_item_registry.py` and
  `tests/test_ui_asset_normalization.py`: navigation reachability and normalized
  visible art.

## Workflow note

Read-only workflow run `f19d541f-c5fb-4419-873b-26b4006bdc5a` was cancelled
after one review leaf consumed 203,470 output tokens without producing a final
answer while two sibling leaves never established sessions. The root
independently reproduced the source and runtime findings. The failed workflow
supplied no accepted implementation claim.

## Final Activities surface

The owner rejected the earlier crowded stack of rich activity cards and then
specified that the top detail region be paginated rather than placed inside a
scroll window. The final Activities surface uses one `QStackedWidget`:

- selecting a rich activity in the grouped tree selects exactly one detail
  page;
- clicking a group header clears the detail page instead of leaving a stale
  activity visible;
- refreshes refit the selected page after dynamic labels change;
- rows without a rich page show only the compact picker; and
- Utilities remains a separate surface and never displays Activities pages.

A restarted native macOS Anki process verified the real dark-theme surface,
one menu instance, one selected Shooting Stars page, a visible grouped picker,
and no nested detail scrollbar. The final offscreen render is generated by
`tools/render_shooting_star_ui.py`.

Kimi K3's bounded taste pass returned a ship verdict and identified the stale
group-header page and dynamic-height refit defects; both are fixed and
regression-covered. Its separate global-icon pass also caught a current-RS3
Combat render and a Mining-only Skills-tab glyph. The final vocabulary uses
the legacy OSRS Combat, Skills, and Stats sprites in standard UI boxes, while
all visible files remain tight-alpha normalized and provenance tracked. The
required Fable pass is externally blocked because the mandatory fresh quota
probe cannot read the Claude Code OAuth credential from macOS Keychain
(`security` exit 51); it was not bypassed.

## Reachability closure

The deterministic item graph now models both activity edges:

- `Activity:shooting_stars:mine` produces Stardust; and
- `Activity:shooting_stars:exchange` consumes Stardust and exposes the
  source-backed reward family.

The live report resolves Stardust through the mining activity and does not
leave the exchange action blocked. This is an audit edge only; it does not
change runtime quantities or probabilities.

## Closure verification

- complete non-Qt discovery: 1,957 tests pass, with 257 expected
  environment skips;
- complete real offscreen-Qt discovery: the same 1,957 methods pass, with one
  intentional platform skip;
- targeted final UI checks: six tab-icon, Combat-icon, pagination, card
  visibility, and Shooting Stars interaction tests pass;
- asset/fetch checks: ten tests pass and all visible alpha bounds are tight;
- test-quality audit: zero hard issues;
- documentation, compilation, JSON, diff, and worktree-safety audits: pass;
- item graph: 1,415 actions, 2,082 reachable items, 168 orphan inputs, and 189
  unresolved actions, with the baseline nonzero exit retained for the known
  backlog; and
- results artifact:
  `memory-bank/status-updates/shooting-stars-horizontal-mvp-results-2026-07-20.html`
  (`https://uhov58kni1bj.postplan.dev`).
