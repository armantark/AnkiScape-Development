# Slayer Ice strykewyrm Combat audit — 2026-07-19

Status: **authority-, source-, dependency-, and representation-blocked; no
Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Ice strykewyrm required by the settled
Duradel/Lapalok and Kuradal registries. The cutoff record closes its level,
LP/XP, Slayer and assignment restrictions, Tale-of-the-Muspah dependency,
cape-or-technique eligibility, attack families, maxima, fire-spell/cape
interaction, ice-spell healing, and visible loot contents.

Activation stops before code changes for five independent reasons:

1. the direct cutoff article and Kuradal audit require completion of The Tale
   of the Muspah, while the settled Duradel/Lapalok audit and current global
   family row omit that gate;
2. Darkan's combat definition is explicitly `nostats`;
3. its fixed Ranged/170-maximum row conflicts with the cutoff mixed
   Melee/Magic/burrow transaction and three distinct maxima;
4. its later custom handler conflicts with the cutoff fire-cape damage rules;
   and
5. its independent-roll drop file is incomplete and materially different from
   the cutoff contents.

The live Slayer reward shop has neither the 2,000-point no-cape technique nor
a family-specific eligibility predicate. No Fire cape, TokHaar-Kal, or
Completionist cape is reachable live equipment. Current Combat also cannot
represent the mound/emergence gate, proximity-dependent mixed attacks,
freeze-cancel branch, avoidable burrow special, or fire/ice spell modifiers.

This pass therefore does **not** add `ice_strykewyrm` to
`COMBAT_ENEMY_DATA`. Duradel/Lapalok remains hidden at **14/35**.

## Period evidence

RuneScape Wiki `Ice strykewyrm`, oldid `6565909`, timestamp
`2012-11-17T10:51:54Z`, establishes:

- combat level 210, 3,000 LP, Slayer level 93, and 300 Slayer XP;
- assignment-only attackability, except for the single Fremennik Elite Task
  kill;
- completion of The Tale of the Muspah before Duradel/Lapalok or Kuradal may
  assign the family;
- original Fire-cape ownership eligibility and the later 2,000-Slayer-point
  technique that permits assignment and damage without it;
- Completionist cape and TokHaar-Kal as qualifying cape substitutes;
- poison susceptibility and a six-tick attack interval;
- Melee, Magic, a freezing Magic attack, and an avoidable burrow special;
- approximate maxima of 174 Melee, 202 Magic, and 300 special damage;
- Protect/Deflect Magic blocking Magic/freezing damage but not the immobilize;
- a roughly three-second freeze that also cancels the player's next attack;
- a Fire cape adding 40 damage with any combat style, fire spells dealing
  `1.5×` without it and `2×` with it, and ice spells healing the target;
- Staff of light at `1/512`; and
- no guaranteed drop, plus the visible rune/talisman, ammunition, herb, seed,
  coin, food, potion, resource, equipment, clue, spin-ticket, effigy,
  court-summons, and rare-drop-table contents.

Source:
<https://runescape.wiki/w/Ice_strykewyrm?oldid=6565909>.

The page does not supply:

- exact Melee/Magic selector probabilities;
- exact freeze or burrow probabilities;
- a numeric normal-hit accuracy model;
- a complete mutually exclusive ordinary drop selector;
- exact charm probabilities; or
- the wall-clock-free review setback corresponding to the short freeze and
  canceled attack.

Those values remain `source_blocked`; they are not inferred from strategy
language.

Cutoff `Talk:Ice strykewyrm`, oldid `6366006`, timestamp
`2012-10-07T20:52:40Z`, corroborates assignment-only attackability, the
quest route, Staff-of-light rarity comparison, ice-spell healing, noted
bird's-nest quantities, and the presence of multiple independent drops. It
also preserves unresolved community reports about post-release drop changes.
It does not close a complete combat or drop selector:
<https://runescape.wiki/w/Talk:Ice_strykewyrm?oldid=6366006>.

The period charm transclusion is no longer recoverable through the current
wiki data page. Exact charm rates therefore remain `source_blocked`.

## Assignment-gate authority stop

The current family row stores:

```python
SlayerFamily(
    "ice_strykewyrms",
    "Ice strykewyrms",
    ("ice_strykewyrm",),
    required_slayer_level=93,
    readiness_features=(
        "assignment_only",
        "strykewyrm_special",
        "fire_cape_or_reward",
    ),
)
```

