# Slayer protective equipment — Cockatrice and Banshee

Date: 2026-07-17
Cutoff: strictly before 2012-11-20T00:00:00Z
Status: Cockatrice and Banshee source-ready and implemented with labeled
bounded abstractions where the surviving formulas conflict.

## Scope

This is the first family-level protective-equipment audit required by owner
decision 21 in `slayer-skill-contract-2026-07-15.md`. It covers the existing
Combat variants `cockatrice` and `banshee`, their required equipped items, the
unprotected trigger, damage and stat drains, and the AnkiScape interaction with
ordinary death, retreat, food and undo.

## Sources

### Pinned period pages

- **Cockatrice**, oldid `6579848`, `2012-11-19T04:56:21Z`.
  - Requires 25 Slayer to kill.
  - A Mirror shield must be equipped; players without 20 Defence were not
    assigned the task because 20 Defence is required to wield it.
  - Without the shield, eye beams always hit a fixed amount, deal more damage
    at higher levels up to 110 LP, and rapidly reduce combat stats including
    Agility to one quarter of their original values.
- **Mirror shield**, oldid `6283470`, `2012-09-23T03:24:32Z`.
  - Slayer-master shop item, shield slot, 20 Defence requirement.
  - Protects against Cockatrice and Basilisk stat reduction only when equipped.
- **Banshee**, oldid `6589075`, `2012-11-19T23:42:06Z`.
  - Earmuffs, masked earmuffs, and Slayer helmets protect.
  - Without protection, the attack damages according to Constitution divided
    by ten and reduces Attack, Strength, Defence, Ranged, Prayer, Magic,
    Agility, and Summoning.
  - The infobox records a maximum hit of 80 without earmuffs.
- **Earmuffs**, oldid `5935584`, `2012-07-14T19:58:19Z`.
  - Purchasable from Slayer masters and worn in the head slot.
  - Masked earmuffs and Slayer helmets inherit their protection.

Literal wikitext was read through the RuneScape Wiki revisions API, not inferred
from current rendered prose.

### Darkan

Repository HEAD inspected: `620bfa9b0b9a88269951363b347a4c0100f0b9f1`.

- `src/main/java/com/rs/game/content/skills/slayer/npcs/combat/CockatriceCombat.java`
  at file commit `347552cad462e96670e3ff04228c0232881da9f5`.
  - Mirror-shield check.
  - Unprotected `Hit.flat` for maximum LP divided by six.
  - No stat drain is implemented.
- `src/main/java/com/rs/game/content/skills/slayer/npcs/combat/BansheeCombat.java`
  at the same file commit.
  - Earmuff-family check.
  - Unprotected fixed maximum-LP/10 damage.
  - One random skill among the implementation's first seven skill indices is
    reduced by five.
- `src/main/java/com/rs/game/content/skills/slayer/Slayer.java`
  at file commit `a7ba60f6cf8edd32ddd2314ac8ce0ad4f4ec8534`.
  - Earmuffs `4166`, masked earmuffs `13277`, and Slayer-helmet variants protect
    Banshee.
  - Mirror shield `4156` in the shield slot is the reflective protection.

### 2011Scape / game-main

