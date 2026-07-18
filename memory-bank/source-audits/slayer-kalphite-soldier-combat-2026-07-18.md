# Slayer Kalphite Soldier Combat audit — 2026-07-18

Status: **source closed for the ordinary level-85 representative**.
Cutoff: `2012-11-20T00:00:00Z`.

## Executable boundary

Admit the ordinary level-85 Kalphite Soldier as the executable representative
for Mazchna/Achtryn's Kalphites assignment family. Kalphite workers, guardians,
the Kalphite Queen, and other variants remain distinct content. This closes the
current family-readiness dependency without claiming the entire Kalphite
species roster.

## Period evidence

RuneScape Wiki `Kalphite Soldier`, oldid `6565809`, timestamp
`2012-11-17T10:22:49Z`:
<https://runescape.wiki/w/Kalphite_Soldier?oldid=6565809>.

The cutoff revision records for this ordinary form:

- Combat 85, 900 life points, and 90 Slayer XP;
- a six-tick stab-style melee attack with an approximate 80-LP maximum hit;
- aggressive and poisonous behavior with an initial poison hit of 48 LP;
- Mazchna assignment membership; and
- no guaranteed drop.

The 80-LP hit is admitted as the source's period approximation because it is
the best surviving cutoff value and Darkan independently encodes the same
number.

## Emulator reconciliation

Darkan combat definition:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/kalphite_soldier.json`

It supplies a 59-tick respawn, 900 life points, maximum hit 80, melee style,
aggressive behavior, and Attack 70, Strength 70, Defence 70, Magic 1, and
Ranged 1. Its generic `CRUSH_ATT` label conflicts with the cutoff page's
explicit stab description. The period page therefore controls the descriptive
substyle; the current Combat row has no sourced numeric attack bonus to encode,
so the conflict does not alter damage math.

Darkan drop definition:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/kalphite_soldier.json`

Its nineteen mutually exclusive entries sum exactly to 128:

- Coins 120/40/200/10/450 at 40/29/10/7/1 slots;
- Fire rune 60/30 at 8/1 slots, Chaos rune 12 at 5, Death rune 3 at 3,
  and Nature rune 1 at 2;
- Steel full helm 4, Steel hatchet 4, Steel scimitar 3, Rune chainbody 1,
  Mithril sq shield 1, and Adamant med helm 1;
- Waterskin (4) at 3;
- the shared gem table at 4; and
- the shared minor-herb table at 1.

All concrete drop identities already resolve through the live item registry.
No name-only item or new economy abstraction is introduced.

## Asset and runtime contract

The target image uses the `2012-03-08T01:49:01Z` revision of
`Kalphite Soldier.png`, fetched through the repository's cutoff-aware asset
pipeline.

The target reuses the existing source-backed Combat poison channel, whose
game-main-shaped initial-damage unit represents ten life points and therefore
cannot encode 48 exactly. The row uses the nearest representable value, 50 LP,
rather than misreading `48` as 480 LP or silently rounding down to 40. A
successful poisoning attack then uses the shared poison cadence, antipoison,
death/grave, persistence, and undo behavior. The repository's existing 40%
poison-on-success abstraction remains unchanged; the cutoff page establishes
that the target is poisonous and the initial magnitude, not a distinct
per-attack chance.

No owner design decision is required.
