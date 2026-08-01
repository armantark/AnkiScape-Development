# System Patterns

## One fixed reviewer strip, one geometry authority

Reviewer chrome is a fixed-height row pinned to the live top edge of Anki's
answer-button bar. Card content never selects its geometry: every new review
document gets a base inset equal to `REVIEW_STRIP_HEIGHT`, open drawers add only
temporary scroll reserve, and late web-content measurements must not move the
row.

- `ReviewStrip` owns four stable left-to-right seats: separate D&D and Farming
  badges, `ReviewHUD`, and the bank-run button. Hidden or empty content does not
  resize or reorder those seats.
- `logic/review_strip_logic.py` decides strip, Event-log, badge, and bank-action
  views. `logic/grand_exchange_logic.py` owns GE row visibility, text, tone, and
  action. `ui/ui.py` renders those projections without re-deriving them.
- `_reposition_review_overlay()` is the only geometry authority. Event log is
  immediately above the XP box, GE is above Event log, and both expand upward.
  Floating XP anchors to the strip and is re-anchored by the same pass.
- Every XP emission goes through the retained Event-log seam. The feedback
  context accumulates the real awarded skill names so a combined popup names
  its complete skill set.
- The strip bank action is only a runtime request seam. Combat uses the existing
  combat bank-run state; carried activities convert the request into their
  existing target-specific travel profile on the next productive review.
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
The add-on is a small Python package loaded by Anki. It separates pure game contracts from Anki-aware orchestration for review dispatch, runtime actions, target rows, and achievements, though some skill behavior still lives in UI, storage, stats, and icon-registration surfaces.

## Documentation Authority

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

## Asset provenance writes are serialized

Asset fetchers update the shared `assets_provenance.json` manifest by reading,
modifying, and replacing the whole document. Do not run two fetch commands
that target that manifest concurrently: both downloads can succeed while the
last writer silently drops the other provenance entry. Fetch shared-manifest
assets serially, or rerun the missing entry with `--force`, then assert every
expected file and provenance key in the asset test.

## Important Modules
- `__init__.py`: runtime orchestration, global player state, review hooks, answer handling, menu callbacks, save/HUD/UI bridge callbacks, and compatibility review-action wrappers.
- `runtime_actions.py`: Anki-free runtime review-action handlers and handler-keyed can-start checks for the complete skill surfaces, unified Combat, Quests, Utilities, and Activities. It mutates `player_data` through a callback/context contract supplied by `__init__.py`.
- `constants.py`: item data, skill source data, image paths, XP table, and compatibility exports.
- `logic_pure.py`: pure helpers for XP/level math, probabilities, crafting, Utilities/Activities, mining, woodcutting, fishing, hunter, smithing, quests, claims, and runecrafting operations.
- `cadence_kernel.py`: pure foreground-action cadence contracts. It declares
  `R = 1000`, exact integer residual scheduling, four admission modes, overflow
  validation, and resource/actor lock shapes.
- `cadence_live.py`: default-on runtime route declarations and exact admission.
  It maps source-compatible targets to rate-limited or embedded-probability
  behavior, Combat to six immediate ticks, and incompatible evidence to an
  explicit `source_blocked` declaration that preserves the handler action.
- `cadence_coverage.py`: complete handler/target catalog and fail-closed
  validation for every selectable foreground route plus Quest, Utility,
  Farming, attached Summoning effects, and future skill attachments.
- `cadence_shadow.py`: retained Phase 3 evidence resolver and reporting support.
  Its old observer state is never advanced by the default runtime and never
  seeds live cadence state.
- `tools/cadence_shadow_report.py`: renders current, proposed, and pinned source
  XP/hour for either the complete six-skill route catalog or accumulated shadow
  state from a player-data JSON export.
- `logic.py`: Anki-aware level-up and achievement checks plus probability wrappers.
- `storage.py`: Anki config persistence.
- `storage_pure.py`: default player shape and migrations.
- `skill_registry.py`: pure skill catalog for current and planned skills, including stable IDs, categories, save keys, and review eligibility.
- `action_registry.py`: pure review-action dispatch metadata. It resolves levelled skills and both no-XP surfaces to handler keys without adding fake registry skills.
- `target_metadata.py`: pure target-row metadata for the Skills hub. It builds labels, tooltips, icon paths, enabled/current state, groups, sort order, and lock reasons for registered skill targets, Combat, Utilities, and Activities without creating Qt widgets.
- `achievement_metadata.py`: pure achievement definitions, difficulty order, grouped row view models, and progress-count helpers while preserving the legacy completed-achievement name contract.
- `hunter_data.py`: source-backed Hunter target data. It uses 2011.rs guide rows for levels/XP/rewards, local 2011Scape cache item names/ids for storage keys, and local 2012scape/Darkan Hunter code only as mechanics/id parity because the local 2011Scape checkout has no Hunter mechanics plugin.
- `item_registry.py`: pure item manifest helpers for current economy items, including stable IDs, storage keys, categories, assets, and source/license notes.
- `prayer_data.py` / `prayer_passive_data.py`: source-backed Prayer training, Combat prayers/curses, composite altar selection, passive reward identities, and enemy mappings.
- `urn_data.py`: the authority for all 26 training-urn tiers, five physical states, source IDs, charge eligibility, sanitation, and custom-layout state materialization.
- `equipment_data.py`: generated worn-equipment contract for Smithing armour/weapons and Mining bonus gear, including slots, combat gates, two-handed flags, attack speed, and combat bonuses.
- `quest_catalog_generated.py`: generated pre-EOC quest catalog. Do not edit manually; regenerate it with `tools/build_pre_eoc_quest_catalog.py`.
- `quest_data.py`: Quest definitions, hand-audited overrides, generated quest item rewards, XP lamp claim definitions, and completion-unlock rules for skill targets.
- `ui.py`: Qt dialogs, HUD, menu, stats, bank, achievements, and settings.
- `hooks.py`: centralized hook registration and dry-run planning.
- `injectors.py` and `deck_injection_pure.py`: floating widget / deck browser injection helpers.

## Current Skill Flow
1. Anki shows a review card and the add-on marks review state.
2. The user shows the answer, then answers with an eligible ease.
3. `on_answer_card` calls `on_good_answer` if the current skill is active and XP has not already been awarded.
4. `__init__.py` resolves the handler key and calls `runtime_actions.py` through a `RuntimeActionContext`; runtime handlers call pure helpers, update `player_data`, check levels/achievements through callbacks, save, and refresh UI.