It has no `required_quest_id`. The settled Duradel/Lapalok audit likewise
lists only Slayer 93 plus the cape-or-technique rule. The newer Kuradal audit
explicitly includes The Tale of the Muspah, matching the direct cutoff target
article.

Because the current family schema is global, silently adding
`required_quest_id="the_tale_of_the_muspah"` would alter both masters and
declare one settled audit incomplete. The closed-design instruction requires
this implementation pass to stop instead. The exact conflict is separately
recorded at
`audits/slayer-ice-strykewyrm-gate-conflict-2026-07-19.md`.

## Cache and executable combat evidence

Rev-727/Darkan identify mound NPC `9462` and active NPC `9463`. The combat
definition provides:

| Field | Darkan value | Cutoff comparison |
|---|---:|---|
| LP | 3,000 | agrees |
| Maximum | 170 | conflicts with 174 / 202 / 300 |
| Style | fixed Ranged | conflicts with Melee / Magic / burrow |
| Respawn | 59 ticks | lower-tier lead |
| Aggression | passive | agrees |
| Real combat levels | absent | blocked |

The file is named `nostats`; Darkan therefore generates equal non-real combat
levels from the combat level and LP. Those generated values cannot be copied
into AnkiScape.

The rev-742 cache preserves the NPC identity and a bonus row with `+20` in one
attack channel and `-50` Ranged defence. It does not supply the five missing
server combat levels or a combat selector.

Pinned Darkan paths and commits:

- combat definition:
  `data/npcs/combatdefs/uncategorized/ice_strykewyrm (nostats).json:1-27`,
  commit `14e49a561bab1441384022421d10dc03a8d837f0`;
- cache rows:
  `developer-information/npcClientScriptData.txt:2474` and
  `developer-information/npcListBonuses.txt:9465`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- custom combat handler:
  `src/main/java/com/rs/game/content/skills/slayer/npcs/Strykewyrm.kt:47-253`,
  commit `32df64ff4d6b9500d5786ec71bce2721190d20b8`;
- Slayer reward handler:
  `src/main/java/com/rs/game/content/skills/slayer/Slayer.java:214-234`,
  commit `e3c2267888bba5d970f9d6d0c43404ed6a8f90a7`; and