The local unversioned snapshot's Cockatrice script is byte-identical to GitHub
commit `833d0491a3ddd86e4588812d86985e6c6b1b9d1f`.

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/scripts/impl/CockatriceCombatScript.kt`
  - Mirror shield must occupy the shield slot.
  - The unprotected hit is forced to land with a configured 110-LP maximum.
  - Each attack subtracts 25% of maximum Attack, Strength, Defence, Ranged, and
    Agility.
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/PawnExt.kt`
  - That configured maximum is still randomly rolled, so it conflicts with the
    period page's fixed-amount statement.
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/scripts/impl/BansheeCombatScript.kt`
  - Earmuff/Slayer-helmet protection.
  - Forced-to-land configured 78-LP maximum.
  - Subtracts 25% of maximum from seven named stats each attack.

### Cache and acquisition

- Rev-742 item config: item `4156`, **Mirror shield**, options
  `[null, Wield, null, null, drop]`.
- Existing generated Shop data exposes Mirror shield in every Slayer-equipment
  shop at 5,000 coins and Earmuffs at 200 coins.
- Existing Equipment data already places Mirror shield in `shield`, requires
  20 Defence, and places Earmuffs in `head`.

## Reconciliation

### Cockatrice — accepted source-ready mapping

| Field | Finding |
|---|---|
| Protection | Mirror shield equipped in `shield`; bank ownership or another slot does not protect. |
| Literal gate | 25 Slayer to kill; assignment also requires the shield's 20 Defence equip gate. Slayer-level task gating remains part of the still-hidden Slayer runtime, not this Combat slice. |
| Trigger | Every Cockatrice attack while the shield is absent. Safespotting does not remove the requirement; Talk:Cockatrice oldid `5874482` confirms the shield is still needed. |
| Damage | Fixed, automatically landed, scales as maximum LP / 6, capped at the period-proven 110 LP. |
| Stat drain | Subtract 25% of each base Attack, Strength, Defence, Ranged, and Agility level per attack, never below one quarter of base. |
| Accuracy/prayer | The eye beam bypasses the ordinary accuracy roll and protection-prayer damage reduction. This maps the period “always hit a fixed amount” and Darkan `Hit.flat` behavior. |
| Food/retreat/death | The result enters Combat's existing atomic damage path: auto-food may respond, auto-flee reevaluates on the next tick, and ordinary PvM death/grave handling applies. |
| Undo | The existing review snapshot restores LP, drained levels, food, grave state, and equipment-sensitive outcome together. No separate undo channel is introduced. |

The exact fixed-damage function is not stated algebraically by the period page.
Darkan supplies maximum-LP/6 while the page supplies the increasing fixed shape
and 110-LP ceiling. `min(maximum_lifepoints // 6, 110)` is therefore recorded
and coded as `abstraction/darkan+period-cap`, not as historically closed.

The stat-drain operation is likewise a bounded reconciliation: the period page
supplies the one-quarter floor, while 2011Scape supplies the repeated
25%-of-base decrement and affected skill set. Darkan's omission is recorded.

### Banshee — accepted bounded abstraction

The protective item set, affected period stats, and dangerous unprotected
damage are established. The exact stat-drain magnitude is not:

- Darkan drains one randomly selected skill by five.
- 2011Scape drains seven named skills by 25% of maximum each attack.
- The period page proves a wider eight-skill set but gives no magnitude or
  selection rule.

Summoning is now live, so the former dependency block is gone. Following owner
decision 21's instruction to use the smallest labeled abstraction when the
hidden magnitude remains source-blocked, AnkiScape uses the period-proven full
eight-skill set with Darkan's smallest surviving flat five-level decrement on
every unprotected scream, floored at level 1. This deliberately rejects
2011Scape's much harsher 25%-of-base drain across only seven skills and does not
pretend that Darkan's random-one-skill selection is historically settled.

Unprotected damage is fixed maximum LP / 10, capped at the period-proven 80 LP
maximum. Earmuffs, masked earmuffs, and the ordinary/full Slayer helmet families
protect only while equipped in the head slot. The scream bypasses ordinary
accuracy and protection-prayer reduction, then enters the existing atomic
food, retreat, death, recovery, and review-undo paths.

## Implementation

- `combat_data.py` carries the Cockatrice protection and unprotected-effect
  record with its labeled source status.
- `logic_pure.py` checks the exact equipment slot, applies fixed damage and
  bounded stat drains on every unprotected attack, exposes the warning/risk
  preview, and reports aggregate unprotected attacks and drains.
- `target_metadata.py` shows the warning in the existing Combat target tooltip
  without disabling the legal dangerous encounter.
- Focused regressions cover the four-attack one-quarter floor, exact fixed
  damage, protection-prayer bypass, reduced later attacks in the same review,
  shield protection, preview state, tooltip warning, and roster schema.

No Qt widget code changed. The warning travels through the existing target-row
metadata surface; real offscreen Qt Combat-picker checks confirm that the
existing consumer renders the enriched Cockatrice and Banshee rows.
