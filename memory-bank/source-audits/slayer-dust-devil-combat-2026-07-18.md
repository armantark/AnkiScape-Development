# Slayer Dust devil Combat closure

Date: 2026-07-18

Status: **the ordinary level-93 Dust devil is executable and advances Vannaka
to 26/35.**

## Cutoff identity and equipment gate

RuneScape Wiki `Dust devil`, oldid `6529409`, timestamp
`2012-11-03T20:26:29Z`, establishes:

- combat level 93, 1,050 LP, level 65 Slayer, and 105 Slayer XP;
- six-tick melee attacks with a 90-LP maximum hit;
- Vannaka, Chaeldar, Sumona, Lapalok, and Kuradal assignment membership;
- guaranteed Bones;
- the Smoke Dungeon and Chaos Tunnels as the two locations; and
- Face mask, Masked earmuffs, Slayer helmet, or Full slayer helmet protection.

The page is unusually explicit that an unprotected player cannot damage the
Dust devil. It also records the resulting constant 145-LP hits and severe
stat/prayer drain. This satisfies owner decision 21's narrow exception for a
hard equipment gate: a hard gate is valid where pinned period evidence says
the player literally cannot damage or continue the target.

AnkiScape therefore uses a continuous head-slot requirement, not the
dangerous-but-legal `protective_equipment` channel used by Basilisks and
Aberrant spectres. `start_equipment.persistent` extends the existing Wall-beast
gate without changing its start-only semantics. Removing the protection during
an active Dust-devil encounter blocks the next Combat review until protection
is restored.

Source:
<https://runescape.wiki/w/Dust_devil?oldid=6529409>.

The target uses the Chaos Tunnels route, which the same cutoff page says does
not impose the Smoke Dungeon's environmental smoke outside the fight. No
Desert Treasure quest gate or quest content is invented, so this slice does
not overlap the Darkan quest-parity thread.

## Combat source

Darkan
`data/npcs/combatdefs/uncategorized/dust_devil.json`
supplies 1,050 LP, maximum hit 90, Attack 105, Strength 70, Defence 40,
Magic 1, Ranged 1, passive aggression, and a 59-tick respawn.

Darkan
`src/main/java/com/rs/game/content/skills/slayer/npcs/combat/DustDevil.java`
and `Slayer.hasMask` independently confirm the protective Face-mask,
Masked-earmuffs, and Slayer-helmet identities. Darkan allows player damage
without the mask and instead applies max-LP/10 damage plus random stat drain;
that emulator behavior conflicts with the direct cutoff page and is rejected
for the gate. It is not blended into an invented hybrid.

The period page's familiar-only Ranged attack has no player-combat effect in
AnkiScape. Exact cutoff defensive bonuses remain `source_blocked`, so the
runtime leaves them at zero rather than borrowing a modern table.

## Ordinary drops

Darkan `data/npcs/drops/dust_devil.json` supplies 21 nonzero ordinary rows:

- 11/128 gem-table and 19/128 herb-table branches;
- Rune dagger 1/128;
- Red d'hide vambraces, 300 Coins, and one 150-Fire-rune row at 2/128;
- Ugthanki kebab and Steel hatchet at 3/128;
- Earth battlestaff, 50 Coins, 37 Fire runes, and two Soul runes at 1/128;
- 12 Rune arrows at 5/128;
- a second 150-Fire-rune row at 8/128;
- 60 Coins at 40/128;
- five Soul runes at 4/128;
- 25 Coins at 6/128;
- Mithril bar at 3/128;
- five Chaos runes and 15 Coins at 7/128; and
- Dragon chainbody at 1/32,768.

Darkan's executable `DropList` puts all nonzero rows into one cumulative
ordinary selector. Their least common denominator is 32,768: 32,513 slots are
occupied and the remaining 255 are empty. Guaranteed Bones and the separately
invoked charm path remain independent.

The referenced `special_tables/herb.json`, `rdt_gem.json`, and
`rdt_mega_rare.json` are the same exact nested tables already used by the
Aberrant-spectre closure. Their shared constants are renamed from the
target-specific `DARKAN_ABERRANT_*` prefix to `DARKAN_*`; their data is
unchanged.

## Charm derivation

Darkan `data/npcs/charmDrops.txt` records Dust-devil thresholds
`12-6-26-1` for Gold, Green, Crimson, and Blue. Its
`src/main/java/com/rs/tools/old/CharmDrop.java` implementation draws one
inclusive 0–100 value, includes every threshold containing that value, and
selects uniformly among the included types.

The resulting exact emulator distribution has denominator 606:

- Gold 31/606;
- Green 13/606;
- Crimson 115/606;
- Blue 3/606; and
- no charm 444/606.

This is exact emulator behavior, not a claim that the cutoff wiki published
the charm rates.

## Items, acquisition, and asset

Face mask item 4164 is already generated head equipment and is available for
200 Coins from multiple live Slayer-equipment shops, including Vannaka,
Turael, Sumona, and Kuradal without a quest gate. Masked earmuffs item 13277
are also live equipment through Smoking Kills.

Red d'hide vambraces item 2489 were already generated equipment. Dragon
chainbody item 3140 is newly source-reachable equipment with the exact body
slot, Defence 60 gate, and cache bonuses. The generator now honours an
optional drop-row `source_item_id` before name fallback; this prevents the
same-name item 2513 from being mistaken for the wearable body.

`combatenemies/dust_devil.png` uses a RuneScape Wiki render. It is visual-only
and is not historical evidence. Exact URL, revision timestamp, and hash are
recorded in `assets_provenance.json`.

## Live mapping

The standard Combat runtime handles Slayer XP, six-tick melee, the persistent
equipment gate, one ordinary selector plus the independent charm selector,
inventory capacity, food, retreat, death, and undo. The picker exposes the
equipment lock, 90-LP maximum hit, representative probabilities, and target
icon.

`tools/audit_slayer_readiness.py` derives Vannaka at 26/35. Nine blockers
remain: eight missing Combat representatives plus Earth warrior's Wilderness
risk. The incomplete master remains hidden and unrenormalized.

No owner-facing design fork emerged.

## Verification

Final focused, full-suite, offscreen Qt, generator, reachability, documentation,
test-quality, provenance, diff, and worktree results are recorded in
`memory-bank/status-updates/slayer-dust-devil-results-2026-07-18.html`
(<https://dylce5d5v14s.postplan.dev>).
