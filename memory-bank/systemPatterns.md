# System Patterns

## Architecture Snapshot
The add-on is a small Python package loaded by Anki. It separates pure game contracts from Anki-aware orchestration for review dispatch, runtime actions, target rows, and achievements, though some skill behavior still lives in UI, storage, stats, and icon-registration surfaces.

## Important Modules
- `__init__.py`: runtime orchestration, global player state, review hooks, answer handling, menu callbacks, save/HUD/UI bridge callbacks, and compatibility review-action wrappers.
- `runtime_actions.py`: Anki-free runtime review-action handlers and handler-keyed can-start checks for Mining, Woodcutting, Fishing, Hunter, Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Quests, and Utility/Activities. It mutates `player_data` through a callback/context contract supplied by `__init__.py`.
- `constants.py`: item data, skill source data, image paths, XP table, and compatibility exports.
- `logic_pure.py`: pure helpers for XP/level math, probabilities, crafting, Utility/Activities, mining, woodcutting, fishing, hunter, smithing, quests, claims, and runecrafting operations.
- `logic.py`: Anki-aware level-up and achievement checks plus probability wrappers.
- `storage.py`: Anki config persistence.
- `storage_pure.py`: default player shape and migrations.
- `skill_registry.py`: pure skill catalog for current and planned skills, including stable IDs, categories, save keys, and review eligibility.
- `action_registry.py`: pure review-action dispatch metadata. It resolves levelled skills and no-XP Utility/Activities to handler keys without adding Utility as a fake skill.
- `target_metadata.py`: pure target-row metadata for the Skills hub. It builds labels, tooltips, icon paths, enabled/current state, groups, sort order, and lock reasons for Mining, Woodcutting, Fletching, Firemaking, Fishing, Hunter, Smithing, Crafting, Cooking, Runecrafting, and Utility/Activities without creating Qt widgets.
- `achievement_metadata.py`: pure achievement definitions, difficulty order, grouped row view models, and progress-count helpers while preserving the legacy completed-achievement name contract.
- `hunter_data.py`: source-backed Hunter target data. It uses 2011.rs guide rows for levels/XP/rewards, local 2011Scape cache item names/ids for storage keys, and local 2012scape/Darkan Hunter code only as mechanics/id parity because the local 2011Scape checkout has no Hunter mechanics plugin.
- `item_registry.py`: pure item manifest helpers for current economy items, including stable IDs, storage keys, categories, assets, and source/license notes.
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
- Skills-hub target lists now consume `target_metadata.TargetRowMetadata` rows. The Qt layer uses one shared `QListWidget` renderer for Mining, Woodcutting, Fletching, Firemaking, Fishing, and the flat list cases, plus one shared grouped `QTreeWidget` renderer for Smithing, Crafting, Cooking, Runecrafting, and Hunter. The pure row metadata owns labels, tooltips, icon paths, group ids, sort keys, current state, enabled state, and lock reasons; Qt only renders rows, persists group expansion where applicable, and guards disabled-row clicks.
- Achievement definitions now live behind `achievement_metadata.py`. `constants.ACHIEVEMENTS` stays as a legacy export for `logic.py`, old tests, and any add-on code that reads the dict shape, while UI code consumes row/progress helpers instead of reconstructing grouped achievement state.
- Fletching is the first staged expansion skill to complete backend + target-panel rollout. It uses stable recipe IDs for save/UI selection, because multiple recipes can produce the same inventory item (for example, several log tiers all output arrow shafts).
- Fletching material-only inputs such as feathers and arrowtips are registered as item-manifest `material` entries. Arrowtips are sourced through Smithing, and feathers have a temporary no-XP Utility bridge (`scavenge_chicken_feathers`) until Combat chicken drops and/or GE exist.
- Utility/Activities are backend actions, not skills. They use stable activity IDs in `UTILITY_ACTIVITY_DATA`, mutate inventory through pure helpers, award zero skill XP, and can batch up to an inventory-sized cap when they represent fast material preparation.
- Utility/Activities can also represent one-shot acquisition bridges while the full shop/GE interface is deferred. These activities declare an `outputs` mapping instead of a single `output_item`, can set `deactivate_after_run = True`, and the runtime switches AnkiScape off after the successful review so the action multiplier cannot repeat the purchase inside the same card.
- Utility/Activities should stay outside `skill_registry.py` unless they gain real level/XP semantics. Runtime dispatch handles them through `action_registry.py` and the handler key `utility`, while the UI may still surface them as a synthetic Skills-hub category.
- Utility/Activities now have a small row-icon contract: each existing `UTILITY_ACTIVITY_DATA` entry can expose an `icon_path` pointing at a dedicated `activityicons/<activity>.png` asset. The Qt target list prefers that activity-level icon and falls back to the old output-item image map if the path is missing. This keeps no-XP activity presentation first-class without adding Utility to the skill registry or changing reward logic.
- Crafting recipe data stores source XP only. Runtime reward handling awards base XP per action tick; review pacing is controlled by the actions-per-review multiplier rather than by inflating a single action's XP.
- Crafting now follows the source-data-module pattern at the backend layer (`crafting_data.py`). `current_craft` stores stable recipe IDs, inventory stores real item names, and the data intentionally includes live input-starved recipes so missing acquisition loops light up later without reshaping the recipe. XP-bearing Crafting ignores recipe `batch_size`; only no-XP Utility/Activities batch material prep.
- Woodcutting now has a focused source-data module (`woodcutting_data.py`) rather than only ad hoc `constants.py` rows. Its stable target IDs are persisted in `current_tree`, while inventory uses real item output names such as `Logs` and `Oak logs`.
- Fishing now follows the source-data-module pattern (`fishing_data.py`) as a Gathering skill. Its stable method IDs are persisted in `current_fishing`, while inventory uses real output item names such as `Raw crayfish`, `Raw salmon`, and `Raw shark`. Mixed-output rows preserve source order during rolls, consumable material is removed only after a successful catch, and Barbarian fish side XP updates hidden Strength/Agility state without exposing those skills in the UI yet.
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
- Hunter separates reusable gear from consumables. `requirements` are deleted only on successful catches; `tools` are bank/inventory gates that remain after a catch. Current reusable gates cover bird snares, box traps, butterfly nets for butterfly/Puro-Puro rows, and small fishing net plus rope for tree-net rows. The temporary `Buy Hunter supplies` Utility bridge spends `500 Coins` for a source-backed starter/restock bundle, then turns itself off after one review. A richer shop interface remains a later economy/UI pass.
- The broad quest catalog is generated, not hand-maintained. `tools/build_pre_eoc_quest_catalog.py` produces a 194-row pre-EOC catalog by real release order, with Recipe for Disaster split into separate subquests. Each row should carry source oldids, strict prerequisites, point/XP/item rewards, lamp rewards, and source-backed journal stages. Hand-audited overrides belong in `quest_data.py` when local 2011-era evidence is stricter than current wiki data.
- Quest starts are strict. A quest with incomplete prerequisite quests or unimplemented required skills must be impossible to start. Completion XP for implemented skills is granted immediately; XP for unimplemented skills is stored in `pending_skill_exp_rewards` and applied by migration when the skill becomes implemented.
- Quest-list availability should flow through `quest_availability_state_pure()`, not ad hoc UI checks. Its states are `can_start`, `in_progress`, `completed`, and `locked`; already-started quests remain `in_progress` because mid-quest skill/action blockers are not modeled yet. Add a stage-aware quest requirement layer before trying to represent "can start but cannot finish" cases.
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
- Utility/Activities can now be grouped by `group` metadata in the Qt tree when an action family gets large. Cooking prep uses this to separate gathering, material processing, container/opening, and Cooking prep actions while staying outside the XP skill registry.
- Mining now follows the same source-data-module pattern (`mining_data.py`). Its stable target IDs are persisted in `current_ore`, while inventory continues to use real item output names such as `Iron ore`, `Pure essence`, `Sandstone (10kg)`, and `Uncut opal`.
- Smithing now follows the source-data-module pattern too (`smithing_data.py`). It is the first skill with two XP-bearing stations under one skill: smelt and forge are both recipes in `SMITHING_DATA`, selected by stable `current_smith` IDs, while `BAR_DATA` is only a compatibility view for old smelt-only UI paths. Runtime uses one pure processing helper for both stations and keeps hammer/tool requirements implicit; level and inventory materials are the only backend gates. Iron bar smelting is the only source-backed random smelt action: after a valid action starts it consumes `Iron ore`, then either produces `Iron bar` and XP or records a `smelt_fail` telemetry failure with no output/XP. Other smelt bars and forge rows stay deterministic unless a source audit proves another post-start failure.
- Gathering tool progression is starting with a hybrid model: source tool items remain ordinary registered items for future acquisition/trading, but review logic can also resolve bound toolbelt IDs. Existing saves get a bound Bronze hatchet so introducing tool requirements does not brick Woodcutting. Reuse this for Mining pickaxes if the pattern holds.
- The hybrid toolbelt pattern now covers Mining too. Toolbelt remains tools-only (`bronze_hatchet`, `bronze_pickaxe`, etc.). Passive/equipable bonuses live outside toolbelt in `player_data["equipment"]`; Mining bonus logic reads the worn `neck`/`body` slots rather than passive ownership.
- Reusable tools are not automatically visible just because the source action has one. Fishing deliberately keeps rods, nets, cages, pots, vessels, and harpoons implicit in labels, tooltips, gating, and assets. Visible progression remains limited to Woodcutting hatchets and Mining pickaxes unless a future design explicitly promotes another tool family.
- Equipment now has both backend and Qt surfaces. `equipment_data.py` is generated from checked-in Smithing data plus local 2011Scape `items.yml`; storage keeps a flat `equipment` mapping (slot -> item name); pure helpers own gate/swap/stat-total rules; runtime callbacks feed a dedicated Equipment tab with right-click Equip/Unequip. Combat gates are real `*_level` checks even though combat training is not implemented yet.
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
Use the project skill at `.cursor/skills/ankiscape-skill-expansion/SKILL.md` before adding or expanding any skill, Utility/Activity, target chain, item economy slice, or achievement set. It encodes the repeatable workflow: source audit first, playable scope cut, registry/item data, asset scraping, pure mechanics, UI surfacing, achievement patterns, tests, manual Anki checks, and memory updates.