- ordinary independent-drop rows:
  `data/npcs/drops/ice_strykewyrm.json:1-248`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`.

## Later handler: useful leads and conflicts

Darkan's custom handler is a period-lineage reconstruction lead, not direct
cutoff authority. Its `0..20` selector yields:

- in Melee range: `8/21` Melee, `12/21` Magic, and `1/21` burrow;
- outside Melee range: `20/21` Magic and `1/21` burrow.

Its Magic branch has a `1/11` freeze check and a three-second freeze. Its
burrow branch makes the NPC temporarily uninteractable, moves toward the
target, and rolls flat damage in the `100..300` call range. These executable
probabilities are useful lower-tier leads, but the cutoff article supplies no
numeric selector with which to corroborate them.

The handler also conflicts with direct period evidence:

- it raises sub-40 Fire-cape hits to a **minimum of 40**, rather than adding
  40 damage;
- it doubles every fire-spell hit regardless of cape ownership, omitting the
  cutoff `1.5×` no-cape branch;
- its base combat row caps every ordinary hit at 170; and
- the Melee helper computes the hit through a Magic combat-style argument.

No live target may use this internally inconsistent combination as an exact
parity source.

## Drop and tertiary evidence

Darkan's ordinary file uses independent rolls, not one mutually exclusive
selector:

- ten noted herb rows at `1/14`, quantity `1–4`;
- Shark at `1/14`, quantity `1–6`;
- Papaya fruit at `1/14`, quantity `3–16`;
- six seed rows at `1/56`;
- Pure essence `200` at `1/56`;
- Spirit shards `1–4` at `1/56`; and
- Staff of light at `1/512`.

Staff of light is directly corroborated by the cutoff article. The remaining
file is not complete enough to activate:

- it omits the cutoff rune/talisman, ammunition, coin, potion, log, bar,
  equipment, clue, spin-ticket, effigy, court-summons, and rare-table rows;
- it adds Papaya fruit, which is not in the visible cutoff table;
- it omits Lantadyme from the ten-herb run; and
- its independent rows cannot be converted into the missing period ordinary
  selector without changing the frequency of multiple-drop outcomes.

Darkan's charm row is `6-3-2-9` for Gold/Green/Crimson/Blue. Its legacy
algorithm rolls `0..100`, includes every threshold passed, then chooses
uniformly among the overlapping candidates. Exact enumeration produces:

| Outcome | Probability |
|---|---:|
| Gold charm | `31/1212` |
| Green charm | `13/1212` |
| Crimson charm | `9/1212` |
| Blue charm | `67/1212` |
| No charm | `1092/1212` |

This is an exact emulator lead, not a recovered period selector. Source:
`data/npcs/charmDrops.txt:90` and
`src/main/java/com/rs/tools/old/CharmDrop.java:54-74`, commits
`3d96f2f98d05f837fa7294566a536b227eddc575` and
`2b63cd96a7859df145204b0e8d96aedbc0515680`.

Darkan separately adds Hard clue `1/128` and Elite clue `1/500`. The cutoff
article attests both tiers but not their rates, so these remain lower-tier
leads:
`src/main/java/com/rs/utils/NPCClueDrops.java:163,176`, commit
`2b63cd96a7859df145204b0e8d96aedbc0515680`.

## Representation and dependency boundary

The complete ordinary fight requires one target-local transaction containing:

- assignment-only mound interaction and emergence;
- Slayer 93, completed Tale-of-the-Muspah, and cape-or-technique assignment
  eligibility;
- no-damage enforcement without a qualifying cape or learned technique;
- distance-sensitive Melee/Magic selection;
- a Magic freeze that still immobilizes through protection and cancels one
  player attack;
- a separately avoidable, temporarily invulnerable burrow special;
- Fire-cape flat bonus and cape-sensitive fire-spell multiplication;
- ice-spell healing; and
- attack-style-specific protection.

Current Combat supports one fixed enemy style, one maximum, fixed defence
bonuses, and ordinary protection. It has no mound, temporary invulnerability,
review-cancel, positional dodge, target-local incoming selector, or
spell-element damage modifier.

`fire_cape_or_reward` is only readiness metadata. The Slayer reward runtime
does not expose the 2,000-point technique, and the qualifying capes are not
reachable equipped identities. The Tale-of-the-Muspah quest exists in the
generated catalog, but quest parity remains owned by the Darkan quest thread.

## Blocking findings

1. **The assignment gate conflicts across settled authority.** Direct cutoff
   evidence and Kuradal require Tale-of-the-Muspah completion; Duradel and the
   current global family omit it.
2. **The combat levels are absent.** Darkan explicitly generates non-real
   values.
3. **The fixed combat row conflicts with the target.** One Ranged/170 row
   cannot preserve Melee, Magic, freeze, and 300-damage burrow.
4. **The custom fire/cape logic conflicts with direct cutoff evidence.**
5. **The ordinary selector is incomplete and structurally different.**
6. **The cape, reward-shop, quest, and Combat dependencies are not live.**

## Explicit omissions

- No Tale-of-the-Muspah quest stage or reward was edited.
- No Fight Caves, Fight Kiln, Fire cape, TokHaar-Kal, Completionist cape, or
  Slayer-reward purchase was introduced.
- The one-off Fremennik Elite Task kill was not folded into ordinary
  assignment behavior.
- No cannon, safespot, obstacle, route, familiar, or wall-clock behavior was
  introduced.
- No sprite or drop assets were installed because the target is not
  runtime-certifiable.

## Required unblock

Before activation:

1. a newer authority record must reconcile the Tale-of-the-Muspah gate across
   the global family and both master audits;
2. period-lineage evidence must close the five combat levels and exact
   attack/freeze/burrow selectors, or the owning contract must explicitly
   authorize bounded abstractions for the missing numeric branches;
3. a drop selector must preserve the cutoff contents and multiple-drop shape;
4. Combat must implement the complete mixed-style strykewyrm transaction; and
5. the qualifying cape or 2,000-point technique must be reachable through its
   owning activity/reward chain.

No owner-facing creative-design question emerged. The gate is an authority
conflict, and the remaining items are source, dependency, and implementation
blockers under the 2026-07-19 closed-design rule.