## Existing Skill Patterns
- Gathering skills use success probabilities and selected resource data.
- Processing skills consume inventory and produce output items.
- All skills use the shared `EXP_TABLE` and per-skill `*_level` / `*_exp` fields.
- Inventory is a single dictionary shared across ores, logs, gems, bars, and crafted items.
- The backend registry preserves current flat save keys while centralizing skill identity. This is deliberate: Anki config is the stable boundary, so registry-driven defaults are safer than a nested save migration right now.
- The item registry uses existing inventory storage names as `storage_key` values. Stable item IDs can support future UI/action metadata without breaking current saves.
- Review dispatch now resolves an `action_registry.review_action_handler_key` before calling the matching `runtime_actions.py` handler. Thin public `on_<skill>_answer` wrappers remain for compatibility and direct tests. This keeps display names, save keys, Utility aliases, handler identity, and runtime mutation logic connected without requiring a large action-engine rewrite.
- Cadence state is a route-keyed `player_data["cadence_profiles"]` mapping with
  exactly five sanitized fields per route: `credit`, `opening_ready`,
  `assigned_reviews`, `opportunities_emitted`, and `cadence_version`. Config v34
  adds the mapping without rewriting existing state. Because review undo diffs
  the complete `player_data`, cadence residuals require no separate undo stack.
- Historical shadow observation used a separate route-keyed
  `player_data["cadence_shadow"]` namespace. The namespace may remain in old
  saves and reports but is not promoted or advanced by live dispatch.
- Live ranged XP/hour evidence uses the exact lower endpoint as a labeled
  conservative abstraction, never a midpoint. Processing routes whose
  authentic probability already embeds cadence reuse one source roll and do not
  enter the residual scheduler or draw a second random number.
- Runtime-to-source mappings must be semantically exact. Missing or incompatible
  rows are reportable `source_blocked` observations, not opportunities to infer a
  replacement rate. This includes ordinary versus concentrated gold, mixed
  leaping fish versus sturgeon-only evidence, runite coins/hour versus XP/hour,
  and urn-inclusive rocktail XP that cannot be decomposed.
- Skill identity has two separate axes: `implemented` means a complete owned review surface, while `surface_state` is `complete`, `partial`, or `planned`; `trainable` covers complete and partial skills. Use `training_source` for partial cross-surface stats and `visible_in_skill_hub` to hide Attack, Constitution, Defence, Ranged, and Strength because they train only through Combat. Prayer and Magic are complete surfaces; Summoning remains planned.
- Composite target choices must be committed atomically. Prayer stores stable material and UI-method identities, resolves them to the runtime target/mode pair in pure logic, validates the pair once, and clears hosted-search/owned-stint state only when that composite selection changes.
- Target-carried passives are physical pack semantics, not global ownership flags. Bonecrusher, Ectoplasmator, and training urns activate only when the selected target's clamped carried view contains the relevant item; bank-only or other-target copies remain inert.
- Saved Advanced layouts describe logical urn slots. `materialize_urn_layout_pure()` follows each slot through runed, active, and full physical names before either skilling or Combat repacks it, prioritizing the active charge-bearing object and then teleportable full urns.
- Direct inventory actions that award XP but do not answer a card use a bounded custom Anki undo stack. Full-urn teleport persists immediately and never consumes or creates the single review-action snapshot; multiple direct teleports undo in LIFO order independently of review undo.
- Owned gilded-altar state is stint-scoped. Starting a new stint consumes one clean marrentill per installed burner, freezes the 250/300/350% multiplier, and does not re-charge herbs until target/mode selection ends that stint.
- Skills-hub target lists now consume `target_metadata.TargetRowMetadata` rows. The Qt layer uses one shared `QListWidget` renderer for Mining, Woodcutting, Fletching, Firemaking, Fishing, and the flat list cases, plus one shared grouped `QTreeWidget` renderer for Smithing, Crafting, Cooking, Runecrafting, and Hunter. The pure row metadata owns labels, tooltips, icon paths, group ids, sort keys, current state, enabled state, and lock reasons; Qt only renders rows, persists group expansion where applicable, and guards disabled-row clicks.
- Achievement definitions now live behind `achievement_metadata.py`. `constants.ACHIEVEMENTS` stays as a legacy export for `logic.py`, old tests, and any add-on code that reads the dict shape, while UI code consumes row/progress helpers instead of reconstructing grouped achievement state.
- Fletching is the first staged expansion skill to complete backend + target-panel rollout. It uses stable recipe IDs for save/UI selection, because multiple recipes can produce the same inventory item (for example, several log tiers all output arrow shafts).
- Fletching material-only inputs such as feathers and arrowtips are registered as item-manifest `material` entries. Arrowtips are sourced through Smithing; feathers come from live NPC shop stock and Combat drops. The retired `scavenge_chicken_feathers` bridge must not return.
- The project-wide parity evidence contract lives in `memory-bank/pre-eoc-source-verification-standard.md` and applies to every skill, quest, activity, item chain, unlock, interface, rate, and future gap-fill—not only owner grills. Source scope is RuneScape content available strictly before the `2012-11-20` EOC cutoff. Ignore OSRS-specific mechanics, items, quests, interfaces, and rates unless an independent pinned pre-cutoff RuneScape source proves the same mechanic existed. OSRS may provide a research lead but is never parity evidence by itself; `fletch-javelin-construction` is the canonical rejected false positive because its shaft/head construction chain belongs to OSRS's 2016 Monkey Madness II family while period RuneScape javelins were shop/drop ammunition. For RuneScape Wiki evidence, prefer the nearest useful pre-cutoff `oldid`, verify its revision timestamp through `api.php?action=query&revids=...&prop=revisions`, and read the archived literal wikitext through `api.php?action=parse&oldid=...&prop=wikitext`. Do not trust a historical page's rendered calculators, exchange values, inline tables, templates, or Lua modules merely because the article oldid is old: recover the dependency's own historical revision, find literal values in the article wikitext, or corroborate with a dated Wayback capture or period cache/script. Likewise, a modern commit in a 2012-emulation repository is reconstruction evidence, not automatically a period source. If wiki/cache evidence and high-fidelity Darkan cannot establish a mechanic, mark it source-blocked and wait; never fill the gap from modern RS3/OSRS or inference.
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
- Historical timers use the global answered-card AnkiScape clock already shared
  by NPC shops and the parked GE: 10 answered cards equal one simulated game
  hour and 240 equal one simulated day. All answered cards advance the clock,
  regardless of skill or reward success; undo rolls time back. Daily/weekly
  allowances currently reset at simulated boundaries without stacking, never
  from the computer's wall-clock date. Owner decision 2026-07-17 supersedes
  this for recurring activity eligibility once implemented: bank one current
  entry plus one reserve by default, while rewards still require playing the
  activity. See `simulation-time-boundary-2026-07-16.md` Decision 2.
