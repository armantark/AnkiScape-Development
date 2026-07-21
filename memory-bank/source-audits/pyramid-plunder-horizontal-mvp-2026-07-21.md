# Pyramid Plunder Horizontal MVP

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **mechanic-complete horizontal slice implemented; exhaustive hidden-roll
precision remains deferred data depth.**

## Authority and pinned evidence

The owner-settled design authority is
`pyramid-plunder-loop-2026-07-17.md`; cadence authority is
`activity-cadence-reconciliation-2026-07-18.md`. The immutable period page is
RuneScape Wiki `Pyramid Plunder` oldid `6529238`, timestamp
`2012-11-03T18:18:22Z`:

<https://runescape.wiki/w/Pyramid_Plunder?oldid=6529238>

The implementation also pins Darkan commit
`ff5b18aaf62d231123f947f3fc13cdcd9e4d2b7d`, specifically
`PyramidPlunder.kt`, `data/npcs/drops/pyramid_plunder/**`, and the matching
cache item list. The period page controls conflicts.

The registered tradeable rewards were also re-harvested through
`tools/generate_ge_period_data.py`. Their cutoff Exchange revisions pin the
ordinary artefact buy limit at `100`, the Pharaoh's sceptre buy limit at `10`,
and exact November 2012 guide prices. The immutable oldids and timestamps are
recorded per item in `grand_exchange_period_generated.py`; examples include
Golden scarab oldid `6570646` (`2012-11-18T03:53:19Z`), Jewelled golden
statuette oldid `6540410` (`2012-11-07T03:50:47Z`), and Pharaoh's sceptre
oldid `6562804` (`2012-11-16T04:42:22Z`).

## Exact period rows shipped

- Entry requires Thieving 21 plus either `Icthlarin's Little Helper` started or
  charged sceptre access. The eight room thresholds are
  `21/31/41/51/61/71/81/91`; the room-eight engraved sarcophagus additionally
  requires Runecrafting 75.
- Room base XP is `20/30/50/70/100/150/225/275`; urn XP is
  `60/90/150/215/300/450/675/825`; chest XP is
  `40/60/100/140/200/300/450/550`; door XP is
  `40/60/100/140/200/300/450/0`; every spear trap awards 10 XP.
- Rooms contain thirteen urns except room three, which contains twelve. The
  period page's room-four 215 urn XP wins over Darkan's computed 210; that
  disagreement is preserved rather than silently averaged.
- Snake bites apply the published 10–40 LP and starting poison 20. Scarab
  poison starts at 38 and a triggered scarab awards no chest XP.
- The eleven ordinary artefact values are
  `50/75/100/150/175/200/750/1000/1250/7500/12500`. Darkan's exact per-room
  urn, sarcophagus, and engraved-sarcophagus tier weights are used. Its
  Pharaoh's-sceptre denominators are
  `3500/2250/1250/750/650/650/650/650`; Black ibis uses `1/2300`, or `1/1150`
  with Sceptre of the gods; Sceptre of the gods uses `1/650` from the engraved
  sarcophagus. Ring of wealth applies Darkan's `0.97` denominator multiplier.
- Sarcophagus success uses Darkan's Strength room gate and endpoint curve;
  failure damages one fifth of current LP. The engraved sarcophagus awards the
  room base as Runecrafting XP.

Darkan has no golden-chest ordinary drop table. The horizontal slice therefore
uses the same room's Darkan sarcophagus ordinary table as an explicitly named
fallback, while keeping chest XP, scarab behavior, and rare-sceptre behavior
separate.

## Shipped review and inventory model

Entry, priority changes, and leave are ordinary direct undo operations. A run
reserves `activity_session`, persists only its room, maximum room, priority,
accumulated XP and retained haul, and selects the Activities target. Casual
packing takes up to eight highest-healing food items plus one strongest
available antipoison; Advanced uses the existing user-defined carried layout.

