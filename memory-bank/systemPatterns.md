# System Patterns

## Delivered rewards use claim records as their ledger

A reward producer delivers stable claim IDs, and Bank Claims owns their
consumption through the generic claim path. The producer derives pending counts
and completion from those records instead of persisting a second counter; a
versioned migration translates any retired counter once before sanitation
removes it.

## Finite room payouts persist their eligible room ledger

A fixed floor payout split across rooms stores the eligible critical-room ids
at entry, then pays each room's deterministic share when that room resolves.
Sanitation intersects the stored ids with current eligibility and migration
distinguishes legacy completed funding from unpaid rooms. This preserves exact
totals across reloads without making optional rooms dilute the payout or making
repair grant the same pool twice.

## Skill target selectors derive presentation from row metadata

The shared target selector renders fewer than 25 rows as a flat `QListWidget`
and at least 25 grouped rows as a collapsible `QTreeWidget`. A row set without
group metadata stays flat even above the threshold. Both renderers own the same
30-pixel item height, alternating rows, green current-target background, and
bold current-target text; per-skill builders supply metadata and callbacks but
do not choose the widget class.

## One native reviewer strip, one geometry authority

Reviewer chrome is a fixed-height native row inserted in Anki's `mainLayout`
immediately after `bottomWeb`, outside the card webview. Card content never
selects or reserves its geometry. Translucent drawers may cover the card while
open, but their upward stack shrinks to remain reachable inside the main window.
A badge popover closes when no placement avoids the measured card rectangle.

- `ReviewStrip` owns the D&D badge, Farming badge, `ReviewHUD`, Shooting Star
  notice, and main-menu button seats; the bank-run button sits inside the HUD.
  `_sync_review_strip_layout()` selects and sizes the visible seats for the
  available width.
- `logic/review_strip_logic.py` decides strip, Event-log, badge, and bank-action
  views. `logic/grand_exchange_logic.py` owns GE row visibility, text, tone, and
  action. `ui/ui.py` renders those projections without re-deriving them.
- `_sync_review_strip_layout()` is the only geometry authority. It attaches the
  native strip after Anki's answer bar, stacks Event log then GE upward as
  translucent overlays, bounds that stack to the window, and re-anchors floating
  XP in the same pass.
- Every XP emission goes through the retained Event-log seam. Award results
  carry their skill identity, while review aggregation verifies names from the
  real experience deltas; silent awards cannot leak into a later row.
- The Event log renders its visible rows as one escaped `QTextBrowser` document,
  not separate row widgets. This preserves cross-row text selection and copy;
  the view model still owns the 10-row lazy limit and **Show more** expansion.
- Review-strip progress puts the complete labeled value first. Optional detail
  follows it and may clip, but a clipped suffix must never resemble a magnitude
  abbreviation.
- Durable notifications and floating popups are separate projections. Music
  unlocks remain in history; only achievement diary tasks enter the achievement
  popup path.
- The strip bank action is only a runtime request seam. Combat uses the existing
  combat bank-run state, carried activities use their target-specific travel
  profile, and actions without a carried pack spend one review on the standard
  bank trip.
- An activity's trained skills come from `ACTIVITY_TRAINED_SKILLS`, which mirrors
  the `ctx.award_skill_exp` sites because no activity spec declares them. Two
  families resolve theirs at award time and answer for themselves. An activity
  absent from both shows no bar rather than a guessed one.

## Per-copy condition state overlays flat item holders

Most Bank items remain flat name-to-count entries, but degradable non-stackable
equipment uses `equipment_instances` as its exact per-copy condition ledger.
Each stable instance records its family, canonical condition identity, exact
remaining condition, and holder (`bank`, `equipped:<slot>`, `grave`, or
`death_office`). The existing Bank counts, equipment slots, and recovery item
lists remain the visible holders; sanitation reconciles the ledger to them while
preserving already-valid assignments first. This avoids a global inventory
rewrite while ensuring two visually identical copies can retain different hidden
durability through equip, death, recovery, discard, and undo.

## Architecture Snapshot
The add-on is a small Python package loaded by Anki. It separates pure game contracts from Anki-aware orchestration for review dispatch, runtime actions, target rows, and achievements, though some skill behavior also lives in UI, storage, stats, and icon-registration surfaces.

## Documentation Authority

- `memory-bank/papercuts.md` is an append-only shared log and has the tracked
  `merge=union` attribute. If that attribute is unavailable during a conflict,
  resolve the three versions with `git merge-file --union`, then verify that
  every line added by either side over the merge base survives. For papercut
  lines, use `grep -qxF -e "$line" --`; because entries begin with `-`, the
  shorter `grep -qxF "$line"` parses the entry as options and reports false
  losses. Do not use line-count arithmetic as the containment test: identical
  papercuts recorded on both branches correctly collapse to one line, making a
  valid union smaller than ours plus theirs minus base.
- `README.md` is the Memory Bank entry point. It names the current core files,
  evidence directories, and archive boundary.
- `future-work-kanban.md`, `activeContext.md`, `progress.md`, and the live
  registries are current truth and must agree after every significant closure.
- Dated source audits, contracts, briefs, and HTML status artifacts are evidence
  snapshots. Preserve their original claims, but add a clear status or
  supersession note when a later implementation would otherwise make the file
  look current.
- `archive/` holds only completed handoffs, superseded baselines, and resolved
  queues with named live successors. `status-updates/archive/YYYY-MM/` holds old
  human-facing plans, results, and their screenshots; the `status-updates/` top
  level is reserved for current orientation reports.
- Run `/opt/homebrew/bin/python3 tools/audit_docs.py` after documentation
  changes. It audits every present tracked or untracked Markdown and HTML file
  for mechanical integrity, including local Markdown links and HTML resources,
  without rewriting historical prose.
- Fix line-citation drift in two passes: run `python3 tools/audit_citation_drift.py`,
  then `python3 tools/memory_bank/fix_citation_drift.py --apply`, commit, and run
  the audit again. The fixer repoints moved citations and pins citations to
  deleted code as `<sha>:path:line`, a form the audit treats as historical; it
  prints every row a person must rewrite. Neither tool reads the papercut logs.
- Each `papercuts.md` entry is one line starting with `- `; the docs audit
  rejects any other form. Move closed entries with
  `python3 tools/memory_bank/move_papercuts.py move <plan.json>` rather than
  by hand, and prove any edit of the papercut logs with
  `python3 tools/memory_bank/move_papercuts.py check <base-revision>`: it
  fails on a lost line or on an entry that is both open and fixed.
  If `move` fails after it replaced the fixed log, `check` reports the moved
  entries as open and fixed; delete them from `papercuts.md` by hand, because
  re-running the plan would archive them twice.

## Asset provenance writes are serialized

Asset fetchers update the shared `assets_provenance.json` manifest by reading,
modifying, and replacing the whole document. Do not run two fetch commands
that target that manifest concurrently: both downloads can succeed while the
last writer silently drops the other provenance entry. Fetch shared-manifest
assets serially, or rerun the missing entry with `--force`, then assert every
expected file and provenance key in the asset test.

## Important Modules
- `__init__.py`: runtime orchestration, global player state, review hooks, answer handling, menu callbacks, save/HUD/UI bridge callbacks, and compatibility review-action wrappers.
- `runtime/runtime_actions.py`: Anki-free runtime review-action handlers and handler-keyed can-start checks for the complete skill surfaces, unified Combat, Quests, Utilities, and Activities. It mutates `player_data` through a callback/context contract supplied by `__init__.py`.
- `core/constants.py`: compatibility exports plus quest/diary assembly that remains in the facade because later projections depend on those names and their execution order; domain-grouped imports and activity, skill, asset, and quest-item projections live under `core/constants_parts/`.
  The facade pins its historical `__all__` order in `core/constants_parts/public_exports.py`; the module-surface digest sorts public names and therefore cannot detect this ordering contract.
- `logic_pure/logic_pure.py`: a re-export facade; the pure helpers live in the `logic_pure/logic_pure_*.py` domain modules (gathering, production, quest, claims, runecrafting, combat, and others).
- `logic/cadence_kernel.py`: pure foreground-action cadence contracts. It declares
  `R = 1000`, exact integer residual scheduling, four admission modes, overflow
  validation, and resource/actor lock shapes.
- `logic/cadence_live.py`: default-on runtime route declarations and exact admission.
  It maps source-compatible targets to rate-limited or embedded-probability
  behavior, Combat to six immediate ticks, and incompatible evidence to an
  explicit `source_blocked` declaration that preserves the handler action.
- `logic/cadence_coverage.py`: complete handler/target catalog and fail-closed
  validation for every selectable foreground route plus Quest, Utility,
  Farming, attached Summoning effects, and future skill attachments.
- `logic/cadence_shadow.py` resolves shadow evidence and supports reports.
  The default runtime does not advance observer state or use it to seed live cadence state.
- `tools/cadence_shadow_report.py` renders current, proposed, and pinned source XP/hour.
  It accepts the complete route catalog or accumulated shadow state from a player-data JSON export.
  Use the tool for the current route census.
- `core/logic.py`: Anki-aware level-up and achievement checks.
  Keep deferred-review scheduling in core/logic.py and the shared Level Up/Slayer completion renderer in ui/completion_dialogs.py.
