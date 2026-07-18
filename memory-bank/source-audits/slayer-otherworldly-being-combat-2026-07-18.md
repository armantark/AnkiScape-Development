# Slayer Otherworldly being Combat closure

Date: 2026-07-18

Status: **the ordinary level-64 Otherworldly being is executable and advances
Vannaka to 22/35.**

## Cutoff identity

RuneScape Wiki `Otherworldly being`, oldid `6554205`, timestamp
`2012-11-14T02:47:46Z`, establishes:

- level 64, 660 LP, 66 Slayer XP, and Vannaka membership;
- six-tick melee with a 70-LP maximum hit;
- Magic weakness;
- no guaranteed drop; and
- the south-west Zanaris location.

Source:
<https://runescape.wiki/w/Otherworldly_being?oldid=6554205>.

Zanaris access is represented by the already-live Lost City completion gate.
This slice adds no quest content and therefore does not overlap the Darkan
quest-parity thread.

## Combat and drops

Darkan `data/npcs/combatdefs/areas/zanaris/otherworldly_being.json`
corroborates 660 LP and maximum hit 70 and supplies Attack 56, Strength 56,
Defence 46, Magic/Ranged 1, and a 59-tick respawn.

Darkan `data/npcs/drops/otherworldly_being.json` supplies an exact 128-slot
mutually exclusive table:

- 59 slots of 15 Coins;
- 10 slots of the shared minor-herb table;
- Nature, Chaos, Law, Cosmic, Death, and Blood runes;
- three slots of the shared gem table;
- Ruby ring, Rune mace, and Mackerel; and
- 18 explicit empty slots.

The cutoff page names additional qualitative drops but does not provide exact
rates. The executable Darkan denominator is used without inventing those rows.

## Asset boundary

`combatenemies/otherworldly_being.png` uses a current RuneScape Wiki render.
Its upload timestamp postdates the cutoff, so it is visual-only and is not
cited as historical evidence. Exact URL, timestamp, and hash are recorded in
`assets_provenance.json`.

## Live mapping

The standard Combat runtime handles the Lost City gate, Slayer XP, six-tick
melee, exact table, inventory capacity, food, retreat, death, and undo. The
picker exposes the route lock, 70-LP maximum hit, complete table, and target
icon.

`tools/audit_slayer_readiness.py` derives Vannaka at 22/35. Thirteen blockers
remain: 12 missing Combat representatives plus Wilderness-risk behavior for
the existing Earth warrior. The incomplete role remains hidden and
unrenormalized. No owner-facing design fork emerged.

## Verification

Focused pure coverage passes all 264 checks and the real `.venv-qt` offscreen
Combat picker regression passes. Full pure discovery passes all 1,609 tests
with 214 declared environment skips. Final quality, documentation, readiness,
provenance, reachability, compilation, diff, and worktree checks are recorded
with the results artifact. Test quality reports zero hard issues and only the
four preexisting clone groups. The expected reachability debt ledger remains
1,231 actions, 1,822 reachable items, 285 orphan inputs, and 311 blocked
actions.

Results:
`memory-bank/status-updates/slayer-otherworldly-being-results-2026-07-18.html`
(<https://q57byaii1o36.postplan.dev>).
