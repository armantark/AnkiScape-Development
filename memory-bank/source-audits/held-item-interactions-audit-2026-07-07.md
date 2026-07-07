# Held-Item Interactions — Audit (2026-07-07)

Owner flagged that many items act by *being present*, not by being consumed
(holy wrench, Excalibur heal, cannonball mould, potions, "plenty of others"),
and asked for a full audit. This is the **territory map**: the categories, what
AnkiScape already models, where the source lives, and how each meets the
carried-inventory toggle. It is deliberately not an exhaustive per-item spec —
each row below becomes its own scoped slice.

## The unifying rule (from the inventory design)

"Present" resolves against the toggle:
- **Inventory management ON:** the item must be in the 28 carried slots (costs a
  slot).
- **OFF (default):** "present" = "owned anywhere in the bank" (possession gate,
  no carry cost).

This single rule covers every category below.

## Category 1 — Required tool present (gates the action)

The 2011Scape skills gate many actions on a held tool. AnkiScape currently
**mostly ignores these** (e.g. Smithing has a documented "no hammer/tool gate"
decision — it gates on level + materials only). Under the inventory model these
become real requirements resolved by the rule above.

| Action | Required tool | Source | AnkiScape today |
| --- | --- | --- | --- |
| Smithing (forge) | Hammer | `smithing.plugin.kts:56`, `SmithingAction.kt:53` | not gated (deliberate) |
| Firemaking | Tinderbox | `FiremakingAction.kt:164` | not gated |
| Jewellery / silver casting | matching mould | `JewelleryAction.kt:85`, `SilverAction.kt:79` | not gated |
| Glassblowing | Glassblowing pipe | `GlassblowingAction.kt:61` | not gated (molten-glass recipe added 2026-07-06) |
| Leather craft | Needle (+ thread) | `LeatherAction.kt:88` | not gated |
| Cannonball smithing | Ammo mould | Darkan `Effect.java` / smithing | not implemented |
| Gem cutting | Chisel | crafting/gems | not gated |

**The toolbelt resolves most of these (owner refinement 2026-07-07).** Just
like real 2011: any tool *addable to the toolbelt* is always available and
needs no inventory slot; only tools that **cannot** go on the belt must be
carried. The 2011 belt included hammer, chisel, needle, knife, tinderbox (plus
the gathering tools AnkiScape's toolbelt already holds). So of the table above,
hammer / firemaking tinderbox / needle / chisel / knife all dissolve into
belt items — leaving a **tiny residual of genuinely non-belt tools**:

- **Moulds** (jewellery, silver, ammo/cannonball) — not belt-able → carried.
- **Glassblowing pipe** — not belt-able → carried.

Those are the only Category-1 items that occupy an inventory slot, and only
when inventory management is ON. With it OFF, owning the mould/pipe satisfies
the gate silently (matches today). So Category 1 shrinks from "gate every
skill" to "expand the toolbelt to its 2011 contents, and require moulds/pipe in
the carried grid." Implementation: extend the toolbelt's belt-able set to the
2011 list; add mould/pipe as carried requirements under the inventory model.

## Category 2 — Held passive effects (modify an action while present)

Items that change outcomes just by being carried/worn.

| Item | Effect | Source | AnkiScape today |
| --- | --- | --- | --- |
| Ring of forging | Iron smelt never fails | (worn) | **modeled** — `has_ring_of_forging_pure`, feeds `calculate_iron_smelting_success_probability_pure` |
| Holy wrench | Prayer potions restore more Prayer | Darkan `Effect.java` | not implemented (needs Prayer + potions) |
| Enhanced Excalibur | Special-attack heal-over-time | Darkan `Effect.java` `EXCALIBUR_HEAL` | not implemented (needs special attacks + the current-level substrate for the Defence boost) |
| Coal/gem bags, rune pouch | Pack unstackables into one slot | wiki | not implemented — **the inventory model's headline content** |

Ring of forging is the proof that this category already has a home (a
`*_present_pure` predicate feeding a probability/effect). Holy wrench and
Excalibur follow the same shape once Prayer / special-heal exist.

## Category 3 — Consumables (present, then consumed)

Already have infrastructure as of today:
- **Kebab, Beer** — implemented via `apply_consumable_pure` + the
  `combat_current_levels` substrate.
- **Potions** — the next big consumable family. They reuse
  `apply_combat_stat_delta_pure` (the substrate built for kebab/beer): Attack/
  Strength/Defence/Ranged/Magic potions set current = base + boost; the boost
  decays toward base at the source restore cadence already implemented. Prayer
  potions need Prayer points first. Antipoison/immunity already exist in
  `combat_status_effects`. Source: Darkan `PotionType.kt` / `Potions.kt`
  (`beerStrength`/`beerDrain` already ported; the potion boost formulas live in
  the same file).

## Dependency ordering (what unblocks what)

1. **Potions** — mostly unblocked now (substrate exists); the biggest-value
   next consumable slice. Prayer potions wait on a Prayer skill.
2. **Tool-present gates (Category 1)** — unblocked, but only *matter* with the
   inventory model ON, so best landed *with* that model.
3. **Holy wrench** — waits on Prayer + prayer potions.
4. **Enhanced Excalibur** — waits on the special-attack system's heal path
   (special energy already regenerates; the heal-over-time is the new piece).
5. **Bags** — part of the inventory model; the reason it earns its keep.

## Recommendation

Land these in order of unblocked value: **potions next** (substrate ready,
huge coverage), then fold **Category 1 tool gates + bags** into the
carried-inventory implementation (where they finally mean something), and defer
**holy wrench / Excalibur** until Prayer and the special-heal path exist. Each
row here becomes a source-audited slice; this doc is the index.