- `core/storage.py`: Anki config persistence.
- `core/storage_pure.py`: default player shape and migrations.
- `core/skill_registry.py`: pure skill catalog for stable IDs, categories, save keys, review eligibility, and complete/partial/planned surface state.
- `core/action_registry.py`: pure review-action dispatch metadata. It resolves levelled skills and both no-XP surfaces to handler keys without adding fake registry skills.
- `core/target_metadata.py`: pure target-row metadata for the Skills hub. It builds labels, tooltips, icon paths, enabled/current state, groups, sort order, and lock reasons for registered skill targets, Combat, Utilities, and Activities without creating Qt widgets.
- `core/achievement_metadata.py`: pure achievement definitions, difficulty order, grouped row view models, and progress-count helpers while preserving the legacy completed-achievement name contract.
- `data/hunter_data.py`: source-backed Hunter target data. It uses 2011.rs guide rows for levels/XP/rewards, local 2011Scape cache item names/ids for storage keys, and local 2012scape/Darkan Hunter code only as mechanics/id parity because the local 2011Scape checkout has no Hunter mechanics plugin.
- `core/item_registry.py`: pure item manifest helpers for current economy items, including stable IDs, storage keys, categories, assets, and source/license notes.
- `data/prayer_data.py` / `data/prayer_passive_data.py`: source-backed Prayer training, Combat prayers/curses, composite altar selection, passive reward identities, and enemy mappings.
- `data/urn_data.py`: the authority for training-urn tiers, physical states,
  source IDs, charge eligibility, sanitation, and custom-layout state materialization.
  Read this file for the current catalog.
- `data/equipment_data.py`: generated worn-equipment contract for Smithing armour/weapons and Mining bonus gear, including slots, combat gates, two-handed flags, attack speed, and combat bonuses.
- `generated/quest_catalog_generated.py`: generated pre-EOC quest catalog. Do not edit manually; regenerate it with `tools/build_pre_eoc_quest_catalog.py`.
- `data/quest_data.py`: a re-export facade over the `data/quest/` package, which holds quest definitions (`definitions/`), hand-audited overrides (`catalog_overrides.py`, `stage_overrides/`), generated quest item rewards, XP lamp claim definitions, and completion-unlock rules for skill targets (`ledger.py`).
- `ui/ui.py`: Qt dialogs, HUD, menu, stats, bank, achievements, and settings.
- `core/hooks.py`: centralized hook registration and dry-run planning.
- `core/injectors.py`: floating widget and reviewer injection helpers; the retired Deck Browser content path has no separate module.

## Current Skill Flow
1. Anki shows a review card and the add-on marks review state.
2. The user shows the answer, then answers with an eligible ease.
3. `on_answer_card` calls `on_good_answer` if the current skill is active and XP has not already been awarded.
4. `__init__.py` resolves the handler key and calls `runtime/runtime_actions.py` through a `RuntimeActionContext`; runtime handlers call pure helpers, update `player_data`, check levels/achievements through callbacks, save, and refresh UI.

## Existing Skill Patterns
- Gathering skills use success probabilities and selected resource data.
- Processing skills consume inventory and produce output items.
- Skills get their XP curve from `exp_table_for_skill()`: Dungeoneering uses `DUNGEONEERING_EXP_TABLE`, every other skill `EXP_TABLE`. Each skill keeps per-skill `*_level` / `*_exp` fields.
- Inventory is a single dictionary shared across ores, logs, gems, bars, and crafted items.
- The backend registry preserves current flat save keys while centralizing skill identity. This is deliberate: Anki config is the stable boundary, so registry-driven defaults are safer than a nested save migration.
- The item registry uses existing inventory storage names as `storage_key` values. Stable item IDs can support future UI/action metadata without breaking current saves.
- Review dispatch resolves an `action_registry.review_action_handler_key` before calling the matching `runtime/runtime_actions.py` handler. Thin public `on_<skill>_answer` wrappers remain for compatibility and direct tests. This keeps display names, save keys, Utility aliases, handler identity, and runtime mutation logic connected without requiring a large action-engine rewrite.
- Cadence state uses the route-keyed `player_data["cadence_profiles"]` mapping.
  Each route contains `credit`, `opening_ready`, `assigned_reviews`,
  `opportunities_emitted`, and `cadence_version`. Sanitation validates these fields.
  Review undo covers the complete `player_data`, so cadence residuals need no separate undo stack.
- `player_data["cadence_shadow"]` is a separate namespace for saved shadow evidence and reports.
  Live dispatch does not advance this state or promote it to live cadence state.
- Live ranged XP/hour evidence uses the exact lower endpoint as a labeled
  conservative abstraction, never a midpoint. Processing routes whose
  authentic probability already embeds cadence reuse one source roll and do not
  enter the residual scheduler or draw a second random number.
- Runtime-to-source mappings must be semantically exact. Missing or incompatible
  rows are reportable `source_blocked` observations, not opportunities to infer a
  replacement rate. This includes ordinary versus concentrated gold, mixed
  leaping fish versus sturgeon-only evidence, runite coins/hour versus XP/hour,
  and urn-inclusive rocktail XP that cannot be decomposed.
- Skill identity has separate implementation and surface-state axes. `surface_state` is `complete`, `partial`, or `planned`; `trainable` covers complete and partial skills. Use `training_source` for partial cross-surface stats and `visible_in_skill_hub` to hide Attack, Constitution, Defence, Ranged, and Strength because they train only through Combat. Prayer, Magic, and Summoning are complete surfaces. Dungeoneering is implemented, trainable, and partial.
- Composite target choices must be committed atomically. Prayer stores stable material and UI-method identities, resolves them to the runtime target/mode pair in pure logic, validates the pair once, and clears hosted-search/owned-stint state only when that composite selection changes.
- Target-carried passives are physical pack semantics, not global ownership flags. Bonecrusher, Ectoplasmator, and training urns activate only when the selected target's clamped carried view contains the relevant item; bank-only or other-target copies remain inert.
- Saved Advanced layouts describe logical urn slots. `materialize_urn_layout_pure()` follows each slot through runed, active, and full physical names before either skilling or Combat repacks it, prioritizing the active charge-bearing object and then teleportable full urns.
- Direct inventory actions that award XP but do not answer a card use a bounded custom Anki undo stack. Full-urn teleport persists immediately and never consumes or creates the single review-action snapshot; multiple direct teleports undo in LIFO order independently of review undo.
- Owned gilded-altar state is stint-scoped. Starting a new stint consumes one clean marrentill per installed burner, freezes the 250/300/350% multiplier, and does not re-charge herbs until target/mode selection ends that stint.
- Skills-hub target lists consume `target_metadata.TargetRowMetadata` rows. `_build_target_selector()` picks the shared flat `QListWidget` renderer when a skill has fewer than 25 rows or no row has a group, and the shared grouped `QTreeWidget` renderer otherwise. The pure row metadata owns labels, tooltips, icon paths, group ids, sort keys, current state, enabled state, and lock reasons; Qt only renders rows, persists group expansion where applicable, and guards disabled-row clicks.
- Achievement definitions live behind `core/achievement_metadata.py`. `constants.ACHIEVEMENTS` stays as a legacy export for `core/logic.py`, old tests, and any add-on code that reads the dict shape, while UI code consumes row/progress helpers instead of reconstructing grouped achievement state.
- Generated Achievement Diary curation preserves source identity rather than
  rewriting it. A task moved within its family keeps its original-tier durable
  ID and records both original and curated tiers in provenance; explicit
  progression anchors are separately flagged and must reuse a skill-level pair
  found in that family's period requirements. Generator validation owns the
  exact 12-row tier invariant and the maximum of three anchors per tier.
- Fletching uses stable recipe IDs for saved selections and UI choices.
  Different recipes can produce the same inventory item, such as arrow shafts.
- Fletching material-only inputs such as feathers and arrowtips are registered as item-manifest `material` entries. Arrowtips are sourced through Smithing; feathers come from live NPC shop stock and Combat drops. The retired `scavenge_chicken_feathers` bridge must not return.
- The project-wide parity evidence contract lives in `memory-bank/pre-eoc-source-verification-standard.md` and applies to every skill, quest, activity, item chain, unlock, interface, rate, and future gap-fill—not only owner grills. Source scope is RuneScape content available strictly before the `2012-11-20` EOC cutoff. Ignore OSRS-specific mechanics, items, quests, interfaces, and rates unless an independent pinned pre-cutoff RuneScape source proves the same mechanic existed. OSRS may provide a research lead but is never parity evidence by itself; `fletch-javelin-construction` is the canonical rejected false positive because its shaft/head construction chain belongs to OSRS's 2016 Monkey Madness II family while period RuneScape javelins were shop/drop ammunition. For RuneScape Wiki evidence, prefer the nearest useful pre-cutoff `oldid`, verify its revision timestamp through `api.php?action=query&revids=...&prop=revisions`, and read the archived literal wikitext through `api.php?action=parse&oldid=...&prop=wikitext`. Do not trust a historical page's rendered calculators, exchange values, inline tables, templates, or Lua modules merely because the article oldid is old: recover the dependency's own historical revision, find literal values in the article wikitext, or corroborate with a dated Wayback capture or period cache/script. Likewise, a modern commit in a 2012-emulation repository is reconstruction evidence, not automatically a period source. If wiki/cache evidence and high-fidelity Darkan cannot establish a mechanic, mark it source-blocked and wait; never fill the gap from modern RS3/OSRS or inference.
- OpenRS2 enum/struct/param harvests go through
  `tools/query_openrs2_cache_configs.sh`. The wrapper accepts immutable disk
  zips or extracted caches, emits deterministic key-sorted definitions, and
  rejects unknown param opcodes. Its output proves client configuration only;
  it never promotes a value into server-side mechanics without the ordinary
  source-verification gate.