- Answer-button semantics are now explicit: every valid answer emits one
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
- Urgent or expiring reviewer state uses the reusable interactive alert-strip
  contract in `review-hud-world-alerts-contract-2026-07-16.md`. It is a sibling
  above the mouse-transparent XP HUD, not a control embedded inside it and not a
  new standalone widget per feature. Initial rows are the existing Gravestone
  and Summoning's expiring Familiar cargo, each with distinct sourced art,
  labels, countdown semantics, and detail actions.
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
- Compatible restore trips coalesce rather than charging duplicate reviews. Summoning's
  `Visiting altar+obelisk` foreground detour consumes the next successful answer,
  replaces the selected target action, and restores ordinary Prayer and Summoning
  points together. An existing combat Bank-run altar stop adds the obelisk restore at
  no further review cost. It cannot fire on Again, run on wall-clock time, restore
  special-move points without source support, or grant the target's ordinary output.
- Enabled automation may also insert an owned-resource Bank detour. Summoning pouch
  depletion converts the next successful answer into a refill/resummon transaction
  when compatible Bank stock exists; it does not also perform the target action and
  never fires on Again. Advanced carried slots reduce detour frequency rather than
  bypassing the same resource rules.
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
- Compact D&D sessions may use explicit answered-card segments when the activity loop
  is the content. Familiarisation uses four segments and three focus pips: success gains
  15 shards, Again gains none and loses one pip, ending at 60 shards, zero focus, or four
  answers. Its rolling weekly cooldown uses world ticks and never the wall clock.
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
- Both no-XP surfaces stay outside `skill_registry.py` unless they gain real
  level/XP semantics. `action_registry.py` maps `Utilities`, `Activities`, and
  the legacy `Utility / Activities` name to the same `utility` review handler.
  Legacy active-skill saves normalize to the surface that owns
  `current_utility`.
- The Skills hub presents those surfaces as distinct categories with separate
  toolkit and period Activity-compass sprites. Activities gives its primary target
  picker guaranteed height beneath a bounded, separately labeled event-status
  region; Utilities never renders those event cards.
- The Activities picker paginates by semantic group instead of scrolling all
  groups at once. Previous/next navigation preserves the selected activity,
  page height is measured from the current rows, and group labels are plain
  headings rather than false expandable-tree affordances.
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
- Crafting now follows the source-data-module pattern at the backend layer (`crafting_data.py`). `current_craft` stores stable recipe IDs, inventory stores real item names, and the data intentionally includes live input-starved recipes so missing acquisition loops light up later without reshaping the recipe. XP-bearing Crafting ignores recipe `batch_size`; only no-XP Utility/Activities batch material prep.
- Woodcutting now has a focused source-data module (`woodcutting_data.py`) rather than only ad hoc `constants.py` rows. Its stable target IDs are persisted in `current_tree`, while inventory uses real item output names such as `Logs` and `Oak logs`.
- Fishing now follows the source-data-module pattern (`fishing_data.py`) as a Gathering skill. Its stable method IDs are persisted in `current_fishing`, while inventory uses real output item names such as `Raw crayfish`, `Raw salmon`, and `Raw shark`. Mixed-output rows preserve source order during rolls, consumable material is removed only after a successful catch, and Barbarian fish side XP updates hidden Strength and the live Agility state without exposing Strength as an independent skill surface.
- Fletching now follows the source-data-module pattern (`fletching_data.py`) as
  an Artisan processing skill. Stable target IDs are persisted in
  `current_fletch`, while inventory uses real output and material item names.
  `constants.FLETCHING_DATA` is only a compatibility export. Fletching target
  metadata carries group/sort data for the shared grouped `QTreeWidget`
  renderer. Common reusable tools remain ambient; only level, materials, and
  generic target unlocks gate rows.
