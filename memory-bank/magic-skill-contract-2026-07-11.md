# Magic Skill Contract — grill closed 2026-07-11

Status: **implemented on `main` at `24fbafd`; the 2026-07-16 Charge duration
amendment is owner-approved but not yet implemented.** The body below preserves
the pre-implementation contract.

This is the implementation-ready contract for the full Magic skill continuation. The
deep grill closed on 2026-07-11 with the owner present; do not re-grill the decisions
recorded here. Remaining open items are mechanical source extractions, marked in the
extraction list at the end. Magic stays under the Combat category per the combat grill
(item 21); noncombat spell actions live under the Magic skill entry there.

## Framing

Magic is currently a partial Combat-trained skill: 16 standard combat spells
(strike→wave families, `combat_data.py:427`), elemental staves with infinite-rune
substitution (`COMBAT_MAGIC_STAFF_DATA`, `combat_data.py:703`), and nothing else. This
slice flips Magic to complete: the full pre-EOC standard book, Ancient Magicks, and the
Lunar book, with alchemy, superheat, enchanting, teleports, charge orbs, telegrab,
conversion spells, and the Lunar skilling utilities.

Sources: game-main implements the standard book only
(`game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/` — SpellbookData.kt,
alchemy/, jewelleryenchanting/, superheat/, telegrab/, teleports/). Everything
game-main lacks (Ancients, Lunar, curse/bind families, bones-to-bananas/peaches,
charge orbs, Iban Blast, Magic Dart, Crumble Undead, Storm of Armadyl, surges' XP
cross-check) is authentic pre-EOC gap-fill via `tools/wiki_parity.py` pinned before
2012-11-20, cited by oldid, per the revised gap-fill policy.

## Existing infrastructure this builds on

- Rune supply is fully solved: 13 Runecrafting altars (air→blood, incl. astral) plus
  live rune shops (Baba Yaga sells through astral/soul/blood; Lundail sells cosmic;
  Magic Guild through law). No new rune wiring needed. Noncombat casts consume runes
  from the bank like any material; combat keeps its rune loadouts.
- Coin economy is live with Darkan cache buy/sell prices in `shop_data.py`. Alch
  values come wholesale from the same cache item definitions.
- The combat preset system (built in the in-flight Prayer slice) is the carrier for
  all combat-side Magic state: autocast spell, Vengeance, Dream, swap slot.
- Skilling actions auto-use the best owned tool (axe/pickaxe precedent); noncombat
  casting treats owned elemental staves the same way, waiving the staff's element
  from the rune cost via the existing substitution table.

## Settled design decisions

1. **Alchemy — full parity, uncapped.** Low (21) and High (55) Alchemy work on any
   tradeable registry item at authentic cache alch values. No invented caps: the
   engine-native bounds are the item consumed plus the nature rune per cast. Staff
   substitution applies (an owned fire staff waives the fire runes). UI: an Alchemy
   target with a bank item picker following the loadout-picker convention; 1 cast
   per review. The owner explicitly declined any faucet safeguard.
2. **Teleports — dual training casts and target-local routes.** The full solo-
   teleport roster across all three books remains available as normal cast targets
   (authentic level/runes/XP and quest gates). Compatible skills/activities may also
   select the same spell through the shared route-profile substrate accepted during
   the Summoning grill. The first travel review consumes exact runes and awards exact
   cast XP once; every rate declares its assumed route so the teleport never stacks a
   second reduction onto a rate that already includes it. This is target-local travel
   abstraction, not persistent location or a standalone transport network.
3. **All three spellbooks in this slice.** Standard completion + Ancient Magicks
   (Desert Treasure gate) + Lunar (Lunar Diplomacy gate). This gives astral, cosmic,
   nature, law, and blood runes their consumers.
4. **Implicit spellbook, strict no-mixing.** No current-spellbook player state and no
   toggle; each target/autocast implies its book, quest gates are the only locks.
   But one go — one combat preset, one skilling stint — may not mix books: pure
   logic derives the preset's book from all its selected magic effects and rejects
   mixes (Vengeance is Lunar, so veng pairs with melee/ranged or Lunar casting,
   never an Ancients autocast). Skilling targets are single spells, so the
   constraint holds by construction there.