- OpenRS2 interface harvests go through `tools/query_openrs2_interfaces.sh`.
  Index 3 stores one archive per interface and one file per component; stable
  identities are `interface:component`. Search only covers client-authored
  labels, while dumps expose layout, visibility, assets, actions, and principal
  script hooks. None of those fields proves the server accepted an action or
  awarded its result.
- OpenRS2 item, NPC/object, and interface searches derive their scan range from each cache index.
  Known unreadable conditions preserve partial hits, then exit 3 with
  `PARTIAL_SEARCH skipped_count=<count> skipped_ids=[...]`.
  Item searches count explicit `MISSING OPCODE` failures.
  NPC/object searches count `BufferUnderflowException`; unrelated runtime failures propagate.
  A claim that a value is absent requires a complete search.
  Reader limitations and untested caches must remain explicit in the evidence.
- Owner grills are for unresolved product tradeoffs, not source transcription.
  If pinned period evidence plus settled AnkiScape architecture determines the
  behavior, decide and document it autonomously and batch routine conclusions.
  Ask only when multiple reasonable implementations would materially change the
  player experience and no existing contract chooses between them.
- **Never use the computer wall clock for gameplay.** Elapsed seconds, dates,
  application uptime, sleep, and time spent answering or pausing must never
  advance, expire, regenerate, reset, or otherwise mutate AnkiScape state.
  Gameplay time advances only through answered reviews/actions or an explicit
  player command, and must participate in the normal snapshot/undo contract.
- Historical timers use the shared answered-card AnkiScape clock, never the computer wall clock.
  All answered cards advance this clock, regardless of skill or reward success; undo restores it.
  `memory-bank/simulation-time-boundary-2026-07-16.md` defines the calendar scale.
  Its recurring-activity decision defines bounded entry reserves, not automatic rewards.
  Each consumer requires an explicit implementation check before a carryover claim.
- Answer-button semantics are explicit: every valid answer emits one
  idle/world tick, while only Hard, Good, and Easy (`ease > 1`) also emit a
  foreground action. Again therefore means the player idled for one simulation
  interval while the world continued. World and foreground mutation share the
  same review snapshot and undo. See
  `simulation-time-boundary-2026-07-16.md` for the consumer reconciliation and
  the distinction between calendar scale, short-duration scale, and action
  budgets.
- AFK is absence of user foreground input, not suspension of passive world
  benefits. A genuinely passive periodic effect may advance and resolve on an
  Again world tick; a foreground-, command-, or encounter-dependent effect still
  requires its own successful action. Producers must declare this classification
  explicitly rather than treating every positive result as foreground work.
- Urgent or expiring reviewer state uses the shared interactive alert-strip contract in
  `memory-bank/review-hud-world-alerts-contract-2026-07-16.md`.
  The strip is a sibling above the mouse-transparent XP HUD, not a control inside it.
  Do not create a standalone widget for each feature.
  Gravestone and expiring Familiar cargo use distinct source art, labels, countdown rules, and detail actions.
  This bullet is contract text: the contract records its implementation as deferred, and no runtime alert strip exists.
- Rare gameplay-created decisions use the sibling contextual-action contract in
  `review-hud-context-actions-contract-2026-07-18.md`: one labeled row, at most
  three direct actions, no duplicate toast, no automatic Casual/Advanced split,
  and no permanent setting by default. Ignoring a safely defaultable row means
  answering the next card; that review atomically applies the last explicitly
  clicked still-valid family choice or the authored conservative default.
- Global gameplay entities may have synchronized contextual projections but only
  one canonical writer. Summoning's familiar is owned by the Equipment surface;
  Bank, reviewer, and per-target controls project that same state. Per-target
  familiar policy may fill an empty slot but must not silently replace the live
  entity during navigation. BoB packing shares the target's existing
  Casual/Advanced inventory mode rather than adding an independent mode switch.
- Compatible restore trips coalesce rather than charging duplicate reviews. The Summoning
  contract specifies a `Visiting altar+obelisk` foreground detour that consumes the
  next successful answer, replaces the selected target action, and restores ordinary
  Prayer and Summoning points together, and an existing combat Bank-run altar stop
  that adds the obelisk restore at no further review cost. The runtime implements only
  the `Visit obelisk` direct command, which restores Summoning points alone. It cannot fire on Again, run on wall-clock time, restore
  special-move points without source support, or grant the target's ordinary output.
- Enabled automation may also insert an owned-resource Bank detour. Summoning pouch
  depletion converts the next successful answer into a refill/resummon transaction
  when compatible Bank stock exists; it does not also perform the target action and
  never fires on Again. Advanced carried slots reduce detour frequency rather than
  bypassing the same resource rules.
- The next four bullets are Summoning contract text. The runtime implements no
  familiar renewal, replacement, or `Best available` policy.
- Consumable automation uses the target-carried inventory as its explicit budget.
  An enabled Summoning familiar policy may atomically renew or replace from matching
  carried pouches, and auto-special may consume a deliberately packed scroll, but
  neither pulls directly from Bank stock. Missing preconditions never partially
  consume resources: the policy stays enabled in a visible lapsed state and re-arms
  when resources return. Catalog metadata, not display names, determines compatible
  roles and trigger conditions.
- Deferred policy replacement may use a safe resource boundary. A mismatched live
  familiar survives target navigation, but the next Bank boundary may first deposit
  BoB cargo and then atomically dismiss and replace it when the new summon is guaranteed.
  Failed preconditions preserve the old familiar rather than trading it for a lapse.
- Mode semantics govern substitution. Casual `Best available` re-resolves the strongest
  owned, level-valid, in-stock familiar inside the configured source role whenever a
  replacement is needed; Advanced exact selection never substitutes. Exhausting one
  pouch type therefore downgrades Casual within-role but visibly lapses Advanced.
- Stock changes do not pre-empt paid duration. A newly restocked stronger pouch never
  replaces a live same-role Casual fallback; resolution waits for renewal, expiry,
  death, or an explicit manual switch.
- Persistent encounters distinguish card boundaries from safe inventory boundaries.
  A BoB cannot transfer during consecutive successful combat bursts against one live
  enemy. Again performs no transfer but disengages; the next successful answer may
  preset-top-up before re-engagement, as may pre-combat, post-kill, and post-retreat.
- Target automation `Off` is not a global dismissal command. It spends no further
  familiar resources for that target but preserves an already-live global familiar;
  manual Dismiss remains the explicit way to discard paid remaining duration.
- Familiarisation uses four successful-answer segments under the2026-10-14 owner rule.
  Each success gains15 shards; Again pauses without progress or cost. Four successes
  finish with60 shards. Focus is absent from the model and sanitized saves.
  Its rolling weekly cooldown uses world ticks and never the wall clock.
- Optional combat exposure is fail-closed to source evidence. An attacking
  Summoning familiar is not a generic second damage target; only a pinned
  retaliation, area, enemy, or explicit aggro/tanking mechanic may reach its LP.
  Missing evidence means zero familiar damage, not an invented targeting roll.
- Player help has one canonical offline content corpus. The full searchable Help
  Center and each page's contextual `?` entry render the same stable topic IDs;
  optional external publication is generated, never separately authored. Complex
  pages share one Qt search-field/controller contract while retaining page-specific
  result adapters.
- The answered-card clock is not a universal action-duration converter. It runs
  background/world/economy timers; ordinary skilling still performs one sourced
  action tick per successful review unless an activity explicitly defines a
  different action grouping.
- AnkiScape has no standalone transportation layer or persistent player
  location. Canoes, hot-air balloons, lodestones, and comparable transport-only
  systems are deliberately excluded, including incidental XP actions whose
  fundamental purpose is travel. When a target or activity needs travel
  friction, model it internally as an abstract route/action phase without a map
  or player-facing transport network.
- Mechanically meaningful locations may still be target-local variants. A
  saved `Train in Wilderness` checkbox abstracts Wilderness presence for the
  selected target's sourced danger, reward multiplier, equipment charges, and
  death/undo behavior; it does not move the player or establish global location
  state.
- Source-equivalent alternate tools do not create duplicate training rows. One
  target owns a saved tool option when the alternate has a meaningful unlock or
  requirement; Casual uses the ordinary tool when the alternate provides no
  benefit. Target-specific skilling equipment likewise modifies the existing
  target: Casual may auto-equip owned beneficial gear, while Advanced obeys the
  target's saved equipment choice.
- Manual NPC/item transformations that award no skill XP and consume no game
  action do not spend a review. They use an inventory/equipment context action,
  enforce their quest/item/coin requirements, persist the transformation, and
  enter the same undo-safe save contract as other non-review inventory changes.
- Utilities and Activities are separate Skills-hub navigation surfaces but share
  one no-XP backend action family. Stable target IDs remain in
  `UTILITY_ACTIVITY_DATA`/`current_utility`; every row carries an exhaustive
  `surface = utilities|activities` classification. Utilities contain gathering,
  preparation, processing, opening, and Bankstanding rows. Activities contain
  minigames and Warriors' Guild rows, plus the injected world-event and landmark
  panels.
- Both no-XP surfaces stay outside `core/skill_registry.py` unless they gain real
  level/XP semantics. `core/action_registry.py` maps `Utilities`, `Activities`, and
  the legacy `Utility / Activities` name to the same `utility` review handler.
  Legacy active-skill saves normalize to the surface that owns
  `current_utility`.
- The Skills hub presents those surfaces as distinct categories with separate
  toolkit and period Activity-compass sprites. Activities gives its primary target
  picker guaranteed height beneath a bounded, separately labeled event-status
  region; Utilities never renders those event cards.
