# Construction Skill Contract — grill closed 2026-07-11

Status: **implemented on `main` at `c628f0d`.** The body below preserves the
pre-implementation contract and its extraction checklist.

This is the implementation-ready contract for the Construction skill. Every
decision below is settled; do not re-grill any of them. The remaining work
before code is the mechanical extraction list at the bottom.

## Framing

Construction is the first skill whose primary source is Darkan, not
game-main: the 2011Scape emulator has **no Construction implementation at
all**, while the Darkan world server carries the complete Nov-2012 build
data (rooms, furniture, servants, sawmill, tablets). Per the gap-fill policy
and the Darkan-supersedes-wiki memory, the Darkan tables at the pinned
checkout are primary; the pre-EOC wiki (cutoff 2012-11-20, cited by oldid)
covers only the two behaviors Darkan defines as data but never implements
(burner lighting, flatpack crafting). Those two gaps are documented for the
restoration loop in
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/handoffs/ankiscape-construction-gap-discoveries-2026-07-11.md`.

Darkan source root:
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/construction/`
(HouseObjects.kt, HouseRooms.kt, HouseConstants.kt, HouseServants.kt,
SawmillOperator.java, TabletMaking.java, EstateAgentDialogue.java). Cite the
same pinned Darkan commit the Prayer build used (`7e7d67b`) unless the
restoration has declared a newer milestone by implementation time.

## Existing infrastructure this builds on

- `constants.py:316-332` — sawmill utilities already convert regular
  (100c) and oak (250c) logs to planks; `make_soft_clay` already exists and
  is the default utility.
- Magic's Plank Make already produces all four plank tiers (the
  `magic_data.py:412` cost path), so shipping Construction closes its
  output-orphan note.
- Teak/mahogany logs are live Woodcutting targets (levels 35/50); nails are
  smithable (`smithing_data.py` TYPE_NAILS family); limestone is mineable at
  level 10.
- Prayer's hosted gilded-altar flow (`ed1327b`) is the integration point for
  the owned-house altar, and its contract explicitly deferred the
  owned-altar/burner question to this grill.
- The landmark-activity pattern (Knight Waves, Mage Arena) covers one-time
  step-counter unlocks wired outside `UTILITY_ACTIVITY_DATA`.

## Settled design decisions

1. **Hybrid house model (owner).** Construction trains through flat XP
   build targets drawn from the full Darkan `HouseObjects.kt` table (one
   build action per successful review, materials consumed per the table),
   while a persistent **house sheet** tracks durable state: which rooms are
   bought (coins + level per the `HouseRooms.kt` ladder), which servant is
   hired, and altar/burner status. Build targets gate on their room being
   bought; rooms are the coin sink, builds are the XP.
2. **Servants as a batch boost (owner).** Hiring a servant raises the
   per-review build batch for material-consuming builds, tiered by the
   Darkan servant ladder (Rick 375c/lvl 20, Maid 750c/25, Cook 2250c/30,
   Butler 3750c/40, Demon butler 7500c/50, speeds from `bankDelay`). Wages
   are paid per stint via the sanctioned batching-per-review device; no
   trip/inventory simulation is invented.
3. **Owned gilded altar (owner, closes the Prayer deferral).** Once the
   Chapel, a gilded altar, and burners are built, Prayer's hosted-altar
   flow gains an owned-house variant with **no 1–10 house-finding roll**.
   Lighting consumes **one clean marrentill per burner** per stint (Chapel
   pin `2012-10-14T18:39:20Z`; Mahogany burners pin `2011-12-06T22:57:30Z`);
   +50% Prayer XP per lit burner on top of the altar bonus, 350% with a
   gilded altar and both burners. Any-herb lighting is post-EOC RS3 and is
   excluded. All three burner kinds give the same bonus (they differ only
   as Construction builds).
4. **Flatpacks ship as wiki gap-fill (owner).** Darkan never implemented
   flatpack crafting, so the pack list comes from a pre-EOC wiki pin at
   implementation time. Workbench-tier gating per the `HouseBuilds.kt`
   workbench ladder; a flatpack grants the same XP as the normal build and
   produces a tradeable, sellable item.
5. **House sheet UI: a section inside the Construction skill tab (owner).**
   A compact summary strip (rooms, servant, altar/burner status) above the
   build-target list, expandable to the room-by-room view. No new top-level
   tab, no function panel: the sheet is a room inventory, and functions
   that do not apply in AnkiScape simply never surface on it.
6. **Full build table, no curation (autonomous).** Every `HouseObjects.kt`
   row ships as a live build target under the standard material/level/room
   gates; decorative furniture is training-only. Input-starved rows ship
   live and un-flagged per the house rule.
