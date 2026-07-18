# Slayer Vannaka live readiness and Ogre Combat closure

Date: 2026-07-18

Status: **Vannaka's complete pool is encoded and remains hidden; the ordinary
Ogre family is executable.**

## Pool contract

The existing cutoff audit
`memory-bank/source-audits/slayer-vannaka-pool-2026-07-17.md` is now represented
directly in `slayer_data.py`:

- all 35 ordinary families;
- every reconciled family weight and count range;
- the provisional 460-point denominator;
- Vannaka's Combat-40 gate; and
- stable target, Slayer-level, quest, skill, and special-mechanic dependency
  identities.

`tools/audit_slayer_readiness.py` derives Vannaka's live state from those rows
instead of a prose blocker count. The master is deliberately
`runtime_enabled=False`: after this slice 16/35 families are ready, so no
missing family is silently removed and no weight is renormalized.

The exact blocker ledger is:

- absent Combat targets: Aberrant spectres, Basilisks, Bloodveld, Brine rats,
  Crocodiles, Dust devils, Green dragons, Harpie bug swarms, Infernal mages,
  Jellies, Jungle horrors, Killerwatts, Mogres, Molanisks, Otherworldly beings,
  Sea snakes, Shadow warriors, and Turoth; and
- missing Wilderness-risk behavior on the already-live Earth warrior.

Quest definitions are not duplicated here. Mogres still wait on the
Darkan-owned `skippy_and_the_mogres` completion ID.

## Ordinary Ogre evidence

RuneScape Wiki `Ogre`, oldid `6565807`, timestamp
`2012-11-17T10:19:18Z`, establishes the ordinary Kandarin variant:

- combat level 53;
- 600 lifepoints;
- melee crush attacks at four-tick speed;
- maximum hit 73;
- 60 Slayer XP and Vannaka assignment membership;
- poison susceptibility;
- Ranged/stab weakness; and
- guaranteed Big bones.

The same page distinguishes and therefore excludes the level-58 God Wars and
level-63 Combat Training Camp variants:
<https://runescape.wiki/w/Ogre?oldid=6565807>.

Darkan's
`data/npcs/combatdefs/uncategorized/ogre/ogre_(53).json` corroborates the period
LP and maximum hit, supplies Attack/Strength/Defence 43, Magic/Ranged 1, and a
59-tick respawn.

Darkan's `data/npcs/drops/ogre.json` supplies three independent drop channels:

- guaranteed item 532, Big bones;
- a `19/128` roll into
  `data/npcs/drops/special_tables/common_seeds.json`; and
- the shared long/curved-bone tertiary table.

The nested seed table is transcribed slot-for-slot at a denominator of 1,000.
Its 23 named weights sum to 999, so the final one slot is preserved explicitly
as no drop. Long bone remains `1/400` and Curved bone `1/5,000`; neither is
collapsed into the main seed roll.

## Live mapping

`combat_data.py` exposes the source-backed level-53 Ogre under the stable
`ogres` Vannaka family. The shared Combat runtime handles the fight, Slayer XP,
guaranteed Big bones, nested seed selection, and independent tertiary rolls.
The Combat picker exposes the exact target, drop families, source citation, and
provenance-backed sprite.

`combatenemies/ogre.png` is pinned to the RuneScape Wiki file revision dated
`2011-11-26T17:47:11Z`, rather than the current upload. Its exact file metadata
is recorded in `assets_provenance.json`.

No owner-facing design fork emerged. The period source does not preserve hidden
seed rates, but Darkan supplies a complete executable table; no invented value
is needed for this target.

## Verification

Focused pure coverage passes all 336 checks, and full pure and real offscreen
Qt discovery each pass all 1,597 tests; the pure runner records 214 declared
environment skips. Test quality has zero hard issues;
documentation, compilation, JSON, readiness, provenance, diff, and worktree
safety checks pass. The expected reachability backlog remains 285 orphan
inputs and 311 blocked actions; this slice adds no new orphan or blocked Ogre
item.

Results:
`memory-bank/status-updates/slayer-vannaka-ogre-results-2026-07-18.html`
(<https://o849m34h9y3r.postplan.dev>).