- The Activities middle column has separate routes for the master tree,
  Minigames, and D&D (`_ACTIVITY_SELECTION_GROUPS`). Master-tree groups are tree
  parents; Minigames and D&D render flat lists.
- Activity group icons are semantic, not decorative fallbacks:
  `distractions_and_diversions` uses the yellow compass and `minigames` uses
  the red compass. The green compass is reserved for Achievement Diaries.
  Familiarisation is an Activities > D&D session, not follower equipment.
- Global tabs must use unique semantic icons. Stats owns the bar graph; Skills
  uses the all-skills Max cape; Shop uses period coin art; Equipment uses worn
  equipment. Transparent source art renders directly; do not synthesize
  backing circles merely to increase contrast. Stats uses the period
  three-column grid rather than a horizontal strip, shows `current / base`,
  and projects temporary levels through the same current-level helper used by
  its selected detail pane.
- Magic target rows use `MAGIC_SPELL_IMAGES`, not their output-item art. A
  family action may intentionally share one authentic spell glyph across
  multiple item variants. Cutoff-pinned files remain the default; any exact
  classic sprite without surviving cutoff file evidence must be labeled
  `visual-fallback` in provenance rather than presented as period proof.
- Fixed-size target rows call `_pixel_path_icon(path, size)`, which performs
  cached, DPR-aware, aspect-preserving nearest-neighbor scaling while retaining
  alpha. Do not reintroduce raw target-tree `QIcon(path)` calls or synthesized
  contrast backings.
- No-XP rows can batch up to an inventory-sized cap when they represent fast
  material preparation. One-shot acquisition bridges may declare an `outputs`
  mapping and `deactivate_after_run = True`, so the action multiplier cannot
  repeat them inside one card.
- No-XP rows have a first-class icon contract: each
  `UTILITY_ACTIVITY_DATA` entry can expose an `icon_path` pointing at a
  dedicated `activityicons/<activity>.png` asset. The Qt target list prefers
  that icon and falls back to output-item art without changing reward logic.
- Crafting recipe data stores source XP only. Runtime reward handling awards base XP per action tick; review pacing is controlled by the actions-per-review multiplier rather than by inflating a single action's XP.
- Crafting follows the source-data-module pattern at the backend layer (`data/crafting_data.py`). `current_craft` stores stable recipe IDs, inventory stores real item names, and the data intentionally includes live input-starved recipes so missing acquisition loops light up later without reshaping the recipe. XP-bearing Crafting ignores recipe `batch_size`; only no-XP Utility/Activities batch material prep.
- Woodcutting has a focused source-data module (`data/woodcutting_data.py`) rather than only ad hoc `core/constants.py` rows. Its stable target IDs are persisted in `current_tree`, while inventory uses real item output names such as `Logs` and `Oak logs`.
- Fishing follows the source-data-module pattern (`data/fishing_data.py`) as a Gathering skill. Its stable method IDs are persisted in `current_fishing`, while inventory uses real output item names such as `Raw crayfish`, `Raw salmon`, and `Raw shark`. Mixed-output rows preserve source order during rolls, consumable material is removed only after a successful catch, and Barbarian fish side XP updates hidden Strength and the live Agility state without exposing Strength as an independent skill surface.
- Fletching follows the source-data-module pattern (`data/fletching_data.py`) as
  an Artisan processing skill. Stable target IDs are persisted in
  `current_fletch`, while inventory uses real output and material item names.
  `constants.FLETCHING_DATA` is only a compatibility export. Fletching target
  metadata carries group/sort data for the shared grouped `QTreeWidget`
  renderer. Common reusable tools remain ambient; only level, materials, and
  generic target unlocks gate rows.
- Cooking follows the source-data-module pattern (`data/cooking_data.py`) as an Artisan skill. Its stable target IDs are persisted in `current_cooking`, while inventory uses real raw/cooked/burnt item names. Cooking failures are productive inventory mutations: the raw input is consumed, the source burnt item is added, and no XP is awarded. Source low/high chances stay in data and are adapted to review-scale probabilities in pure logic.
- Runecrafting follows the source-data-module pattern (`data/runecrafting_data.py`) as an Artisan skill. Its stable target IDs are persisted in `current_runecrafting`, while inventory uses real rune/access item names. Rune Mysteries quest state, Bank Claims, Wicked hood fed-altars, pouch degradation, and Binding necklace charges are explicit flat side-state keys in `player_data`. Quests are review actions through `core/action_registry.py`, not fake skills in `core/skill_registry.py`.
- Hunter follows the source-data-module pattern (`data/hunter_data.py`) as a Gathering skill. Its stable target IDs are persisted in `current_hunter`, while inventory uses canonical cache item names such as `Red feather`, `Kebbit claws`, `Imp-in-a-box (2)`, `Gourm' impling jar`, and `Ess' impling jar`. The local 2011Scape cache/snapshot is treated as identity evidence, not a mechanics implementation; 2011.rs guide rows supply levels/XP/rewards, and local 2012scape/Darkan Hunter code supplies mechanics/id parity. Hunter outputs are first-class `hunter` bank items, while jars/traps such as `Butterfly jar`, `Impling jar`, and `Magic box` remain material items. Quest locks cover completion gates and narrow route precedents only; partial-route access such as Regicide-start content stays in notes until a route model exists.
- Hunter separates reusable gear from consumables. `requirements` are deleted only on successful catches; `tools` are bank/inventory gates that remain after a catch. Current reusable gates cover bird snares, box traps, butterfly nets for butterfly/Puro-Puro rows, and small fishing net plus rope for tree-net rows. Hunter supplies come from live NPC shops; the retired `Buy Hunter supplies` Utility bridge must not return.
- `tools/build_pre_eoc_quest_catalog.py` generates the pre-EOC quest catalog in release order.
  Recipe for Disaster subquests have separate rows. Use the generator for the current catalog size.
  Catalog and stage rows provide coverage structure, not proof of full quest parity.
  Verify stages, routes, branches, item transformations, combat, rewards, and unlocks under
  `memory-bank/pre-eoc-source-verification-standard.md`. Wait for high-fidelity Darkan evidence where necessary.
  Rows carry source oldids, strict prerequisites, rewards, lamp definitions, and source-backed journal stages.
  Put hand-audited overrides in `data/quest/catalog_overrides.py` or `data/quest/stage_overrides/` when pinned pre-EOC evidence is stricter than generated or emulator data.
- Generated quest reward prose can misclassify an unlock or post-quest XP as an immediate item or XP reward. Correct runtime rewards through `QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID` and `QUEST_XP_REWARD_REPLACEMENTS_BY_ID`, then also correct `quest_reward_items_as_dict()`: it reads generated catalog rows independently, so an obsolete generated item otherwise remains a fake Bank definition and changes the reachability seed set even when runtime no longer grants it. Reward regressions must complete every `QUEST_DATA` entry through `apply_quest_progress_pure()`, because reachable-only sets leave latent catalog rewards untested. Whole-tuple guards pin exact flat grants for every item replacement, exact lamp definitions for every lamp replacement, and exact unlocks only for quests with unlock replacements; they must not claim union coverage.
  Because quest reward definitions feed the canonical item registry, removing a fake reward identity can also retire a generated Grand Exchange alias; regenerate `generated/grand_exchange_period_generated.py` so its keys remain a subset of the live market catalog.
- Quest starts are strict. A quest with incomplete prerequisite quests or unimplemented required skills must be impossible to start. Completion XP for implemented skills is granted immediately; XP for unimplemented skills is stored in `pending_skill_exp_rewards` and applied by migration when the skill becomes implemented.
- Quest-list availability should flow through `quest_availability_state_pure()`, not ad hoc UI checks. Its states are `can_start`, `in_progress`, `blocked_at_stage`, `completed`, and `locked`. `locked` means the quest cannot start; `blocked_at_stage` means a started quest is waiting on current-stage inventory, tools, actions, routes, or combat. Keep that separation: stage requirements are not start locks.
- Product implementation readiness and player progression eligibility are separate gates. Exhaustive source/completeness ledgers may contain unfinished content, but live UI, search, rolls, rewards, and action registries must not expose implementation gaps as disabled, locked, placeholder, inert, or `coming later` rows. Derive readiness from stable dependency identities so content materializes automatically when its complete runtime graph exists, without a migration, cleanup pass, release allowlist, or duplicated registry. Replace hidden player-facing debt with a developer audit that assigns every catalog row a machine-checkable readiness result and rejects unknown or stale blockers. Only after a row is runtime-ready should authentic player quest/level/item/unlock eligibility run; a finished surface may show those real progression locks where its owner-approved design calls for them.
- `QuestDefinition.stage_requirements` defines current-stage quest requirements.
  `quests_as_dict()` serializes them; pure helpers in `logic_pure/logic_pure_quest.py` enforce them.
  Use `quest_current_stage_blockers_pure()` and `quest_current_stage_blocker_reasons_pure()` for display.
  Use `can_progress_quest_pure()` for review readiness and `apply_quest_progress_pure()` for advancement and local item changes.
  Quest-used items do not block a start unless source evidence defines them as start requirements.
- `QuestStageRequirement.variant` defines mutually exclusive routes at a stage.
  Rows without a variant are mandatory. Only matching variant rows can block, consume, produce, or resolve combat.
  Structured `QuestDefinition.choices` defines branch and co-op decisions, not fake inventory requirements.
  `quest_current_stage_choices_pure()` reports unresolved choices.
  `apply_quest_route_choice_pure()` saves the route in `quest_route_states`.
  A started quest has a `quest_choice` blocker until its required choice is complete.
  Co-op contacts and route-specific rewards must match the selected branch.