One successful answered card resolves one whole room bundle. Max XP rushes the
early rooms and searches every urn in the two deepest accessible rooms;
Balanced opens each chest and adds those deepest-room urns; Treasure opens the
chest and sarcophagus in every room plus the engraved sarcophagus in room eight.
Foreground multiplier `M` resolves at most `M` rooms, stopping at the first
death, full-pack exit, Pharaoh's-sceptre expulsion, or natural completion.
`Again` performs no activity action. There is no wall-clock state, hidden
Combat encounter, extra object review, or second Thieving cadence gate.

Max XP discards every ordinary artefact. Balanced retains the exact 750-coin
and higher set. Treasure retains all. Retained items occupy real carried slots
and share the same flat Bank quantities; filling the final slot ends the run
and clears only the carried view, thereby banking the haul. Natural completion
and explicit leave do the same. Black ibis, Pharaoh's sceptre, and Sceptre of
the gods go directly to the protected Bank path. Pharaoh's sceptre immediately
ends the run. Dangerous death routes ordinary carried items to the shared grave
and reports that destination instead of claiming they were banked.

## Disclosed source-blocked abstractions

The pinned period page and local emulator do not expose every trigger or damage
row. The following bounded values are implementation balance constants, not
period claims:

- snake poison trigger: `25%` after a failed urn search;
- scarab trigger: `20%`;
- scarab damage: `40 LP`;
- awakened-mummy trigger: `20%`; and
- awakened-mummy damage: `60 LP`.

The `20%` hazard triggers are anchored to Darkan's recovered one-in-five mummy
roll but are still labeled abstractions where the exact row is unavailable.
These rates may be replaced by stronger period evidence without redesigning
the state machine.

## UI, assets, persistence, and verification

Pyramid Plunder is an Activities-only Minigames row with a compact dark-safe
card. The card shows gate or live room state, carried slots, food, antipoison,
haul, saved priority, entry/select state, and confirmed leave without nested
scrolling. Switching away confirms the bank-and-leave boundary. The cutoff
Pharaoh's-sceptre activity icon and all twenty reward/item sprites are fetched
through one reproducible pre-cutoff helper, scaled through the shared 28-pixel
UI path, and recorded in `assets_provenance.json`.

Schema 61 adds sanitized persistent state and reconciles it with Fight Caves,
Stealing Creation, and Barrows ownership. Runtime dispatch awards Thieving,
Strength, and Runecrafting XP once per answered-card transaction; cadence
coverage declares the bounded room group and terminal stop rules. Focused pure,
hook, storage, runtime, cadence, asset, integration, and offscreen Qt coverage
exercises every mechanic above.

Opus's bounded UI pass found one material state defect: entry selection was
committed before the run command succeeded. The command now enters first and
preserves the previous review target on rejection. The same pass drove visible
prior-result copy, a persistent Priority label, active-status contrast, clearer
locked-state and leave-cost copy, and distinct poison-immunity wording. Fable
was reserved by owner instruction; Kimi was not retried at its remaining 4%
quota.

Final closure passes all 2,118 non-Qt tests with 275 expected platform skips
and all 2,118 real offscreen-Qt tests with one intentional skip. Documentation,
test quality, compilation, JSON, diff, all twenty-one new RGBA assets at no
more than 64 pixels, focused reachability coverage, and worktree safety pass.
The reachability report contains 1,438 actions, 2,128 reachable items, 168
known orphan inputs, and 189 unresolved actions. A fully quit and relaunched
native macOS Anki process showed one AnkiScape menu, the paginated Minigames
page, and the normalized Pyramid Plunder row/icon without clipping. The live
account is entry-locked, so its save was not altered to force the active panel.
Results are recorded in
`status-updates/pyramid-plunder-horizontal-mvp-results-2026-07-21.html` and at
`https://8tc4efyc7zls.postplan.dev`.

No owner design gap surfaced. Exact hidden hazard rates and a distinct golden-
chest ordinary drop table remain data-depth work under the breadth-first goal.
