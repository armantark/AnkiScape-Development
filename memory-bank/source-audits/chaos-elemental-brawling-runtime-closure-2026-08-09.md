# Chaos Elemental and brawling-gloves runtime closure — 2026-08-09

Backlog id: `skilling-brawling-gloves-runtime`

Status: implemented and verified. This audit supersedes the acquisition and
dependency blocks in `skilling-brawling-gloves-source-closure-2026-08-09.md`.
The period value table and the settled product shape in that audit remain
authoritative.

## Acquisition evidence and abstraction boundary

- RuneScape Wiki `Chaos Elemental` oldid `6544162`, timestamp
  `2012-11-09T01:43:14Z`, establishes the period boss identity, combat level
  305, 2,500 lifepoints, three attack styles, teleport and equipment-removal
  specials, Wilderness location, and brawling-glove drops.
- Darkan restoration commit `16b695bcb5ec6f2ed1a195eb43a5f1f525490416`
  supplies the mechanically complete local encounter reconstruction in
  `src/main/java/com/rs/game/content/bosses/ChaosElementalCombat.java`,
  `data/npcs/combatdefs/uncategorized/chaos_elemental.json`, and
  `data/npcs/drops/chaos_elemental.json`. Its evidence manifest is
  `memory-bank/audit/evidence/runtime/bosses/chaos-elemental/manifest.json` in
  the shared Darkan checkout.
- No period-qualified table recovered the relative special-attack weights or
  the glove drop probability. AnkiScape therefore registers Darkan's `11 / 8 /
  27 / 27 / 27` attack weights and `187 / 1,300,000` per supported pair as
  explicit placeholders. The drop table has a blank remainder and does not add
  any of the seven glove families outside this settled six-skill slice.
- Mining's period page gives a 30-minute use window and an estimate of 350 to
  800 ores. Gameplay never uses wall-clock time. The registered midpoint of
  575 XP actions is the deterministic action-count abstraction.

## Live implementation

- The Chaos Elemental is an obtainable Combat target in the Wilderness bosses
  group. It uses all three ordinary styles, delays the next player attack when
  it teleports, and moves one worn item into the active target carried pack
  when its equipment-removal special lands.
- All six supported gloves are physical, non-stackable hands-slot equipment.
  Each acquired copy owns an independent condition record. Exactly one charge
  is consumed for each XP-awarding action; zero-XP outcomes consume none, and a
  depleted pair disintegrates.
- Matching gloves multiply only their own skill action: 1.5 times outside the
  Wilderness, 4 times inside for Woodcutting, Mining, Smithing, and Cooking,
  and 5 times inside for Fishing and Firemaking.
- Every supported target has a saved `Train in Wilderness` policy in Target
  Details. Enabling it requires a default-No risk confirmation. The action uses
  the existing target-local carried pack and rolls the shared one-percent,
  250-lifepoint PKer-risk channel once per XP action. Food, death, grave,
  training stop, persistence, direct policy undo, and review undo reuse the
  existing shared paths.
- Schema 115 sanitizes the target-local policies and the established equipment
  instance ledger repairs old saves when a glove first appears.

## Assets and visual review

The six glove sprites use provenance-recorded 2010 file revisions and are
normalized below the 64-pixel item ceiling. Chaos Elemental uses a
provenance-recorded `2012-06-05T20:12:51Z` file revision normalized to the
48-pixel combat-target ceiling.

Kimi K3 requested two small copy changes: state the Wilderness XP reward before
the risk in confirmation, and label charge state as `remaining (of maximum)`.
Both changes shipped. Fable independently accepted the final compact Target
Details surface, its default-No confirmation, signal-safe rejection path,
dark-mode text, and coexistence with Cooking's Gauntlets controls.

## Native Anki proof

The real `User 1 - Anki` process opened the current add-on from the canonical
checkout. The native AnkiScape menu showed `Wilderness bosses (1)` in the
Combat selector and rendered the normalized Chaos Elemental row art without a
duplicate dialog or layout regression. macOS accessibility exposed the custom
category controls but rejected coordinate activation with the exact error
`Accessibility error: AXError.notImplemented`; the target-local brawling toggle
is therefore proven by real offscreen Qt coverage, not claimed as a native
interaction.

## Verification

- Focused brawling, Combat, runtime, storage, placeholder, and offscreen Qt
  coverage: 370 plain tests and 2 real Qt tests passed.
- Full plain discovery: 3,972 tests passed in 409.413 seconds with 486 expected
  skips.
- Full real offscreen Qt discovery: 3,972 tests passed in 826.142 seconds with
  3 intentional skips.
- The simplification pass removed duplicate imports and caught one adjacent
  generic-Combat regression before closure: ordinary enemies with a
  player-class-dependent style now remain dynamic when no weighted attack
  table exists.
- Documentation passed for 537 Markdown and 431 HTML files. Test quality found
  3,938 tests across 180 files, zero hard issues, and the unchanged 19
  structural clone groups. Compilation, tracked JSON, diff, asset
  normalization, and worktree safety pass.
- Reachability reports 1,537 actions, 2,339 reachable items, 168 orphan inputs,
  and 188 blocked actions. Its nonzero result is the established dependency
  ledger, not a brawling-glove regression; all six new pairs are reachable.

## Explicit omissions

- Revenants remain outside this slice; Chaos Elemental provides the complete
  obtainable route.
- Combat, Prayer, Agility, Hunter, and Thieving brawling gloves remain outside
  the settled six-skill scope.
- The three registered placeholder values remain candidates for later source
  replacement. No owner design question remains.
