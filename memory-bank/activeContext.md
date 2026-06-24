# Active Context

## Current Focus
Protect the local fork before any large expansion. The agreed direction is to augment the existing add-on, not rebuild it first.

## Equipment backend contract
The backend equipment pass is complete. `tools/generate_equipment_data.py`
joins checked-in Smithing recipe metadata, local 2011Scape `items.yml`
equipment blocks, and Mining bonus item data into generated `equipment_data.py`.
That module exposes 11 ordered slots, 131 unique equippable items, real combat
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
The next meaningful engineering step should be a skill-registry refactor. That refactor should preserve the current playable skills while making future skills cheaper and safer to add.

The add-on folder has been renamed from the AnkiWeb ID `1808450369` to `ankiscape_fork` so public AnkiWeb updates do not overwrite local work.

Backend registry implementation has started on `main` in a local git repository. The first backend pass adds pure skill and item registry modules, keeps existing flat save keys for safety, and wires review eligibility/level-up/storage defaults through registry metadata without changing the visible UI.

Asset-fetch tooling now exists as a standalone developer CLI at `tools/fetch_assets.py`. It is not imported by the add-on runtime. It resolves one item icon at a time from the official RuneScape wikis, prefers OSRS with RS3 fallback, supports registry-key path resolution, normalizes PNG output when fetching, and records provenance.

Fletching source integration is now complete. Inline `constants.FLETCHING_DATA`
was replaced by source-backed `fletching_data.py`; `constants.FLETCHING_DATA`
remains a compatibility export. The live table is grouped as Whittling,
Stringing, Arrows, Feathering, Bolts, Darts, and Specials, with rows sourced
from local 2011Scape rev 667 plus pinned 2011 KB bolt-tip/dart deltas. The old
tiered arrow-shaft pilot rows were removed because the source only binds normal
logs to arrow shafts. Broad arrows/bolts are visible disabled rows until the
flat `unlocked_abilities` list contains `broad_fletching`; leaping fish now uses
the same generic ability-lock substrate for `barbarian_fishing`. Fishing side XP
is exported and awarded through normalized `xp_rewards` instead of ad hoc
`strength_exp`/`agility_exp` fields. `tools/fetch_fletching_assets.py` derives
its asset manifest from `fletching_data.py`, and the full Fletching output/input
manifest resolves to icons under `fletcheditems/` with provenance.

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

Smithing 2011Scape backend parity is now complete. Source data lives in `smithing_data.py`, generated by `tools/generate_smithing_data.py` from local 2011Scape `SmeltingData.kt`, `BarType.kt`, `SmithingType.kt`, `BarProducts.kt`, `Items.kt`, and `items.yml`. `SMITHING_DATA` is a unified recipe table for all 9 smelt bars plus 157 forge rows; `BAR_DATA` remains a smelt-only compatibility view. Runtime uses `current_smith` stable recipe IDs, storage config version is 9, and legacy `current_bar` plus `Adamantite bar`/`Runite bar` inventory names migrate to source-shaped targets/items. No hammer/toolbelt gate was added; Smithing gates only on level and materials. Iron bar smelting is the source-backed exception to deterministic processing: valid `smelt_iron_bar` actions consume `Iron ore` first, then succeed on the 50% to 80% Smithing-level curve from `SmeltingAction.kt`; failures award no XP/bar and log `smelt_fail` telemetry. Ring of Forging state is supported if present in `player_data["equipment"]["ring"]`, but acquisition/enchanting remains future work.

