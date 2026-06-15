# Active Context

## Current Focus
Protect the local fork before any large expansion. The agreed direction is to augment the existing add-on, not rebuild it first.

## Equipment backend contract
The backend equipment pass is complete. `tools/generate_equipment_data.py`
joins checked-in Smithing recipe metadata, local 2011Scape `items.yml`
equipment blocks, and Mining bonus item data into generated `equipment_data.py`.
That module exposes 11 ordered slots, 117 unique equippable items, real combat
requirements, two-handed flags, attack speed, and full combat bonus blocks.

`player_data["equipment"]` is now the single worn-equipment source of truth
(slot -> item name). Storage config version is 10, planned combat level/exp keys
are scaffolded with authentic defaults (combat levels 1; Constitution 10), and
legacy `owned_equipment` is removed during migration. Mining bonuses now read
from worn slots: glory in `neck`, Varrock armour in `body`.

The original frontend handoff for Equipment is complete: the UI now has a
dedicated Equipment tab, right-click Equip/Unequip in the Bank/Equipment views,
slot icons, and compact bonus/requirement tooltips. The backend callbacks are
`on_equip_item(item_name)` and `on_unequip_slot(slot)`; pure helpers are
documented in `memory-bank/equipment-combat-contract-design.md`.

The equipment **frontend** pass is now complete. `ui.show_main_menu` gained a
dedicated **Equipment tab** that always renders all 11 `EQUIPMENT_SLOTS` (greyed
"(empty)" placeholder + OSRS slot icon when empty; item name + icon when filled)
plus a summed **stat-totals** panel driven by `equipment_stat_totals_pure`.
Right-click **Equip** is offered on equippable Bank inventory rows (enabled only
when `can_equip_item_pure` passes; otherwise a disabled action carrying the lock
reason, e.g. "Equip (Requires level 40 Defense)"), and right-click **Unequip** on
filled Equipment slots. Both route through the new `on_equip_item` /
`on_unequip_slot` callbacks (bridged in `__init__`) and then call a shared
`_refresh_equipment_views` so the Bank inventory and Equipment tab repaint in
place — no dialog rebuild. Equippable inventory rows and worn slots carry a
multi-line bonus + requirement tooltip (`equipment_full_tooltip`). The Bank gear
strip is now **toolbelt-only**: the old "Equipped"/"Nothing equipped yet."
placeholder was dropped in favor of the tab. Combat-skill vocabulary in the UI
deliberately matches the backend lock-reason wording ("Defense", not "Defence")
so the tooltip and the menu speak with one voice. Slot art is fetched by
`tools/fetch_equipment_assets.py` into `equipment_slots/<slot_id>.png` (11/11,
provenance recorded; ammunition resolves from the wiki's `Ammo slot.png`); rows
degrade to text-only if a file is missing. Twelve offscreen Qt tests in
`tests/test_main_menu_widget.py` cover all-slots render + placeholder icons,
bronze enabled Equip, rune disabled Equip + reason, equip moving item into slot,
unequip returning to inventory, empty-slot no-menu, 2h clearing the shield,
summed stat totals, and the equippable-row bonus tooltip. The test seam exposes
`dialog._ankiscape_equip_menu_for` / `_ankiscape_unequip_menu_for` so the menus
are asserted without a native popup.

## Recent Decision
The next meaningful engineering step should be a skill-registry refactor. That refactor should preserve the current four skills while making future skills cheaper and safer to add.

The add-on folder has been renamed from the AnkiWeb ID `1808450369` to `ankiscape_fork` so public AnkiWeb updates do not overwrite local work.

Backend registry implementation has started on `main` in a local git repository. The first backend pass adds pure skill and item registry modules, keeps existing flat save keys for safety, and wires review eligibility/level-up/storage defaults through registry metadata without changing the visible UI.

Asset-fetch tooling now exists as a standalone developer CLI at `tools/fetch_assets.py`. It is not imported by the add-on runtime. It resolves one item icon at a time from the official RuneScape wikis, prefers OSRS with RS3 fallback, supports registry-key path resolution, normalizes PNG output when fetching, and records provenance.

Fletching is now playable in the Skills hub and has had its first data-accuracy hardening pass. The target list uses stable recipe keys, includes tiered arrow-shaft yields, headless arrows, metal arrows through rune, and unstrung shortbows. Fletching output/material icons live under `fletcheditems/` and are recorded in `assets_provenance.json`.

Review-answer XP/items now respect Anki undo. The runtime records changed `player_data` keys for each successful review reward and restores them when Anki emits `state_did_undo`, fixing the Command-Z case where the card was undone but XP remained.

A project-local Cursor skill now exists at `.cursor/skills/ankiscape-skill-expansion/`. Use it before any future skill/action expansion so source audit, assets, target items, Utility/Activities, achievements, tests, and memory updates happen consistently instead of being rediscovered each time.

Crafting/Utility backend rework is now complete. `Soft clay` is no longer a Crafting XP target; no-XP Utility/Activities handle `Clay -> Soft clay` in batches up to 28. The audited Crafting pilot now includes pottery shaping/firing, wool spinning, bowstring spinning, and silver bolts (unf). Source XP is preserved in recipe data; pacing now comes from the review action multiplier rather than scaling XP after a single action.
Crafting 2011Scape **backend parity foundation** is now complete. Legacy inline `constants.CRAFTING_DATA` has been replaced by source-backed `crafting_data.py` with stable recipe IDs in `current_craft`, real output item names in inventory, corrected 2011Scape values (Emerald cut 67.0 XP; Sapphire necklace 55.0 XP), and live input-starved targets for dragonstone/onyx, hides, glass, battlestaves, selected urns, and other dependency-heavy rows. XP-bearing Crafting now always runs one action per review; 28x batching is reserved for no-XP Utility/Activities. Storage config version is 11 and migrates legacy display-name Crafting targets through `LEGACY_CRAFTING_TARGETS`; `Soft clay` still migrates to `current_utility = make_soft_clay`. Minimal Qt compatibility was included so Crafting rows render `display_name` while storing stable IDs; full grouped Crafting frontend polish remains a frontend handoff.


Crafting 2011Scape **frontend grouping + assets** pass is now complete.
`_build_craft_list` was rebuilt from a flat `QListWidget` into a `QTreeWidget`
grouped by `CraftingRecipe.family` (Gem cutting → Combinations), mirroring the
Smithing metal-tier pattern: each family is a collapsible parent, children render
`display_name` + level (+ `— makes N` when `output_qty > 1`), store the stable
recipe ID on `UserRole`, and persist via the existing `on_set_craft`
(== `current_craft`). Families are collapsed by default with per-family
expand/collapse persisted in Anki config (`ankiscape_craft_expanded_families`
via `craft_expanded_families` / `set_craft_family_expanded`, mw-guarded for
headless tests); the family holding the current target is force-expanded.
Tooltips show output item/qty, base XP, and per-material owned counts; lock
reasons come straight from `can_craft_item_pure` (level/materials only).

**Dependency-heavy targets are wired identically to every other target** —
dragonstone/onyx cuts + jewellery, dragonhide bodies, glassblowing, battlestaves
are NOT hidden, NOT tagged, and carry no distinct visual/semantic state. They are
simply, emergently un-runnable because the player holds 0 of a material whose
acquisition route doesn't exist yet — the exact same state as a Sapphire ring
with 0 sapphires. An earlier attempt added an inline "— input-starved" tag plus
an `INPUT_STARVED_RECIPE_IDS` structured flag; both were **removed** at the
maintainer's direction (the inertness must be implicit, never labelled). The
skill MD's live-content non-negotiable was rewritten to make this explicit so it
isn't re-litigated.

**Disabled-row click bug fixed across all target builders.** Qt fires
`itemClicked` even on disabled rows (the enabled flag gates *selection*, not the
click signal), so clicking a greyed/locked target used to set it active and then
fail the next review with "you don't have X". Every selection handler
(`_on_ore_selected`, `_on_tree_selected`, `_on_smith_clicked`, `_on_craft_clicked`,
`_on_fletch_selected`, `_on_utility_selected`) now ignores disabled rows
(`item.isDisabled()` for trees / `flags() & ItemIsEnabled` for lists).

**Assets:** `tools/fetch_crafting_assets.py` derives its manifest from
`CRAFTING_DATA` (all outputs + crafting-specific raw materials; cross-skill
ores/gems/bars/logs are skipped since the registry resolves those from their own
folders) and fills `crafteditems/`. Intermediate pottery/urn states and unstrung
amulets use `WIKI_TITLE_OVERRIDES`. `constants` now wires `CRAFTED_ITEM_IMAGES`
for both outputs **and** input materials (existence-guarded) so the Bank shows
material icons too. Legacy CamelCase `crafteditems/*.png` files still resolve on
macOS's case-insensitive FS; the fetcher writes lowercase `_asset_slug` names.

Qt tests cover family grouping, stable recipe IDs (incl. the colliding
"Dragonstone ammy" rows), level-ordering, dependency-heavy targets being wired
like any other (present, untagged, material-gated only), owned-count tooltips,
`on_set_craft` persistence, family-node click-inertness, current-target
auto-expand, and the disabled-row click guard on both the Crafting and Smithing
trees.

Woodcutting 2011Scape **frontend/assets** pass is complete. The Skills-hub tree list now renders stable target IDs as friendly display names + level, shows output/base-XP/best-usable-hatchet in tooltips, distinguishes level vs "no usable hatchet" lock reasons (via `can_chop_woodcutting_target_pure` + `best_woodcutting_axe_pure` over `player_data["toolbelt"]`), and flags Ivy inline as "— XP only" (no logs). `Open bird nests` is surfaced as a visible no-XP Utility/Activities row, locked until a nest is held (`can_open_bird_nests_pure`). The legacy `show_stats`/`show_tree_selection_dialog` were de-landmined for the ID schema, and fetched log/hatchet/nest sprites are wired through `LOG_IMAGES` / `WOODCUTTING_EXTRA_ITEM_IMAGES` with graceful gaps only for rare unresolved egg assets.

Depletion handling for processing skills: when a Crafting target or Utility activity runs out of its required materials, the runtime now names the *specific* missing item (e.g. "Pot" reports a missing "Unfired pot", not the Soft clay the player has plenty of) and switches the active skill off (`current_skill -> "None"`) via `_deactivate_current_skill`, instead of re-raising the same error on every card. The player re-picks a target from the menu to resume. Error dialogs also force the style's standard warning glyph so macOS stops substituting the host app's "folder" icon.

The Crafting/Utility **frontend** pass is now also complete. Utility/Activities is surfaced as a synthetic, visually-distinct Skills-hub category (it is deliberately *not* a registry XP skill — no level/exp keys — and is routed through `_UTILITY_SKILL_NAMES` + `current_utility`). Its target list shows batch + "no Crafting XP" tooltips and persists the active activity via a new `on_set_utility` callback bridged in `__init__`. Crafting tooltips now show output qty / batch size; Soft clay no longer appears as a craft target. The review HUD recognizes the active Utility activity and states it earns no XP. Settings are reorganized into Gameplay / Notifications / Floating Widget / Developer, with a clamped Actions-per-review spin under Gameplay writing `ankiscape_review_action_multiplier`.

Woodcutting backend parity is now complete. Source data lives in `woodcutting_data.py` and is audited against local 2011Scape rev 667 source. Woodcutting now uses stable target IDs (`tree`, `oak`, `ivy`, etc.), real output item keys (`Logs`, `Oak logs`, `Bark`), source-shaped Anki-tuned chop probabilities, hybrid tool resolution from bound toolbelt IDs plus owned hatchet items, and rare bird nest subtype drops. Existing saves migrate legacy target names and tree-named inventory keys into the new shape; Redwood is removed as OSRS-only content. `Open bird nests` is a no-XP Utility/Activities backend action that opens up to 28 source nests into inert seed/ring/egg contents for future systems.

Mining 2011Scape **frontend** pass is now complete. The Skills-hub ore list (`_build_ore_list`) mirrors the Woodcutting tree-list pattern: rows render stable target IDs as friendly `display_name` + level with the ID on `UserRole`, tooltips show output / base XP / best-usable-pickaxe / source, and lock reasons split level vs "no usable pickaxe" via `can_mine_target_pure` + `best_mining_pickaxe_pure` over `player_data["toolbelt"]`. Variable-output rocks (Sandstone, Granite, Gem rocks) are flagged `— variable output` inline and list their weighted items in tooltips; essence shows `— Pure essence at Lvl 30+`. Coal/Gold tooltips note that the `concentrated` deposits are deliberately deferred. Mining bonus gear now flows through the general Equipment tab and worn `player_data["equipment"]` slots, not a backend-only passive collection. Bank/Stats are registry-driven on real item names, and the legacy `show_ore_selection_dialog` icon fallback was de-landmined for output-less rocks. Eight offscreen Qt tests cover Mining rows in `tests/test_main_menu_widget.py`.

The Mining **assets** pass is now complete. `tools/fetch_mining_assets.py` batch-fetches (via the shared rate-limited `tools/fetch_assets.py` client + provenance) the parity ore art (Pure essence, Blurite ore, Limestone, Sandstone 1/2/5/10kg, Granite 500g/2kg/5kg into `ores/`), the gem-rock gems (Uncut opal/jade/red topaz into `gems/`), and the standard pickaxe tiers (Bronze→Dragon into a new `miningitems/`). Gilded pickaxes are intentionally skipped (cosmetic, don't resolve cleanly, share base-tier behavior). Wiring: `GEM_IMAGES` gained opal/jade/red topaz (existence-guarded); `MINING_EXTRA_ITEM_IMAGES` now also resolves tools from `miningitems/` by `_asset_slug`; the `_build_ore_list` row-icon lookup falls back ORE_IMAGES→GEM_IMAGES so variable rocks show their first weighted output (Gem rocks→Uncut opal). One landmine fixed: `build_item_definitions` resolved weighted gem outputs from the `ore_images` map (and `seen_storage_keys` blocked the later override), so the `ITEM_DEFINITIONS` call now passes a merged `{**ORE_IMAGES, **GEM_IMAGES}` for ore art. Asset-path tests live in `tests/test_skill_and_item_registry.py`.

Mining backend parity is now complete. Source data lives in `mining_data.py`: stable target IDs (`rune_essence`, `iron`, `gem_rocks`, etc.), real output item keys, source low/high Mining chances, respawn-time data, pickaxe metadata, weighted sandstone/granite/gem-rock outputs, incidental gem drops, and Mining bonus metadata that now resolves through worn Equipment slots. Storage config version is 8 and migrates legacy display-name `current_ore` values while preserving existing inventory item names. The item manifest records `tradeable` plus minimal equipable metadata; Mining-specific non-tradable decisions include Blurite ore, Inferno adze, and Varrock armour. Dragon pickaxe is normalized to item 15261 because local `PickaxeType.kt` references 15259 but `items.yml` marks 15261 as the tradeable "Used for mining" item.

Review pacing has been reworked from an XP-only multiplier to a time/action multiplier. The Settings UI now exposes an integer `Actions per review` spinner (1x-10x) backed by `ankiscape_review_action_multiplier`; runtime falls back to the legacy `ankiscape_xp_multiplier` config only to preserve existing user settings. A successful review now runs up to N normal action ticks inside one undo-aware review transaction, so XP increases because more actions run, alongside item outputs, material consumption, gathering failures, gems/nests, and Utility batches. Floating XP/activity feedback is aggregated once per review, and processing/Utility stop silently when materials are depleted after a productive sub-action.

Smithing 2011Scape backend parity is now complete. Source data lives in `smithing_data.py`, generated by `tools/generate_smithing_data.py` from local 2011Scape `SmeltingData.kt`, `BarType.kt`, `SmithingType.kt`, `BarProducts.kt`, `Items.kt`, and `items.yml`. `SMITHING_DATA` is a unified recipe table for all 9 smelt bars plus 157 forge rows; `BAR_DATA` remains a smelt-only compatibility view. Runtime uses `current_smith` stable recipe IDs, storage config version is 9, and legacy `current_bar` plus `Adamantite bar`/`Runite bar` inventory names migrate to source-shaped targets/items. No hammer/toolbelt gate was added; Smithing gates only on level and materials.

Smithing 2011Scape **frontend + assets** pass is now complete. The Skills-hub Smithing panel (`_build_smith_list`) replaces the old smelt-only `_build_bar_list` and is fully `SMITHING_DATA`-driven. Because the unified table is ~166 recipes, the panel is a **`QTreeWidget` grouped by metal type** (Bronze → Rune): each tier is a collapsible parent holding its smelt bar first, then the forge items made from it. Groups are **collapsed by default** and the per-tier expand/collapse state persists across sessions in Anki config (`ankiscape_smith_expanded_tiers` via `smith_expanded_tiers` / `set_smith_tier_expanded`, mw-guarded so headless tests no-op); the group holding the current target is always force-expanded so the selection stays visible. Recipe children render `display_name` + level (+ `makes N` when `output_qty > 1`), store the stable recipe ID on `UserRole`, and persist via a new `on_set_smith` callback (`_set_value("current_smith", id)` in `__init__`); the legacy `on_set_bar` bridge is kept only as a smelt-row fallback. Tooltips show station word, output qty, base XP, and requirements with owned counts. The dev-facing **`source` audit path was removed from tooltips** (Smithing, and for consistency also Mining/Woodcutting) — it lives in the source-audit docs/data, not the player UI. Lock reasons come straight from `can_smith_item_pure` (level or materials only — no hammer/tool gate, matching the gathering-only toolbelt decision). Icons resolve through the item registry: bars via `BAR_IMAGES`, forged items via a new existence-guarded `SMITHING_EXTRA_ITEM_IMAGES` (from `smithingitems/` by `_asset_slug`), and forged pickaxes/hatchets reuse the gathering tool art. `tools/fetch_smithing_assets.py` now **derives its manifest from `SMITHING_DATA`** (so it can't drift) and fetched the **entire** forge table plus the Blurite bar — 139 new sprites, 0 failures, all alpha-trimmed via the shared client. Coverage is **166/166 distinct Smithing outputs have an icon** (the existence-guard remains the safety net if a future row's wiki title doesn't resolve). Nine offscreen Qt tests cover metal-tier grouping, collapsed-by-default + current-target auto-expand, collapse-state persistence round-trip (via an injected dict-backed config), stable recipe IDs, level/material locks, owned-count tooltips with no source line, `on_set_smith` persistence, tier-node click-inertness, and current-target highlight; a registry test asserts full icon coverage + no dead asset paths.

## Key Product Decision
The project can borrow broad inspiration from idle-RPG progression, including Melvor Idle-like long-term loops, but should not copy Melvor's concrete content, balancing, UI, or structure (because it is inferior to RuneScape, but combat is an interesting carryover). The Anki review loop remains the core mechanic.

The target economy is now a compressed 2011-era RuneScape-style skill set adapted to Anki. Categories are Combat, Gathering, Artisan, Support, plus a visible Utility/Activities bucket for material-only no-XP actions. Magic remains one skill with separate combat and noncombat action families.

Roadmap direction: add an optional fake Grand Exchange-style market later so the default experience does not have to be fully ironman. The GE **design is now fully grilled and parked** in `memory-bank/fake-grand-exchange-design.md` (engine = hidden true-price + stochastic fill model with no persisted order book; GP = convenience-abundant, gated by buy limits + market clock, never sells XP; undo rolls back the market tick via deterministic RNG + per-tick delta snapshot; 8 slots, partial fills, OSRS price improvement, 40-action buy-limit windows, 240-action guide-price days capped +/-5%, alch-anchored seeding). It is intentionally **blocked on item-economy breadth**: the GE only earns its keep once many more tradable items exist.

Active priority (updated 2026-06-15): use `memory-bank/future-work-kanban.md` as the source of truth for future threads. Existing-skill architecture and old debt are the best next cleanup target; Utility/Activities icons are the next polish target; feathers remain the focused Fletching input gap; the GE remains a later candidate, not the next default project. Firemaking can still proceed in a separate skill-expansion thread.

P0 architecture cleanup first pass is complete on 2026-06-15. A new pure
`action_registry.py` resolves review-action handler keys for Mining,
Woodcutting, Smithing, Crafting, Fletching, and the no-XP Utility/Activities
aliases. Runtime review dispatch now uses that registry for answer eligibility
and handler lookup, and `_can_start_current_action` delegates to a handler-keyed
readiness map instead of a single long skill-name branch. Utility/Activities
remains synthetic and outside `skill_registry.py`; no flat save keys or XP/item
behavior changed. Frontend target-list builders in `ui.py` remain hardcoded by
skill because the backend still does not expose enough target-widget metadata to
migrate them safely; that is the next frontend boundary for continued P0 work.
Verification: `python3 run_tests.py` passed with 233 tests (57 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 233 tests.

P1 Utility/Activities icon set is complete on 2026-06-15. The backend metadata
contract is deliberately small: existing `UTILITY_ACTIVITY_DATA` rows now expose
`icon_path` entries pointing to dedicated `activityicons/` PNGs for Make soft
clay, Gather wool, Gather flax, and Open bird nests. The Qt Skills-hub Utility
target list prefers those activity icons and falls back to the old output-item
image map when a path is absent. No reward logic, storage migration, XP behavior,
activity list, or new acquisition system changed. New source-derived assets were
fetched through `tools/fetch_assets.py` and provenance was recorded in
`assets_provenance.json` (`Soft clay`, `Wool`, and `Flax` from OSRS wiki art;
`Bird's nest (seeds)` from runescape.wiki). Verification: `python3 run_tests.py`
passed with 235 tests (58 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 235 tests.

## Current Risks
- Skill behavior is still spread through hardcoded branches and dictionaries.
- Adding many skills before refactoring would likely multiply duplication.
- Combat could sprawl if started before noncombat action patterns are generalized.
- Anki config migration mistakes could affect persisted player progress.
- Running both the upstream `1808450369` copy and the local `ankiscape_fork` copy at the same time could double-register menus/hooks.
- The backend registry is only the first layer; the Qt menu is still per-skill/top-tab oriented and will overload once many skills become playable.
- The asset scraper records provenance, but existing asset provenance is still unaudited until icons are re-fetched or manually cataloged.
- Future game state stored outside `player_data` must be made undo-aware; the current rollback is intentionally scoped to review reward mutations in `player_data`.

## Next Recommended Work
Use `memory-bank/future-work-kanban.md` as the current future-thread source of truth.

1. **Continue P0 only if the owner wants another architecture slice**: the next
   useful boundary is frontend target-list metadata or decomposing the remaining
   `__init__.py` runtime orchestration, not repeating review handler dispatch.
2. **P2 feather source for Fletching**: feathers still need a legitimate source; arrowtips are not an open source gap because Smithing supplies them.
3. **P3 Grand Exchange candidate**: GE remains a valid future pressure valve, but it is not the next default priority. If reprioritized, start backend-first from `memory-bank/fake-grand-exchange-design.md`.
4. **Parked by current owner preference**: dependency-heavy Crafting acquisition loops and special Mining/Woodcutting content should stay out of scope until explicitly reprioritized.
5. **Parallel skill option**: Firemaking can be implemented in another thread and does not need to block the architecture cleanup.

## Frontend Handoff Status
The first frontend slice is done: the consolidated menu now uses a global top bar (Skills, Bank, Stats, Achievements, Settings) and a registry-backed Skills hub (`skill_hub.py` view-model + `ui.show_main_menu` three-pane category/skill/target layout). Developer mode reveals planned skills as disabled entries. Skills-hub click routing is fixed and now covered by an offscreen Qt behavior test. Fletching is now a fully playable hub skill (target panel, gating, `on_set_fletch`, OSRS `(detail)` icon), completing the backend pilot's frontend handoff.

The Crafting/Utility frontend handoff is also complete (see above): Utility/Activities surfaced as a no-XP hub category, Crafting target tooltips show batch/output, the HUD speaks the no-XP Utility state, and Settings carry the Gameplay XP-multiplier control. Pattern worth remembering: **non-XP "skills" (Utility/Activities) are injected at the ui view layer as a synthetic `CategoryView`/`SkillCardView`, not added to `skill_registry`**, so the XP registry stays honest (no fake level/exp keys). Reuse this approach for any future no-XP action family.

The Smithing frontend handoff is now complete (see the Smithing frontend + assets paragraph above): the hub renders `SMITHING_DATA` grouped by `station` with tier subheaders, persists stable `current_smith` IDs via `on_set_smith`, gates only on level/materials, and resolves icons through the registry with graceful degradation. The legacy `show_bar_selection_dialog` remains as an unwired smelt-only compatibility path; the live hub list is the full smelt+forge surface.

## Testing Workflow Note
UI-behavior regressions in the menu/HUD should be exercised with the offscreen Qt loop (`.venv-qt` + `aqt`, `QT_QPA_PLATFORM=offscreen`, see `tests/test_main_menu_widget.py`) before falling back to a manual Anki restart. Enable `ANKISCAPE_DEBUG=1` (or Developer Mode) and tail `ankiscape_debug.log` to read the `hub.*` navigation trace.

## Handoff Notes
- Backend work means Python game logic, storage, migrations, and tests.
- Frontend work means Qt dialogs/HUD/menu/stats/bank UX and any injected web UI.
- Split backend and frontend planning explicitly when implementation starts, because model choice may differ by side.
