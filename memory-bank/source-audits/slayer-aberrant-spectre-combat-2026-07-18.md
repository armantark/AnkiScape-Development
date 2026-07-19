# Slayer Aberrant spectre Combat closure

Date: 2026-07-18

Status: **the ordinary level-96 Aberrant spectre is executable and advances
Vannaka to 25/35.**

## Cutoff identity

RuneScape Wiki `Aberrant spectre`, oldid `6555339`, timestamp
`2012-11-14T15:17:06Z`, establishes:

- combat level 96, 900 LP, level 60 Slayer, and 90 Slayer XP;
- six-tick Magic attacks with a 119-LP protected maximum hit;
- Vannaka, Chaeldar, Sumona, Lapalok, and Kuradal assignment membership;
- the Priest in Peril route into Morytania;
- no guaranteed drop; and
- Nose peg or Slayer-helmet protection against the stench, with a 160-LP
  unprotected maximum.

Source:
<https://runescape.wiki/w/Aberrant_spectre?oldid=6555339>.

The existing `priest_in_peril` completion gate represents access. This slice
adds no quest definition or quest stage and does not overlap the Darkan
quest-parity thread.

## Combat and stench behavior

Darkan
`data/npcs/combatdefs/uncategorized/aberrant_spectre.json` supplies 900 LP,
maximum hit 119, Attack 1, Strength 1, Defence 90, Magic 105, Ranged 1,
aggression, and a 59-tick respawn.

Darkan
`src/main/java/com/rs/game/content/skills/slayer/npcs/combat/AberrantSpectre.java`
and `Slayer.hasNosepeg` establish the unprotected attack:

- a Nose peg or accepted Slayer helmet disables the special attack;
- otherwise every attack deals one tenth of maximum LP;
- the damage is not blocked by protection prayer;
- without Protect from Magic, one random implemented combat stat is drained by
  five current levels, flooring at zero; and
- Protect from Magic suppresses the drain but not the fixed damage.

The runtime adds one narrow data field,
`stat_drain_protection_prayer`, so that this source behavior is not confused
with Basilisk's inverse rule, where protection prayer blocks damage but the
stat drain remains.

## Drops

Darkan `data/npcs/drops/aberrant_spectre.json` supplies ten weighted ordinary
rows:

- a 78/128 herb-table roll;
- a 19/128 rare-seed-table roll;
- a 5/128 gem-table roll;
- Steel hatchet at 3/128;
- Mithril kiteshield, Lava battlestaff, Adamant platelegs, Rune full helm, and
  460 Coins, each at 1/128; and
- Mystic robe bottom (dark) at 1/512.

`DropList.genDrop` sorts all nonzero ordinary rows into one mutually exclusive
selector. Their least common denominator is 512: the ten rows occupy 441 slots
and the remaining 71 are empty. The separately invoked charm algorithm remains
independent of that selector.

The referenced `special_tables/herb.json`, `rare_seeds.json`, `rdt_gem.json`,
and `rdt_mega_rare.json` are represented exactly rather than substituted with
the repository's older 2011Scape global tables. Their denominators are 128,
125, 128, and 256 respectively. The mega-rare branch therefore retains Rune
spear, Shield left half, Dragon spear, and Vecna skull, including its empty
mass.

## Charm derivation

Darkan `data/npcs/charmDrops.txt` records thresholds `12-6-4-5`.
`src/main/java/com/rs/tools/old/CharmDrop.java` draws one inclusive 0–100
value, includes every charm threshold containing that value, and selects
uniformly among the included types. Converting that algorithm to one exact
selector produces denominator 1,212:

- Gold 97/1,212;
- Green 25/1,212;
- Crimson 15/1,212;
- Blue 19/1,212; and
- no charm 1,056/1,212.

These are exact emulator odds, not a claim that the cutoff wiki published the
rates.

## Equipment and assets

The 1/512 dark Mystic bottom is cache item 4103. RuneScape Wiki
`Mystic robe bottom`, oldid `6436814`, timestamp
`2012-10-18T13:33:17Z`, establishes that every colour uses the legs slot,
requires 40 Magic and 20 Defence, and carries +15 Magic attack and defence;
the game-main item block independently matches the slot and bonuses.
Regenerating `equipment_data.py` also repaired two source-reachable
Shadow-warrior drops that the prior slice had not regenerated: Adamant spear
and Black dagger (p).

Source:
<https://runescape.wiki/w/Mystic_robe_bottom?oldid=6436814>.

The target, dark Mystic bottom, and Vecna skull have real sprites with URL,
revision timestamp, and hash provenance in `assets_provenance.json`. The
target render is visual-only and is not used as historical evidence.

## Honest boundaries

Exact cutoff-era defensive bonuses for the NPC remain `source_blocked`; the
runtime keeps them at zero rather than borrowing modern values. This does not
block the ordinary target because identity, attack behavior, stench behavior,
stats, drops, and access are otherwise closed.

No owner-facing design fork emerged.

## Verification

All 331 focused pure/runtime/registry checks and the real `.venv-qt` offscreen
Combat picker regression pass. Full discovery runs 1,614 methods: 1,400
ordinary passes and 214 declared environment skips. Documentation, test
quality, Slayer readiness, compilation, provenance JSON, diff, and worktree
checks pass. The expected reachability debt ledger remains nonzero at 1,231
actions, 1,827 reachable items, 285 orphan inputs, and 311 blocked actions.

Results:
`memory-bank/status-updates/slayer-aberrant-spectre-results-2026-07-18.html`
(<https://fr3fmom6akth.postplan.dev>).