- Cooking now follows the source-data-module pattern (`cooking_data.py`) as an Artisan skill. Its stable target IDs are persisted in `current_cooking`, while inventory uses real raw/cooked/burnt item names. Cooking failures are productive inventory mutations: the raw input is consumed, the source burnt item is added, and no XP is awarded. Source low/high chances stay in data and are adapted to review-scale probabilities in pure logic.
- Runecrafting now follows the source-data-module pattern (`runecrafting_data.py`) as an Artisan skill. Its stable target IDs are persisted in `current_runecrafting`, while inventory uses real rune/access item names. Rune Mysteries quest state, Bank Claims, Wicked hood fed-altars, pouch degradation, and Binding necklace charges are explicit flat side-state keys in `player_data`. Quests are review actions through `action_registry.py`, not fake skills in `skill_registry.py`.
- Hunter now follows the source-data-module pattern (`hunter_data.py`) as a Gathering skill. Its stable target IDs are persisted in `current_hunter`, while inventory uses canonical cache item names such as `Red feather`, `Kebbit claws`, `Imp-in-a-box (2)`, `Gourm' impling jar`, and `Ess' impling jar`. The local 2011Scape cache/snapshot is treated as identity evidence, not a mechanics implementation; 2011.rs guide rows supply levels/XP/rewards, and local 2012scape/Darkan Hunter code supplies mechanics/id parity. Hunter outputs are first-class `hunter` bank items, while jars/traps such as `Butterfly jar`, `Impling jar`, and `Magic box` remain material items. Quest locks cover completion gates and narrow route precedents only; partial-route access such as Regicide-start content stays in notes until a route model exists.
- Hunter separates reusable gear from consumables. `requirements` are deleted only on successful catches; `tools` are bank/inventory gates that remain after a catch. Current reusable gates cover bird snares, box traps, butterfly nets for butterfly/Puro-Puro rows, and small fishing net plus rope for tree-net rows. Hunter supplies now come from live NPC shops; the retired `Buy Hunter supplies` Utility bridge must not return.
- The broad quest catalog is generated, not hand-maintained. `tools/build_pre_eoc_quest_catalog.py` produces a 194-row pre-EOC catalog by real release order, with Recipe for Disaster split into separate subquests. Catalog/stage-row presence is coverage scaffolding, not a claim of full quest parity: later passes must still verify authentic stages, routes, branches, item transformations, combat, rewards, and unlocks under `memory-bank/pre-eoc-source-verification-standard.md`, waiting for high-fidelity Darkan where necessary. Each row should carry source oldids, strict prerequisites, point/XP/item rewards, lamp rewards, and source-backed journal stages. Hand-audited overrides belong in `quest_data.py` when pinned pre-EOC evidence is stricter than generated or emulator data.
- Quest starts are strict. A quest with incomplete prerequisite quests or unimplemented required skills must be impossible to start. Completion XP for implemented skills is granted immediately; XP for unimplemented skills is stored in `pending_skill_exp_rewards` and applied by migration when the skill becomes implemented.
- Quest-list availability should flow through `quest_availability_state_pure()`, not ad hoc UI checks. Its states are `can_start`, `in_progress`, `blocked_at_stage`, `completed`, and `locked`. `locked` means the quest cannot start; `blocked_at_stage` means a started quest is waiting on current-stage inventory, tools, actions, routes, or combat. Keep that separation: stage requirements are not start locks.
- Product implementation readiness and player progression eligibility are separate gates. Exhaustive source/completeness ledgers may contain unfinished content, but live UI, search, rolls, rewards, and action registries must not expose implementation gaps as disabled, locked, placeholder, inert, or `coming later` rows. Derive readiness from stable dependency identities so content materializes automatically when its complete runtime graph exists, without a migration, cleanup pass, release allowlist, or duplicated registry. Replace hidden player-facing debt with a developer audit that assigns every catalog row a machine-checkable readiness result and rejects unknown or stale blockers. Only after a row is runtime-ready should authentic player quest/level/item/unlock eligibility run; a finished surface may show those real progression locks where its owner-approved design calls for them.
- Stage-aware quest requirements live in `QuestDefinition.stage_requirements` data, serialized by `quests_as_dict()` and enforced by pure helpers in `logic_pure.py`. Use `quest_current_stage_blockers_pure()` / `quest_current_stage_blocker_reasons_pure()` for display, `can_progress_quest_pure()` for review readiness, and `apply_quest_progress_pure()` for stage advancement and stage-local consumed/produced items. The first proof case is The Knight's Sword: Mining 10 remains a start requirement, Redberry pie is consumed at Thurgo's stage, Blurite ore plus two Iron bars are consumed at the later Thurgo materials stage, and the 12,725 Smithing XP reward fires only on valid completion. A later 2011Scape starter batch added `produced_inventory` for quest intermediates such as Druidic Ritual enchanted meats, Pirate's Treasure chest key/message, and Vampyre Slayer stake/stake hammer. A follow-up intermediate batch added `start_inventory` and source-backed produced/consumed chains for Rune Mysteries, The Restless Ghost, and Lost City, including Ghostspeak amulet, Muddy skull, Air talisman, Research package, Research notes, Dramen branch, and Dramen staff. Demon Slayer is now a Darkan-backed focused replacement: it uses a nine-stage internal model so bucket water, 25 bones, three Silverlight keys, Silverlight, Delrith, and the incantation all gate at their source-backed stages before completion. Dragon Slayer is now a Darkan/local-2011Scape-backed focused replacement: 32 quest points remains the start lock, then Oziach, Guildmaster, anti-dragon shield, Melzar's Maze combat, Wormbrain's paid map piece, Oracle items, Crandor map assembly, Lady Lumbridge purchase/repair, Ned's route, Elvarg, and the Oziach report are separate current-stage gates. `QuestStageRequirement.variant` now models mutually exclusive route rows on the same stage; rows with no variant are mandatory, and route-matched variant rows are the only branch rows that can block, consume, produce, or resolve combat. Shield of Arrav proves this with Phoenix Gang and Black Arm Gang branches, Jonny the beard and Weaponsmaster combat gates, route-specific shield/certificate halves, and the partner half-certificate combine stage. Fight Arena now proves a Darkan-backed non-branch replacement where disguise production/equipment, Khali brew purchase/consumption, key theft/use, mandatory arena fights, and the Lady Servil return are stage gates rather than start locks. The Quests tab may show "Used during quest" item requirements before start, but those items must not block starting unless the source says they are start requirements.
- Branch and co-op quest decisions use structured `QuestDefinition.choices`, not fake inventory requirements. `quest_current_stage_choices_pure()` reports unresolved player choices, `apply_quest_route_choice_pure()` writes the selected route to flat `quest_route_states`, and started quests expose a `quest_choice` blocker until the choice is made. Shield of Arrav, Heroes' Quest, Temple of Ikov, Hazeel Cult, and The Void Stares Back are the current choice-backed coverage set. Shield/Heroes single-player co-op pieces are contextual contacts: Black Arm Shield no longer asks for manual Phoenix-partner key actions, Shield certificate merging consumes only the player's own duplicate half, and Heroes' Phoenix mansion route no longer requires a manual Black Arm partner action. Heroes' Quest inherits the Shield of Arrav route when it exists, with a fallback stage-9 choice for older saves. Hazeel Cult no longer grants both branch artifacts as unconditional completion rewards.
- Witch's House now supersedes its earlier two-row combat proof with a full
  12-stage Darkan-backed chain: potted-plant Door key, door entry, cupboard
  Magnet, Cheese/Magnet mouse-hole mechanism, witch patrol route, Leather gloves
  electric gate, fountain Backroom key, shed door, four experiment forms, Ball
  pickup, and Harvey hand-in. Cheese is consumed at the mouse stage, Ball is
  consumed only at Harvey, and 6,325 Constitution XP remains pending until that
  skill exists.
- Merlin's Crystal is an 8-stage Darkan/local-2011Scape focused replacement. It
  keeps quest-used items out of start locks, routes through the round-table
  investigation and Catherby crate, resolves Sir Mordred as a source-backed
  combat encounter, then gates Morgan questioning, Bucket/Insect repellent wax,
  Bucket of wax to Black candle, Bread to Excalibur, Bat bones/Black candle plus
  Tinderbox, Excalibur crystal smash, and King Arthur report at their current
  stages. Stage 8 is the completed state, so the ritual, crystal smash, and
  Arthur report all live on stage 7. Thrantax is intentionally an action/dialogue
  gate, not a combat gate, because local Darkan binds him through ritual dialogue.
- Generated combat source matching is token-safe, not raw substring based.
  `tools/build_pre_eoc_quest_catalog.py` supports explicit aliases such as
  `Poisonous Spider` -> `Poison Spider`, and singularizes plural source names as
  full tokens only. Temple of Ikov's generated `Guardians of Armadyl` row now
  resolves to Darkan's level 45 `Guardian of Armadyl` combatdef, and Observatory
  Quest's `Poisonous Spider` resolves to local 2011Scape's level 31 `Poison
  Spider`. This also prevents false positives such as `Bear` matching `Johnny
  The Beard`. `Lvl 2 Goblins` now parses as `Goblins`, but remains a
  missing-stats blocker because the local goblin source has ID-dependent
  attack/defence expressions.
