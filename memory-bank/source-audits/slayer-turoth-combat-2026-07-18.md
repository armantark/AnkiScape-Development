# Slayer Turoth Combat source audit — 2026-07-18

## Decision

Implement the ordinary level-83 Turoth as Vannaka's 34th executable family.
The target is source-ready and does not require an owner-facing design choice.
It uses the existing review-native Combat encounter, with ineffective attacks
represented as a precise pre-review lock rather than spending a review on
zero damage.

## Period authority

RuneScape Wiki `Turoth`, oldid `6565315`, timestamp
`2012-11-17T07:13:42Z`, is inside the frozen cutoff:
<https://runescape.wiki/w/Turoth?oldid=6565315>.

The revision's infobox and body establish:

- levels 83, 85, 87, 88, and 89;
- 760 LP and 76 Slayer XP for the level-83 representative;
- Slayer 55;
- passive six-tick melee;
- a 97-LP maximum hit for level 83;
- guaranteed Bones and poison immunity;
- ineffective attacks unless the player uses a Leaf-bladed spear,
  Leaf-bladed sword, Magic Dart, Broad arrows, or Broad-tipped bolts.

The level-83 representative is the smallest ordinary member and follows the
existing one-representative-per-Slayer-family contract. The period page lists
drop contents and rarity bands, but not a complete numeric table.

## Combat definition

Darkan
`data/npcs/combatdefs/uncategorized/turoth/turoth_(83).json:1-30`
supplies 760 LP, Attack 53, Strength 83, Defence 83, Magic 1, Ranged 1,
passive melee, a 97-LP maximum hit, and a 59-tick respawn.

Darkan `developer-information/npcListBonuses.txt:1630` supplies zero attack
bonuses, +20 slash defence, +20 crush defence, zero stab/Magic/Ranged defence,
and zero strength bonuses.

## Effective-damage routes

Darkan
`src/main/java/com/rs/game/content/items/CombatEnhancers.kt:136-156`
sets overall damage to zero unless:

- melee uses item 4158 or 13290;
- Ranged uses compatible Broad arrows or Broad-tipped bolts;
- Magic uses `MAGIC_DART`.

The live lock preserves all three combat classes:

- Leaf-bladed spear or Leaf-bladed sword for melee;
- Broad arrows from a Magic shortbow/longbow or Broad-tipped bolts from a Rune
  crossbow for Ranged;
- Magic Dart with the canonical obtainable `Slayer's staff`.

The Ranged integration also closes the previously deferred source-backed Broad
arrow compatibility and enforces ammunition skill requirements before combat.
Magic Dart's stale `Slayer staff` spelling is corrected to the existing
`Slayer's staff` shop/equipment identity. The staff is now recognized as a
Magic staff rather than a generic melee weapon.

The period Staff of light alternative is not manufactured in this slice. It
has no live AnkiScape acquisition route yet and belongs with its own Slayer
drop family. This omission does not block Turoth because the obtainable
Slayer's staff route is live and exact.

## Executable drops

Darkan `data/npcs/drops/turoth.json:1-447` contains guaranteed Bones and 37
non-zero ordinary rows. Darkan
`src/main/java/com/rs/utils/drop/DropList.java:43-68,98-109` sorts those rows
into one mutually exclusive cumulative selector and appends the remaining
probability as empty.

The exact 100,000-slot ordinary selector is:

| Output | Slots |
|---|---:|
| Grimy guam | 5,597 |
| Grimy marrentill | 5,597 |
| Grimy tarromin | 5,597 |
| Grimy harralander | 5,597 |
| Limpwurt root | 5,597 |
| Law runes ×3 | 5,597 |
| Coins ×44-440 | 5,597 |
| Steel platelegs | 5,597 |
| Mithril kiteshield | 5,597 |
| Mithril hatchet | 5,597 |
| Poison ivy seed | 5,597 |
| Cactus seed | 5,597 |
| Belladonna seed | 5,597 |
| Toadflax seed | 5,597 |
| Irit seed | 5,597 |
| Grimy ranarr | 1,272 |
| Grimy irit | 1,272 |
| Grimy avantoe | 1,272 |
| Grimy kwuarm | 1,272 |
| Nature runes ×3-15 | 1,272 |
| Adamant full helm | 1,272 |
| Rune dagger | 1,272 |
| Avantoe seed | 1,272 |
| Snapdragon seed | 1,272 |
| Cadantine seed | 1,272 |
| Morchella mushroom spores ×3 | 1,272 |
| Death runes ×50 | 186 |
| Grimy cadantine | 169 |
| Grimy dwarf weed | 169 |
| Grimy lantadyme | 169 |
| Mystic robe bottom (light) | 169 |
| Ranarr seed | 169 |
| Kwuarm seed | 169 |
| Lantadyme seed | 169 |
| Dwarf weed seed | 169 |
| Torstol seed | 169 |
| Leaf-bladed sword | 169 |
| Empty | 177 |

The 159/12,500 rows are losslessly scaled to 1,272/100,000 and the
93/50,000 Death-rune row to 186/100,000. These exact rates are labeled Darkan
executable parity, not period-rate parity.