- Generated combat source matching uses full tokens, explicit aliases, and token-safe singular forms.
  It must not use raw substring matching or infer missing stats from a similar name.
  `tools/build_pre_eoc_quest_catalog.py` owns this parser.
- The catalog generator extracts quest-wide blockers from pre-EOC `Quest details` item and combat fields.
  Rows can carry `required_inventory`, `required_inventory_options`, `consumed_inventory`,
  `consumed_inventory_options`, `produced_inventory`, `required_tools`, and `combat_encounters`.
  Option groups preserve alternatives. The outer tuple requires every group; each inner tuple requires any member.
  `((A, B),)` means A or B; `((A,), (B,))` means A and B.
  `quests_as_dict()` emits each inner group as a tuple of item-count mappings.
  Audit parsers merge those mappings within the group and also accept the native dataclass tuple-pair shape.
  Do not pass an entire option group to the flat item-count parser.
- Remove a false item gate when the schema cannot express its source predicate.
  Report the missing predicate instead of excluding valid source paths.
  This applies to mixed family quantities, compound bundles, excluded members, equipment, followers, performed state, and equivalent-item capabilities.
- `data/quest/catalog.py` deserializes generated rows into `QuestStageRequirement`.
  It combines generated rows, hand-authored rows, focused replacements, and focused additions.
  Replacements correct conflicts with stronger source evidence. Additions express sourced actions that the generator cannot infer.
  Do not edit `generated/quest_catalog_generated.py` directly.
  Consumed option groups block at the current stage; advancement consumes the first satisfied option group.
  Produced inventory does not block progress by itself. It records items from a successful stage transition.
- Earlier quest stages must produce quest-only items before later stages require or consume them.
  `start_inventory` can supply quest items at entry. Partner actions can supply items without implying prior player ownership.
  Model items obtained during a quest as stage actions rather than quest-wide inventory gates.
  Use `auto_actions` for deterministic steps that do not block review progress.
  Use `required_actions` for true player or manual gates. Worn equipment can satisfy quest-required tools through `logic_pure._has_quest_tool()`.
- `tools/audit_quest_local_item_gates.py` rejects quest-wide requirements for items that the same quest produces or supplies through `start_inventory`.
  Keep route, location, skill, spell, and checklist prose out of inventory and tool fields.
  Use source-backed action, route, or combat gates instead. Mid-quest item production is not an unconditional completion reward.
  Source dialogue or rituals must not become invented combat encounters.
- `python3 tools/audit_quest_stage_gate_coverage.py` produces the current census of quests, stage rows, and blocker families.
  Machine-readable stage coverage does not prove detailed historical simulation.
  The dated evidence index and rollout record are in
  `memory-bank/source-audits/quest-stage-gates-catalog-wide-2026-06-22.md`.
  Check the relevant source audits before a quest-stage completion claim.
- Generated combat quantity rows should preserve source quantities. Numeric
  prefixes, `xN` suffixes, "at least N", and written quantities through ten
  are parsed in `tools/build_pre_eoc_quest_catalog.py`; do not collapse rows
  such as "Two Lava monsters" or "Five Ice Trolls" to a single combat
  completion.
- Quest combat uses the persistent shared combat engine without an enable switch.
  `apply_quest_combat_encounter_pure()` uses the player's equipment, food, and prayers.
  Surviving enemy lifepoints persist in `player_data["quest_combat_active_encounters"]`.
  Player death uses the ordinary combat death path. The live cadence contract owns the review action budget.
  A combat-level gate applies only when the encounter supplies `minimum_player_combat`.
- Combat quantities track progress per enemy, not completion of the whole group.
  Progress lives in `player_data["quest_combat_encounter_counts"][quest_id][encounter_id]`.
  The sourced `QuestCombatEncounter.quantity` determines completion.
  Completed IDs live in `player_data["quest_combat_encounters"]`; existing completed IDs still satisfy the blocker.
  Encounters without required stats stay blocked as `combat_missing_stats`.
- Focused stage additions in `data/quest/stage_additions.py` can carry local 2011Scape NPC stats with a recorded source path.
  Generated enrichment prefers 2011Scape NPC definitions, then Darkan/2012scape combat definitions with an exact NPC name and combat level.
  Duplicate Darkan sources are acceptable only when all captured battle stats and configurations agree.
  Conflicting duplicates require focused source resolution; otherwise they remain without stats.
  Focused replacements can split ambiguous fights into sourced encounters and preserve unrelated stage requirements.
- Resolver readiness depends on attack style.
  Magic requires hitpoints, defence, and magic. Ranged requires hitpoints, defence, and ranged.
  Melee or unknown styles require hitpoints, attack, strength, and defence.
  A complete melee fallback handles inconsistent style metadata. Hitpoints alone do not establish readiness.
- Darkan `developer-information/beasts.txt` can fill missing or zero attack, defence, magic, and ranged values.
  The combat definition needs an exact ID match or an unambiguous name and level.
  The merged payload must satisfy the same attack-style contract. Do not infer melee Strength from beast metadata.
  `npc_stats_source` names `beasts.txt` only when a beast value contributes to the payload.
  Definitions without `combatLevels` require hitpoints, configurations, and an exact name/level signature that satisfy the resolver contract.
  Merge multi-ID definitions per matched name and level. Do not transfer stats between unrelated levels.
- Replace false generated combat rows when stronger local quest evidence defines a different stage chain.
  Route access and ritual actions must not become invented battles.
  Preserve source quantities and route-specific encounters in focused replacements.
  `tools/audit_quest_combat_stat_gaps.py` classifies unresolved combat rows and supplies the current census.
- `tools/audit_quest_historical_wiki_combat_stats.py` audits historical Wiki monster pages as a separate source tier.
  Lifepoints, maximum hit, and attack-style prose are metadata, not resolver-ready hidden combat stats.
- Completed quest reviews intentionally turn Quest training off and show a modal `Quest complete` stop-point dialog through the same centralized warning-dialog helper used by material depletion. Keep that paired with the existing floating completion gain so the player sees both immediate feedback and a clear action stop.
- XP lamps from quest rewards are flattened into Bank Claims. Preserve the source amount, quantity, skill option set, and minimum level, but use one consistent `Choose skill` claim flow instead of copying every historical quest-specific lamp/chatbox interface.
- Bank Claims are a compact action inbox above the Bank inventory, not an item category. The frontend should render eligible rows only, summarize locked rewards, hide claimed rewards behind the all-caught-up state, and cap the rows to keep the inventory list as the main scroll surface.
- The Wicked hood claim is intentionally gated by Rune Mysteries only in AnkiScape. Do not re-add a Runecrafting level 5 claim gate; historical 2012 evidence shows that level prompt was not a reliable hard claim requirement, and the hood's actual altar use still remains constrained by Runecrafting target gates.
- Generic target unlock locks are exported as `QUEST_UNLOCK_RULES` for
  compatibility, but the rule shape supports both `quest_completed` and
  `ability_unlocked` requirements. This registry feeds Mining, Fishing,
  Cooking, Firemaking, Runecrafting, Fletching, and Utility/Activities lock
  reasons. Route/location gates normally stay out of global locks, but can be
  flattened to logical quest precedents when the current generic row effectively
  represents that locked route: Shilo Village gates `gem_rocks`, Priest in Peril
  gates Morytania-flavored slimy eel/snail rows plus Hunter `catch_swamp_lizard`,
  The Fremennik Isles gates Neitiznot/yak/arctic pine rows, As a First Resort
  gates Hunter `catch_wimpy_bird`, Eagles' Peak gates Hunter `catch_ferret`, and
  Rocking Out gates Hunter pirate implings. Ability gates are flat
  `player_data["unlocked_abilities"]` ids such as
  `broad_fletching` and `barbarian_fishing`.
- Utilities and Activities are grouped independently by `group` metadata in
  their own Qt trees. Group metadata also feeds the explicit surface
  classification; tests require every registered no-XP row to belong to exactly
  one side.
- Mining follows the same source-data-module pattern (`data/mining_data.py`). Its stable target IDs are persisted in `current_ore`, while inventory continues to use real item output names such as `Iron ore`, `Pure essence`, `Sandstone (10kg)`, and `Uncut opal`.
- Smithing uses `data/smithing_data.py` for smelt and forge recipes in `SMITHING_DATA`.
  Stable `current_smith` IDs select recipes; `BAR_DATA` is a compatibility view for smelt-only consumers.
  Runtime uses the same pure processing helper for both stations. Hammer and tool requirements remain implicit.
  Level and inventory materials are the backend gates.
  Iron smelting consumes `Iron ore` after a valid start, then grants `Iron bar` and XP or records `smelt_fail` without output or XP.
  Other smelt and forge recipes are deterministic unless a source audit proves a post-start failure.