- `tools/build_pre_eoc_quest_catalog.py` also emits generated quest-wide
  stage blocker rows from pre-EOC `Quest details` item and combat fields.
  Generated rows can carry `required_inventory`, `required_inventory_options`,
  `consumed_inventory`, `consumed_inventory_options`, `produced_inventory`,
  `required_tools`, and `combat_encounters`; option groups must preserve
  alternatives instead of flattening them into separate hard requirements.
  `quest_data.py`
  deserializes them into the same `QuestStageRequirement` contract used by hand
  overrides. `logic_pure.py` treats consumed option groups as current-stage
  blockers and consumes the first satisfied option group when the stage
  advances. Produced inventory is not a blocker by itself; it is the
  source-backed item state created by a successful current-stage transition.
  `quest_data.py` then combines generated rows, hand-authored stage rows,
  focused replacement rows, and focused addition rows; use replacements when
  generated data conflicts with stronger 2011Scape/Darkan evidence, and use
  additions when a source-backed quest action exists but the generated item or
  combat parser cannot infer it. The current audit reports 194/194 quests with
  at least one stage requirement, and the Priest in Peril focused override
  fixes its generated stage-61/prose-parser row into nine source-backed stages.
  The 2011Scape starter batch then replaced bad generated rows for Cook's
  Assistant, Imp Catcher, Druidic Ritual, Pirate's Treasure, and Vampyre Slayer.
  Quest-only products must be produced by earlier quest stages before a later
  hand-in consumes or requires them; Cook's Assistant proves this by producing
	  Super large egg, Top-quality milk, and Extra fine flour in stages, with only
	  Bucket and Empty pot acting as external inventory blockers. Common items
	  bought or obtained as part of the same quest should be action-modeled instead
	  of shown as quest-wide inventory gates; easy deterministic steps belong in
	  `auto_actions` so review progression records them without blocking, while
	  true player/manual gates stay in `required_actions`. Vampyre Slayer's Blue
	  Moon Inn talk/beer path is the proof case, while its Stake and Stake hammer
	  are produced by Dr Harlow.
	  `tools/audit_quest_local_item_gates.py` enforces the narrow invariant that
	  quest-wide `Used during quest` requirements must not list items produced by
	  that same quest or granted by its `start_inventory`. The 2026-06-24 sweep
	  removed those misleading broad gates from The Restless Ghost, Ernest the
	  Chicken, Pirate's Treasure, Dragon Slayer, Witch's House, Heroes' Quest,
	  Fight Arena, and Rune Mysteries while preserving their current-stage blockers.
	  The same produced-item rule now protects Clock Tower rat poison/cogs, Monk's
	  Friend blanket, Dwarf Cannon railings/remains/Nulodion items, Sheep Herder
  cattleprod/bones, and Biohazard's rotten apple. Partner-supplied quest items
  should follow the same
  principle without pretending the player already owns the item: Shield of
  Arrav's Black Arm weapon-store key is modeled as Phoenix-partner action gates
  that produce the key and crossbows when the stage advances. Generated rows
  that misclassify route/location/skill/prose text as inventory or tools belong
  in the focused cleanup layer in `quest_data.py`, not in start locks or
  direct edits to `quest_catalog_generated.py`.
  The 2011Scape intermediate batch then replaced The Restless Ghost, Rune
  Mysteries, and Lost City with local source-backed item/action/route/combat
  chains. The Demon Slayer focused replacement then moved bucket water, bones,
  Silverlight keys, Silverlight, Delrith, and incantation requirements out of a
  broad generated combat row. The early Darkan stage batch then replaced Goblin
  Diplomacy, Ernest the Chicken, and Black Knights' Fortress with source-backed
  item/action chains, and `logic_pure._has_quest_tool()` now lets quest-required
  tools be satisfied by worn equipment for disguise stages. Dragon Slayer then
  replaced its broad generated row with source-backed gates for the anti-dragon
  shield, map pieces, Oracle items, Lady Lumbridge repair, Ned route, and Elvarg
  report. Shield of Arrav then replaced the generated branch prose with a
  route-variant stage chain for Phoenix Gang and Black Arm Gang, including
  partner half-certificate exchange as a finish-stage gate instead of a start
  lock. Fight Arena then replaced generated all-in-one requirements with a
  12-stage Darkan-backed chain for Khazard disguise production/equipment,
  Jeremy/lazy guard actions, Khali brew purchase/consumption, cell-key
  production/use, Khazard ogre, Khazard scorpion, Bouncer, and Lady Servil
  reward. Witch's House then superseded the old combat-only proof with a
  12-stage Darkan-backed chain for keys, Magnet, Cheese, witch patrol, Leather
  gloves, experiment forms, Ball pickup, and Harvey hand-in. A local Darkan
  quest-stage batch then replaced Fishing Contest, Gertrude's Cat, Clock Tower,
  Monk's Friend, Tribal Totem, and Scorpion Catcher with focused item/action/
  route chains. It proves that generated detail rows should be replaced when
  local quest handlers provide finer item transformations: fishing pass and
  trophy stages, milk bucket and doogle sardine stages, Clock Tower cog
  placement, Cedric supply stages, RPDT label/totem stages, and scorpion-cage
  stages all advance independently instead of being flattened into start locks.
  Sheep Herder then proves the same pattern for noncombat animal-disposal
  quest stages: poisoned sheep feed is produced and retained, Doctor Orbon's
  clothing is bought mid-quest, the cattleprod and coloured sheep bones are
  produced before later stages require or consume them, and the clothing remains
  a reusable tool gate. Plague City
  then proves that generated item rewards can be narrowed when stronger local
  stage evidence produces a quest item mid-quest: the gas mask is produced by
  Alrena and only `A magic scroll` remains a final item reward. Waterfall Quest
  proves that future combat-skill XP rewards stay structured in
  `pending_skill_exp_rewards` while the stage chain still handles book/key,
  Glarial item, rune, amulet, and urn gates. Biohazard then proves the same
  focused replacement pattern on a longer route chain: Jerico/Omart wall
  routing, Bird feed and Pigeon cage production/use, rotten-apple stew poisoning,
  Doctors' gown production, the level 13 Mourner, Distillator recovery, Elena's
  reagent vials, chemist Touch paper, errand-boy smuggling, Priest gown x2 for
  Guidor, and Elena/King Lathas reports are all current-stage gates. Heroes'
  Quest then proves a long branch-and-proof replacement: Blamish oil and oily
  fishing rod preparation, raw/cooked lava eel handling, Ice Queen/Ice gloves,
  Entrana Fire feather, Black Arm/Phoenix route-variant candlestick rows,
  armband exchange, and final Achietties proof items are current-stage gates.
  The Ice Queen lair access is a route blocker rather than a mandatory Jailer
  combat row because the source allows a Dusty key route or Agility shortcut.
  Family Crest then proves a source-backed long item-transformation chain where
  cooked fish, perfect gold ore/bars, perfect ruby jewellery, crest pieces,
  Johnathon's antipoison, Chronozon's blast-spell combat, and the final Family
  crest hand-in all gate at their current stages while Crafting 40, Magic 59,
  Mining 40, and Smithing 40 remain start locks. Temple of Ikov then proves a
  true ending branch: the Fire Warrior requires ice arrows plus one compatible
  bow option, Winelda consumes 20 Limpwurt roots, the Guardian route produces an
  Armadyl pendant and requires Lucien combat, and the Lucien route requires a
  Guardian encounter before the Staff of Armadyl is consumed at the final hand-in.
  Holy Grail and Tree Gnome Village then prove focused replacement rows can
  correct generated false positives and source-only unlocks: Holy Grail removes
  the false Brimhaven requirement, keeps Excalibur as the Black Knight Titan
  stage tool, splits Magic whistle/Holy grail production and consumption before
  the final King Arthur hand-in, and Tree Gnome Village consumes six logs,
  models tracker actions, two Khazard commanders, the Khazard warlord, orb/orbs
  hand-ins, and Gnome amulet reward while leaving spirit tree access as an
  unlock. A final all-catalog pass then made generated stage rows fail closed
  with source-backed action/checkpoint blockers for every pre-EOC catalog quest,
  fixed generated combat heading false positives, preserved prefix quantities
  such as `3x Warped terrorbirds` and `4x Living rock brawler`, split Shilo
  Village's Nazastarool into three sourced forms, set Legends' Quest's
  Nezikchened to three kills, and added focused resolver-ready Tough guy and
  Black Dragon rows. A 2026-06-23 cleanup pass then removed generated
  pseudo-inventory blockers such as Lletya, Oronwen, Tears of Guthix cavern,
  Crafting table 3, Agility Pyramid, Rimmington, Love Story, Thieving, Mining,
  Monkey Madness route items, generated teleport/tablet travel text, literal
  quest-name blockers, generated spell names, broad Food/Armour checklist text,
  and other parser-shaped blockers from inventory/tool fields. Rat Catchers now
  makes rat poison from Hooknosed Jack's ingredients during its stage, Dwarf
  Cannon completion now leaves a represented Ammo mould source for later
  cannonball and quest gates, bucket-of-sap uses are action gates, Within the
  Light's keys/crystal puzzle objects are action-gated, and The Fremennik
  Isles yak-hide armour/round shield prep is modeled as current-stage actions.
  The live audit now reports 194/194 quests with stage requirements, 1,120
  stage rows, 174 quests with item/tool blockers, 190 quests with action
  blockers, 32 quests with route blockers, 120 quests with combat blockers, 121
  produced-inventory rows, and 185/288 resolver-ready combat rows.
  This is all-catalog machine-readable stage-gate coverage, not proof of
  minute-detail historical simulation for every quest.
  Use
  `tools/audit_quest_stage_gate_coverage.py`,
  `memory-bank/source-audits/quest-stage-gates-catalog-wide-2026-06-22.md`, and
  `memory-bank/source-audits/quest-stage-no-stage-closure-2026-06-22.md`, plus
  `memory-bank/source-audits/quest-priest-in-peril-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-2011scape-starter-stage-batch-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-2011scape-intermediate-stage-batch-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-demon-slayer-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-early-darkan-stage-batch-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-dragon-slayer-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-shield-of-arrav-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-fight-arena-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-witchs-house-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-merlins-crystal-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-dwarf-cannon-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-generated-combat-name-matching-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-local-noncombat-stage-batch-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-sheep-herder-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-plague-city-waterfall-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-heroes-quest-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-family-crest-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-holy-grail-tree-gnome-stage-detail-2026-06-22.md`
  and
  `memory-bank/source-audits/quest-all-catalog-stage-gate-final-2026-06-22.md`
  before claiming a quest-stage pass is complete.
