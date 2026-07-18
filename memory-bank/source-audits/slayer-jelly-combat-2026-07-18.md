# Slayer Jelly Combat closure

Date: 2026-07-18

Status: **ordinary Jelly is executable and advances Vannaka to 17/35.**

## Cutoff identity

RuneScape Wiki `Jelly`, oldid `6530513`, timestamp
`2012-11-04T05:27:09Z`, establishes the ordinary non-Daemonheim target:

- combat level 78;
- 750 lifepoints;
- Slayer 52 to kill and 75 Slayer XP;
- passive magic-based melee;
- six-tick attack speed;
- approximate maximum hit 60;
- no guaranteed drop outside Soul Wars; and
- Vannaka and Chaeldar assignment membership.

The page explicitly distinguishes the Soul Wars variant, which drops two Soul
fragments and is exposed to PvP. This slice implements the ordinary Fremennik
Slayer Dungeon identity only:
<https://runescape.wiki/w/Jelly?oldid=6530513>.

## Combat and drops

Darkan
`data/npcs/combatdefs/uncategorized/jelly.json` corroborates 750 LP and maximum
hit 60 and supplies Attack 45, Strength 45, Defence 120, Magic 45, Ranged 1,
and a 59-tick respawn. The period page wins for the sourced six-tick speed.

Darkan `data/npcs/drops/jelly.json` supplies one complete mutually exclusive
128-slot ordinary table. It contains:

- four coin quantities;
- Steel battleaxe, Steel 2h sword, Steel hatchet, Mithril kiteshield, Mithril
  boots, and Rune full helm;
- Chaos and Death runes;
- Gold bar and Thread; and
- the shared gem table.

The 16 row weights sum to exactly 128. No guaranteed Bones are added: the
period page explicitly says ordinary Jellies drop nothing at 100%, despite the
bones visible inside the model.

## Mithril boots

RuneScape Wiki `Mithril armoured boots`, oldid `6007782`, timestamp
`2012-07-28T12:25:08Z`, establishes item 4127's Defence-20 gate, feet slot,
tradeability, non-stackability, and Jelly acquisition:
<https://runescape.wiki/w/Mithril_armoured_boots?oldid=6007782>.

The primary 2011Scape `data/cfg/items.yml` item 4127 supplies the executable
bonuses: Magic attack -3, Ranged attack -1, and melee defences +8/+9/+10.
`tools/generate_equipment_data.py` owns the row so regeneration cannot erase
it.

## Asset boundary

`combatenemies/jelly.png` and `combatitems/mithril_boots.png` use OSRS Wiki
renders. Their uploads postdate the cutoff, so they are visual-only assets and
are not cited as historical evidence. They were chosen as the closest legacy
visuals rather than modern RS3 redesigns. Exact URLs, timestamps, and hashes
remain in `assets_provenance.json`.

The rejected RS3 Jelly candidate resolved to a 2014 upload despite the cutoff
request and was overwritten; it is not retained or cited.

## Live mapping

The shared `magic_melee` channel already used by Pyrefiend gives Jelly its
distinct defence roll while keeping Protect from Melee as the correct prayer.
The standard Combat runtime handles the Slayer gate/XP, six-tick pacing, exact
drop roll, inventory capacity, undo, and death paths. The Combat picker exposes
the attack semantics, maximum hit, full drop table, and target sprite.

`tools/audit_slayer_readiness.py` now derives Vannaka at 17/35. Eighteen
blockers remain: 17 missing Combat representatives plus Wilderness-risk
behavior for the existing Earth warrior. No owner-facing design fork emerged.

## Verification

Focused pure coverage passed all 356 checks. The production state passed full
pure and real offscreen Qt discovery at 1,601 tests; after two redundant pure
test methods were consolidated, the current 1,599-test pure suite also passes
with 214 declared environment skips. Equipment regeneration is byte-stable,
the real Combat picker shows Jelly's attack/drop/icon surface, and
documentation, test-quality, JSON, compilation, readiness, focused
reachability, diff, and worktree-safety checks pass. The repository-wide
reachability audit retains its established 285-orphan/311-blocked backlog and
correctly exits non-zero; Jelly makes Mithril boots reachable and adds no debt.

Results: `memory-bank/status-updates/slayer-jelly-results-2026-07-18.html`
(<https://qvrpp85jnouq.postplan.dev>).
