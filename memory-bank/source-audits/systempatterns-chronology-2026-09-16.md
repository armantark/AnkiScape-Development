# System patterns chronology

These passages preserve historical claims verbatim. They do not establish current behavior.

## Cadence shadow evidence

Original line range: 136-138.

- `logic/cadence_shadow.py`: retained Phase 3 evidence resolver and reporting support.
  Its old observer state is never advanced by the default runtime and never
  seeds live cadence state.

## Training urn catalog

Original line range: 152-152.

- `data/urn_data.py`: the authority for all 26 training-urn tiers, five physical states, source IDs, charge eligibility, sanitation, and custom-layout state materialization.

## Cadence save state

Original line range: 174-181.

- Cadence state is a route-keyed `player_data["cadence_profiles"]` mapping with
  exactly five sanitized fields per route: `credit`, `opening_ready`,
  `assigned_reviews`, `opportunities_emitted`, and `cadence_version`. Config v34
  adds the mapping without rewriting existing state. Because review undo diffs
  the complete `player_data`, cadence residuals require no separate undo stack.
- Historical shadow observation used a separate route-keyed
  `player_data["cadence_shadow"]` namespace. The namespace may remain in old
  saves and reports but is not promoted or advanced by live dispatch.

## Fletching rollout

Original line range: 205-205.

- Fletching is the first staged expansion skill to complete backend + target-panel rollout. It uses stable recipe IDs for save/UI selection, because multiple recipes can produce the same inventory item (for example, several log tiers all output arrow shafts).

## OpenRS2 search coverage

Original line range: 220-234.

- OpenRS2 item, NPC/object, and interface searches derive their scan range from
  each cache index, then exit 3 and emit
  `PARTIAL_SEARCH skipped_count=<count> skipped_ids=[...]` after preserving
  partial hits whenever a known unreadable condition occurs. Item searches count
  the loader's explicit `MISSING OPCODE` failures; NPC/object searches count
  `BufferUnderflowException`; unrelated runtime failures propagate. Before this
  gate, the readers used hard-coded bounds and swallowed every runtime failure,
  so past conclusions that a value was absent from the client are not generally
  trustworthy unless the search can be rerun and shown complete. The rev-742
  interface reader currently refuses
  components beginning with `0x03`: the library's pre-decoder guard labels any
  first byte other than `0xFF` as `if1`, although its decoder handles that
  version. Fixing that guard is separate work. Future work: interface integration
  coverage uses only rev 727 and rev 742 although seven extracted caches exist;
  five remain untested.

## Generated quest catalog census

Original line range: 422-422.

- The broad quest catalog is generated, not hand-maintained. `tools/build_pre_eoc_quest_catalog.py` produces a 194-row pre-EOC catalog by real release order, with Recipe for Disaster split into separate subquests. Catalog/stage-row presence is coverage scaffolding, not a claim of full quest parity: later passes must still verify authentic stages, routes, branches, item transformations, combat, rewards, and unlocks under `memory-bank/pre-eoc-source-verification-standard.md`, waiting for high-fidelity Darkan where necessary. Each row should carry source oldids, strict prerequisites, point/XP/item rewards, lamp rewards, and source-backed journal stages. Hand-audited overrides belong in `data/quest_data.py` when pinned pre-EOC evidence is stricter than generated or emulator data.

## Quest combat rollout and source census

Original line range: 649-746.