- Generated combat quantity rows should preserve source quantities. Numeric
  prefixes, `xN` suffixes, "at least N", and written quantities through ten
  are parsed in `tools/build_pre_eoc_quest_catalog.py`; do not collapse rows
  such as "Two Lava monsters" or "Five Ice Trolls" to a single combat
  completion.
- Quest combat encounters fail closed through one global flat save config:
  `player_data["quest_combat_config"]["resolver_enabled"]`. It defaults to
  `False`, so incomplete encounters produce `combat_locked` blockers instead of
  silently progressing. When the resolver is enabled, current-stage encounters
  still require source-backed NPC stats for the encounter's attack style and a
  player combat level at least as high as the encounter level before
  `apply_quest_combat_encounter_pure()` can resolve combat. Combat quantities
  are per-enemy progress, not group-complete flags: one Quest review increments
  `player_data["quest_combat_encounter_counts"][quest_id][encounter_id]`, and
  only when the count reaches the sourced `QuestCombatEncounter.quantity` does
  the runtime write the completed encounter id into
  `player_data["quest_combat_encounters"]` for compatibility with older saves.
  Existing saves that already have the completed id still satisfy the blocker.
  Encounters missing stats remain blocked as `combat_missing_stats`; this keeps
  the global switch from turning no-stats prose rows into completable fights.
  Focused `quest_data.py`
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
  encounters with Darkan resolver stats while keeping both routes blocked by
  the global combat config until battle support is enabled. Fight Arena adds
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
  Evil Chicken stays missing-stats blocked. Current stat coverage is 185/288
  combat rows; the remaining 103 statless rows
  are classified by
  `tools/audit_quest_combat_stat_gaps.py` and remain active quest debt.
  Historical RuneScape Wiki monster pages are now audited by
  `tools/audit_quest_historical_wiki_combat_stats.py` as a separate source tier:
  LP, max hit, and attack-style prose are useful metadata, but they must not be
  counted as resolver-ready hidden combat stats. The 2026-06-22 pass found 77
  metadata-only pages, 32 rows without monster metadata, and 0 remaining rows
  with resolver-ready historical-wiki hidden stats.
