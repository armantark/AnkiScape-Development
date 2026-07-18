# Slayer Shadow warrior Combat closure

Date: 2026-07-18

Status: **the ordinary level-48 Shadow warrior is executable and advances
Vannaka to 24/35.**

## Cutoff identity

RuneScape Wiki `Shadow warrior`, oldid `6555920`, timestamp
`2012-11-15T01:24:57Z`, establishes:

- level 48, 670 LP, 67 Slayer XP, and Vannaka/Chaeldar membership;
- six-tick melee with a 65-LP maximum hit;
- no guaranteed drop;
- Crush weakness and non-undead identity; and
- the Legends' Guild basement route after Legends' Quest.

Source:
<https://runescape.wiki/w/Shadow_warrior?oldid=6555920>.

Legends' Guild access is represented by the already-live Legends' Quest
completion gate. This slice adds no quest definition or stage and therefore
does not overlap the Darkan quest-parity thread.

## Combat and ordinary drops

Darkan
`data/npcs/combatdefs/uncategorized/shadow_warrior (noanims).json`
corroborates 670 LP and maximum hit 65 and supplies Attack 36, Strength 36,
Defence 33, Magic/Ranged 0, and a 59-tick respawn.

Darkan `data/npcs/drops/shadow_warrior.json` supplies 14 independent 128-way
rolls:

- Coins, Cosmic/Blood/Air/Death runes, and a Mithril bar;
- Adamant spear, Black dagger (p), Black knife, Black longsword, Black robe,
  and Weapon poison; and
- the shared minor-herb and gem tables.

Each roll is represented as its own hit-or-empty table. Combining these rows
into one mutually exclusive denominator would change the source behavior and
is therefore rejected. The cutoff page names additional qualitative drops but
does not provide exact rates; those rows are not invented. Exact period
defensive bonuses are `source_blocked`, so the Darkan row's absent bonuses
remain zero rather than borrowing a modern table.

## Charm derivation

Darkan `data/npcs/charmDrops.txt` records Shadow warrior thresholds
`10-5-13-1` for Gold, Green, Crimson, and Blue. Its
`src/main/java/com/rs/tools/old/CharmDrop.java` implementation draws one
inclusive 0–100 value, includes every threshold that contains that value, and
selects uniformly among the included types.

The resulting exact emulator distribution has denominator 606:

- Gold 26/606;
- Green 11/606;
- Crimson 44/606;
- Blue 3/606; and
- no charm 522/606.

This preserves the executable emulator algorithm while labeling it as Darkan
evidence, not an exact period-wiki rate.

## Asset boundary

`combatenemies/shadow_warrior.png` uses a current RuneScape Wiki render. It is
visual-only and is not cited as historical evidence. Exact URL, timestamp, and
hash are recorded in `assets_provenance.json`.

## Live mapping

The standard Combat runtime handles the Legends' Quest gate, Slayer XP,
six-tick melee, 14 independent ordinary rolls, the charm table, inventory
capacity, food, retreat, death, and undo. The picker exposes the route lock,
65-LP maximum hit, representative probabilities, and target icon.

`tools/audit_slayer_readiness.py` derives Vannaka at 24/35. Eleven blockers
remain: 10 missing Combat representatives plus Wilderness-risk behavior for
the existing Earth warrior. The incomplete role remains hidden and
unrenormalized. No owner-facing design fork emerged.

## Verification

Focused pure coverage passes all 266 checks and the real `.venv-qt` offscreen
Combat picker regression passes. Full discovery and final quality,
documentation, readiness, provenance, reachability, compilation, diff, and
worktree checks are recorded with the results artifact.
Full pure discovery passes all 1,611 tests with 214 declared environment
skips. Test quality reports zero hard issues and only the four preexisting
clone groups. The expected reachability debt ledger contains 1,231 actions,
1,825 reachable items, 285 orphan inputs, and 311 blocked actions; Black
dagger (p) and Black robe account for the two newly reachable item outputs.

Results:
`memory-bank/status-updates/slayer-shadow-warrior-results-2026-07-18.html`
(<https://4c0ztjs0b4cs.postplan.dev>).