- Gathering tools remain ordinary Bank items until the player explicitly attaches them; buying or looting an upgrade never changes the active hatchet/pickaxe. The attach action moves one item into the toolbelt, whose best usable attached ID drives review logic; migrated saves retain attached Bronze defaults.
- The hybrid toolbelt pattern covers Mining too. Toolbelt remains tools-only (`bronze_hatchet`, `bronze_pickaxe`, etc.). Passive/equipable bonuses live outside toolbelt in `player_data["equipment"]`; Mining bonus logic reads the worn `neck`/`body` slots rather than passive ownership.
- The custom carried-pack editor has three distinct projections: desired 28-slot layout, clickable Bank inventory, and live current inventory (including loot pickups). Layout edits refresh only the plan; Bank/current grids refresh when their source inventory changes.
- Reusable tools are not automatically visible just because the source action has one. Fishing deliberately keeps rods, nets, cages, pots, vessels, and harpoons implicit in labels, tooltips, gating, and assets. Visible progression remains limited to Woodcutting hatchets and Mining pickaxes unless a future design explicitly promotes another tool family.
- Equipment has backend and Qt surfaces. `data/equipment_data.py` is generated from checked-in Smithing data plus local 2011Scape `items.yml`; storage keeps a flat `equipment` mapping (slot -> item name); pure helpers own gate/swap/stat-total rules; runtime callbacks feed a dedicated Equipment tab with right-click Equip/Unequip. Attack, Strength, Defence, Constitution, and Ranged are partial skills trained through unified Combat; Magic has its own complete review surface.
- `tools/audit_item_reachability.py` builds a deterministic route graph from registered seeds and transformations, including quest `start_inventory`, stage `produced_inventory`, and final rewards. Use `--rank-roots N` to prioritize source work by simulated transitive gain. The instrument measures declared routes and can credit inaccessible combat drops or shop stock; check runtime access gates before a claim of player acquisition. Never silence an orphan by inventing a recipe or free seed. Its report modes exit 0 whenever the report builds, because known orphans are a pinned baseline, not a failure; only `--check` fails, when the report differs from the pins in `tests/test_item_reachability_audit.py`.
- Combat death/reclaim state stays flat and review-transaction friendly. `combat_grave.items` is the active five-safe-review recovery list, while `death_office.items` holds gear collapsed out of the active grave path, such as a second Combat death before recovery. Death's Office reclaim consumes Coins and returns gear to inventory through a pure helper plus Bank-tab callback, so Anki undo can still roll the whole review transaction back by restoring `player_data`.
- Combat bank runs are target-scoped supply-recovery state. If `combat_bank_run.target_id` no longer matches the current Combat target, reset the run before deciding whether the new target needs its own two-review bank trip; never complete an old run against a different enemy. Bank-run supply decisions must use the same enemy table being simulated so quest/injected enemies with poison can load antipoison correctly.
- Quest combat reuses the ordinary burst engine but must not leak quest target ids into ordinary Combat progression. Keep ordinary `combat_kill_counts` scoped to selectable Combat targets; restore the pre-quest ordinary encounter after partial/kill quest bursts, but let quest-combat death clear ordinary encounter state because the shared death path has killed the player.
- Source game tick odds should not be copied directly into review odds. Probabilistic review skills preserve audited source chance data, then pass the source roll chance through the shared `normalize_review_success_probability_pure` adapter so one Anki review action remains the pacing unit. Firemaking can still apply its separate target-tier cap because source Firemaking odds mostly vary by player level rather than log tier.
- `ItemDefinition.tradeable` defines item tradability from source evidence.
  Grand Exchange eligibility must use item metadata, not category alone.
  Document source anomalies in the relevant item audit.
- `food` is a first-class item category for cooked/prepared/burnt Cooking items. Burnt Cooking items are intentionally registered as non-tradeable junk in this fork even though RuneScape player-to-player tradability is historically weird, because future AnkiScape GE/trading will not distinguish marketing from trading.
- Random no-XP Utility actions can use dedicated pure helpers.
  `Open bird nests` consumes a known nest subtype and rolls source contents.
  It does not use a fixed `requirements -> output_item` recipe.
- Review rewards are paired with Anki undo via `gui_hooks.state_did_undo`. When an eligible answer changes game state, the runtime records the original values for only the changed `player_data` keys; undo restores those values and saves config so Command-Z does not leave XP/items ahead of the card schedule.
- Review pacing is an integer **actions-per-review** multiplier, not an XP-only scalar. Runtime reads `ankiscape_review_action_multiplier` (falling back to the old `ankiscape_xp_multiplier` key), executes up to N normal action ticks inside one eligible review, aggregates floating feedback, and records one undo snapshot for the whole review. Gathering skills spend N independent probability rolls; processing and Utility/Activities stop cleanly when materials run out before an extra sub-action.
- Every started review action should record durable telemetry in `player_data["action_telemetry"]`. The stable row key is `skill_id:action_id`; rows track attempts, successes, failures, expected successes, dry streaks, output counts, and failure kinds. Blocked actions such as missing materials or insufficient level do not count as attempts, but dry RNG outcomes, Cooking burns, and iron smelt failures do save telemetry.

## Landmark activity pattern

Step-counter landmarks such as the Stronghold of Security and Knight Waves are
one-time activities, not repeatable material conversions. They stay outside
`UTILITY_ACTIVITY_DATA`; the source-backed Stronghold of Player Safety is the
exception, a `landmarks`-group entry in it. Step-counter landmarks use this contract:

- `logic_pure/logic_pure_landmarks.py` owns `default_*_state_pure`, `sanitize_*_state_pure`, and
  `apply_*_step_pure`. Sanitation clamps the step, implies completion at the
  maximum, and repairs garbage to 0. The step helper advances once and reports
  `advanced` and `just_completed`; `grant_*_reward_pure` guards on a claim field
  being `None`, so a second claim is inert. Names, step totals, and reward
  choices are module constants.
- `core/storage_pure.py` seeds the state in `default_player_data` and backfills it
  through `sanitize_*` in `migrate_loaded_data`.
- `runtime/runtime_actions.py` branches `handle_utility_answer` on the landmark activity
  key and calls a dedicated `_handle_*_answer(ctx)`. On `just_completed`, it
  deactivates the activity, toasts, and invokes a new optional
  `RuntimeActionContext` callback, `ctx.prompt_*_reward()`.
- `ui/ui.py` injects a synthetic tree group instead of reading the conversion
  table. Its click path starts the activity, claims the reward, or remains inert
  after a claim; the reward dialog returns the selected choice. Every non-group
  row needs an icon or `test_utility_rows_use_activity_icon_contract` fails.
- `__init__.py` persists through `_claim_*_reward` and defers
  `_prompt_*_reward` with `QTimer.singleShot(0, ...)`, so the modal cannot open
  during Anki answer-card processing. Wire both callbacks into the runtime
  context and the menu route.

Generate reward equipment through `tools/generate_equipment_data.py`; do not
hand-edit `data/equipment_data.py`. Stronghold's reward identities are Fancy boots
9005 and Fighting boots 9006. Step-counter landmarks are add-on-original content, not
parity-locked; Stronghold of Player Safety carries period source pins in
`data/stronghold_player_safety_data.py`.

## Architectural Pressure
Adding many skills by copying the current pattern would increase duplication in:
- skill selection UI
- stats rendering
- storage defaults and migrations
- answer dispatch
- icon/image registration
- tests

Backend modules own skill, item, review-action, runtime-handler, target-row,
grouped target-tree, and achievement metadata.
Keep these contracts separate from Anki and menu orchestration in `__init__.py` and `ui/ui.py`.
Stats rendering, icon registration, and tests are shared by many features.

## Skill Expansion Workflow
Use the project skill at `.codex/skills/ankiscape-skill-expansion/SKILL.md` before adding or expanding any skill, Utility/Activity, target chain, item economy slice, or achievement set. It encodes the repeatable workflow: source audit first, playable scope cut, registry/item data, asset scraping, pure mechanics, UI surfacing, achievement patterns, tests, manual Anki checks, and memory updates.

## Compatibility Pattern
Persisted Anki config is the stable boundary. Schema changes should go through `core/storage_pure.py` migrations and keep existing user data intact.

Source-complete data can be broader than a live catalog. Herblore keeps Daemonheim rows in explicit `DUNGEONEERING_*` tuples so item identities and historical transcription survive, while its ordinary exported targets filter them out. Supported dungeon Herblore chains run against the Dungeoneering session inventory instead. When a live target is removed this way, migrate the saved selection to the skill default but preserve inventory keys and quantities.

Anki's add-on directory is a runtime import boundary, not a harmless place for
parallel checkouts. Every enabled direct child of `addons21` with an
`__init__.py` is imported as a separate add-on package. Keep only the canonical
AnkiScape checkout there; linked worktrees belong in the sibling
`Anki2/ankiscape_worktrees/` root and should be created/audited through
`tools/worktree_guard.py`.

Production Anki hook wrappers expose their callbacks through `_hooks` but are
not themselves iterable. Idempotent registration must inspect
`getattr(hook, "_hooks", hook)` and still use the public `append`/`remove`
methods. Tests for hook replacement should use a non-iterable production-shaped
fake so a list-shaped test double cannot hide this API mismatch.

Review-answer side effects must follow Anki's undo semantics. If a future skill mutates new `player_data` keys during an answer, the generic snapshot diff should catch them; if a future system writes outside `player_data`, it needs its own undo-aware rollback path.

## Live cadence route pattern

`logic/cadence_live.py` is the only runtime admission resolver. A rate-limited route
owns one `cadence_profiles[profile_id]` residual; the active target alone
advances it, waits persist residuals and cadence-wait telemetry without an
attempt, and the outer review snapshot makes admission and reward undo-atomic.
Source rates above `R = 1000` must declare `CAP_ONE_ACTION`; never round a
rational rate or compensate by changing base XP. Embedded-probability routes
receive one authentic attempt with no second gate. Source-blocked routes retain
their existing handler unit until a compatible row is proven.