Smithing 2011Scape **frontend + assets** pass is now complete. The Skills-hub Smithing panel (`_build_smith_list`) replaces the old smelt-only `_build_bar_list` and is fully `SMITHING_DATA`-driven. Because the unified table is ~166 recipes, the panel is a **`QTreeWidget` grouped by metal type** (Bronze → Rune): each tier is a collapsible parent holding its smelt bar first, then the forge items made from it. Groups are **collapsed by default** and the per-tier expand/collapse state persists across sessions in Anki config (`ankiscape_smith_expanded_tiers` via `smith_expanded_tiers` / `set_smith_tier_expanded`, mw-guarded so headless tests no-op); the group holding the current target is always force-expanded so the selection stays visible. Recipe children render `display_name` + level (+ `makes N` when `output_qty > 1`), store the stable recipe ID on `UserRole`, and persist via a new `on_set_smith` callback (`_set_value("current_smith", id)` in `__init__`); the legacy `on_set_bar` bridge is kept only as a smelt-row fallback. Tooltips show station word, output qty, base XP, and requirements with owned counts. The dev-facing **`source` audit path was removed from tooltips** (Smithing, and for consistency also Mining/Woodcutting) — it lives in the source-audit docs/data, not the player UI. Lock reasons come straight from `can_smith_item_pure` (level or materials only — no hammer/tool gate, matching the gathering-only toolbelt decision). Icons resolve through the item registry: bars via `BAR_IMAGES`, forged items via a new existence-guarded `SMITHING_EXTRA_ITEM_IMAGES` (from `smithingitems/` by `_asset_slug`), and forged pickaxes/hatchets reuse the gathering tool art. `tools/fetch_smithing_assets.py` now **derives its manifest from `SMITHING_DATA`** (so it can't drift) and fetched the **entire** forge table plus the Blurite bar — 139 new sprites, 0 failures, all alpha-trimmed via the shared client. Coverage is **166/166 distinct Smithing outputs have an icon** (the existence-guard remains the safety net if a future row's wiki title doesn't resolve). Nine offscreen Qt tests cover metal-tier grouping, collapsed-by-default + current-target auto-expand, collapse-state persistence round-trip (via an injected dict-backed config), stable recipe IDs, level/material locks, owned-count tooltips with no source line, `on_set_smith` persistence, tier-node click-inertness, and current-target highlight; a registry test asserts full icon coverage + no dead asset paths.

## Key Product Decision
The project can borrow broad inspiration from idle-RPG progression, including Melvor Idle-like long-term loops, but should not copy Melvor's concrete content, balancing, UI, or structure (because it is inferior to RuneScape, but combat is an interesting carryover). The Anki review loop remains the core mechanic.

The target economy is now a compressed 2011-era RuneScape-style skill set adapted to Anki. Categories are Combat, Gathering, Artisan, Support, plus a visible Utility/Activities bucket for material-only no-XP actions. Magic remains one skill with separate combat and noncombat action families.

Roadmap direction: add an optional fake Grand Exchange-style market later so the default experience does not have to be fully ironman. The GE **design is now fully grilled and parked** in `memory-bank/fake-grand-exchange-design.md` (engine = hidden true-price + stochastic fill model with no persisted order book; GP = convenience-abundant, gated by buy limits + market clock, never sells XP; undo rolls back the market tick via deterministic RNG + per-tick delta snapshot; 8 slots, partial fills, OSRS price improvement, 40-action buy-limit windows, 240-action guide-price days capped +/-5%, alch-anchored seeding). It is intentionally **blocked on item-economy breadth**: the GE only earns its keep once many more tradable items exist.

Active priority (updated 2026-06-19): use `memory-bank/future-work-kanban.md` as the source of truth for future threads. The current P0 existing-skill architecture board is complete; Utility/Activities icons, the focused feather source, Firemaking v1, Fishing v1, Cooking v1, Runecrafting v1, the priority quest-lock catalog, and the route-precedent locks are complete. The GE remains a later candidate, not the next default project.

Combat V1 ordinary training is now implemented as of 2026-06-23. Combat is a
synthetic review action in the Skills hub, not a registry skill. Its enabled
source-backed target set is Chicken, Rat, Spider, Spider level 24, Giant rat,
Giant spider level 2, Giant spider level 50, Goblin level 2 armed/unarmed,
Goblin levels 5/11/13/16/25, Cow, Cow calf, Ram, Highwayman, Mugger, Thug,
Thief, Guard level 21 Varrock/sword/battleaxe variants, Al-Kharid warrior,
Farmer, Barbarian level 8/9, Barbarian level 10, Seagull, Scorpion, Poison
scorpion, Deadly red spider, and Poison spider; each review simulates 50 RuneScape ticks per
`Actions per review`, caps at one kill,
persists lifepoints/enemy encounter state, routes melee damage XP through the
selected attack style plus Constitution, consumes real auto-eat food, and rolls
source-backed drops including inclusive drop quantity ranges. The follow-up
recovery foundation is also in place:
finite carried food and potion loadouts refill only at safe boundaries, safe noncombat
reviews apply one rollback-safe recovery packet per card, special-attack energy
regenerates on review ticks, stat-drain recovery state is scaffolded, and enemy
tooltips show loaded/banked food readiness. Persistent poison status now uses
the local source tick/damage curve, advances during Combat bursts and safe
noncombat recovery reviews, clears on death, and appears in the review HUD while
active. Source-backed poison enemies now roll the local 40% NPC poison chance
from `poisonDamage = 3`, write the same persistent player poison status, and
surface poison threat in target previews. Loaded Antipoison and Super
antipoison doses now auto-cure active poison, preserve source dose replacement,
grant poison-immunity timers, and suppress poison preview damage while immunity
is active. Safe recovery now also refills Ranged ammo from inventory when the
current Combat style is Ranged. The Ranged
path now covers standard bows from Shortbow through Magic longbow with Bronze
through Rune arrow compatibility, using the same Combat burst engine, consuming
one arrow per attack attempt from `combat_supply_loadout["ammo"]`, and routing
Ranged accurate/rapid/longrange XP from source-shaped Ranged formulas. Broad
arrows remain deferred until per-ammo Slayer/level gates exist. The first Magic
path is also live: standard
elemental spells from Wind Strike
through Fire Wave consume source runes from `combat_supply_loadout["runes"]`,
award source base Magic XP on cast attempts, and route damage XP to
Magic/Constitution. Basic Staff of air/water/earth/fire rune substitution is
live too: covered elemental runes are not missing, not loaded from inventory,
and not consumed per cast. Future Combat work should expand source-backed
monsters beyond the clean early rows, add god/Ancient/Lunar spell gates and
effects, broaden Ranged equipment/ammo beyond the standard bow ladder, add deeper
potion/cannonball/per-ammo preference controls, improve richer risk previews
and Wilderness/equipment-risk opt-ins, add source-exact death-fee/expiry
variants, and migrate quest combat gates onto this shared engine.

The Combat bootstrap now includes a source-backed Tutorial Island starter kit as
a one-time Bank Claim. The generic `item_bundle` claim path grants Bronze sword,
Wooden shield, Shortbow, 50 Bronze arrows, Air rune x5, Mind rune x5, Bronze
pickaxe, Hammer, Bronze hatchet, Tinderbox, and Small fishing net, with missing
Wooden shield/Tinderbox icons fetched under `combatitems/`. Storage config
version is 23. The source note is
`memory-bank/source-audits/combat-tutorial-starter-kit-2026-06-23.md`. Wooden
shield is claimable and registered, but broad non-Smithing shield/equipment
mechanics are still future Combat equipment work.

The first humanoid Combat target is now live: Highwayman imports the local
2011Scape level-5 row with guaranteed Bones/Cape, Iron bolts x2-12 at 1/20,
source combat stats/bonuses, a fetched Cape icon, and Cape slot equipment
metadata. Source proof lives in
`memory-bank/source-audits/combat-highwayman-2026-06-23.md`.

Mugger is now live as another low-level Humanoids target: the level-6 source
row imports all three source IDs, 80 lifepoints, attack speed 4, respawn delay
25, guaranteed Bones, the 1024-slot main table, nested `minorHerbTable`, Bronze
bolts x2-12, ordinary item drops, and the 128-slot easy clue tertiary table.
Source proof lives in
`memory-bank/source-audits/combat-mugger-2026-06-23.md`.

Thug is now live as a level-10 Humanoids target: the source row imports all
seven shared IDs, 180 lifepoints, attack speed 4, respawn delay 50, guaranteed
Bones, the 128-slot main table, nested `minorHerbTable`, 1000-slot charms, and
the 128-slot easy clue tertiary table. Source proof lives in
`memory-bank/source-audits/combat-thug-2026-06-23.md`.

Thief is now live as a level-16 Humanoids target: the source row imports all
four shared IDs, 170 lifepoints, attack speed 4, respawn delay 25, guaranteed
Bones, the 128-slot main table, Bronze bolts x2-12, nested `minorHerbTable`,
and the 128-slot easy clue tertiary table. Thieving gameplay is not inferred
from the NPC name. Source proof lives in
`memory-bank/source-audits/combat-thief-2026-06-23.md`.

Guard is now live as three level-21 Humanoids variants: Varrock, sword, and
battleaxe. The complete melee source rows share the Guard drop table, including
Iron bolts x2-12, allotment seed table rolls, medium clue tertiary drops, and
charms. The source-commented crossbow Guard stays disabled because it has no
complete combat definition yet. Source proof lives in
`memory-bank/source-audits/combat-guard-2026-06-23.md`.

Barbarian Combat coverage now includes two separate source-backed Humanoids
targets: `barbarian` for the level 8/9 source twins and `barbarian_level_10` for
the level 10 greataxe, spear, two-hand sword, and 2h sword variants. The level
10 row keeps its source attack speed 4, respawn delay 50, 180 LP, bonuses, and
shared Barbarian drop tables instead of merging into the earlier row. Source
proof lives in `memory-bank/source-audits/combat-barbarian-2026-06-23.md` and
`memory-bank/source-audits/combat-barbarian-level-10-2026-06-23.md`.

Combat target selection now asks for non-persistent confirmation before
activating any enabled target whose existing preview risk band is `Death
possible`. The row remains visible and enabled, but choosing `No` leaves the
previous target unchanged; choosing `Yes` calls the normal target-save callback
without adding a new save flag. Source proof lives in
`memory-bank/source-audits/combat-danger-confirmation-2026-06-23.md`.

Safe noncombat Combat recovery now has supply parity for the first Ranged path:
if the current Combat style is Ranged and the equipped weapon resolves through
`COMBAT_RANGED_WEAPON_DATA`, recovery refills compatible ammo from inventory
into `combat_supply_loadout["ammo"]` alongside food and Magic runes. Source
proof lives in
`memory-bank/source-audits/combat-safe-recovery-ammo-2026-06-23.md`.

Combat persistent status recovery now has the first source-backed poison path:
`combat_status_effects["poison"]` stores source poison ticks and tick progress,
poison advances every 30 source ticks during Combat bursts and safe noncombat
reviews, damage follows local `Poison.getDamageForTicks`, and poison death uses
the existing Combat grave path. Poison scorpion and Poison spider now apply that
status from source `poisonDamage = 3` attacks with the local 4-in-10 NPC poison
roll; Cave slime stays deferred until Slayer gates and shared gem-table drops
exist. Antipoison and Super antipoison dose handling now auto-cures active
poison from `combat_supply_loadout["potions"]`, preserves source dose
replacement, grants source immunity timers, and blocks new poison while
immunity is active. Weapon poison, broader enemy poison coverage,
non-antipoison immunity sources, and broader status/potion effects remain
deferred. Source proof lives in
`memory-bank/source-audits/combat-poison-status-recovery-2026-06-23.md` and
`memory-bank/source-audits/combat-poison-enemies-2026-06-23.md`, plus
`memory-bank/source-audits/combat-antipoison-loadout-2026-06-23.md`.

Combat ordinary critter coverage now also includes source-backed Scorpion,
Spider level 24, Deadly red spider, and Giant spider level 50 rows. These reuse
the existing Combat target, drop-table, and quantity-range machinery with local
2011Scape stats/drop tables instead of adding new mechanics. Source proof lives
in `memory-bank/source-audits/combat-scorpion-spider-variants-2026-06-23.md`.

Combat shared drop-table support now exists for explicit nested table slots.
The first use is Al-Kharid warrior, which imports the local 2011Scape level-9
row plus `Herbs.minorHerbTable` instead of flattening or omitting herb drops.
Source proof lives in
`memory-bank/source-audits/combat-al-kharid-warrior-2026-06-23.md`.

Combat higher-Goblin coverage now uses the same nested table support. Goblin
levels 5, 11, 13, 16, and 25 import their local 2011Scape stats, shared
128-slot main table, Charms table, easy clue tertiary, and explicit
`minorHerbTable` slot. The source main table declares 127 explicit slots under
`total(128)`, leaving one implicit no-drop slot. Source proof lives in
`memory-bank/source-audits/combat-higher-goblins-2026-06-23.md`.

Combat Farmer coverage now adds the level-7 Humanoids target using the same
nested table support. Farmer imports its local 2011Scape stats, guaranteed
Bones, 128-slot main table, nested `minorHerbTable`, nested
`Seeds.allotmentSeedTable`, farming tool drops, and easy clue tertiary. Farming
gameplay remains deferred; the new seeds/tools are inventory-visible drops only.
Source proof lives in `memory-bank/source-audits/combat-farmer-2026-06-23.md`.

Combat Citizen coverage now adds the source level-2 Man/Woman row as an
ordinary Humanoids target. The row imports the local 2011Scape shared Man/Woman
ID set, guaranteed Bones, 1024-slot main table, Bronze bolts x2-12, nested
`minorHerbTable`, and easy clue tertiary. All drops reuse existing item registry
coverage; no new Combat-owned icons were required. Source proof lives in
`memory-bank/source-audits/combat-citizen-2026-06-23.md`.

Combat low-level Humanoids coverage now adds source-backed Monk, Cuffs, and
Narf/Jeff/Rusty rows. Monk is a Bones-only level-5 target from the local
`MONK_7727` row. Cuffs and Narf/Jeff/Rusty reuse the same source 1024-slot
low-level human table as Citizen, including Bronze bolts x2-12, nested
`minorHerbTable`, and easy clue tertiary. Johnny the Beard remains deferred
because his local source row only declares hitpoints and needs default-stat
semantics audited before import. Source proof lives in
`memory-bank/source-audits/combat-low-level-humanoids-2026-06-23.md`.

Combat Rat/Unicorn coverage now adds source-backed level-6 and level-26 Giant
rat variants plus Unicorn and Black unicorn rows. Giant rats reuse the source
Bones/Raw rat meat table. Unicorns share the source guaranteed Bones/Unicorn
horn table plus 1000-slot charm table, and `Unicorn horn` now has Combat item
registry/icon coverage with fetched provenance. Source proof lives in
`memory-bank/source-audits/combat-rats-unicorns-2026-06-23.md`.

Combat Duck coverage now splits the source level-1 Duck file into land and water
rows. Land ducks (`DUCK_6113`/`DRAKE`) keep the registered Bones drop callback;
water ducks (`DUCK`/`DUCK_2693`) share the same stats and Bird Slayer XP but
expose no drops because the local source has no water-duck death drop callback.
Source proof lives in `memory-bank/source-audits/combat-ducks-2026-06-23.md`.

Combat Pirate coverage now adds the local source level-23 Humanoids target with
the full 1024-slot main table, Iron bolts x2-12, Eye patch, and nested
no-Ring-of-Wealth `Gems.gemTable` support. `Eye patch` now has Combat item
metadata and a fetched Combat icon. No frontend component change was needed
because the existing Combat target-row tooltip renderer exposes the new row,
drop slots, and source file. Source proof lives in
`memory-bank/source-audits/combat-pirate-2026-06-23.md`.

Combat Monk of Zamorak coverage now adds the local source level-45 Humanoids row
with fixed Bones, Zamorak robe top/bottom, and charm drops. The local source
names item IDs 1033 and 1035 both `Zamorak robe`; AnkiScape disambiguates them
as bottom/top storage keys to avoid collapsing two equipment slots in the flat
inventory model, with exact source constants recorded in the row and audit.
The level-30 Monk of Zamorak file stays deferred because its Golden key branch
is conditional on player inventory. Source proof lives in
`memory-bank/source-audits/combat-monk-of-zamorak-2026-06-23.md`.

Guard also proves one source-overfilled ordinary drop table. The source file
declares `total(128)` but uses 146 listed slots; AnkiScape stores the active
source-runtime roll range as 146 because 2011Scape's `DropTableFactory` rolls
against the final entry index after logging the mismatch.

Combat Dwarf coverage now adds the level-10 and level-11 Humanoids variants as
source-backed ordinary targets. Both rows share the local Dwarf drop table,
including Bronze bolts x2-12, charms, easy clue tertiary, and the first nested
`Gems.gemTable` -> `MegaRare.megaRareTable` chain. The implemented gem tables
preserve the source no-Ring-of-Wealth slot weights; Ring of Wealth boosts remain
deferred until Combat has equipment-conditioned drop modifiers. Source proof
lives in `memory-bank/source-audits/combat-dwarf-2026-06-23.md`.

Combat Ranged progression now extends beyond the Tutorial Island starter pair:
Shortbow through Magic longbow are source-backed two-handed Ranged weapons, and
Bronze through Rune arrows have source item IDs/strength values and bow
compatibility. Broad arrows are still deferred because their source item has a
Slayer requirement and the current ammo path has no per-ammo gate. Source proof lives in
`memory-bank/source-audits/combat-ranged-progression-2026-06-23.md`.

The first combat Magic ladder is now live: standard elemental Strike, Bolt,
Blast, and Wave spells are available through the Combat hub's
attack-style/spell controls, require their source Magic levels and runes,
consume only uncovered runes per cast from `combat_supply_loadout["runes"]`,
award source base Magic XP even on splashes, route damage XP into
Magic/Constitution, and surface selected spell plus loaded/banked or
staff-covered rune readiness in Combat target tooltips. Basic Staff of
air/water/earth/fire items are registered as weapon equipment from local
`items.yml` and provide their matching elemental runes. Source audits are
`memory-bank/source-audits/combat-magic-runes-2026-06-23.md`,
`memory-bank/source-audits/combat-magic-staves-spells-2026-06-23.md`, and
`memory-bank/source-audits/combat-standard-spells-2026-06-23.md`. Broader
Magic work remains open for battlestaves/mystic staves, god/Ancient/Lunar
spells with source gates/effects, noncombat Magic actions, and turning the planned Magic
registry row into a real playable skill panel.

Player-facing Combat loadout controls are now live in the Combat hub. The panel
shows and persists auto-eat threshold, preferred food priority, a finite
food/potion/ammo/rune loadout summary, and safe-boundary Refill/Unload buttons. The
callbacks use pure helpers in `logic_pure.py`, refuse manual refill/unload while
an active fight is in progress, and preserve the existing rule that food, ammo,
potions, and runes come from `combat_supply_loadout` rather than the whole Bank during a
burst.

Combat death recovery now includes the first Death's Office implementation.
The existing active grave still recovers equipped gear through five safe
non-Again reviews, but a second Combat death while a grave is active moves the
old grave's items into flat `death_office.items` before creating the new grave.
The Bank tab renders a Death's Office reclaim row when gear is waiting there;
reclaim consumes `100 Coins` per item and returns the gear to inventory. Source
proof and exclusions live in
`memory-bank/source-audits/combat-death-office-reclaim-2026-06-23.md`.

Combat ordinary-enemy expansion now includes the level 8/9 Barbarian twin row as
a single Humanoids target. It imports the full source-backed main/charm/easy
clue drop tables, registers generic `Staff` equipment from `items.yml`, and adds
Combat icons for Staff, Bear fur, Beer, Coins, and Clue scroll (easy). Source
proof and the level 10 greataxe exclusion live in
`memory-bank/source-audits/combat-barbarian-2026-06-23.md`.

Combat ordinary-enemy expansion also includes the level-2 Goblin source row as
two selectable Goblins targets: unarmed IDs and the one armed ID are split
because their source stats differ. Higher Goblins are now covered separately
after shared `minorHerbTable` support landed, and Farmer is covered after adding
`Seeds.allotmentSeedTable`. Source proof lives in
`memory-bank/source-audits/combat-goblin-level-2-2026-06-23.md` and
`memory-bank/source-audits/combat-higher-goblins-2026-06-23.md`, plus
`memory-bank/source-audits/combat-farmer-2026-06-23.md`.

Quest-stage parity is still active debt, not complete. As of 2026-06-22, all
194 pre-EOC quests have at least one machine-readable stage requirement, 174
quests have item/tool/option blockers, and 120 quests have combat blockers.
Current resolver-ready source-backed combat coverage is 179/284 rows after
generator enrichment, style-aware magic/ranged handling, Darkan `beasts.txt`
fallbacks, no-`combatLevels` fallbacks, focused `quest_data.py` name-shape
replacements, A Soul's Bane's full-stage combat split, Death to the Dorgeshuun's
Senior H.A.M. guard quantity replacement, and focused full-stage replacements up
through Fight Arena, Witch's House, Merlin's Crystal, Dwarf Cannon, and Heroes'
Quest. Merlin's Crystal now keeps quest-used items out of start locks, resolves
Sir Mordred as combat, and treats Thrantax as ritual dialogue/action. A generator/source-matching follow-up
then made safe token/plural/alias matches for Temple of Ikov's Guardians of
Armadyl and Observatory Quest's Poisonous Spider. Dwarf Cannon then replaced the
generated level-2 Goblins row with Darkan-backed noncombat rail, remains,
hideout, Lollk, toolkit, cannon repair, Nulodion, and Lawgof gates because the
local quest handler marks combat as none. A local Darkan quest-stage batch then
replaced broad generated rows for Fishing Contest, Gertrude's Cat, Clock Tower,
Monk's Friend, Tribal Totem, and Scorpion Catcher. It adds stage-local
item production/consumption for fishing passes, garlic, raw giant carp, fishing
trophies, milk buckets, doogle sardines, kittens, Clock Tower cogs, child
blankets, Cedric's supplies, RPDT address labels, the Rantuki totem, and
scorpion cages. Scorpion Catcher now has a source-backed level 39 jailer combat
gate at the Taverley Dungeon scorpion stage. A Sheep Herder focused replacement
then models poisoned sheep feed, Doctor Orbon clothing, the cattleprod route,
and all four sheep-bone incinerations as stage-local gates instead of start
locks. A Plague City and Waterfall Quest focused replacement then models
dwellberries-to-gas-mask, Edmond sewer entry, Jethick/Rehnison/Bravek prison
steps, hangover cure mixing, warrant/key rescue, Baxtorian book, Golrie,
Glarial's tomb items, rune/amulet waterfall completion, and Waterfall's pending
Attack/Strength XP rewards as source-backed stage-local gates. Post-batch audit
reports 519 stage rows, 68 produced-inventory rows, 285 combat encounters, and
180 resolver-ready combat encounters. Biohazard then adds a Darkan-backed
13-stage chain for Jerico/Omart wall routing, Bird feed and Pigeon cage
production/use, rotten-apple stew poisoning, Doctors' gown production, the level
13 Mourner, Distillator recovery, Elena's reagent vials, chemist Touch paper,
errand-boy smuggling, Priest gown x2 for Guidor, and Elena/King Lathas reports.
Post-Biohazard audit reports 529 stage rows, 73 produced-inventory rows, 285
combat encounters, and 180 resolver-ready combat encounters. Heroes' Quest then
replaces generated/broad rows with a source-backed chain for Blamish oil and
oily fishing rod prep, raw/cooked lava eel handling, Ice Queen gloves, Entrana
Fire feather, Black Arm/Phoenix route variants, candlestick/armband exchange,
and the final Achietties proof hand-in. The Ice Queen lair remains a route gate
instead of a mandatory Jailer fight because the source allows alternate access.
Post-Heroes audit reports 542 stage rows, 85 produced-inventory rows, 284 combat
encounters, and 179 resolver-ready combat encounters. The remaining 105 statless
combat rows stay hard-blocked and are classified by
`tools/audit_quest_combat_stat_gaps.py` as 51 Darkan hitpoints-only rows, 18
Darkan rows missing style-critical resolver stats, 7 same-name/wrong-level rows,
10 no-local-source rows, and 19 parser/variant-level rows. Combat quantities count one enemy per review action:
`tools/build_pre_eoc_quest_catalog.py` extracts written quantities, runtime
stores partial encounter progress in `quest_combat_encounter_counts`, and the
legacy completed id is written to `quest_combat_encounters` only when the
source quantity is fully resolved.
Family Crest then replaces generated/broad rows with a 16-stage source-backed
chain for Caleb's fish salad, Avan's perfect-gold jewellery, Boot/Witchaven
perfect gold routing, Johnathon's antipoison, Chronozon's blast-spell combat,
crest-piece combination, and Dimintheis' final hand-in. Post-Family-Crest audit
reports 554 stage rows, 92 produced-inventory rows, 284 combat encounters, and
179 resolver-ready combat encounters. Temple of Ikov then replaces its
generated broad start item/combat row with an 11-stage, 12-row Darkan-backed
chain for Lucien's pendant, light-source entry, web/Boots of lightness, lever
and ice-arrow route, Fire Warrior bow/ammo combat, Winelda's 20 limpwurt-root
teleport, Guardian/Lucien route variants, Staff of Armadyl hand-in, and Shiny
key reward. The Fire Warrior, Guardian of Armadyl, and Lucien rows all carry
resolver-ready Darkan stats, while the Guardian chamber remains modeled as one
blocking Guardian because Darkan uses line-of-sight rather than a fixed kill
count. Post-Temple audit reports 564 stage rows, 97 produced-inventory rows,
285 combat encounters, and 180 resolver-ready combat encounters. Source audit:
`memory-bank/source-audits/quest-temple-of-ikov-stage-detail-2026-06-22.md`.
The user clarified that
`memory-bank/status-updates/` artifacts should stay paused until every quest in
the catalog is updated to minute-detail stage parity.

P0 architecture cleanup first pass is complete on 2026-06-15. A new pure
`action_registry.py` resolves review-action handler keys for Mining,
Woodcutting, Smithing, Crafting, Fletching, and the no-XP Utility/Activities
aliases. Runtime review dispatch now uses that registry for answer eligibility
and handler lookup, and `_can_start_current_action` delegates to a handler-keyed
readiness map instead of a single long skill-name branch. Utility/Activities
remains synthetic and outside `skill_registry.py`; no flat save keys or XP/item
behavior changed. At this point, frontend target-list builders in `ui.py`
remained hardcoded by skill because the backend still did not expose enough
target-widget metadata; later P0 passes added the flat and grouped metadata
contracts.
Verification: `python3 run_tests.py` passed with 233 tests (57 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 233 tests.

P0 architecture cleanup second pass is complete on 2026-06-16. The new pure
`target_metadata.py` module defines `TargetRowMetadata` and row builders for the
flat Skills-hub target lists: Mining, Woodcutting, Fletching, Firemaking,
Fishing, and Utility/Activities. `ui.show_main_menu` now renders those rows
through one shared `QListWidget` helper, preserving the same labels, icons,
tooltips, disabled-row click guards, active-target highlighting, grouped/flat
layout split, flat save keys, XP/item math, action multiplier behavior, and
undo semantics. Smithing and Crafting were intentionally left on their grouped
`QTreeWidget` builders because parent rows, expand/collapse persistence, and
family/tier grouping need their own contract. `__init__.py` still owns the
individual runtime handler bodies. Verification:
`python3 run_tests.py` passed with 287 tests (69 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 287 tests.

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

P2 feather source is complete on 2026-06-15. `Scavenge chicken feathers` is a
no-input, no-XP Utility/Activities action that grants `28 Feather` per action
tick and uses a dedicated `activityicons/scavenge_chicken_feathers.png` icon.
The source rationale is recorded in
`memory-bank/source-audits/feather-utility-2026-06-15.md`: the local 2011Scape
Ranged instructor points arrow makers to chickens for feathers, and the local
chicken drop table includes Feather drops. The route is intentionally a bridge:
no Combat, shops, coins, GE, bones, raw chicken, Fletching recipe change, or
Smithing arrowtip change landed. Combat chicken drops and/or GE can later
replace, supplement, or rebalance this Utility route. Verification:
`python3 run_tests.py` passed with 240 tests (59 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 240 tests.

Firemaking v1 is complete on 2026-06-16 as an independent skill-expansion
thread. Source data lives in `firemaking_data.py`, audited against local
2011Scape `FiremakingData.kt`, `FiremakingAction.kt`, `firemaking.plugin.kts`,
and `items.yml` in
`memory-bank/source-audits/firemaking-2011scape-2026-06-16.md`. Firemaking is a
current Artisan review skill with flat save keys (`firemaking_level`,
`firemaking_exp`, `current_firemaking`), 13 source-backed burnable targets,
review-scale lighting chance helpers, implicit tinderbox behavior, success-only
log consumption, source XP, `Ashes x1`, achievements, assets, and offscreen Qt
coverage. Bonfires/fire spirits are intentionally deferred as a 2012 pre-EOC
extension rather than part of line Firemaking v1.

Fishing v1 is complete on 2026-06-16 as a Gathering skill-expansion thread.
Source data lives in `fishing_data.py`, audited against local 2011Scape
`Fish.kt`, `FishingTool.kt`, `FishingSpot.kt`, `Fishing.kt`, `items.yml`, and
Lumbridge Fishing Supplies in
`memory-bank/source-audits/fishing-2011scape-2026-06-16.md`. Fishing is a
current Gathering review skill with flat save keys (`fishing_level`,
`fishing_exp`, `current_fishing`), stable output-first method IDs, source
min/max chance rows adapted to AnkiScape review pacing, ordered mixed-output
rolls, success-only material consumption, hidden Strength/Agility side XP for
Barbarian fish, generic Fishing achievements, and a no-XP `Gather fishing bait`
Utility bridge. Reusable fishing tools are implicit and do not appear in labels,
tooltips, or fetched assets. The wiki gap check found no missing ordinary
Fishing training catch between the 2011 snapshot and pre-EOC; Stone fish,
Fish Flingers updates, cosmetics, Dungeoneering fish, and Fishing Trawler are
recorded as separate audit-only/future-slice content. Verification:
`python3 run_tests.py` passed with 281 tests (69 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 281 tests.

Cooking v1 is complete on 2026-06-16 as an Artisan skill-expansion thread.
Source data lives in `cooking_data.py`, audited against local 2011Scape
`CookingData.kt`, `CookingAction.kt`, `raw_food_cooking.plugin.kts`, `Items.kt`,
and `items.yml` in
`memory-bank/source-audits/cooking-2011scape-2026-06-16.md`. Cooking is a
current review skill with flat save keys (`cooking_level`, `cooking_exp`,
`current_cooking`), 54 stable targets, source XP/level/raw/cooked/burnt/chance
data, beef/bear sinew as distinct stable targets, review-scale burn chances,
success counters, burn counters, achievements, and a grouped Cooking target
tree. Burn failures consume the raw input and produce the source burnt item with
no XP. Cooking prep is intentionally no-XP Utility/Activities: wheat/flour/dough,
water/container actions, pie/stew/pizza assembly, simple gathering/scavenging,
and food-prep bridges are grouped under Utility. A new `food` item category and
`cookingitems/` icon folder are wired through the item registry and Bank; burnt
food is treated as non-tradeable junk for future GE/trading semantics. The Bank
now offers confirmed `Discard all` for every item, not only equippable gear.

Runecrafting v1 is complete on 2026-06-17 as a combined backend/frontend
skill-expansion thread. Source data lives in `runecrafting_data.py`, audited
against local 2011Scape Runecrafting source plus Rune Mysteries in
`memory-bank/source-audits/runecrafting-2011scape-2026-06-17.md`. Runecrafting
is a current Artisan review skill with flat save keys (`runecrafting_level`,
`runecrafting_exp`, `current_runecrafting`), 61 source-backed targets across
standard runes, combination runes, tiara binding, and Wicked hood feeding, plus
storage config version 15 state for `quests`, `quest_points`, `claims`,
`wicked_hood`, `runecrafting_pouches`, and `item_charges`. Rune Mysteries is a
review action, not an XP skill: it advances through 6 successful quest reviews,
awards 1 quest point, an Air talisman, 250 Runecrafting XP, and 250 pending
Magic XP, then unlocks Runecrafting. The Wicked hood is a one-time Bank Claim
after Rune Mysteries with no Runecrafting level gate; hood feeding is an
explicit Runecrafting target that permanently consumes
talisman/tiara access items. Binding necklace uses one equipment item plus
`item_charges["Binding necklace"]` (15 initial charges), not item variants; each
combination trip consumes one charge and removes the worn necklace at zero.
Assets are fetched into `runecraftingitems/` plus `icon/runecrafting_icon.png`.
The Bank Claims frontend now treats claims as a compact action inbox above the
inventory, not as bank items: eligible rows show icon/title/metadata/action,
claimed rows disappear into an all-caught-up state, locked rows collapse into a
summary, and the action list is capped to three visible rows so inventory remains
the primary Bank surface. The locked summary uses dark-mode-safe dim text and
names the primary blocker, so a locked Wicked hood reads as requiring Rune
Mysteries instead of hiding the reason in near-black text. The
focused Bank Claims Qt tests, `python3 run_tests.py`, and full offscreen Qt
discovery all pass with this polish.
Verification: `python3 run_tests.py` passed with 317 tests (79 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 317 tests.

Full pre-EOC Quest catalog second pass is complete on 2026-06-17. Runtime Quest
data now comes from generated `quest_catalog_generated.py` (194 rows: all quests
available before the 2012-11-20 Evolution of Combat cutoff, with Recipe for
Disaster split into 10 subquests) via `tools/build_pre_eoc_quest_catalog.py`.
The generator caches RuneScape Wiki old revisions, keeps source oldids and real
release order, includes quests that only became `former` after EOC, excludes
pre-EOC replacements, parses item rewards, parses XP lamps, and supplies
source-backed journals for every quest from local 2011Scape `QuestStage` text,
quick-guide checklist stages, or oldid walkthrough prose. `quest_data.py` layers
hand-audited overrides for unlock-critical quests and turns generated XP lamps
into Bank Claims with preserved skill choices/minimum levels. Quest starts
remain strict for incomplete prerequisite quests and unimplemented skills;
generated unimplemented-skill XP parks in `pending_skill_exp_rewards`. The
Quests tab renders the full catalog as collapsed sortable cards. Shilo Village
now gates Mining `gem_rocks` globally by owner choice until a route/location
model exists. Verification: `python3 run_tests.py` passed with 336 tests
(80 skipped), and `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 336 tests.

Quest route-precedent locks are now a deliberate narrow exception to the old
route-gate caution. When the current generic target effectively represents a
locked region route, it may be gated by the logical quest precedent: Priest in
Peril gates Morytania-flavored slimy eel/snail rows, The Fremennik Isles gates
Neitiznot-flavored yak/arctic pine rows, and Shilo Village gates `gem_rocks`.
Verification: `python3 run_tests.py` passed with 342 tests (83 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passed
with 342 tests.

Quest-list filtering is complete on 2026-06-19. `logic_pure.py` now exposes
`quest_availability_state_pure()` with UI-facing states: `can_start`,
`in_progress`, `blocked_at_stage`, `completed`, and `locked`. The Quests tab adds filters for Hide
completed, Hide unable to start, Access, Difficulty, Length, and Timeline, plus a
showing-count label. As of 2026-06-22, started quests can surface
`blocked_at_stage` when current-stage machine-readable blockers exist; Hide
unable to start still only hides `locked` quests so in-progress blockers stay
visible. The Knight's Sword is the first source-backed stage-gate proof case,
with Redberry pie and later Blurite ore/Iron bar blockers modeled separately
from its Mining 10 start lock. A catalog-wide generator follow-up now extracts
quest-wide item/tool/option requirements and combat encounters, and a focused
no-stage closure pass adds source-backed overrides/additions so the audit now
reports 194/194 quests with at least one machine-readable stage requirement.
119 quests currently carry combat blockers, and combat fails closed through
`player_data["quest_combat_config"]["resolver_enabled"] == False` by default.
The first resolver-enabled write path exists for current-stage stat-backed
encounters. The Restless Ghost Skeleton Warlock is the current focused
proof that a hand-authored stage addition can carry local 2011Scape NPC stats
and become `Battle required` in the UI. The generated catalog also enriches
combat rows from local source data in strict precedence order: 2011Scape NPC
definitions first, then Darkan/2012scape exact name+level combatdef matches.
Identical duplicate Darkan sources can now be accepted when their captured
battle stats/configs agree; conflicting duplicates stay blocked until focused
quest/combat evidence resolves them. Demon Slayer now has a focused
Darkan-backed nine-stage replacement covering coin, bucket water, 25 bones,
three Silverlight keys, Silverlight, Delrith, and the incantation before
completion; Delrith is a focused stage row now, not just a generated proof case.
Elvarg, Earth Elemental, focused Jogre, focused Sea Troll Queen, Priest in Peril's Monk of Zamorak, and Troll
Stronghold's Dad are current proof cases. Witch's House now supersedes the old
combat-only proof with a 12-stage Darkan-backed chain for Door key, Magnet,
Cheese, witch patrol, Leather gloves, Backroom key, four experiment forms, Ball,
and Harvey hand-in. A style-aware resolver pass then made source-backed magic/ranged
rows with zero melee Strength resolver-ready, adding H.A.M. mage, The Void
Stares Back Torcher/Defiler, and The Elder Kiln TokHaar-Xil. Combat stat
coverage is now 179/284 rows after the Darkan beast fallbacks, focused
name-shape replacements, A Soul's Bane's split combat stages, Death to the
Dorgeshuun's Senior H.A.M. guard quantity replacement, Demon Slayer's focused
Delrith row, Witch's House's four form chain, Merlin's Crystal's Sir Mordred,
the generated safe-name matches for Temple of Ikov's Guardians of Armadyl and
Observatory Quest's Poisonous Spider, and Dwarf Cannon's Darkan-backed
noncombat replacement that removes the generated goblin blocker, plus Scorpion
Catcher's Darkan-backed level 39 jailer gate, and Heroes' Quest's Ice Queen and
Grip resolver rows. The remaining 105 statless rows are
classified by
`tools/audit_quest_combat_stat_gaps.py` as 51 hitpoints-only Darkan rows, 18
Darkan rows missing style-critical resolver stats, 7 same-name/wrong-level
rows, 10 no-local-source rows, and 19 parser/variant-level rows; remaining NPC stat enrichment and full combat
simulation remain open.
Generated item alternatives now preserve
independent option groups, so stage gates such as Goblin Diplomacy dye
alternatives remain finishability blockers instead of being flattened into
impossible all-item requirements.
The live stage audit now reports 554 stage rows and 92 produced-inventory rows
after the Demon Slayer, early Darkan, Dragon Slayer, Shield of Arrav, Fight
Arena, Witch's House, Merlin's Crystal, Dwarf Cannon, the local noncombat
Darkan batch, Sheep Herder, Plague City, Waterfall Quest, and Biohazard focused
replacements, plus Heroes' Quest's source-backed branch-and-proof chain and
Family Crest's source-backed fish/jewellery/Chronozon chain. This is broad blocker
coverage, not minute-detail parity for every quest; use
`memory-bank/source-audits/quest-stage-gates-catalog-wide-2026-06-22.md` and
`memory-bank/source-audits/quest-demon-slayer-stage-detail-2026-06-22.md` plus
`memory-bank/source-audits/quest-early-darkan-stage-batch-2026-06-22.md` plus
`memory-bank/source-audits/quest-witchs-house-stage-detail-2026-06-22.md` plus
`memory-bank/source-audits/quest-sheep-herder-stage-detail-2026-06-22.md` plus
`memory-bank/source-audits/quest-plague-city-waterfall-stage-detail-2026-06-22.md` plus
`memory-bank/source-audits/quest-biohazard-stage-detail-2026-06-22.md` plus
`memory-bank/source-audits/quest-heroes-quest-stage-detail-2026-06-22.md` plus
`memory-bank/source-audits/quest-family-crest-stage-detail-2026-06-22.md` plus
`tools/audit_quest_stage_gate_coverage.py` before making completion claims.

Quest completion UX now mirrors depletion handling. When a review completes the
active quest, `runtime_actions.handle_quest_answer()` still awards rewards,
records telemetry, switches `current_skill` to `None`, saves, refreshes
availability, and emits the floating completion gain; it also opens a modal
`Quest complete` dialog through the existing warning-dialog helper so the player
gets a clear stop point instead of silently continuing with Quest training off.
Focused runtime/integration tests cover the dialog title/body and deactivation.

P0 grouped target-tree metadata cleanup is complete on 2026-06-19. Smithing,
Crafting, Cooking, and Runecrafting now build their grouped Skills-hub rows
through `target_metadata.py` before Qt renders them. The shared grouped
`QTreeWidget` renderer in `ui.py` preserves existing parent role ids,
Smithing/Crafting expand-state persistence, Cooking/Runecrafting current-target
auto-expand, icons, tooltips, disabled-row click guards, and flat save keys.
`logic_pure.py` now owns Smithing/Crafting locked-reason helpers, so
level/material/quest reasons are computed once for row metadata instead of
being reconstructed inside Qt. No recipe data, XP math, storage migration, item
rewards, or quest rules changed. Verification: `python3 run_tests.py` passed
with 345 tests (83 skipped), and the offscreen Qt discovery suite passed with
345 tests.

P0 runtime handler extraction is complete on 2026-06-19. `runtime_actions.py`
now owns the review-action mutation bodies and handler-keyed can-start checks
for Mining, Woodcutting, Fishing, Smithing, Crafting, Fletching, Firemaking,
Cooking, Runecrafting, Quests, and Utility/Activities. `__init__.py` keeps
Anki hooks, global state, save/HUD/UI callback wiring, undo snapshots, and thin
`on_<skill>_answer` compatibility wrappers that build a `RuntimeActionContext`.
No save schema, XP math, item rewards, target metadata, quest rules, assets, or
frontend surfaces changed. Verification: `python3 run_tests.py` passed with
347 tests (83 skipped), and the offscreen Qt discovery suite passed with 347
tests.

P0 achievement metadata and final handler-plumbing cleanup is complete on
2026-06-19. `achievement_metadata.py` now owns the 105 achievement definitions,
the shared difficulty order, grouped row models, and progress-count helpers while
`constants.ACHIEVEMENTS` preserves the legacy dict export for achievement checks.
The main menu Achievements tab and the standalone achievement dialog render from
the same metadata helpers. `__init__.py` now resolves current-action readiness
and review-answer handlers through `action_registry.py` plus `runtime_actions.py`
instead of maintaining duplicate per-skill can-start helpers or a private handler
map. No save schema, achievement names, completion semantics, XP math, item
rewards, quest rules, target metadata, assets, or visual behavior changed.
Verification: `python3 run_tests.py` passed with 352 tests (84 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 352 tests.

Hunter v1 is complete on 2026-06-20. The local 2011Scape cache/snapshot was not
missing Hunter item identity; it was missing a local Hunter mechanics plugin.
The implemented scope therefore uses 2011.rs guide rows for levels/XP/rewards,
local cache names/ids for inventory keys, and local 2012scape/Darkan Hunter
code as mechanics/id parity evidence. `hunter_data.py` now drives 55 targets
across bird snaring, butterfly netting, deadfall, box trapping, net trapping,
falconry, magic boxes, and Puro-Puro/world implings. Hunter is a current
Gathering review skill with stable `current_hunter`, storage config version 18,
Hunter item/icon registration, `hunter_success_count` achievements, grouped
target rows, Stats/Bank/HUD support, action multiplier support, and undo
rollback. Quest locks cover Eagles' Peak, As a First Resort, Rocking Out, and
Priest in Peril route precedent. Tracking, pitfall, rabbit snaring, barehand
catches, Herblore Habitat/Jadinkos, grenwall herb drops, and Regicide-start
partial-route modeling remain deferred. Source audit:
`memory-bank/source-audits/hunter-2011scape-2026-06-20.md`. Verification:
`python3 run_tests.py` passed with 374 tests (89 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 374 tests.

Hunter supply bridge follow-up completed on 2026-06-20. Reusable Hunter gear is
now modeled separately from consumed materials: target specs expose reusable
`tools` gates for snares, box traps, butterfly nets, and tree-net gear, while
`requirements` still represent items deleted on successful catches such as jars,
logs, and magic boxes. `Buy Hunter supplies` is a temporary no-XP
Utility/Activities bridge that spends `500 Coins` for a Darkan-stock-backed
starter/restock bundle and then automatically switches AnkiScape off after one
successful review, preventing action-multiplier repeats. The richer shop/GE
interface is intentionally deferred to a later UX/economy pass. Verification:
`python3 run_tests.py` passed with 377 tests (89 skipped), and
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
passed with 377 tests.

NPC shop design seed captured on 2026-06-20 in
`memory-bank/npc-shop-design-seed.md`. The intended future system is a separate
Shop menu surface, not the parked fake GE: source-backed in-game shop
inventories, dynamic price/stock behavior, shared stock pools, buy/sell rules,
and location/quest locks. Use local 2011Scape and local Darkan/2012scape as
primary sources, with historical wiki revisions as conflict checks. Open design
decisions still need grilling before implementation, especially navigation,
location modeling, restock timing, exact price formulas, sell policies, and the
first scope cut.

Combat V1 design grill completed on 2026-06-23 in
`memory-bank/combat-design-grill-2026-06-23.md`. It is the source of truth for
ongoing Combat implementation boundaries: one generic undo-safe 0.6s-tick
combat engine shared by ordinary monsters, quest encounters, bosses, quantities,
and phase/form chains; 50 ticks per `Actions per review`; damage-based combat
XP; finite supply loadouts; auto-eat and review-tick recovery; PvM grave/Death's
Office recovery; explicit Wilderness risk; full source-backed enemy/equipment/
drop audits; incomplete source data kept in audit/backlog artifacts rather than
enabled gameplay; and explicit backend/frontend/assets/balance/testing handoffs.
The ordinary Combat runtime is now partially implemented through the current
source-backed target set; broader enemy classes and quest handoff remain future
slices.

As of the current Combat implementation session, the owner explicitly paused
status update HTML artifacts until the overall goal is complete. Continue source
audits, tests, Memory Bank markdown, and commits normally, but do not create,
open, or upload visual status artifacts mid-goal.

## Current Risks
- The current P0 architecture board is closed, but a larger action-engine design
  could still be justified later if a future feature needs behavior beyond the
  current dispatch, runtime, target-row, and achievement metadata contracts.
- Adding many skills will still add pressure to stats, icons, tests, and storage
  migrations even though target/action duplication is lower than before.
- Combat could still sprawl during implementation; use the completed Combat V1
  design grill as the boundary and keep incomplete source data out of enabled
  gameplay.
- Anki config migration mistakes could affect persisted player progress.
- Running both the upstream `1808450369` copy and the local `ankiscape_fork` copy at the same time could double-register menus/hooks.
- The Qt menu remains a large monolithic function; target rows are shared, but stats, achievements, bank, equipment, settings, and other surfaces are not fully componentized.
- The asset scraper records provenance, but existing asset provenance is still unaudited until icons are re-fetched or manually cataloged.
- Future game state stored outside `player_data` must be made undo-aware; the current rollback is intentionally scoped to review reward mutations in `player_data`.

## Next Recommended Work
Use `memory-bank/future-work-kanban.md` as the current future-thread source of truth.

1. **Move past the current P0 architecture board**: dispatch, runtime handlers,
   flat/grouped target metadata, achievement metadata, and the final duplicated
   handler plumbing are done. Do not continue P0 by default unless the owner
   names a new concrete architecture boundary.
2. **P3 economy candidates**: NPC shops and GE are both valid future pressure
   valves, but neither is the next default priority. If NPC shops are
   reprioritized, start backend-first from
   `memory-bank/npc-shop-design-seed.md`; if GE is reprioritized, start
   backend-first from `memory-bank/fake-grand-exchange-design.md`.
3. **Parked by current owner preference**: dependency-heavy Crafting acquisition loops and special Mining/Woodcutting content should stay out of scope until explicitly reprioritized.
4. **Future Fishing extensions**: Dungeoneering fish, Fishing Trawler, quest-only fish, Fish Flingers, and real shop/GE bait sourcing are separate systems and should stay deferred until explicitly prioritized.
5. **Future Firemaking extension**: bonfires/fire spirits are the next natural Firemaking-specific follow-up, but should stay deferred until explicitly prioritized.
6. **Future Runecrafting extensions**: Magic Imbue, Wicked hood daily resources/teleports/reclaim, Abyss/abyssal creatures, talisman sourcing, and broader rune economy routes should stay separate from v1 until explicitly prioritized.
7. **Future Hunter extensions**: tracking trails, pitfall trapping, rabbit snaring, barehand catches, Herblore Habitat/Jadinkos, grenwall herb drops, and Regicide-start partial-route modeling should stay separate from v1 until explicitly prioritized.
8. **Future quest work**: `memory-bank/quest-unlock-audit-2026-06-17.md` is the durable source for the completed 194-row pre-EOC catalog, RFD subquest split, implemented completion gates, route-precedent locks, generated rewards, and content that should or should not be quest-gated. `memory-bank/source-audits/quest-stage-gates-2026-06-22.md` records the stage-aware foundation and The Knight's Sword proof case; `memory-bank/source-audits/quest-stage-gates-catalog-wide-2026-06-22.md` records the generated catalog-wide blocker layer; `memory-bank/source-audits/quest-stage-no-stage-closure-2026-06-22.md` records the 194/194 no-stage closure; `memory-bank/source-audits/quest-combat-resolver-contract-2026-06-22.md` records the first resolver-enabled stat-backed combat write path; `memory-bank/source-audits/quest-darkan-combat-stat-enrichment-2026-06-22.md` records the local 2011Scape-first plus Darkan/2012scape exact-match generated combat stat enrichment; `memory-bank/source-audits/quest-identical-combat-source-enrichment-2026-06-22.md` records the identical duplicate-source/focused override stat follow-up; `memory-bank/source-audits/quest-conflict-combat-stat-enrichment-2026-06-22.md` records grouped item-option repair, Monk/Dad conflict resolution, and the classified 137-row combat backlog; `memory-bank/source-audits/quest-witchs-house-combat-forms-2026-06-22.md` records the Witch's House four-form replacement and refined 132-row combat backlog; `memory-bank/source-audits/quest-style-aware-combat-resolver-2026-06-22.md` records style-aware magic/ranged combat stat readiness; `memory-bank/source-audits/quest-darkan-beast-stat-fallback-2026-06-22.md` and `memory-bank/source-audits/quest-darkan-no-combatlevels-beast-stat-fallback-2026-06-22.md` record the Darkan beast-stat fallbacks; `memory-bank/source-audits/quest-focused-combat-row-splits-2026-06-22.md` records the 118-row backlog after focused name-shape replacements; `memory-bank/source-audits/quest-a-souls-bane-dorgeshuun-combat-split-2026-06-22.md` records the 109-row backlog after A Soul's Bane and Death to the Dorgeshuun focused replacements; `memory-bank/source-audits/quest-historical-wiki-combat-stat-audit-2026-06-22.md` records the historical-wiki source-tier pass that found 77 metadata-only pages, 32 pages without monster metadata, and 0 remaining rows with resolver-ready hidden stats; `memory-bank/source-audits/quest-priest-in-peril-stage-detail-2026-06-22.md` records the Priest in Peril full-stage replacement, consumed essence alternatives, corrected nine-stage completion, and remaining Temple guardian dog stat gap; `memory-bank/source-audits/quest-2011scape-starter-stage-batch-2026-06-22.md` records the produced-inventory contract and the Cook's Assistant, Imp Catcher, Druidic Ritual, Pirate's Treasure, and Vampyre Slayer source-backed replacement batch; `memory-bank/source-audits/quest-demon-slayer-stage-detail-2026-06-22.md` records the Demon Slayer focused replacement; `memory-bank/source-audits/quest-early-darkan-stage-batch-2026-06-22.md` records the Goblin Diplomacy, Ernest the Chicken, and Black Knights' Fortress focused replacement batch; `memory-bank/source-audits/quest-heroes-quest-stage-detail-2026-06-22.md` records the Heroes' Quest branch-and-proof replacement. Current quest-stage debt is still the remaining generated-row surface plus explicit combat/stat and branch/route gaps; only reopen this area for remaining minute-detail per-stage extraction, route/location gates, remaining combat stat enrichment, full combat simulation, quest-item transformations, puzzle/follower/branch state, new quest-unlocked skill targets, or generator/source corrections.
9. **Future Combat V1 implementation**: start from `memory-bank/combat-design-grill-2026-06-23.md`. Treat it as a full-system build with source audits, backend engine/schema, frontend Combat tab, assets, balance, tests, rollback, and manual Anki QA split explicitly.

Current quest-work addendum: later 2026-06-22 focused audits for Dragon Slayer,
Shield of Arrav, Fight Arena, `memory-bank/source-audits/quest-witchs-house-stage-detail-2026-06-22.md`,
`memory-bank/source-audits/quest-merlins-crystal-stage-detail-2026-06-22.md`,
`memory-bank/source-audits/quest-dwarf-cannon-stage-detail-2026-06-22.md`, and
`memory-bank/source-audits/quest-local-noncombat-stage-batch-2026-06-22.md`,
plus `memory-bank/source-audits/quest-sheep-herder-stage-detail-2026-06-22.md`,
plus
`memory-bank/source-audits/quest-plague-city-waterfall-stage-detail-2026-06-22.md`,
plus `memory-bank/source-audits/quest-biohazard-stage-detail-2026-06-22.md`,
plus `memory-bank/source-audits/quest-heroes-quest-stage-detail-2026-06-22.md`,
plus `memory-bank/source-audits/quest-family-crest-stage-detail-2026-06-22.md`,
supersede the older generated-row debt count above. The live audit now reports
554 stage rows, 92 produced-inventory rows, 284 combat encounters, and 179
resolver-ready combat encounters; full all-quest minute-detail parity remains
open until remaining generated rows, route/location state, quest-item
transformations, optional branches, combat stat gaps, and real combat simulation
are resolved.

## Frontend Handoff Status
The first frontend slice is done: the consolidated menu now uses a global top bar (Skills, Bank, Stats, Achievements, Settings) and a registry-backed Skills hub (`skill_hub.py` view-model + `ui.show_main_menu` three-pane category/skill/target layout). Developer mode reveals planned skills as disabled entries. Skills-hub click routing is fixed and now covered by an offscreen Qt behavior test. Fletching is now a fully playable hub skill (target panel, gating, `on_set_fletch`, OSRS `(detail)` icon), completing the backend pilot's frontend handoff.

The Crafting/Utility frontend handoff is also complete (see above): Utility/Activities surfaced as a no-XP hub category, Crafting target tooltips show batch/output, the HUD speaks the no-XP Utility state, and Settings carry the Gameplay XP-multiplier control. Pattern worth remembering: **non-XP "skills" (Utility/Activities) are injected at the ui view layer as a synthetic `CategoryView`/`SkillCardView`, not added to `skill_registry`**, so the XP registry stays honest (no fake level/exp keys). Reuse this approach for any future no-XP action family.

The Smithing frontend handoff is now complete (see the Smithing frontend + assets paragraph above): the hub renders `SMITHING_DATA` grouped by `station` with tier subheaders, persists stable `current_smith` IDs via `on_set_smith`, gates only on level/materials, and resolves icons through the registry with graceful degradation. The legacy `show_bar_selection_dialog` remains as an unwired smelt-only compatibility path; the live hub list is the full smelt+forge surface.

## Testing Workflow Note
UI-behavior regressions in the menu/HUD should be exercised with the offscreen Qt loop (`.venv-qt` + `aqt`, `QT_QPA_PLATFORM=offscreen`, see `tests/test_main_menu_widget.py`) before falling back to a manual Anki restart. Enable `ANKISCAPE_DEBUG=1` (or Developer Mode) and tail `ankiscape_debug.log` to read the `hub.*` navigation trace.

Telemetry/normalization baseline completed on 2026-06-20. Backend owns durable `player_data["action_telemetry"]` rows plus the pure summary helper; future Stats/frontend work should consume `summarize_action_telemetry_pure` rather than reimplement observed-vs-expected math. Dry RNG outcomes now save telemetry even when no XP/item state changes, so manual QA should include at least one forced-dry Fishing or Firemaking review and confirm the save key changes.

## Handoff Notes
- Backend work means Python game logic, storage, migrations, and tests.
- Frontend work means Qt dialogs/HUD/menu/stats/bank UX and any injected web UI.
- Split backend and frontend planning explicitly when implementation starts, because model choice may differ by side.