- Quest combat encounters use the persistent shared combat engine without an
  enable switch. Each Quest review applies one combat burst through
  `apply_quest_combat_encounter_pure()` using the player's equipment, food, and
  prayers; surviving enemy lifepoints persist in
  `player_data["quest_combat_active_encounters"]`, and player death follows the
  ordinary combat death path. Resolver readiness still requires source-backed
  NPC stats for the encounter's attack style. A player combat-level gate applies
  only when the encounter explicitly provides `minimum_player_combat`; a missing
  value means no level gate. Combat quantities are per-enemy progress, not
  group-complete flags: one Quest review increments
  `player_data["quest_combat_encounter_counts"][quest_id][encounter_id]`, and
  only when the count reaches the sourced `QuestCombatEncounter.quantity` does
  the runtime write the completed encounter id into
  `player_data["quest_combat_encounters"]` for compatibility with older saves.
  Existing saves that already have the completed id still satisfy the blocker.
  Encounters missing stats remain blocked as `combat_missing_stats`.
  Focused `data/quest_data.py`
  stage-addition combat rows may carry local 2011Scape NPC stats directly when
  the source path is recorded, and the catalog generator may enrich generated
  encounters from local source data in strict precedence order: 2011Scape NPC
  definitions first, then Darkan/2012scape combat definitions keyed by exact
  NPC name plus combat level. Darkan duplicates can be accepted only when all
  captured battle stats/configs agree; conflicting duplicates stay statless.
  The Restless Ghost Skeleton Warlock is the focused override proof case;
  Demon Slayer's Delrith is now a focused Darkan stage replacement, Dragon
  Slayer's Elvarg proves the generated Darkan fallback, and Elemental Workshop's Earth Elemental proves the identical
  duplicate-source path, while Priest in Peril's Monk of Zamorak and Troll
  Stronghold's Dad prove focused conflict resolution from area-specific Darkan
  quest/combat sources. Witch's House first proved a focused replacement can
  split an ambiguous generated fight into four resolver-ready Darkan-backed
  forms; its current full-stage replacement keeps those forms at stage 9 after
  keys, Magnet, Cheese, patrol, glove, and shed-door gates.
  Focused combat replacements may also expand one generated row into multiple
  source-backed encounters without replacing the quest's other stage
  requirements; Spirits of the Elid's generic `Golem x3` row now expands into
  Black, White, and Grey golems while preserving its generated item/tool rows.
  Resolver readiness is attack-style aware: magic encounters require
  hitpoints, defence, and magic; ranged encounters require hitpoints, defence,
  and ranged; melee/unknown encounters require hitpoints, attack, strength, and
  defence. A complete melee fallback handles inconsistent style metadata such
  as TokHaar-Mej, but hitpoints-only Darkan files still stay blocked until
  style-critical combat stat evidence exists. H.A.M. mage, The Void Stares
  Back's Torcher/Defiler, and The Elder Kiln's TokHaar-Xil prove the
  style-aware generated path. The Darkan `developer-information/beasts.txt`
  fallback may fill missing or zero generated Darkan combatdef attack,
  defence, magic, and ranged values only when the combatdef has an exact ID
  match or an unambiguous name/level identity and the merged payload satisfies
  the same attack-style-aware resolver contract. It must not infer melee
  Strength from beast metadata, and `npc_stats_source` should mention
  `beasts.txt` only when a beast value actually contributed to the generated
  payload. Darkan combatdefs without `combatLevels` may still become
  resolver-ready when their hitpoints/configs plus an exact name/level
  `beasts.txt` signature satisfy the style-aware contract; multi-id combatdefs
  must be merged per matched name/level so one dungeoneering file cannot smear
  stats across unrelated levels. TokTz-Ket-Dill's Lava monster, Nomad's
  Requiem's Nomad, Forgiveness of a Chaos Dwarf's Chaos dwarf hand cannoneer,
  The Blood Pact's Caitlin, Love Story's Pit scabarite, and Salt in the Wound's
  Forgotten mage/ranger prove these paths. Focused name-shape replacements now
  make Heroes' Quest's Entrana Fire Bird and Another Slice of H.A.M.'s
  H.A.M. ranger resolver-ready from Darkan combat sources. A Soul's Bane proves
  that a focused full-stage replacement can remove bad generated anger-room
  combat rows, keep the rage room as a required-action gate, and split later
  Darkan-backed room fights into multi-count enemies. Death to the Dorgeshuun's
  Senior H.A.M. guard proves focused generated-row replacement can preserve a
  historical quantity while mapping to a local Darkan NPC/combatdef identity.
  Shield of Arrav adds route-specific Jonny the beard and Weaponsmaster
  encounters with Darkan resolver stats; both routes now resolve those fights
  through the shared engine, while statless encounters are reported as
  unmodelled. Fight Arena adds
  Bouncer as a Darkan resolver-ready focused stage row while keeping the
  Khazard ogre and Khazard scorpion blocked as missing-stats encounters because
  their available Darkan combatdefs carry hitpoints/max-hit metadata but no
  style-critical melee stats. Merlin's Crystal adds Sir Mordred as a
  Darkan-stat-backed resolver encounter while treating Thrantax as a ritual
  action instead of an invented battle. The generated combat parser now also
  resolves safe historical-name mismatches for Temple of Ikov's Guardians of
  Armadyl and Observatory Quest's Poisonous Spider. When stronger local quest
  source says a generated combat row is a false positive, replace the live stage
  chain instead of carrying the false row: Dwarf Cannon proves this by replacing
  generated level-2 Goblins with a Darkan-backed noncombat chain and `combat:
  None.` Scorpion Catcher then adds a source-backed level 39 jailer combat gate
  from Darkan quest and combatdef evidence while keeping the other scorpion
  catches as route/action gates. Heroes' Quest now adds Ice Queen and Grip
  source-backed resolver rows while keeping Ice Queen lair access as a route
  blocker rather than the old generated Jailer assumption. Shilo Village now
  splits Nazastarool into three focused sourced forms, Legends' Quest preserves
  Nezikchened as a three-kill encounter, The Feud adds Tough guy, and Recipe for
  Disaster: Freeing Sir Amik Varze adds a resolver-ready Black Dragon while the
  Evil Chicken stays missing-stats blocked. Statless combat rows
  are classified by
  `tools/audit_quest_combat_stat_gaps.py` and are active quest debt; the
  current count lives on `memory-bank/future-work-kanban.md` (Pass 13 follow-ups).
  Historical RuneScape Wiki monster pages are now audited by
  `tools/audit_quest_historical_wiki_combat_stats.py` as a separate source tier:
  LP, max hit, and attack-style prose are useful metadata, but they must not be
  counted as resolver-ready hidden combat stats. The 2026-06-22 pass found 77
  metadata-only pages, 32 rows without monster metadata, and 0 remaining rows
  with resolver-ready historical-wiki hidden stats.

