# Bork daily loop — 2026-07-30

Authority: `source-audits/bork-loop-2026-07-18.md`,
`multi-enemy-encounter-contract-2026-07-18.md`,
`boss-instance-contract-2026-07-18.md`, and
`design-thread-queue.md` section 4.14 item 1, whose miniquest ledger landed the
first of the two things the 2026-07-18 contract was waiting on.

## What shipped

A recurring Distraction and Diversion: one Bork kill per answered-card day,
gated on the `hunt_for_surok` miniquest, fought through live six-tick Combat
slices, paying the sourced Slayer XP, coins, charms, gems and rare drops.

- `data/bork_data.py` — period rows, the four-column guaranteed drop table, the
  three rare rolls, and the Bork, Ork legion and caster enemy blocks.
- `logic/bork_logic.py` — state, view, `enter`/`leave` commands and the review
  reducer.
- Registrations: `core/constants.py` (activity, icon, effigy item),
  `core/storage_pure.py` (default, sanitize, activity arbitration),
  `runtime/runtime_actions_activities.py` (review handler and telemetry),
  `runtime/runtime_actions_utility.py` and `runtime/runtime_actions_gates.py`
  (routing and the can-review gate), `__init__.py` (command seam through
  `commit_direct_action`), `logic/cadence_coverage.py` (cadence row),
  `ui/ui.py` (the compact D&D card and the switch-away arbitration).
- `tools/fetch_bork_assets.py` — period art for both enemies.

## Pinned period sources

| Fact | Source |
|---|---|
| Level 267, 3,000 LP, max hit 254, crush, attack speed 6 | `Bork` oldid 6565904 (`2012-11-17T10:41:40Z`); Darkan `bork (nostats).json` gives the same 3,000 / 254 |
| Once per day, during and after the miniquest | same revision |
| 250 repeat Slayer XP, 500 after the Varrock Elite tasks | same revision; Darkan `Bork.repeatKillSlayerXp` |
| Coins 2,000–10,000, or 4,000–20,000 with the elite tasks | same revision's drop table; Darkan `Utils.random(2000, 10001)` / `(4000, 20001)` |
| The four guaranteed-drop columns | the same revision's drop table, reproduced exactly by Darkan `Bork.guaranteedDrops` |
| Rare drops: Starved ancient effigy 1/64, elite clue 1/32, hard clue 1/16 | Darkan `Bork.drop()`; the revision lists the same three items as Rare / Very rare with no rate |
| Ork legion level 70, 500 LP, max hit 82, melee within one tile and ranged otherwise | `Ork legion` oldid 6269351 (`2012-09-20T01:16:17Z`); Darkan `ork_legion (nostats).json`; `Bork.kt:110-111,184-205` |
| The legion arrives once, at 2,000 LP, 3 to 9 strong | Darkan `Bork.ORK_SUMMON_THRESHOLD_HITPOINTS`, `ORK_SUMMON_MINIMUM`, `ORK_SUMMON_MAXIMUM` and the `npcCombat` block |
| The lair caster fires every 20 seconds for 100–250 magic, zeroed by Protect from Magic | Darkan `BorkController.process()` and `BorkController.mageDamage` |
| The repeat visit's caster is the Dagon'hai Elite, npc 7137 | Darkan `BorkController.onBuildInstance`; npc 7136 (Surok Magis) is the miniquest-run caster |
| Both npcs are immune to poison | `Bork` oldid 6565904 and `Ork legion` oldid 6269351 both print `immune to poison = Yes`; Darkan's `Bork.processEntity()` calls `poison.reset()` around every tick |
| All-zero attack, defence and strength bonuses for both npcs | rev-727 `developer-information/npcListBonuses.txt` rows 7134 and 7135 |

## Judgements recorded

**The 2018-07-18 charm conflict is closed.** That audit marked the default charm
bundle `source_blocked` because the pinned revision's prose (4 blue, 7 crimson,
3 green) contradicts its own drop table (5, 7, 2). Darkan's `guaranteedDrops`
returns 5 blue, 7 crimson and 2 green for its default mode and matches the table
in all four columns, including the gem rows. That is the reconciled server
evidence the audit asked for, so the table stands and the prose is the error.

**Every kill in this loop is a repeat kill.** The sourced 5,000 first-kill
Slayer XP belongs to the Hunt for Surok miniquest, which the ledger already pays
on completion, and the loop only opens once that miniquest is complete. Darkan
reads identically: `drop()` awards `repeatKillSlayerXp` only when the kill is
not the miniquest kill. Paying 5,000 again here would have double-counted it.