## Compatibility Pattern
Persisted Anki config is the stable boundary. Schema changes should go through `storage_pure.py` migrations and keep existing user data intact.

Review-answer side effects must follow Anki's undo semantics. If a future skill mutates new `player_data` keys during an answer, the generic snapshot diff should catch them; if a future system writes outside `player_data`, it needs its own undo-aware rollback path.

## UI Gotcha: nested-closure name collisions in `show_main_menu`
`show_main_menu` is a very large function that defines many nested helpers (one per tab/section). All of these are locals of the *same* scope, so two sections defining a helper with the same name (e.g. `_select_skill`) silently rebind it — the later definition wins, and earlier callers route into the wrong function with no error. This caused the Skills-hub panel to ignore clicks (the Stats tab's `_select_skill` shadowed the hub's). Mitigation: prefix section-scoped helpers with their section (`_select_hub_skill`, etc.), and prefer the offscreen Qt behavior test to catch misrouted handlers. Longer term, splitting these sections into their own builder functions/classes would remove the shared scope entirely.

## UI Gotcha: dark-mode text colors (`palette(mid)` is NOT a text role)
Recurring bug: greyed/disabled/placeholder text rendered with `palette(mid)` / `QPalette.Mid` becomes **invisible in dark mode**, because `mid` is a frame/border role that resolves to a near-black grey. It has bitten the Skills-hub train button, the Smithing locked rows, and the Equipment empty slots. Fix at the root: `ui.dim_text_color(widget)` (for `setForeground`) and `ui.dim_text_css(widget)` (for stylesheet `color:`), which derive the color from the theme's real `Text` role and drop the alpha so contrast holds in both themes. `palette(mid)` is fine for borders only. Also prefer `palette(text)`/`palette(base)` over `buttonText`/`button` for button labels (the button face renders light on macOS dark mode). Enforced going forward by `.cursor/rules/qt-dark-mode-text.mdc` and the regression test `test_empty_slot_text_is_dark_mode_safe_not_palette_mid`. When changing UI colors, verify in dark mode, not just light.
