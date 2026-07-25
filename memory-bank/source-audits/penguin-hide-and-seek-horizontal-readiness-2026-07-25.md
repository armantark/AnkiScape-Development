# Penguin Hide and Seek horizontal readiness

Date: `2026-07-25`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **horizontal mechanic closure implemented and verified.**

Owning design and earlier evidence ledger:
`memory-bank/source-audits/penguin-hide-and-seek-loop-2026-07-17.md`.
The owner-settled contract is the flattened weekly search loop recorded there;
this pass closes the carried-ring gate and the missing direct undo for spy
selection without reopening that design.

## Exact period evidence

- `Penguin Hide and Seek`, oldid `6569778`,
  `2012-11-17T23:47:37Z`:
  <https://runescape.wiki/w/Penguin_Hide_and_Seek?oldid=6569778>.
  The literal cutoff wikitext establishes:
  - ten ordinary weekly penguin spies;
  - five ordinary spies upgraded from one point to two after `Cold War`;
  - one additional one-point polar-bear agent after `Hunt for Red Raktuber`;
  - one additional three-point invisible penguin after `Some Like It Cold`,
    the required `Desert Treasure` progress, and possession of a Ring of
    visibility in the period character's inventory or equipment;
  - weekly maxima of 10, 15, 16, or 19 points for those unlock states;
  - a 50-point storage cap;
  - `6,500 × points` coins on redemption; and
  - `25 × current skill level × points` XP in the chosen skill.
- The local Darkan reconstruction corroborates the ten-spy count, `Cold War`
  point upgrade, polar-bear completion gate, 50-point cap, all-points
  redemption, coin formula, and XP formula:
  - commit `758b41e8c16f1ad424b98aa5812e8f9d06dab541`,
    `src/main/java/com/rs/game/content/dnds/penguins/PenguinHASController.kt`;
  - commit `61c5ab917ce0632088d74be698bbdd4a1e57cc34`,
    `src/main/java/com/rs/game/content/items/Lamps.java:189-205`; and
  - commit `166fced5187dd6f2539d52e23bf21a9ab92660f7`,
    `src/main/java/com/rs/game/content/world/areas/ardougne/npcs/east_ardougne/Larry.kt:130-151`.
- Darkan's reconstructed base `Cold War` entry gate conflicts with the pinned
  cutoff page. The cutoff page controls: the base ten-point roster remains
  available, and `Cold War` upgrades only the five two-point spies.
- The period icon remains the pre-EOC `Rock (Penguin Hide and Seek).png`
  revision timestamped `2010-10-13T03:24:23Z`, recorded in
  `assets_provenance.json` and fetched by
  `tools/fetch_penguin_hide_and_seek_assets.py`.

## Labelled AnkiScape abstractions

- `abstraction/owner-settled-flattening`: selecting a disclosed weekly roster
  entry abstracts travel, roaming, trapping, and community sightings. The next
  successful Activity review spies exactly that selected entry.
- `abstraction/answered-card-calendar`: one weekly reset is `1,680` answered
  cards on `shop_market_clock`; no wall-clock deadline or reset is simulated.
- `abstraction/compact-roster-depth`: breadth one rotates five rows from six
  source-qualified locations in each ordinary point tier and rotates the six
  period polar-bear wells. The complete location corpus is deferred data depth,
  not a missing gameplay state.
- `abstraction/carried-pack-model`: AnkiScape's flat `inventory` is the Bank.
  The Ring of visibility satisfies the invisible-penguin gate only when it is
  present in the Penguin activity's `carried_inventory` view, backed by a real
  Bank copy, or when it is equipped. A Bank-only ring does not satisfy the
  source possession gate.
- `abstraction/atomic-direct-policy`: choosing the next spy is a persisted
  direct action. Like point redemption, it creates an AnkiScape direct-action
  undo snapshot; review undo separately restores the completed spy, points,
  telemetry, and answered-card clock.

## Source-blocked values and deferred depth

No numeric value used by the breadth-one mechanics is source-blocked.

The following remain explicitly `source_blocked/data-depth` and are not guessed:

- the exhaustive cutoff ordinary location and disguise pools;
- the complete historical weekly-location dependency tables;
- exact roaming paths, trap behavior, Larry/Chuck hint wording and deduction,
  and community-sighting coordination; and
- a surviving authoritative period server implementation for the entire
  activity. Darkan remains reconstruction evidence and does not override the
  pinned cutoff page where they conflict.

## Implemented closure

- `logic/penguin_hide_and_seek_logic.py` now rejects a Ring of visibility that
  exists only in the Bank and accepts the ring from the Penguin carried pack or
  an equipment slot.
- `__init__.py` now records spy selection through the same bounded custom undo
  stack used by other direct Penguin actions.
- The Activities card resolves any persistent-activity switch before it saves
  the spy selection. Declining a switch leaves both the current activity and
  Penguin selection unchanged; selection undo therefore restores only the
  accepted direct policy change.
- The Activities card derives the invisible-penguin row and unlock text from
  the corrected pure view, so Bank-only, carried, and equipped states cannot
  diverge between backend and UI.
- Pure tests cover Bank-only rejection, carried acceptance, equipped
  acceptance, quest point tiers, the cap, weekly reset, and both redemption
  formulas.
- Integration tests cover the full two-stack sequence: direct selection,
  review completion, review undo restoring the selection, and direct undo
  clearing the selection. Direct redemption undo remains covered separately.
- Real offscreen-Qt coverage checks Bank-only, carried, and equipped ring
  states and proves that declining a conflicting activity switch does not save
  the proposed Penguin selection.

Verification:

- `python3 run_tests.py`: `2,721` executed, `2,390` passed, `331` skipped.
- `QT_QPA_PLATFORM=offscreen PYTHONDONTWRITEBYTECODE=1 .venv-qt/bin/python -m unittest discover tests`:
  `2,721` executed, `2,720` passed, `1` skipped.

Low-level manual verification remains reachable: open Activities, select any
base-roster penguin, confirm it becomes the next review target, use Anki Undo,
and confirm the prior selection state returns. The quest-gated invisible-ring
matrix is covered automatically because it is not low-level-reachable during
normal owner play.

No owner design gap is present.