Darkan `data/npcs/charmDrops.txt:163` gives `7-22-5-1`.
`src/main/java/com/rs/tools/old/CharmDrop.java:51-94` rolls an inclusive
0-100 value, collects every threshold it meets, and uniformly chooses among
overlapping eligible charms. Lossless enumeration produces the 1,212-slot
selector:

| Output | Slots |
|---|---:|
| Gold charm | 34 |
| Green charm | 214 |
| Crimson charm | 22 |
| Blue charm | 6 |
| Empty | 936 |

Darkan `src/main/java/com/rs/utils/NPCClueDrops.java:160` adds an independent
1/128 hard clue.

## Item identity and art

- Leaf-bladed sword item 13290 is generated one-handed Attack-50/Slayer-55
  equipment with its exact source bonuses and four-tick speed.
- Leaf-bladed spear item 4158 is corrected to Attack 50 and Slayer 55 instead
  of conflating the Slayer requirement with Attack 55.
- Rune crossbow item 9185 uses its literal `items.yml` Ranged-61 equipment
  requirement. The equipment generator no longer substitutes the level-69
  Fletching recipe gate for this item.
- Mystic robe bottom (light) item 4113 is generated legs equipment requiring
  Defence 20 and Magic 40.
- `combatenemies/turoth.png` comes from `Turoth icon.png`, revision
  `2011-11-30T02:42:28Z`, SHA-1
  `a622a84e3c81b6a7db20ad2ff5ff63a9acfe7423`.
- `combatitems/leaf_bladed_sword.png` comes from
  `Leaf-bladed sword.png`, revision `2012-10-08T18:05:04Z`, SHA-1
  `98d23e9e80b992e35fb344158bbb20b6693fdb1c`.
- `combatitems/mystic_robe_bottom_light.png` comes from
  `Mystic robe bottom.png`, revision `2012-03-06T23:33:11Z`, SHA-1
  `2dd6af9c859600d8a2cd6842920525c736be58b9`.

## Scope, workflow, and design-gap record

No owner-facing design fork emerged. The standard representative, Combat lock,
equipment, ammunition, spell, loot, and Slayer-readiness patterns settle the
slice.

The requested independent read-only Codex Workflows checker did not create a
model session. Runtime build `0.1.0+codex.20260718175850`, run
`d5c62383-9fec-401e-bc3a-727b92c1a2dc`, failed with
`provider emitted no startup event within 30s` and zero session, tools, or
tokens. The root reproduced the evidence and arithmetic serially; no native
subagent fallback was used.

After the runtime-update handoff, a fresh bounded two-leaf run
`f94b9cfb-a31e-4400-85b3-3c09c54469f8` failed with the same pre-session
signature on both Sol-high jobs. Each leaf reports one launch attempt, no
session ID, zero tools/tokens, provider exit `-15`, and
`provider emitted no startup event within 30s`. This is a genuinely new run
record, not a replay of the earlier failure. The root again continued serially.

Build `0.1.0+codex.20260718215406` was installed after that failure with a
machine-wide serialized startup handshake and a successful independent
two-leaf smoke proof. The already completed root review was not replayed solely
to exercise the repaired runtime; the next new delegation boundary will use
the installed build.

## Verification

Focused Combat, Slayer, registry, generated-equipment, metadata, and UI
coverage passes all 622 methods with 211 expected non-Qt skips. The focused
real offscreen Qt Combat-picker regression passes.

The first full non-Qt pass exposed a cross-surface regression: registering Rune
crossbow under the generic equipment type `weapon` made the fallback ranged
classifier treat Saradomin staff and other ordinary weapons as ranged. Giving
Rune crossbow a unique `rune_crossbow` type preserves its name-based ranged
route and restores Magic classification. The existing Charge-preview
regression failed before the correction and passes afterward.

Root review also caught a mixed-ammunition edge case: Magic bows list ordinary
arrows before Broad arrows, so a pack containing both Rune and Broad arrows
initially selected the ineffective Rune arrow and locked Turoth. Target-local
ammunition restrictions now narrow selection itself before preview, skill
gating, damage, and consumption. A mixed loaded pack is runnable and previews
`Broad arrows`; a pack with only ordinary arrows still shows the precise
Turoth ammunition lock.

The same route exposed a generated-equipment defect: Rune crossbow had inherited
Fletching 69 as its combat requirement despite the local source item block
declaring Ranged 61. A narrow source-ID override now preserves Ranged 61 in
generated data, and determinism plus focused equipment coverage pin it.

Full non-Qt discovery then passes all 1,661 methods with 215 expected Qt-only
skips. Generated equipment is byte-stable. Test quality reports zero hard
issues across 73 files and 1,661 methods; its four structural-clone groups are
pre-existing and intentional/high-signal. Compilation, JSON parsing, diff
hygiene, and worktree safety pass. Readiness derives Turael/Spria at 23/23,
Mazchna/Achtryn at 26/27, and Vannaka at 34/35, with Mogres the sole blocker
for both incomplete masters. Reachability reports 1,253 actions, 1,851
reachable items, 293 existing orphan inputs, and 320 existing unresolved
actions.

Full real offscreen Qt discovery executes all 1,661 methods with zero skips,
failures, or errors. The documentation audit, rerun after the final status
artifact, reports no issues. Results:
`memory-bank/status-updates/slayer-turoth-results-2026-07-18.html`; mobile copy:
<https://gimdeversiok.postplan.dev>.
