# Slayer Mogre Combat audit — 2026-07-18

Status: **combat source closed; runtime dependency-blocked by the Mogre
miniquest**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Executable boundary

The ordinary level-60 Mogre is the correct representative for Mazchna/Achtryn's
Mogres assignment family. It must not become selectable until the player has
completed the Mogre miniquest and can spend one ordinary Fishing explosive to
lure one encounter from an ominous fishing spot.

The existing Slayer family row already encodes the stable completion ID
`skippy_and_the_mogres` and the `lure` readiness feature. The completion ID is
not present in the live quest catalog, so adding only the Combat target would
create a permanently locked row while incorrectly advancing the readiness
ledger. This slice therefore records the complete target contract and leaves
the family dependency-blocked for the quest-owned implementation.

## Period evidence

RuneScape Wiki `Mogre`, oldid `6493220`, timestamp
`2012-10-29T17:57:37Z`:
<https://runescape.wiki/w/Mogre?oldid=6493220>.

The cutoff revision records:

- Combat 60, 480 life points, Slayer 32, 48 Slayer XP, Mazchna and Vannaka
  assignment membership;
- aggressive melee combat, six-tick attack speed, 89-LP maximum hit, low
  Defence, Ranged weakness, and poison immunity;
- one guaranteed Big bones drop;
- completion of the Mogre miniquest before any Mogre can be killed;
- one Fishing explosive used on an ominous fishing spot to lure the Mogre that
  attacks that player; and
- only one spawned Mogre at a time.

`Fishing explosive`, oldid `6153110`, timestamp
`2012-08-27T17:08:17Z`, corroborates that the stackable, non-tradeable,
60-coin Slayer-master item is consumed to lure a Mogre:
<https://runescape.wiki/w/Fishing_explosive?oldid=6153110>.

The live shop catalog already carries cache item 6664 in the period Slayer
shops at 60 coins. The item is registered, stackable, reachable, and has an
installed icon, so no new shop policy is required.

`Super fishing explosive`, oldid `6333518`, timestamp
`2012-10-02T12:50:19Z`, records the optional post-`Kennith's Concerns`
alternative: Herblore 31, Guam potion (unf) plus Rubium, 55 Herblore XP, and an
immediate 150-LP hit when it lures the Mogre:
<https://runescape.wiki/w/Super_fishing_explosive?oldid=6333518>.

That alternative is not part of the minimum executable boundary. Rubium, the
recipe, and the finished item are not live. Preserve it as a
Herblore/quest-acquisition dependency rather than inventing a second shop row.

## Miniquest dependency

RuneScape Wiki `Mogre (lore activity)`, oldid `6070158`, timestamp
`2012-08-10T03:44:02Z`:
<https://runescape.wiki/w/Mogre_%28lore_activity%29?oldid=6070158>.

The period miniquest is a short non-combat chain:

1. Cooking 20 and the listed supplies are required.
2. Use a Bucket of water to sober Skippy.
3. Make and give Nettle tea.
4. Make Chocolatey milk from Chocolate dust and a Bucket of milk, add Snape
   grass, and give the resulting Hangover cure.
5. Completion grants the ability to kill Mogres at Slayer 32.

The supporting `Skippy` page, oldid `6274860`, timestamp
`2012-09-21T07:00:52Z`, independently describes the same three hand-ins and
states that Mogres cannot be killed beforehand:
<https://runescape.wiki/w/Skippy?oldid=6274860>.

This is quest/activity-owned one-time state. It must not be simulated by a
permanent Combat unlock, a Slayer shop purchase, or automatic completion when
the first Fishing explosive is used. The Darkan quest agent handoff is recorded
in `memory-bank/codex-briefs/darkan-quest-agent-handoff-2026-07-18.md`.

## Emulator reconciliation

Darkan combat definition:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/mogre (noanims).json`

It supplies 480 life points, melee style, aggression, Attack 58, Strength 55,
Defence 48, Magic 1, Ranged 1, an 89-LP maximum hit, and a 59-tick respawn.
These values do not conflict with the cutoff page.

Darkan drop definition:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/mogre.json`

Its mutually exclusive main table is exactly 128 slots:

| Slots | Output |
|---:|---|
| 30 | 5 Fishing bait |
| 20 | 1 Raw swordfish |
| 13 | one `common_seeds` roll |
| 10 | 15 Fishing bait |
| 9 | 1 Raw tuna |
| 7 | 1 Raw pike |
| 5 | 1 Mudskipper hat |
| 4 each | 5, 7, or 14 Water runes; 1 Raw salmon |
| 3 each | 1 Raw herring, Raw sardine, Raw shark, or Oyster |
| 2 each | 1 Flippers or Seaweed |
| 1 | 1 Staff of water |

Big bones are a separate guaranteed row. Darkan's shared
`long_curved_bone` tertiary table adds Curved bone at `1/5000` and Long bone at
`1/400`.

The cutoff page's drop table is qualitative and includes additional rows that
do not survive with probabilities. Use Darkan's exact 128-slot table for the
ordinary roll instead of inventing weights for those qualitative entries.
`Mogre bone` is explicitly conditional on the Rag and Bone Man wish list and
must remain quest-context loot rather than an ordinary drop.

Mudskipper hat and Flippers need canonical item rows and pre-cutoff icons when
the target is implemented. Every other direct output already has a canonical
identity; the `common_seeds` expansion must be validated against the live seed
registry at implementation time.

## Asset and runtime contract

Use the `2011-11-26T04:39:41Z` revision of `Mogre icon.png` for the Combat
target. The archived bitmap is 22 × 28 and predates the cutoff.

The eventual action is atomic: verify the miniquest, Slayer 32, and one Fishing
explosive; consume exactly one explosive; then start one ordinary persistent
Combat encounter. A blocked start consumes nothing. Normal death/grave, food,
equipment, Slayer credit, drops, persistence, and review undo remain
authoritative. Poison immunity suppresses the already-live Ancient Smoke
poison effect.

No owner design decision is required. The only blocker is the exact quest-owned
completion state.