5. **Spellbook Swap (Lunar 96) is the single sanctioned no-mixing exception.** A
   preset/stint whose spells are otherwise one-book may include exactly one off-book
   spell if the player has 96 Magic + Lunar Diplomacy, paying the swap's rune cost
   (3 astral, 2 cosmic, 1 law) per fight/stint on top of the spell's own runes.
6. **Dream (Lunar 79) — review-cost heal policy.** A combat preset option: between
   fights, missing HP heals via Dream casts at a review cost derived from its
   authentic heal rate (rune cost per cast, small Magic XP), reducing food
   consumption in exchange for slower stint throughput. Reviews are our time.
7. **Casual mode: dial + three toggles.** The three-position pack-mode dial
   (balanced / max_output / max_safety) auto-derives prayer/curse selection, uptime,
   Vengeance, and the swap slot from the player's levels and unlocks (max_safety →
   protection prayer vs the enemy's strongest style + Dream + conservative uptime;
   max_output → best offensive prayer/curse + aggressive uptime). Casual mode
   surfaces exactly three toggles: (1) Prayers/Curses master on/off, (2) autocast
   spell picker shown only when the preset wields a magic weapon, (3) Dream thrift
   toggle. Everything else lives in the advanced preset editor. Owner note: "we'll
   probably have to tweak it" — the toggle set is expected to iterate, keep it
   data-driven. The derivation ships in this slice as a layer atop the Prayer
   slice's preset machinery; do not churn the in-flight Prayer work.
8. **Salvage ledger — spells with preserved function:**
   - Bake Pie (65): no-burn Cooking method; casts cook uncooked pies, Magic +
     Cooking XP.
   - Humidify (68): batch-fills owned water vessels (buckets, jugs, vials) per cast.
   - Hunter Kit (71): produces the kit tool items (registry items awaiting Hunter —
     standard output-orphaned state).
   - Superglass Make (77), Tan Leather (78), String Jewellery (80), Plank Make (86):
     direct material transforms feeding Crafting/Construction; Plank Make output is
     output-orphaned until Construction and ships anyway.
   - Magic Imbue (82): waives the opposing talisman on the existing
     `COMBINATION_RUNE_TARGETS` crafts while active during an RC stint.
   - Crumble Undead: combat spell restricted to undead enemies (roster has them).
   - Monster Examine (66): pure cast on the selected combat target; the cast result
     displays the enemy's authentic stat block (info is already free in the UI —
     no gating).
   - Telegrab: the authentic acquisition route for Wine of Zamorak (Herblore
     secondary), 1 grab/review, air+law runes, 43 XP, wiki-pinned; other grab
     targets only if source-backed.
9. **Pure-cast bucket (world/self-targeted, function abstracted or awaiting a
   skill):** all solo teleports, Cure Plant (66), Fertile Soil (83), NPC Contact
   (67), Dream's castable form is covered by decision 6. **Farming-pass note
   (owner-mandated): when Farming ships, Cure Plant and Fertile Soil must gain real
   function — e.g. a farming-run option/checkbox — not stay ceremonial.** This note
   is mirrored on the Farming kanban card.
10. **not_applicable bucket (strictly require a second player):** Tele-other ×3,
    all Tele Group variants, Cure Other/Group, Heal Other/Group, Stat Spy, Stat
    Restore Pot Share, Boost Potion Share, Energy Transfer, Vengeance Other,
    Teleport Block (PvP-only).
11. **Livid Farm spells deferred** (Vengeance Group, Disruption Shield, and the
    other Livid Farm unlocks): they wait for the Livid Farm activity grill — their
    unlock is a grindy points economy, not a one-time landmark. The Lunar book is
    otherwise complete this slice.
12. **God spells + Charge** unlock via a one-time Mage Arena landmark activity
    (Knight Waves / stronghold landmark pattern). Charge's cape/staff boost per
    pinned sources.
13. **Charge orbs** close the reachability audit's elemental-orb orphan category:
    unpowered orb + 30 elemental runes + 3 cosmic per cast (obelisk travel
    abstracted), outputs feed battlestaff Crafting.
14. **Enchanting** ships all gem tiers × rings/necklaces/amulets/bracelets from
    game-main `EnchantmentData.kt`, plus the enchant-bolt spell ladder (wiki-pinned).
    Enchanted outputs carry their cache equipment stats; Ring of recoil gets the
    existing deflect-style EV. Teleport jewellery supplies exact-charge alternate
    routes through the same target-local substrate as teleport spells and familiar
    teleports.
