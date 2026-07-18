# Slayer Feral vampyre Combat audit — 2026-07-18

Status: **source closed for the ordinary level-61 representative**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Executable boundary

Admit the ordinary level-61 Feral vampyre as the executable representative for
Mazchna/Achtryn and Vannaka's Vampyres assignment family. This is the ordinary
all-weapons-vulnerable creature reached after Priest in Peril, not a Vampyre
Juvinate, Vyrewatch, God Wars variant, Temple Trekking encounter, or
Daemonheim creature.

## Period evidence

RuneScape Wiki `Feral vampyre`, oldid `6545273`, timestamp
`2012-11-09T21:17:01Z`:
<https://runescape.wiki/w/Feral_vampyre?oldid=6545273>.

The cutoff revision records:

- level variants 61, 72, and 77, with the ordinary level-61 creature selected
  here;
- 400 life points and 40 Slayer XP for the level-61 variant;
- aggressive melee combat, a six-tick attack, and a 74-LP maximum hit;
- Mazchna and Vannaka assignment membership;
- poison susceptibility and a guaranteed Vampyre dust drop;
- ordinary weapon vulnerability, unlike the special Vampyre Juvinate weapon
  rules;
- a Holy symbol weakness that lowers the creature's accuracy and damage; and
- an occasional bite that drains a combat or non-combat skill while healing a
  small amount of the Vampyre's life points.

Priest in Peril is the existing route into Morytania and is already the
Mazchna master gate. The Combat target uses the same completed-quest state
instead of introducing a second unlock.

The cutoff page preserves the direction of the Holy-symbol and bite effects
but not executable numeric magnitudes. The runtime therefore labels and uses
the following bounded abstractions:

- a worn ordinary `Holy symbol` multiplies enemy accuracy and maximum hit by
  `0.8`; and
- each landed damaging attack has a `1/8` bite chance. A bite heals no more
  than the damage dealt or 20 LP and drains one uniformly selected implemented
  skill by one current level, to a floor of 1.

The random skill set contains every implemented main skill with a current-level
identity and excludes Dungeoneering, which is not live. These values are
deliberately data-declared so later surviving evidence can replace them without
rewriting the Combat loop. The UI names the Holy-symbol effect and the review
result reports bite healing instead of mislabeling it as passive regeneration.

## Emulator reconciliation

Darkan combat definition:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/vampyre/vampyre_(61).json`

It supplies NPC 1223, 400 life points, aggressive melee, Attack 55, Strength
60, Defence 55, Magic 0, Ranged 0, and a 59-tick respawn. Its 70-LP maximum
hit conflicts with the cutoff page's explicit 74-LP value, so the period page
controls that field.

Darkan drop definition:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/vampyre.json`

Vampyre dust, cache item 3325, is a separate guaranteed row. The 41 ordinary
probability rows reconcile losslessly to one 100,000-slot table:

- four rows at `5247/25000` become 20,988 slots each;
- twenty rows at `699/100000` remain 699 slots each;
- twelve rows at `143/100000` remain 143 slots each;
- five rows at `37/100000` remain 37 slots each; and
- 167 slots remain empty.

Every output already has a canonical live item identity, including cache item
3325 as `Vampyre dust`, cache item 12176 as `Spirit weed seed`, and cache item
21620 as `Morchella mushroom spore`. No duplicate item rows or acquisition
routes are introduced.

## Asset and runtime contract

The target image uses the `2011-08-18T17:21:50Z` revision of
`Vampire (historical) (level 61).png`, fetched through the cutoff-aware asset
pipeline. The generic remembered title `Vampire (level 61).png` does not
resolve on the current file API; the historical title is the provenance-backed
identity.

The existing Combat selection, encounter persistence, death/grave, poison,
Slayer credit, drop, achievement, persistence, and review-undo paths remain
authoritative. Holy-symbol weakening is evaluated from the equipped neck slot
for both preview and live attacks. Bite RNG is consumed only after a landed,
damaging enemy attack and cannot resurrect a Vampyre killed by Vengeance or a
deflect curse.

No owner design decision is required.
