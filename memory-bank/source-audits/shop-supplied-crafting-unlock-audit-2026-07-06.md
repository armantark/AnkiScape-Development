# Shop-Supplied Crafting Unlock Audit

Generated: 2026-07-06 (shop-economy integration pass, stage 3)

## Question

Which recipes that were parked as "input-starved" gained a real acquisition
route when the NPC shops went live — and what was still missing?

## Inputs that live NPC shops (or coin-paid conversions) now supply

| Input | Route | Recipes lit up |
| --- | --- | --- |
| Uncut sapphire/emerald/ruby/diamond | Ardougne Gem Stall (live coin stock) | Gem cutting → jewellery chains |
| Silver bar | silver stalls | All seven silver-casting recipes |
| Leather / Hard leather | `tan_soft_leather` / `tan_hard_leather` Utility conversions (Cowhide + 1/3 Coins per hide) | Leather armour family |
| Battlestaff | staff shops | Battlestaff attachment rows (orbs still unsourced) |
| Ball of wool, Jute fibre, Hair | craft shops | Weaving/rope rows |
| Soda ash + Bucket of sand | Skulgrimen/charter-adjacent shops (live coin stock) | Glassblowing via the new recipe below |
| Elemental runes | rune shops | Urn rune-attachment rows |

No recipe row changed for any of these: they were always fully wired and
material-gated, exactly like a sapphire ring with zero sapphires. The shops
just made the materials obtainable.

## The one real gap: Molten glass

Glassblowing products (Beer glass, Vial, Unpowered orb) existed but nothing
produced their input. The 2011Scape furnace source defines the missing step:

- Source: `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/objs/furnaces/furnaces.plugin.kts`, `handleMoltenGlass`
- 1 Soda ash + 1 Bucket of sand → 1 Molten glass **plus the emptied Bucket back**
- 20.0 Crafting XP, no level gate (level 1)

Implemented as `glass_molten_glass` in `crafting_data.py` (family `glass`,
station `furnace`). The byproduct required a small optional `byproducts`
field on `CraftingRecipe` plus support in `apply_crafting_pure` and the
Crafting tooltip ("Also returns: Bucket x1"). Icon: existing
`crafteditems/molten_glass.png` (provenance already recorded). The stale
"input-starved until molten glass source exists" notes on the three
glassblowing products were removed; dragonhide-body rows keep theirs (dragon
leather still has no source: Ellis tans cowhide only).

## Still parked (honestly)

- Dragonhide bodies: no dragonhide drops or dragon-leather tanning yet.
- Battlestaff orbs: obelisk charging belongs to future Magic design.
- Seaweed → Soda ash cooking (`seawead_cooking.plugin.kts`) is a possible
  future Cooking slice; unnecessary now since shops sell Soda ash directly.

## Verification

- `tests/test_crafting_data.py::test_molten_glass_matches_furnace_source`
- `tests/test_logic.py::test_molten_glass_smelt_returns_bucket_byproduct`
- Full suites at the end of the integration pass.