**Bork is the sole engaged target; the legion is pure pressure.** The settled
multi-enemy contract allows a homogeneous front to collapse into one aggregate,
and the period gives no reason to engage a legion at all: they despawn the
moment Bork dies (Darkan finishes every nearby npc 7135 in `sendDeath`) and the
pinned page says they "are usually ignored because they disappear when Bork is
killed". So there is no target choice to offer, and no Casual/Advanced target
picker is invented. The orks press in melee every review, through the ordinary
defence and protection-prayer contract, so Protect from Melee answers them the
way the period guide says it does.

**Darkan settles the summon, not the page.** The Ork legion revision says "up to
six legions ... at 75% health, each consisting of three orks"; Darkan says once,
at 2,000 of 3,000 life points, 3 to 9 strong. The server constants are exact
where the page is approximate, and the same revision pair already resolved the
charm bundle in the server's favour, so the server reading is used. The two
sources also count in different units: Darkan's `orkCount` counts individual npc
7135 spawns, while the page's "legion" is a group of three of them. AnkiScape
counts orks, and every counted figure in the interface says ork for that reason.

**Entry is gated, not the payout.** Darkan lets a player re-enter after the
daily kill and simply pays nothing. The pinned page says Bork "may be battled
once per day". AnkiScape gates entry, because a rewardless repeat fight is
review time spent for nothing. Leaving, dying and being killed by the legion all
leave the daily kill unspent; only a victory closes the day.

**The caster's bolt uses the engine's protection arithmetic.** Darkan zeroes the
bolt outright while Protect from Magic is on. AnkiScape prayers carry an uptime
fraction, and the shared combat engine already reduces incoming damage by that
fraction, so the bolt does the same. Full uptime reproduces the period zero.

**Death is dangerous.** The Chaos Tunnels are ordinary world, not a minigame
instance, so both the Combat slice and the legion's pressure run the live
`safe_death=False` path.

## Placeholders

Both enemy stat blocks reuse the existing
`dominion_tower.unsourced_boss_stat_blocks` conversion — 72% of combat level,
capped at 99, in attack, strength, defence and magic alike — because both Darkan
combat definitions are `nostats` files. Bork's block is the same one the Hunt
for Surok quest encounter ships, and both were corrected on 2026-07-30: they had
carried a magic of 1 and a ranged stat the registered conversion does not
produce at all, which made the register's own description untrue of the code it
was cited for.

The 2026-08-03 depth pass retires `bork.ork_legion_attack_style`. Darkan's
authentic handler states the exact boundary: `withinDistance(target, 1)` selects
melee and every other position selects ranged. AnkiScape's owner-settled
homogeneous pressure front has no distance state and represents the pinned
guide's stand-near-Bork route, so its always-melee pressure is the exact
adjacent branch. This is a disclosed encounter abstraction, not a missing
period value, and therefore does not belong in the placeholder register. The
page's qualitative claim that the ranged attack is slightly less accurate is
outside that collapsed branch and no ranged penalty is invented.

## Recorded gaps

1. **Two wiki-only drops are omitted.** The revision lists a Rune helm and a
   10× Gold charm drop as "Very rare" and a Femur bone available only during the
   Fur 'n Seek wish list. Darkan drops none of them and no source gives a rate,
   so shipping them would have required inventing one.
2. **The legion drops nothing.** The page says each legion "usually drops a
   single charm" without a rate. Since the legion is never a kill in AnkiScape,
   the question does not arise; it would if a later contract makes them
   engageable.
3. **No Firemaking or Summoning XP exists for Bork.** Neither the pinned
   revision nor Darkan awards any. The Summoning link is the charm bundle, which
   ships in full.

## Verification

`tests/test_bork.py` covers the period rows and all four drop columns, the
miniquest gate, the world-day close and reopen, leaving and dying preserving the
daily kill, activity arbitration, the legion's single arrival and its sourced
size range, the caster's tick budget and its answer by Protect from Magic, the
default, Varrock Elite and Ring of Wealth reward columns, the three independent
rare rolls, save round-tripping, and one answered card driven through the real
`handle_utility_answer` reducer into the real Combat kernel.

Most of those tests stub the combat burst, which is right for the reducer's own
arithmetic and wrong as the only coverage of the fight. Two seeded tests added
on 2026-07-30 drive a whole fight through the real kernel with no stub: an
equipped player kills Bork in under forty reviews for exactly 250 Slayer XP and
the 5/7/2 charm column, the world day then refuses re-entry and reopens on the
next one, and a death to the orks is reported as a death. The last one is a
regression test for a real defect — the combat burst survives the review that
kills the player, so the reducer has to raise the `died` flag itself or the
runtime records the death as a clean success.