7. **Function-trails ledger (autonomous).** Builds whose in-game function
   has no AnkiScape analog ship for XP with the function trailing:
   - Menagerie → pet system (none exists).
   - Whetstone/armour stand (`HouseObjects.kt:393-394`) → equipment
     degradation/repair (none exists).
   - Costume-room storage (armour cases, costume boxes, treasure chests,
     `HouseObjects.kt:172-201, 589-593`) → moot; the Bank already stores
     everything.
   - Portal Chamber (`HouseObjects.kt:283-297`, frames at 50, directed
     portals at 80 consuming hundreds of runes) → travel is moot; portals
     are high-level rune-sink builds, exact parity with Magic's
     teleports-as-pure-training-casts. Pre-EOC authentic, not OSRS-only.
   - Amulet-of-glory mounting, exit portal, and similar service builds →
     moot the same way.
8. **Lectern tablets (autonomous).** Per `TabletMaking.java`: Magic-level
   gated, consume soft clay plus the spell's rune set at the appropriate
   lectern tier, award **Magic** XP, and produce tradeable tablet items
   (travel-abstracted like all teleports). This is a Construction-enabled
   Magic method, not Construction XP.
9. **Materials economy (autonomous).** Planks via the existing sawmill
   utilities plus new teak (500c) and mahogany (1500c) tiers per
   `SawmillOperator.java`; soft clay via the existing utility; limestone
   bricks via an authentic Crafting gap-fill row (chisel mined limestone);
   nails from Smithing with tier-based bend chance from a pre-EOC pin;
   bolt of cloth, gold leaf, marble block, and magic stone as shop rows
   (Darkan `construction_supplies` / stonemason pricing, wiki-pinned at
   implementation). House styles ship as an optional cosmetic coin-sink row
   on the house sheet per the estate-agent ladder.

## Post-closure clarifications (owner Q&A, 2026-07-11)

Four points the owner probed after closure; all resolved, none reopen the
nine decisions above.

- **Build-and-remove is implicit in repetition.** The authentic primary
  training method (build a piece, demolish it, build it again) is exactly
  what a repeatable flat XP target models: each successful review is one
  build+remove cycle, materials consumed, nothing reclaimed (authentic —
  removing furniture returns no materials). No visible demolish mechanic.
  Stateful rows (altar, burners, workbench) set their house-sheet flag
  permanently on first successful build and remain repeatable as pure
  training afterward.
- **Initial house purchase: rung zero of the room ladder.** A one-time
  instant coin purchase on the house sheet, exactly like buying a room.
  Price and starting-room set come from a pre-EOC wiki pin at
  implementation (expected 1,000 coins from an estate agent),
  cross-checked against Darkan.
- **Crystal saw ships (uses the existing boost substrate).** Darkan
  implements it: `House.kt:468` adds +3 to the effective Construction
  level for non-water builds when item 9625 is held. AnkiScape's
  current-vs-base level substrate (the potion boost model in
  `logic_pure.py`) already accepts any skill id, so this is a held-item
  +3 on build level checks, gated behind The Eyes of Glouphrie (already
  in the quest catalog). Spicy stew is authentic too but lives on the
  RFD/Evil Dave side and trails there.
- **Whetstone/armour stand confirmed as function trails.** Owner wants an
  equipment degradation/repair system eventually; the builds ship now and
  their repair function lights up when that system exists (already a
  kanban dependency item).

Darkan discovery for the handoff file: `EstateAgentDialogue.java:64`
labels Fremennik-style wood "25,000 coins" but the code passes 20000 —
the pre-EOC wiki says 25,000, so the code value looks wrong.

## Implementation-time extraction list (mechanical, no product decisions)

- Full `HouseObjects.kt` build table → data module rows (itemId, level, XP,
  materials), grouped by room; `HouseRooms.kt` price/level ladder.
- Servant wage/speed table from `HouseServants.kt`; translate `bankDelay`
  tiers into batch sizes.
- Sawmill teak/mahogany utility rows (500c/1500c) from
  `SawmillOperator.java`.
- Flatpack list + workbench tiers: pre-EOC wiki pin required (record the
  oldid in the data module).
- Nail bend-chance column: pre-EOC wiki pin (Construction or Nails page).
- Limestone brick Crafting row (level, XP): pre-EOC wiki pin.
- Specialty material prices (bolt of cloth, gold leaf, marble block, magic
  stone): Darkan shop table, cross-checked against a pre-EOC pin.
- Tablet ladder from `TabletMaking.java` (lectern tiers, spells, Magic
  levels, XP).
- House style ladder and prices from `EstateAgentDialogue.java`.
- Estate-agent room-count/build-level caps if Darkan enforces them.
- Asset manifest derived from the data module via a
  `tools/fetch_construction_assets.py` following the Prayer/Magic pattern.

## Dependency-blocked items (do not build now)

- Menagerie pet function → a future pet system.
- Armour stand repairs → a future equipment-degradation system.
- Brewery, spice rack, and other consumable-producing builds whose outputs
  feed systems that do not exist ship as builds with output-orphaned items
  per the reachability policy.
- The owned-altar variant requires the Prayer integration hooks from
  `ed1327b`; no separate Prayer changes beyond the variant flag.