## Smithing station rollout

Original line range: 769-769.

- Smithing now follows the source-data-module pattern too (`data/smithing_data.py`). It is the first skill with two XP-bearing stations under one skill: smelt and forge are both recipes in `SMITHING_DATA`, selected by stable `current_smith` IDs, while `BAR_DATA` is only a compatibility view for old smelt-only UI paths. Runtime uses one pure processing helper for both stations and keeps hammer/tool requirements implicit; level and inventory materials are the only backend gates. Iron bar smelting is the only source-backed random smelt action: after a valid action starts it consumes `Iron ore`, then either produces `Iron bar` and XP or records a `smelt_fail` telemetry failure with no output/XP. Other smelt bars and forge rows stay deterministic unless a source audit proves another post-start failure.

## Item tradability rollout

Original line range: 780-780.

- Item tradability is now explicit in `ItemDefinition.tradeable`, seeded from source data for Mining additions. Do not infer GE eligibility from category alone; future economy work should consult item metadata and document source anomalies (for example Dragon pickaxe 15259/15261 and Varrock armour 4).

## Random utility action rollout

Original line range: 782-782.

- Random no-XP Utility actions can need special pure helpers. `Open bird nests` is the first example: it is a Utility/Activities action, but it consumes any known nest subtype and rolls source contents instead of using a fixed `requirements -> output_item` recipe.

## Landmark release

Original line range: 789-792.

Stronghold of Security, shipped on 2026-07-08 in commit `d3d1f57`, is the first
landmark: a one-time step-counter activity in the Utility hub. Landmarks are
counters rather than repeatable material conversions, so they stay outside
`UTILITY_ACTIVITY_DATA` and use this wiring:

## Architecture board rollout

Original line range: 829-829.

The current P0 architecture board now has backend modules for skill, item, review-action, runtime-handler, target-row, grouped target-tree, and achievement metadata. Remaining architecture pressure is lower-priority and mostly around stats rendering, icon/image registration, tests, and the large Anki/menu orchestration surface in `__init__.py` / `ui/ui.py`.

## Nested closure incident

Original line range: 942-942.

`show_main_menu` is a very large function that defines many nested helpers (one per tab/section). All of these are locals of the *same* scope, so two sections defining a helper with the same name (e.g. `_select_skill`) silently rebind it — the later definition wins, and earlier callers route into the wrong function with no error. This caused the Skills-hub panel to ignore clicks (the Stats tab's `_select_skill` shadowed the hub's). Mitigation: prefix section-scoped helpers with their section (`_select_hub_skill`, etc.), and prefer the offscreen Qt behavior test to catch misrouted handlers. Longer term, splitting these sections into their own builder functions/classes would remove the shared scope entirely.

## Deferred tab rollout and measurements

Original line range: 946-974.

