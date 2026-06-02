# Smithing 2011Scape Source Audit

## Status

Planning/audit completed 2026-06-01. Scope decision: **Option C — full `BarProducts`
forge table** (every emulator forge item, ~150 rows), plus all 9 smelt bars.
Backend implementation handed to a separate GPT thread; frontend follows after the
backend contract is stable. No code beyond this audit + the plan artifact yet.

## Primary Sources (local 2011Scape rev 667)

Base path: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/smithing/`

- `data/SmeltingData.kt` — ore→bar recipes (level, XP, primary/secondary ore + count).
- `data/BarType.kt` — per-bar **forge** XP (XP earned per bar consumed at the anvil) + forge level gate.
- `data/SmithingType.kt` — per-shape bars-required, produced amount, UI button ids.
- `data/BarProducts.kt` — the full forge table: (bar tier, shape, result item id, level).
- `SmithingAction.kt` — forge mechanics; **item XP = `barType.experience * smithingType.barRequirement`** (line 42), hammer required, removes `barRequirement` bars, adds `producedAmount` outputs.
- `SmeltingAction.kt` — smelt mechanics; iron 50%→80% success interpolation over lvl 15–45 (`rollIronBar`), Ring of Forging behavior.
- Item ids → names: `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`.

Cross-check (2007/2011-shared only, never primary): runescape.wiki 2011 Smithing revisions.

## Confirmed Mechanics

- **Smelt XP** is a flat per-bar value (`SmeltingData.experience`).
- **Forge item XP** is fully derived: `bars_required(shape) × xp_per_bar(tier)`. There is no
  per-item XP table — every forged item's XP falls out of its tier and shape. This means the
  backend can generate the whole forge table from two compact tables plus the
  `(tier, shape, result_id, level)` rows in `BarProducts.kt`.
- Smelting consumes primary ore + N secondary (coal); forging consumes N bars + requires a hammer.

## Smelting Table (all 9 — implemented)

| Bar | Lvl | Smelt XP | Inputs |
| --- | --- | --- | --- |
| Bronze | 1 | 6.2 | Tin ore + Copper ore |
| Blurite | 8 | 8.0 | Blurite ore |
| Iron | 15 | 12.5 | Iron ore |
| Silver | 20 | 13.7 | Silver ore |
| Steel | 30 | 17.5 | Iron ore + 2 Coal |
| Gold | 40 | 22.5 | Gold ore |
| Mithril | 50 | 30.0 | Mithril ore + 4 Coal |
| Adamant | 70 | 37.5 | Adamantite ore + 6 Coal |
| Rune | 85 | 50.0 | Runite ore + 8 Coal |

Note: current `constants.BAR_DATA` already has 8 of these; it is **missing Blurite** and uses
Silver `13.67` (source `13.7`). It is display-name keyed (needs stable IDs + source notes).

## Forge XP Per Bar (`BarType.kt`)

Only these 7 tiers have forge products. **Silver and Gold bars are smeltable but have NO forge
products** in the emulator — they are Crafting jewellery inputs (AnkiScape already models gold
jewellery + silver tiara/symbol/bolts under Crafting). Do not invent silver/gold forge rows.

| Tier | Forge lvl gate | XP per bar |
| --- | --- | --- |
| Bronze | 1 | 12.5 |
| Blurite | 8 | 16.0 |
| Iron | 15 | 25.0 |
| Steel | 20 | 37.5 |
| Mithril | 50 | 50.0 |
| Adamant | 70 | 62.5 |
| Rune | 85 | 75.0 |

## Forge Shapes (`SmithingType.kt`)

| Shape | Bars | Produced | Notes |
| --- | --- | --- | --- |
| Dagger, Hatchet, Mace, Med helm, Sword | 1 | 1 | |
| Crossbow bolts (unf) | 1 | 10 | ammo |
| Dart tips | 1 | 10 | → Fletching |
| Nails | 1 | 15 | → Construction (future) |
| Arrow tips | 1 | 15 | → Fletching |
| Throwing knife | 1 | 5 | ammo |
| Wire, Iron spit, Studs, Oil lantern, Bullseye, Grapple tip, Crossbow limbs | 1 | 1 | misc/utility |
| Scimitar, Longsword, Full helm, Square shield, Claws, **Pickaxe** | 2 | 1 | pickaxe → Mining toolbelt |
| Warhammer, Battleaxe, Chainbody, Kiteshield, 2h sword, Plateskirt, Platelegs | 3 | 1 | |
| Platebody | 5 | 1 | |

The exact per-row `(tier, shape, result_item_id, level)` for all ~150 items is in
`BarProducts.kt`. The forge **level** is per-row (it is NOT just the tier gate — e.g. Bronze
platebody is level 18, Rune dagger 85, Rune platebody 99). Transcribe levels from `BarProducts.kt`.

## Implemented Scope (Option C — full table)

- All 9 smelt bars (add Blurite, stable IDs, source notes, Silver→13.7).
- Every `BarProducts.kt` forge row across Bronze/Blurite/Iron/Steel/Mithril/Adamant/Rune.
- Result item names resolved from `items.yml` by id. Many ids are `Items.*` constants (self-naming);
  the rest are raw ints (e.g. `1203` Iron dagger, `9377` Iron bolts unf, `40/41/42/43/44` arrow tips).
  Suggest a one-time helper that greps `items.yml` for each id → canonical name, recorded in the audit/data.

## Loops Closed (callouts for implementation)

- **Smithed pickaxes/hatchets are usable tools immediately**: `best_mining_pickaxe_pure` /
  `best_woodcutting_axe_pure` already scan inventory by display name, so a forged "Rune pickaxe"
  upgrades gathering with no extra wiring. Keep forged tool names identical to the tool item names.
- **Dart tips / arrow tips feed Fletching**; **bolts (unf)** already exist as a Crafting output
  (Silver bolts unf). Watch for name collisions when adding Bronze/Iron/etc. bolts (unf).

## Edge Cases / Notes

- **Blurite** forge products are only crossbow bolts (lvl 8) + limbs (lvl 13) — members/Slayer-flavored
  but mechanically plain; include as normal rows (no gating this pass, matching Mining/WC policy).
- **Studs (2370)** in-game also need leather; emulator `BarProducts` models it as a plain bar product.
  Keep it as a bar→item XP row; if a leather requirement is wanted later, treat as Crafting cross-dep.
- **Oil lantern frame / Bullseye lantern / Iron spit / Wire / Grapple tips** are valid XP rows; low
  downstream use today — fine as bankable XP items.
- Item ids that are raw ints must be mapped via `items.yml`; do not guess names.

## Deferred / Not Modeled

- **Iron 50% smelt-fail** (`rollIronBar`, 50→80% over lvl 15–45) and **Ring of Forging**: documented,
  NOT modeled. One successful card = one finished bar/item, consistent with Crafting/Mining (no fail
  rolls in the review loop). Record `respawn`/fail data as notes only.
- **Cannonballs, Goldsmith gauntlets, Artisan's Workshop, blast furnace** — not in this plugin / out of
  era scope; `future_content`.
- **Combat use of forged gear** — gear is bankable/tradeable XP output now; actual equipping waits on
  the Combat prototype + GE.

## Architecture Decisions (grilled with owner, 2026-06-01)

These four were the genuinely-new forks (Smithing is the first skill with two XP-bearing verbs
under one skill); the rest follows the Mining/WC/Crafting precedent.

1. **Unified recipe model.** Smelt and forge are NOT two handlers — they are both generic recipes in
   one `SMITHING_DATA` table (shaped like `CRAFTING_DATA`: `requirements → output_item/output_qty +
   exp + level`), each tagged `station: "furnace"` (smelt) or `"anvil"` (forge). The review handler
   reuses the existing `apply_crafting_pure` inputs→output→xp path (a thin `apply_smithing_pure`
   wrapper is fine for a separate `smithing_exp` key). The smelt/forge distinction is a pure UI
   grouping off `station`. Single `current_smith` target key (migrate legacy `current_bar`).
2. **No batching for XP actions.** Every Smithing action is XP-bearing, so each is **1 per card** —
   no `batch_size` on any Smithing recipe (`apply_crafting_pure`'s default of 1 is correct). A
   recipe's `output_qty` still yields multi-output (1 bar → 10 bolts) in a single card; that is
   output quantity, not batching. **Rationale (owner principle):** 28-batching exists only for the
   no-XP Utility prep activities (e.g. wetting clay) that would be instant at an in-game sink/fountain;
   real skilling stays gated. *(Follow-up, out of scope: Crafting's `Ball of wool` / `Bow string`
   currently batch 28 while granting XP — inconsistent with this principle; drop to 1/card in the
   Crafting re-audit.)*
3. **No tool gate.** The hammer is implicit (treated like the water source for Soft clay) — there is
   NO `toolbelt["smithing"]` seed and forge recipes do NOT gate on a hammer. **Toolbelt is
   gathering-only** (pickaxes + hatchets, plus the temporary Mining equipable in progress); processing
   skills gate on materials + level only. Smithing row lock reasons are exactly two: insufficient
   level, or missing inputs (ores for smelt, bars for forge).
4. **Bank category.** One new `Smithed` category for forged gear + ammo; forged **pickaxes/hatchets →
   `tool`** (so they sit with the gathering tools they become); bars stay `bar`. Category is just
   registry metadata, so re-bucketing later is cheap.

## Mechanics Decisions (proposed for backend thread)

- Apply the global `ankiscape_xp_multiplier` after base XP, before level checks.
- Undo-safe: record changed `player_data` keys for rollback like other review rewards.
- "Can do any Smithing" availability = can smelt any bar **or** forge any item (update
  `can_smelt_any_bar` callers to a broader `can_smith_any` check that scans the unified table).

## Tradability

- Bars: tradeable. Forged metal gear/tools/ammo: tradeable. Blurite items: follow Mining's
  Blurite-ore non-tradeable precedent only for ore; blurite **bolts/limbs** are tradeable item forms.
  Confirm each via `items.yml` `tradeable` and record explicitly in `smithing_data.py`.

## Storage and Tests (planned)

- Bump storage config version; migrate legacy display-name `current_bar` into the single stable
  `current_smith` target key (a smelt recipe id). No hammer/toolbelt seed. Never delete unknown inventory.
- Tests: data integrity (smelt table, forge XP = bars×barXP, level transcription spot-checks), pure
  smelt/forge mechanics, the multi-input deduction (one forge card consuming N bars correctly, and
  failing cleanly when short a bar/coal), review dispatch + undo, asset-path coverage, offscreen Qt rows.