Combat consumes `6 × M` immediate ticks per successful card and persists the
unfinished encounter across cards. Ordinary Combat chains kills until the budget
is spent or a danger stop fires. Both kill branches reset the new enemy's LP,
regeneration, retaliation, attack delay, Magic effects and Curse ramp while
preserving the player's weapon cooldown. The engine reports the exact tick and
stop reason; the runtime passes the matching Slayer assignment's remaining count
so the chain cannot overshoot its last kill. Banking is checked after each kill;
the next card starts the trip. Step handlers compare shared danger projections
after each step. The world tick exposes a familiar's pre-drain lifetime through
transient dispatcher state, which caps the foreground budget with
`familiar_ended`; an earlier danger keeps its own reason. Again advances world
consumers only and marks an active encounter disengaged for safe automation
without granting either side a combat beat.
Quest combat takes the same `6 × M` slice and carries its own encounter,
attack clocks included, from card to card, so a boss fight spans reviews. Its
explicit first-kill boundary preserves the quest roster. The cadence rollback
retains the legacy 50-tick quest-combat burst and its existing kill boundaries.

Utility/Activity exemption is an owning contract, not a cadence bypass.
Activity routes must declare whether one review is a world-clock tick, live
Combat slice, one source action, finite grouped beat, direct command, or
source-blocked grouping. Every real activity Combat encounter uses the ordinary
`6 × M` tick reducer even when its map, crowd, or enemy roster is aggregated.
A finite grouped beat may preserve a bounded performance, room, route, or
production circuit, but must name its grouped operations and fixed reward,
stop at terminal boundaries, and never replay hidden subactions or add a second
skill cadence gate. The complete reconciliation table is
`memory-bank/source-audits/activity-cadence-reconciliation-2026-07-18.md`.

Persistent multi-enemy activities use one sealed session plus one visible
roster. A successful review applies the ordinary live six-tick Combat reducer
to exactly one engaged member, stops at a terminal boundary, then resolves one
bounded pressure pass from the remaining roster through the same player
Defence and protection-prayer state. Preserve the player's full data mapping
when sanitizing Combat state for pressure; replacing it with the sanitizer's
Combat-only projection silently discards skill levels and disables protection
prayers. Sealed instances pass `allow_bank_run=False`, use `safe_death=True`
where the source says the activity is safe, and own explicit leave/resume
rather than leaking ordinary Combat target or Bank-trip state. Fight Caves is
the reference implementation.

Closed-economy combat activities must also close the actor, not just the item
ledger. Build the temporary combat input from the minimum session-owned stats,
lifepoints, equipment, and encounter state; explicitly neutralize ordinary
inventory supplies, auto-flee, prayers, spell effects, and passive healing;
then merge back only the session consequences named by the activity contract.
A terminal flee, death, or failed burst must clear or reschedule the encounter
so one bad combat result cannot wedge the session. Stealing Creation is the
reference implementation.

Persistent XP multipliers belong on the shared XP-award seam, but that seam is
a hot path. Guard it with a cheap pure applicability predicate before copying
player state, and require the selected review-action family to match the tool
form before charging it. This prevents lamps, quests, and activity side rewards
from draining a skill tool while keeping the actual XP award and tool charge in
one review-undo delta.

In a shared canonical checkout, a whole-suite result is valid only for the
source/test snapshot imported when discovery began. Before recording or
committing a long verification run, compare source and test modification times
against the run start and rerun if another thread wrote during discovery.

A stun ends the card and owes its ticks to the card's running budget
(`stun_card` in `runtime/runtime_actions_context.py`, owner decision 5 and
ruling F4). The stunning step is charged first; the card's unspent ticks then
pay the stun, and only the rest carries in the saved `card_tick_debt`, which
the next card pays before any step starts. A step may start with fewer than six
ticks left, and its overrun carries too, so no tick is forfeited. A Thieving
failure costs the target's `stun_ticks`, and a Wild jade vine bind costs 6.
Handlers return `False` only for a review they reject; a failure that really
happened is a completed step and stops the card through the budget. Skills
whose failures use shared combat LP must be excluded from post-review safe
combat recovery, or the integration layer will silently heal away the failure
stake.

## Public derivative release pattern

GitHub fork metadata is not package-level attribution. Any public AnkiScape
release must carry its own original-creator credit, explicit compatible license,
source links, derivative-maintainer identity, and distinct AnkiWeb listing. Do
not reuse Wilson's item `1808450369`, and do not leave the in-product review
link pointing at his listing. Public source must match the exact release
candidate rather than a stale fork snapshot.

Code lineage and asset redistribution are separate gates. A public release
requires an explicit repository license, Wilson's acknowledgement, and the
provenance of RuneScape-derived assets; the AGPL-3.0 basis from AnkiWeb covers
none of these.
Follow
`memory-bank/public-release-lineage-and-license-2026-07-17.md` in order and
upload only after every rights, attribution, asset, packaging, and real-profile
verification gate is closed.

## UI Gotcha: nested-closure name collisions in `show_main_menu`
`show_main_menu` defines nested helpers in a shared local scope.
A later definition with the same name replaces the earlier binding without an error.
Prefix section-scoped helpers with the section name, such as `_select_hub_skill`.
Use offscreen Qt behavior checks to detect callbacks that reach the wrong section.
Separate builder functions or classes remove this shared-scope hazard.

## Main-menu deferred tabs (`ui/ui_menu_ctx.py`, `ui_tab_*.py`)

Shop, Quests, Challenges, Achievements, and Collections build their tabs on first show.
Each exports `build_<name>_tab(ctx) -> QWidget`.
`show_main_menu` inserts placeholder pages and fills them through `QTabWidget.currentChanged`.
Skills, Grand Exchange, Equipment, Stats, and Settings build at open.
The Bank widget tree also builds at open behind its placeholder.

- Connect `currentChanged` only after all placeholders exist. The first `addTab` emits `currentChanged(0)`.
- Cross-tab refreshes use `ctx.refreshers` keys `active_label`, `gear`, `shop`, and `quests`.
  A missing key is an intentional no-op. Builders derive all rendered state from `player_data` and `ctx.selection` at build time.
  Refreshers take no data arguments. Callbacks must write state before they request a refresh.
- Tests must open deferred tabs before they inspect widgets.
  Use `_open_shop_tab`, `_open_quests_tab`, and `_open_achievements_tab` where applicable.
  Quest journals fill on first expansion; use `_expand_quest_card` before journal text checks.
- Skills, Bank, and Equipment call each other through `_refresh_equipment_views`.
  Separate builders must preserve this shared refresh contract.
  Measure open-time costs before performance claims; `memory-bank/future-work-kanban.md` owns current targets and evidence.

`shop_logic.shop_view_models_pure` shares a save snapshot across shop view models.
`ensure_shop_state_pure` copies the whole save, so repeated calls per shop duplicate that cost.

## Activities master-route and simulated-clock placement

The top-level Activities entry is a navigation route, not a resume command. It
must render the Activities master tree even when a saved or last-open activity
exists. Explicit activity deep links and activated tree rows may open a named
detail, and returning to the master tree must not erase the saved activity.

The Activities category has three icon rows in its middle Selection column:
Activities, Minigames, and Distractions and Diversions. The Activities row owns
only the Warriors' Guild and Landmarks master groups. Minigames and D&D render
their entries as flat, case-insensitive alphabetical lists. Deep links select
the owning middle row before opening details; returning through the top-level
Activities row must show the master groups without clearing the saved activity.
The 250-pixel middle-column width is Activities-only; all other categories keep
the shared 190-pixel width. The simulated world clock belongs in the main-menu
status row only. It shows `12 + calendar hours inside the world day`, preserving
the noon origin at migration; it never reads wall-clock time.

## UI Gotcha: nested hook callbacks are not removable by a fresh closure

`injectors.register_deck_browser_button()` may run more than once during profile/setup flows. Its callbacks are nested functions, so recreating them and calling `hook.remove(new_callback)` does not remove the prior function object. Register these callbacks through the stable AnkiScape hook-key replacement helper; otherwise one browser message is dispatched once per surviving registration before the menu-open guard can observe the first scheduled dialog.

## UI Gotcha: dark-mode text colors (`palette(mid)` is NOT a text role)
`palette(mid)` and `QPalette.Mid` are frame and border roles, not text roles.
They can make disabled or placeholder text invisible in dark mode.
Use `ui.dim_text_color(widget)` for `setForeground` and `ui.dim_text_css(widget)` for stylesheet text colors.
These helpers derive color from the theme's `Text` role and reduce alpha.
Use `palette(mid)` only for borders. Prefer `palette(text)` and `palette(base)` for button labels and faces.
The macOS dark-mode button face can render light.
`.cursor/rules/qt-dark-mode-text.mdc` and `test_empty_slot_text_is_dark_mode_safe_not_palette_mid` enforce the contract.
Verify color changes in dark mode and light mode.

## Skill-icon and Stats projection pattern

Every skill-facing UI reads the same canonical `icon/<skill>_icon.png` file
through `skill_icon_path_for`; do not create a second Stats-only, Training-only,
or Combat-only art family. Canonical skill sprites are cutoff-pinned,
provenance-recorded, tightly cropped, and scaled by Qt with aspect ratio
preserved plus `FastTransformation` so small pixel art stays crisp. Asset
normalization is a source-file invariant, while each surface owns only its
display size.

Stats projects `current / base`, not `level / cap`. Base levels come from the
skill registry's save keys. Temporary Combat boosts and drains come from
`combat_current_levels`, while action-bounded non-Combat boosts must be
projected from their owning settled state. The same calculation must feed both
the three-column cell and the selected detail block so those two surfaces
cannot disagree.

## Melee attack-type resolver