Opening the menu cost about 1.2 s on a real save (measured 2026-07) when every
tab was built up front. Five tabs build on first show: Shop, Quests,
Challenges, Achievements, and Collections each export a
`build_<name>_tab(ctx) -> QWidget`, and `show_main_menu` inserts an empty
placeholder page per tab and fills it from a `QTabWidget.currentChanged` hook.
Skills, Grand Exchange, Equipment, Stats, and Settings build at open, and the
Bank widget tree also builds at open behind its placeholder.
Rules that keep this correct:

- Connect the `currentChanged` hook only after every placeholder is inserted.
  The first `addTab` already emitted `currentChanged(0)`.
- Cross-tab refreshes go through `ctx.refreshers` (keys: `active_label`, `gear`,
  `shop`, `quests`). A missing key is a deliberate no-op: every builder derives
  its whole rendered state from `player_data` and `ctx.selection` at build time,
  so a skipped refresh is deferred work, not lost information. Refreshers must
  take no data arguments, and a callback must write state into `player_data` (or
  `ctx.selection`) before firing one.
- Tests must open a deferred tab before touching its widgets
  (`_open_shop_tab` / `_open_quests_tab` / `_open_achievements_tab`), and quest
  journal bodies fill on first expand, so reading journal text needs
  `_expand_quest_card`.
- Skills, Bank and Equipment are mutually recursive through
  `_refresh_equipment_views`; splitting them means splitting that coupling.
  No profiler exists in `tools/`, so open-cost shares are unmeasured; the
  open-time target and facts sit on `memory-bank/future-work-kanban.md`.

Related: `shop_logic.shop_view_models_pure` exists because
`ensure_shop_state_pure` deep-copies the entire save, and the browse list needs
a view model per shop — one snapshot for the batch instead of ~270 copies.

## Dark-mode text incidents

Original line range: 999-999.

Recurring bug: greyed/disabled/placeholder text rendered with `palette(mid)` / `QPalette.Mid` becomes **invisible in dark mode**, because `mid` is a frame/border role that resolves to a near-black grey. It has bitten the Skills-hub train button, the Smithing locked rows, and the Equipment empty slots. Fix at the root: `ui.dim_text_color(widget)` (for `setForeground`) and `ui.dim_text_css(widget)` (for stylesheet `color:`), which derive the color from the theme's real `Text` role and drop the alpha so contrast holds in both themes. `palette(mid)` is fine for borders only. Also prefer `palette(text)`/`palette(base)` over `buttonText`/`button` for button labels (the button face renders light on macOS dark mode). Enforced going forward by `.cursor/rules/qt-dark-mode-text.mdc` and the regression test `test_empty_slot_text_is_dark_mode_safe_not_palette_mid`. When changing UI colors, verify in dark mode, not just light.

## Melee resolver release

Original line range: 1020-1043.

The stab, slash, and crush resolver shipped on 2026-07-08 in commit `a799d02`.
It combines the equipped weapon's `weapon_type` ID with the selected slot through
`WEAPON_TYPE_ATTACK_STYLES` in `data/combat_data.py`, transcribed from 2011Scape's
`AttackStyleData.kt`. Storage deliberately keeps two orthogonal fields:
`combat_attack_style` retains the weapon-style string
(`accurate`/`aggressive`/`defensive`/`controlled`/`ranged_*`/`magic_*`), while
`combat_attack_style_type` selects `auto`, `stab`, `slash`, or `crush` within
that slot. `auto` uses the weapon's first matching slot, defaults to `auto`, and
requires no migration for old saves.

Do not collapse base weapon style and XP mode. `TWO_HANDED_SWORD` slot 3 is the
only anomaly: its `weaponStyle` is `AGGRESSIVE`, but its `xpMode` is `SHARED`.
Effective level and accuracy therefore use the base weapon style, while XP uses
the resolved slot's `xp_mode` through `melee_xp_style_id` and
`_COMBAT_XP_MODE_TO_STYLE_ID`.

D1's type-specific player roll uses `attack_<type>` and `defence_<type>`, but an
enemy attacking the player still uses `max(attack_*)` and `max(defence_*)`.
Enemy data exposes only `attack_style: "melee"`, with no concrete physical
subtype to resolve, so that `max()` boundary is intentional parity behavior.
The pure entry points are `combat_melee_attack_type_pure`, which returns
`(style_type, xp_style_id)`, `combat_weapon_attack_style_slots_pure`, and
`combat_weapon_style_options_pure`. Typeless weapons and bare fists use
`WEAPON_TYPE_UNARMED_STYLES`, all crush.