15. **Combat ladder gap-fill:** surges (81–95) and Wind Rush from game-main
    SpellbookData (present there, omitted from Combat V1 by oversight); god spells
    (60); Iban Blast (quest-gated, Underground Pass), Magic Dart (Slayer staff —
    ships input-starved), Crumble Undead, Storm of Armadyl (77; its Armadyl
    components are already orphaned registry items), the bind family
    (bind/snare/entangle → freeze-style EV) and curse family
    (confuse/weaken/curse/vulnerability/enfeeble/stun → stat-drain EV), all pinned
    pre-EOC where game-main lacks them.
16. **Ancients EV:** in single-enemy fights, burst/barrage multi-target value is
    moot (hits one target); smoke = poison EV, shadow = accuracy-drain EV, blood =
    heal-on-damage EV (Soul Split toolkit), ice = freeze EV (enemy hits skipped =
    freeze duration / enemy attack interval, capped by fight length). Reuse the
    curse EV toolkit from the Prayer contract.
17. **Conversion spells:** Bones to Bananas (15) and Bones to Peaches (60,
    behind its Mage Training Arena unlock only if MTA evidence is pinned; otherwise
    flag) convert inventory bones — an authentic tension with Prayer's bone demand,
    left to player choice.
18. **Superheat (43):** 53 Magic XP + authentic Smithing XP per bar, nature rune
    cost, consumes ore per the smelting tables (game-main superheat plugin).
19. **Pacing:** 1 cast per review everywhere; per-cast batch semantics stay
    authentic (Superglass/Humidify process the authentic inventory batch per cast).
    Audited XP stays in data; AnkiScape knobs stay separate.
20. **Undo:** every cast reward survives Anki undo rollback like existing actions.

## Implementation-time extraction list (mechanical, no product decisions)

1. Full standard-book roster from game-main `SpellbookData.kt` (levels, runes, XP —
   includes teleport XP values and surge/god-spell entries).
2. Alch value extraction wholesale from Darkan cache item definitions (the same
   source shop prices already use); low = authentic low-alch value, high = high-alch
   value, per item.
3. Enchantment table from `EnchantmentData.kt` + enchant-bolt ladder (wiki pin).
4. Ancients roster (wiki pin: Ancient Magicks page pre-EOC oldid) — levels, runes,
   max hits, effect magnitudes/durations.
5. Lunar roster (wiki pin: Lunar spells page pre-EOC oldid) — levels, runes, XP,
   batch sizes for Superglass/Humidify/Bake Pie/Tan Leather/String Jewellery/
   Plank Make (Plank Make per-plank coin cost included).
6. Curse/bind family numbers (wiki pins) + Iban Blast / Magic Dart / Crumble Undead /
   Storm of Armadyl pins.
7. Charge orb data (obelisk requirements, XP) — game-main lacks it; wiki pin.
8. Wine of Zamorak telegrab pin (XP 43, spawn abstraction note).
9. Mage Arena landmark + Charge spell + god cape/staff pins.
10. Dream heal-rate → review-cost derivation (documented as an AnkiScape knob on top
    of the authentic heal rate).
11. Casual-dial derivation rules (data-driven table, expected to iterate).

## Dependency-blocked items (do not build now)

- Livid Farm spell set → Livid Farm activity card.
- Cure Plant / Fertile Soil real function → Farming card (note mirrored there).
- Plank Make consumers → Construction.
- Hunter Kit consumers → Hunter.
- Magic Dart's Slayer staff acquisition → Slayer.

## Charge duration amendment — 2026-07-16

Status: **owner-approved design; implementation pending on `main`.**

Charge uses the shared review-driven temporary-effect clock, never wall time and
never the answered-card world/economy calendar. At 1x Actions per Review, every
successful review advances temporary effects by 50 game ticks; the advancement
scales linearly with Actions per Review. The source 700-tick Charge duration is
therefore fourteen successful reviews at 1x.

Temporary effects advance during simulated activity globally, including safe
non-combat reviews, so Charge dissipates out of combat rather than pausing. A
review that casts Charge advances already-active durations first and installs
the new Charge state afterward, preserving its full duration. The cadence
kernel remains an action-admission/rate scheduler, not this global effect clock.