The melee attack-type resolver combines the equipped weapon's `weapon_type` ID with the selected slot.
`WEAPON_TYPE_ATTACK_STYLES` in `data/combat_data.py` contains the contract from 2011Scape's `AttackStyleData.kt`.
Storage separates weapon style from physical attack type.
`combat_attack_style` stores `accurate`, `aggressive`, `defensive`, `controlled`, `ranged_*`, or `magic_*`.
`combat_attack_style_type` selects `auto`, `stab`, `slash`, or `crush` within that slot.
The default `auto` uses the weapon's first matching slot and needs no migration for old saves.

Do not merge base weapon style and XP mode.
The `TWO_HANDED_SWORD` slot with `AGGRESSIVE` weapon style and `SHARED` XP mode requires separate calculations.
Effective level and accuracy use the base weapon style.
XP uses the slot's `xp_mode` through `melee_xp_style_id` and `_COMBAT_XP_MODE_TO_STYLE_ID`.

Player rolls use `attack_<type>` and `defence_<type>`.
Untyped melee enemy attacks use `max(attack_*)` and `max(defence_*)` because enemy data supplies only `attack_style: "melee"`, not a physical subtype; ranged, magic, and `magic_melee` attacks use their own resolver paths.
`combat_melee_attack_type_pure` returns `(style_type, xp_style_id)`.
`combat_weapon_attack_style_slots_pure` and `combat_weapon_style_options_pure` expose slot and selection data.
Typeless weapons and bare fists use `WEAPON_TYPE_UNARMED_STYLES`, which contains crush styles.

## Combat selector restore timing

The Combat target tree's saved row is selected while the tree is built, but Qt
cannot reliably scroll that row into view until the mounted widget has completed
layout. Schedule the restore scroll for the next event-loop turn, verify that the
callback still owns the live rebuilt tree, and tolerate deletion before the
timer fires. A restored saved row stays green and bold; blue selection remains a
transient keyboard or pointer state and must not change persistence until
activation.

## Promotion gate and landing lock

`tools/promotion_gate.py` owns verification and landing. `tools/run_remote_tests.py` owns remote lane commands and acceptance thresholds.
Read these tools for current command options and threshold values; do not copy changing limits into this document.
`run` compares the gate's own source files (`GATE_SOURCES` in `tools/promotion/cli.py`) with the candidate's copies and re-executes the candidate's `tools/promotion_gate.py` when they differ, so a candidate that changes what the gate expects is judged by its own gate code.
Remote mode runs the plain and Qt lanes serially.
Both lanes and the documentation, test-quality and reachability checks read one private snapshot of the recorded commit; remote sync uses that same snapshot. The snapshot's worktree-layout tool audits the original repository, as do the clean-tree, diff and final HEAD checks.
The papercut check runs `tools/memory_bank/move_papercuts.py check` in that snapshot against the commit's merge base with `main`, so a merged tree that lost a papercut line or holds an entry both open and fixed fails with the tool's own lines.
Local test lanes remain supported. A plain-only branch check cannot authorize landing.

Remote acceptance requires minimum discovery and active coverage (`tests - skipped`).
Do not substitute an absolute skip limit for active coverage.
Dispatches on the same machine share a fixed absolute lock path.
An exclusive local flock covers rsync and polling while the local dispatch process lives.
Another dispatch reports the lock path and waits before it touches the shared mirror.
This lock does not provide cross-machine exclusion or protection after the local process exits.

An interruption or timeout can leave a detached remote lane active after lock release.
Run-specific IDs isolate logs and reports, but a later dispatch can still fail because of shared remote state.
Reconcile that state before a retry.

A successful gate atomically records the exact commit, passed checks, and a `remote_lanes` boolean in the shared Git common directory.
Evidence without that field parses as local evidence. Remote evidence is not a universal landing requirement.
The source worktree must be clean before a receipt is written. The snapshot is a private Git checkout of the recorded commit, so temporary source edits cannot change the files under test. It links the canonical `.venv-qt` for local Qt discovery; remote sync supplies the remote Qt environment.
The reachability check compares the gated tree's pins with its own JSON audit, which must exit 0.
Only an exact match passes. Content additions must update the affected pins in the same commit.

A rerun removes prior evidence for that commit. A failed rerun writes no evidence.
Gate logs use `ankiscape_worktrees/gate-<short-sha>.log` and `ankiscape_worktrees/gateplain-<short-sha>.log`.
The remote checkout is an rsync mirror without `.git`.
Remote tests must use filesystem fixtures and must not invoke Git.

The canonical Git common directory owns gate registration, commit checks, evidence, landing locks, and landing state.
Gates for different commits can run together. An OS file lock protects each active marker against recycled PIDs.
Use the promotion tool to land, not a manual `git merge --ff-only`.
Landing is serialized and requires full-gate evidence for the exact target commit.
It refuses another active gate, a target that does not descend from current `main`, or a canonical checkout with uncommitted tracked changes before or after the fast-forward; untracked files do not block it.
An unlocked gate marker is stale regardless of its stored PID; report it before removal.
- A global pseudo-item removal in `quest_reward_items_as_dict()` is safe only after every catalog quest that parsed the same name has a `QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID` entry; enumerate all catalog references first.

## Quest reward replacement dicts REPLACE, not extend

`QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID`, `QUEST_UNLOCK_REPLACEMENTS_BY_ID`, and
`QUEST_XP_REWARD_REPLACEMENTS_BY_ID` in `data/quest/catalog_overrides.py` replace a quest's whole tuple.
They do not extend it. Each replacement must contain every valid entry, not just the corrected entry.
Subset checks cannot detect lost entries; use whole-tuple guards.

Load `QUEST_DATA` on canonical main and on the branch.
Compare reward, unlock, and experience sets for every catalog quest; derive the census from `QUEST_DATA`.
A lost entry is a regression unless source evidence requires its removal.
Access text belongs in `unlocks`, not item rewards.
Verify every genuine item reward against the pinned source before a whole-tuple replacement.


## Item registry ownership is first-write-wins

`build_item_definitions()` keeps the first row for each storage key, so an early
skill-output row can mask later cache-backed extra-item metadata. When those rows
overlap, keep the skill target's level and XP but overlay the authoritative item
ID, stackability, and tradeability; order the owning extra-item map after
consumer-only maps so incomplete rows cannot erase those fields.

## Quest ID dict keys are source-unique after alias resolution

Direct `*_BY_ID` dict literals can mix string constants and literal quest IDs;
Python resolves both to the same key and silently keeps the later payload. The
quest-catalog guard parses the module source and resolves module-level string
constants before checking key uniqueness.

## Review-earned dialog tests

A runtime test that attaches the real `check_achievements` callback must wrap
it with `DeferredAchievementDialogs().defer(check_achievements)`. A direct
callback can pass without a `QApplication`, then open a guarded modal in the
monolithic Qt lane after another test creates the application.

## Module-surface identity omits the defining module (2026-09-21)

A published object is identified by its published path and qualified name, not by the module that defines it, because nothing in the product pickles and re-exports keep old import paths working. Decision and proof: `handoffs/fable-grill-papercuts-2026-09-21-decisions.md`, decision 4.

## Owner decisions — 2026-10-15: game speed and world day

These are approved design decisions, not shipped behavior. The [decision queue](design-thread-queue.md#answered-owner-decisions--2026-10-15-game-speed-and-world-day) retains all 11 decisions and the exact owner authority.

- The speed default is ×10 and its range is ×1–×20. Name it Game speed; the copy model writes the tooltip.
- The global speed rule replaces the earlier deferral. Per-method balancing remains deferred; sourced XP amounts stay fixed.
- Each card supplies 6 game ticks × speed. Handlers spend this budget. Quests and Dungeoneering deliberately keep one stage/room per card.
- Danger stops the card at every condition in decision 5. Combat can chain only within the budget and before danger.
- Fish Flingers uses its sourced ten-minute duration and eight catches; Master Angler remains automatic by owner ruling. No past XP rollback.
- Adaptive World day reads `ease > 0` revlog entries from the 60 completed Anki days before the current day, grouped at the scheduler cutoff. The median is bounded 100–1,000 cards; fewer than 7 study days uses 240. Query only on a boundary card, before Anki writes its row; fixed override remains available.
- Change day length only at a boundary. Share it across reset, growth and restock consumers. Undo must restore the boundary and length exactly.
- Each card advances 3.6 seconds × speed inside a day. The boundary skips the remaining 24-hour span as logged-out time.
- Farming walks calendar deadlines in order, preserving fractional minutes and disease RNG across the gap. Market time advances at one tick per 600 calendar ticks; Fish Flingers tickets settle inside the boundary transaction. Undo restores every changed save key and RNG; re-answer reads the current config again.
- Part H event conversion remains held under F1: the 30-minute notices and two-hour events exceed a default ×1 play window, and Big Chinchompa's 12-hour interval exceeds even the default ×20 window. No shorter interval or replacement phase is approved; other calendar work is independent.
- Timers use the same budget. Thieving stuns spend stun_ticks; Restaurant fairness spends the actual successful-card budget. Again advances only the clock.
- Show one pace dialog at first launch for a new player, or once after this update for an existing player. Defaults, current values, hours and close behavior follow decision 10; the owner save has no special path.
- Ship all pace/calendar parts together after rate/lump/daily-share/danger/chain/Undo/native proof. Only the approved Settings changes and dialog receive new UI. Opus authors UI and a taste-qualified model reviews it.

The2026-10-15 nit rulings settle sourced text/gates (R1), first performed-deed endpoints (R2), enforceable constraints (R3), and clipped text defects (R4). The [owner decision queue](design-thread-queue.md) retains each application and its evidence. No rule authorizes unrelated layouts or erases source disputes.