## Promotion commands and threshold history

Original line range: 1057-1110.

The active remote procedure is
`python3 tools/promotion_gate.py run <promotion-worktree> --remote-lanes`,
followed by the unchanged
`python3 tools/promotion_gate.py land <promotion-worktree>`. Remote mode runs
only the plain and Qt test lanes, serially, through
`/opt/homebrew/bin/python3 tools/run_remote_tests.py <exact-worktree> {plain,qt}`.
Documentation, test-quality, reachability, worktree-layout, clean-tree, and diff
checks still run locally in the promotion worktree. Omitting `--remote-lanes`
keeps the original local lane commands. Use `--plain-only` only for a
branch-side check when the merged-tree promotion seat will run the Qt lane;
plain-only evidence cannot authorize a landing.

The remote runner accepts a lane only when discovery is at least 4,506 tests and
active coverage (`tests - skipped`) is at least 3,994 tests for plain or 4,503
for Qt. Pin active coverage rather than an absolute skip count: adding a valid
Qt-only test increases plain skips without reducing the plain lane's executed
coverage. Dispatches started on the same machine share one fixed absolute lock
path and hold its exclusive local flock through rsync and polling while the
local dispatching process lives. Promotion gates may still register
concurrently, but a second dispatch from that machine reports the lock path and
waits before touching the shared mirror. The flock provides neither
cross-machine nor remote-process-lifetime exclusion: interruption or timeout can
leave the detached MacBook lane running after lock release. Run-specific IDs
prevent that orphan from mixing its logs or report into later evidence, but a
later dispatch can still fail spuriously and requires operator reconciliation
before retry.

A successful gate atomically records the exact commit, every passed check, and
a real `remote_lanes` boolean in the shared Git common directory; old evidence
without that field parses as local evidence. Remote evidence is recorded, not a
global landing requirement, because local mode remains supported. The gate
requires a clean worktree so those checks measure that commit rather than
uncommitted files. The reachability check reads all seven reachability pins from
the gated tree, compares them with that tree's own JSON audit and expected exit
code, and accepts only an exact match. A content addition must update those
pinned assertions in the same commit. This supersedes the 2026-08-22 05:52
papercut's interim rule to preserve the old grep-based informational behavior.
Starting any rerun removes that commit's prior evidence, and a failed rerun
writes none. The established `ankiscape_worktrees/gate-<short-sha>.log` and
`ankiscape_worktrees/gateplain-<short-sha>.log` paths remain unchanged.

The remote verification checkout is an rsync mirror of the working tree and has
no `.git` directory. Tests that run there must build fixtures from the
filesystem and must not shell out to Git. Gate registration, exact-commit
checks, evidence, landing locks, and landing state remain authoritative in the
canonical Git common directory. Gates for different commits may run together,
and each active marker is protected by an OS file lock so a recycled PID cannot
impersonate the gate process.

Land only with the command above, not a hand-written `git merge --ff-only`.
Landing is serialized, requires full-gate evidence for the exact target commit,
refuses while another tree is being gated, and refuses a target that is not
descended from current `main`. An unlocked active-gate marker is stale
regardless of the PID written inside it and is reported before removal.

## Quest reward replacement incident and census

Original line range: 1115-1127.

`QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID`, `QUEST_UNLOCK_REPLACEMENTS_BY_ID`, and
`QUEST_XP_REWARD_REPLACEMENTS_BY_ID` in `data/quest_data.py` replace a quest's
whole tuple; they do not extend it. Writing one corrected string deletes every
generated entry the catalog supplied for that quest. Four separate agents made
this mistake on one branch, and it cost three review rounds. The symptom is
silent: the test suite stayed green because the unlock check used `issubset`.

The check that catches it: load `QUEST_DATA` on canonical main and on the
branch, then difference the reward, unlock, and experience sets for all 196
quests. Any quest that loses an entry is a regression unless the loss is a
deliberate, sourced rewrite. Access text belongs in `unlocks`, never in the item
reward tuple; use a whole-tuple replacement only after verifying every genuine
item reward on the pinned source.

## Cadence report catalog

Original line range: 139-141.

- `tools/cadence_shadow_report.py`: renders current, proposed, and pinned source
  XP/hour for either the complete six-skill route catalog or accumulated shadow
  state from a player-data JSON export.