- Completed quest reviews intentionally turn Quest training off and show a modal `Quest complete` stop-point dialog through the same centralized warning-dialog helper used by material depletion. Keep that paired with the existing floating completion gain so the player sees both immediate feedback and a clear action stop.
- XP lamps from quest rewards are flattened into Bank Claims. Preserve the source amount, quantity, skill option set, and minimum level, but use one consistent `Choose skill` claim flow instead of copying every historical quest-specific lamp/chatbox interface.
- Bank Claims are a compact action inbox above the Bank inventory, not an item category. The frontend should render eligible rows only, summarize locked rewards, hide claimed rewards behind the all-caught-up state, and cap the rows to keep the inventory list as the main scroll surface.
- The Wicked hood claim is intentionally gated by Rune Mysteries only in AnkiScape. Do not re-add a Runecrafting level 5 claim gate; historical 2012 evidence shows that level prompt was not a reliable hard claim requirement, and the hood's actual altar use still remains constrained by Runecrafting target gates.
- Generic target unlock locks are still exported as `QUEST_UNLOCK_RULES` for
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
  `player_data["unlocked_abilities"]` ids, currently including
  `broad_fletching` and `barbarian_fishing`.
- Utilities and Activities are grouped independently by `group` metadata in
  their own Qt trees. Group metadata also feeds the explicit surface
  classification; tests require every registered no-XP row to belong to exactly
  one side.
- Mining now follows the same source-data-module pattern (`mining_data.py`). Its stable target IDs are persisted in `current_ore`, while inventory continues to use real item output names such as `Iron ore`, `Pure essence`, `Sandstone (10kg)`, and `Uncut opal`.
- Smithing now follows the source-data-module pattern too (`smithing_data.py`). It is the first skill with two XP-bearing stations under one skill: smelt and forge are both recipes in `SMITHING_DATA`, selected by stable `current_smith` IDs, while `BAR_DATA` is only a compatibility view for old smelt-only UI paths. Runtime uses one pure processing helper for both stations and keeps hammer/tool requirements implicit; level and inventory materials are the only backend gates. Iron bar smelting is the only source-backed random smelt action: after a valid action starts it consumes `Iron ore`, then either produces `Iron bar` and XP or records a `smelt_fail` telemetry failure with no output/XP. Other smelt bars and forge rows stay deterministic unless a source audit proves another post-start failure.
- Gathering tool progression is starting with a hybrid model: source tool items remain ordinary registered items for future acquisition/trading, but review logic can also resolve bound toolbelt IDs. Existing saves get a bound Bronze hatchet so introducing tool requirements does not brick Woodcutting. Reuse this for Mining pickaxes if the pattern holds.
- The hybrid toolbelt pattern now covers Mining too. Toolbelt remains tools-only (`bronze_hatchet`, `bronze_pickaxe`, etc.). Passive/equipable bonuses live outside toolbelt in `player_data["equipment"]`; Mining bonus logic reads the worn `neck`/`body` slots rather than passive ownership.
- Reusable tools are not automatically visible just because the source action has one. Fishing deliberately keeps rods, nets, cages, pots, vessels, and harpoons implicit in labels, tooltips, gating, and assets. Visible progression remains limited to Woodcutting hatchets and Mining pickaxes unless a future design explicitly promotes another tool family.
- Equipment has backend and Qt surfaces. `equipment_data.py` is generated from checked-in Smithing data plus local 2011Scape `items.yml`; storage keeps a flat `equipment` mapping (slot -> item name); pure helpers own gate/swap/stat-total rules; runtime callbacks feed a dedicated Equipment tab with right-click Equip/Unequip. Attack, Strength, Defence, Constitution, Ranged, and Magic levels are trainable partial skills through unified Combat even though they do not yet own complete review surfaces.
- Live item acquisition is audited as a graph by `tools/audit_item_reachability.py`. Seed only authentic live sources, close over action/item transformations, and report missing consumed inputs as roots or cascades. This audit measures route existence, not source fidelity; never silence an orphan by inventing a recipe or free seed.
- Combat death/reclaim state stays flat and review-transaction friendly. `combat_grave.items` is the active five-safe-review recovery list, while `death_office.items` holds gear collapsed out of the active grave path, such as a second Combat death before recovery. Death's Office reclaim consumes Coins and returns gear to inventory through a pure helper plus Bank-tab callback, so Anki undo can still roll the whole review transaction back by restoring `player_data`.
- Combat bank runs are target-scoped supply-recovery state. If `combat_bank_run.target_id` no longer matches the current Combat target, reset the run before deciding whether the new target needs its own two-review bank trip; never complete an old run against a different enemy. Bank-run supply decisions must use the same enemy table being simulated so quest/injected enemies with poison can load antipoison correctly.
- Quest combat reuses the ordinary burst engine but must not leak quest target ids into ordinary Combat progression. Keep ordinary `combat_kill_counts` scoped to selectable Combat targets; restore the pre-quest ordinary encounter after partial/kill quest bursts, but let quest-combat death clear ordinary encounter state because the shared death path has killed the player.
- Source game tick odds should not be copied directly into review odds. Probabilistic review skills preserve audited source chance data, then pass the source roll chance through the shared `normalize_review_success_probability_pure` adapter so one Anki review action remains the pacing unit. Firemaking can still apply its separate target-tier cap because source Firemaking odds mostly vary by player level rather than log tier.
- Item tradability is now explicit in `ItemDefinition.tradeable`, seeded from source data for Mining additions. Do not infer GE eligibility from category alone; future economy work should consult item metadata and document source anomalies (for example Dragon pickaxe 15259/15261 and Varrock armour 4).
- `food` is now a first-class item category for cooked/prepared/burnt Cooking items. Burnt Cooking items are intentionally registered as non-tradeable junk in this fork even though RuneScape player-to-player tradability is historically weird, because future AnkiScape GE/trading will not distinguish marketing from trading.
- Random no-XP Utility actions can need special pure helpers. `Open bird nests` is the first example: it is a Utility/Activities action, but it consumes any known nest subtype and rolls source contents instead of using a fixed `requirements -> output_item` recipe.
- Review rewards are paired with Anki undo via `gui_hooks.state_did_undo`. When an eligible answer changes game state, the runtime records the original values for only the changed `player_data` keys; undo restores those values and saves config so Command-Z does not leave XP/items ahead of the card schedule.
- Review pacing is now an integer **actions-per-review** multiplier, not an XP-only scalar. Runtime reads `ankiscape_review_action_multiplier` (falling back to the old `ankiscape_xp_multiplier` key), executes up to N normal action ticks inside one eligible review, aggregates floating feedback, and records one undo snapshot for the whole review. Gathering skills spend N independent probability rolls; processing and Utility/Activities stop cleanly when materials run out before an extra sub-action.
- Every started review action should record durable telemetry in `player_data["action_telemetry"]`. The stable row key is `skill_id:action_id`; rows track attempts, successes, failures, expected successes, dry streaks, output counts, and failure kinds. Blocked actions such as missing materials or insufficient level do not count as attempts, but dry RNG outcomes, Cooking burns, and iron smelt failures do save telemetry.

## Architectural Pressure
Adding many skills by copying the current pattern would increase duplication in:
- skill selection UI
- stats rendering
- storage defaults and migrations
- answer dispatch
- icon/image registration
- tests

The current P0 architecture board now has backend modules for skill, item, review-action, runtime-handler, target-row, grouped target-tree, and achievement metadata. Remaining architecture pressure is lower-priority and mostly around stats rendering, icon/image registration, tests, and the large Anki/menu orchestration surface in `__init__.py` / `ui.py`.

## Skill Expansion Workflow
Use the project skill at `.codex/skills/ankiscape-skill-expansion/SKILL.md` before adding or expanding any skill, Utility/Activity, target chain, item economy slice, or achievement set. It encodes the repeatable workflow: source audit first, playable scope cut, registry/item data, asset scraping, pure mechanics, UI surfacing, achievement patterns, tests, manual Anki checks, and memory updates.

## Compatibility Pattern
Persisted Anki config is the stable boundary. Schema changes should go through `storage_pure.py` migrations and keep existing user data intact.

Source-complete data can be broader than a live catalog. Herblore keeps Daemonheim rows in explicit `DUNGEONEERING_*` tuples so item identities and historical transcription survive, while its ordinary exported targets filter them out until a session-scoped Dungeoneering product contract exists. When a live target is removed this way, migrate the saved selection to the skill default but preserve inventory keys and quantities.

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

`cadence_live.py` is the only runtime admission resolver. A rate-limited route
owns one `cadence_profiles[profile_id]` residual; the active target alone
advances it, waits persist residuals and cadence-wait telemetry without an
attempt, and the outer review snapshot makes admission and reward undo-atomic.
Source rates above `R = 1000` must declare `CAP_ONE_ACTION`; never round a
rational rate or compensate by changing base XP. Embedded-probability routes
receive one authentic attempt with no second gate. Source-blocked routes retain
their existing handler unit until a compatible row is proven.

Combat consumes `6 × M` immediate ticks per successful card and persists the
same encounter across cards. Again advances world consumers only and marks an
active encounter disengaged for safe automation without granting either side a
combat beat. Kill, death, flee, and bank boundaries stop the current review.
Finite quest combat is deliberately exempt: live mode resolves one collapsed
quest stage, while an explicit cadence rollback retains the legacy 50-tick
quest-combat burst.

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

Failure state that must consume exactly one outer review returns `False` from
the handler after mutation. That stops review multipliers from clearing a stun
or repeating damage in the same card. The next review clears the persisted stun
and also returns `False`. Skills whose failures use shared combat LP must be
excluded from post-review safe combat recovery, or the integration layer will
silently heal away the failure stake.

## Public derivative release pattern

GitHub fork metadata is not package-level attribution. Any public AnkiScape
release must carry its own original-creator credit, explicit compatible license,
source links, derivative-maintainer identity, and distinct AnkiWeb listing. Do
not reuse Wilson's item `1808450369`, and do not leave the in-product review
link pointing at his listing. Public source must match the exact release
candidate rather than a stale fork snapshot.

Code lineage and asset redistribution are separate gates. The working
AGPL-3.0 basis from AnkiWeb does not close the repository's missing explicit
license, Wilson acknowledgement, or the provenance of RuneScape-derived assets.
Follow
`memory-bank/public-release-lineage-and-license-2026-07-17.md` in order and
stop before upload if any rights, attribution, asset, packaging, or real-profile
verification gate remains open.

## UI Gotcha: nested-closure name collisions in `show_main_menu`
`show_main_menu` is a very large function that defines many nested helpers (one per tab/section). All of these are locals of the *same* scope, so two sections defining a helper with the same name (e.g. `_select_skill`) silently rebind it — the later definition wins, and earlier callers route into the wrong function with no error. This caused the Skills-hub panel to ignore clicks (the Stats tab's `_select_skill` shadowed the hub's). Mitigation: prefix section-scoped helpers with their section (`_select_hub_skill`, etc.), and prefer the offscreen Qt behavior test to catch misrouted handlers. Longer term, splitting these sections into their own builder functions/classes would remove the shared scope entirely.

## Main-menu deferred tabs (`ui_menu_ctx.py`, `ui_tab_*.py`)

Opening the menu used to cost ~1.2 s on a real save because every tab was built
up front. The three expensive surfaces now build on first show: `ui_tab_shop.py`,
`ui_tab_quests.py` and `ui_tab_achievements.py` export a
`build_<name>_tab(ctx) -> QWidget`, and `show_main_menu` inserts an empty
placeholder page per tab and fills it from a `QTabWidget.currentChanged` hook.
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
- Skills, Bank and Equipment stay inline. They are ~3% of the open cost and are
  mutually recursive through `_refresh_equipment_views`, so splitting them buys
  nothing and pays the whole coupling bill.

Related: `shop_logic.shop_view_models_pure` exists because
`ensure_shop_state_pure` deep-copies the entire save, and the browse list needs
a view model per shop — one snapshot for the batch instead of ~270 copies.

## UI Gotcha: nested hook callbacks are not removable by a fresh closure

`injectors.register_deck_browser_button()` may run more than once during profile/setup flows. Its callbacks are nested functions, so recreating them and calling `hook.remove(new_callback)` does not remove the prior function object. Register these callbacks through the stable AnkiScape hook-key replacement helper; otherwise one browser message is dispatched once per surviving registration before the menu-open guard can observe the first scheduled dialog.

## UI Gotcha: dark-mode text colors (`palette(mid)` is NOT a text role)
Recurring bug: greyed/disabled/placeholder text rendered with `palette(mid)` / `QPalette.Mid` becomes **invisible in dark mode**, because `mid` is a frame/border role that resolves to a near-black grey. It has bitten the Skills-hub train button, the Smithing locked rows, and the Equipment empty slots. Fix at the root: `ui.dim_text_color(widget)` (for `setForeground`) and `ui.dim_text_css(widget)` (for stylesheet `color:`), which derive the color from the theme's real `Text` role and drop the alpha so contrast holds in both themes. `palette(mid)` is fine for borders only. Also prefer `palette(text)`/`palette(base)` over `buttonText`/`button` for button labels (the button face renders light on macOS dark mode). Enforced going forward by `.cursor/rules/qt-dark-mode-text.mdc` and the regression test `test_empty_slot_text_is_dark_mode_safe_not_palette_mid`. When changing UI colors, verify in dark mode, not just light.

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
