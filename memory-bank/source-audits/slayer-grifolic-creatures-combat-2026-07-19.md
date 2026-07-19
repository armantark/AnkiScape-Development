# Slayer Grifolic-creatures Combat audit — 2026-07-19

Status: **source-blocked; no Combat rows activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Grifolapine and Grifolaroo representatives behind
Chaeldar's two Grifolic assignment families. It closes their visible period
identities, Slayer and Magic gates, hybrid attacks, fungal hazards, neem
transformations, drop sets, cache identities, and Darkan execution boundary.
It does **not** add either target to `COMBAT_ENEMY_DATA`.

Both Darkan combat definitions are explicitly named `nostats`; Darkan generates
all five combat levels and marks them non-real. The Grifolaroo definition also
conflicts with the period article's LP and maximum hit. More decisively, the two
Darkan ordinary-drop files are byte-for-byte equivalent after their names even
though the cutoff articles give the monsters materially different rune,
resource, seed, and quantity rows. Darkan's shared Polypore handler also does
not implement the cutoff Magic-to-Ranged attack switch while neemed.

Chaeldar therefore remains hidden at **25/34**. `grifolapines` and
`grifolaroos` retain their `combat_target` blockers, and their existing
`neem_oil` readiness feature remains incomplete with the shared canonical oil
chain.

## Period evidence

### Grifolapine

RuneScape Wiki `Grifolapine`, oldid `6548124`, timestamp
`2012-11-11T15:39:49Z`, literal wikitext establishes:

- level 200, 2,000 LP, Slayer 88, and 205 Slayer XP;
- Magic 60 to receive the assignment;
- non-aggression, poison immunity, Magic/Ranged attacks, and a 234-LP maximum;
- Magic weakness and strong Melee/Ranged resistance;
- mostly Magic attacks before neem and Ranged attacks after neem, with the
  relevant protection prayer changing accordingly;
- a fast fungal charge for 14–22 LP and skipped attack turns when the charge
  is blocked;
- guaranteed Bones and Neem drupe ×1–3;
- Death runes ×9–13, Chaos runes ×56–80 or ×100, three simultaneous seeds,
  Polypore spores ×1–300, Grifolic flakes ×1–100, noted Gorajian mushrooms ×5,
  noted Snape grass ×15–24, Eye of newt, Anagogic orts, Spin ticket, and
  ancient effigy; and
- Chaeldar, Duradel/Lapalok, and Kuradal assignment membership.

Source:
<https://runescape.wiki/w/Grifolapine?oldid=6548124>.

The cutoff talk page, oldid `5516960`, timestamp
`2012-04-21T16:37:47Z`, questions whether the displayed maximum is attainable
after observations of much smaller Magic/Ranged hits. It does not supply a
replacement maximum:
<https://runescape.wiki/w/Talk:Grifolapine?oldid=5516960>.

### Grifolaroo

RuneScape Wiki `Grifolaroo`, oldid `6377087`, timestamp
`2012-10-09T23:49:53Z`, literal wikitext establishes:

- level 180, 1,800 LP, Slayer 82, and 184.4 Slayer XP;
- Magic 60 to receive the assignment;
- non-aggression, poison immunity, five-tick Magic/Ranged attacks, and a
  214-LP maximum;
- Magic weakness and strong Melee/Ranged resistance;
- rapid 7–13 LP infestation inside melee range;
- a three-to-four-square hop which pauses attacks;
- neem immediately causing a hop, suppressing Magic, slowing Ranged attacks,
  disabling the infestation, and producing an independent item;
- guaranteed Bones and Neem drupe ×1–3;
- Death runes ×4–10, Chaos runes ×31–60, usually two simultaneous seeds,
  Polypore spores ×1–500, Grifolic flakes ×1–100, noted Gorajian mushrooms ×3,
  noted Snape grass ×10–20, Spin ticket, and ancient effigy; and
- Chaeldar, Sumona, Duradel/Lapalok, and Kuradal assignment membership.

Source:
<https://runescape.wiki/w/Grifolaroo?oldid=6377087>.

The cutoff talk page, oldid `6343325`, timestamp
`2012-10-04T04:02:37Z`, contains only a positional safespot observation and
supplies no additional numeric value:
<https://runescape.wiki/w/Talk:Grifolaroo?oldid=6343325>.

The settled no-position Combat contract already makes hopping, charging, and
safespot movement contextual attack/risk state rather than tile
micromanagement. It does not license fabricated combat levels, attack
selectors, or drop tables.

## Cache evidence

Rev-742, dated `2012-11-07`, contains attackable normal and neemed identities:

- 14688/14689, `Grifolapine`;
- 14700/14701, `Grifolaroo`; and
- item 22450, `Grifolic flake`.

The shared Neem-oil identities remain item 22444 (`Sprinkle`, `Check`, `Empty`)
and item 22445 (`Squish`). These records prove client identities and
interactions, not hidden server values.

Darkan's cache-derived bonus and CS2 dumps give both families the same form
change: Stab/Slash/Crush/Magic/Ranged defences `60/70/50/-30/0` become
`60/70/50/-50/0`, while CS2 key 14 changes from `4` to `6`. Zero attack and
strength bonuses remain unchanged. As with Fungal mage, these are preserved as
cache configuration observations rather than asserted as a complete
server-combat formula.

## Executable evidence

Pinned Darkan paths and commits:

- `data/npcs/combatdefs/uncategorized/grifolapine (nostats).json`, commit
  `e1e71c9fb5979ba72bc66f4a251c725c8d0e1239`;
- `data/npcs/combatdefs/uncategorized/grifolaroo (nostats).json`, same commit;
- `data/npcs/drops/grifolapine.json`, repository root commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- `data/npcs/drops/grifolaroo.json`, same commit;
- `data/npcs/charmDrops.txt:80-81`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`;
- `src/main/java/com/rs/game/content/skills/slayer/npcs/PolyporeNPC.java`,
  neem/infestation commit `c971be5fe`; and
- `src/main/java/com/rs/game/model/entity/npc/combat/NPCCombatDefinitions.java`,
  current fallback lineage through
  `e1e71c9fb5979ba72bc66f4a251c725c8d0e1239`.

The Grifolapine combat row agrees on 2,000 LP, 234 maximum, Magic style,
passivity, and a 59-tick respawn. The Grifolaroo row instead supplies 1,780 LP,
175 maximum, Magic style, passivity, and a 119-tick respawn; the player-visible
LP/maximum conflicts lose to the cutoff article's 1,800/214, but the five
hidden combat levels remain absent in both rows.

`NPCCombatDefinitions.getDefs()` fills those omissions through
`generateLevels(combatLevel, hitpoints / 10)` and explicitly sets
`realStats = false`. These equal generated levels are executable fallback
values, not recovered period stats.

The shared `PolyporeNPC` handler supplies Grifolapine infestation of 10–19 LP,
conflicting with the cutoff 14–22, and Grifolaroo infestation of 7–13 LP,
agreeing with its cutoff page. It applies a 20-second neem form, one-fifth
incoming Melee/Ranged damage before neem, half outgoing Magic/Ranged damage
after neem, and the cache defence swap. It never changes either combat
definition away from `MAGIC`, so Darkan does not implement the period
Magic-to-Ranged transition while neemed.

The two ordinary-drop JSON files are structurally identical after their target
names. Both encode guaranteed Bones and Neem drupe ×1–3, then the same
Gorajian mushroom ×3, Polypore spore ×1–500, noted Snape grass ×10–20, Death
rune ×4–10, Chaos rune ×5–60, Grifolic flake ×1–112, and seed rows with the
same probabilities. That approximately resembles Grifolaroo but conflicts even
there on Chaos-rune and flake quantities. It materially contradicts
Grifolapine's different rune, spore, mushroom, grass, flake, and three-seed
rows. The duplicate files are therefore reconstruction stubs, not two
independently usable ordinary selectors.

Both charm rows use thresholds `4-2-11-1`. Lossless enumeration of
`CharmDrop.getCharmType()` yields the same 606-slot selector for each target:
11 Gold, 5 Green, 53 Crimson, 3 Blue, and 534 empty. Both cutoff articles
corroborate charm drops but do not expose the hidden distribution. Neither
target appears in Darkan's clue-drop registry, and neither cutoff article names
a clue scroll; no clue channel is inferred.

## Blocking findings

1. **Combat levels are absent.** Both executable definitions generate
   explicitly non-real Attack, Strength, Defence, Magic, and Ranged levels.
   The source standard does not allow provisional levels.
2. **Grifolaroo's visible row conflicts.** Darkan supplies 1,780 LP and a
   175 maximum against the cutoff article's 1,800 and 214.
3. **Grifolapine's hazard conflicts.** Darkan's 10–19 infestation disagrees
   with the cutoff article's 14–22.
4. **Neem attack switching is missing.** The cutoff pages require the neemed
   forms to suppress Magic and use slowed Ranged attacks. Darkan leaves both
   forms on the same Magic combat definition.
5. **The ordinary selectors are duplicated stubs.** The two Darkan files are
   the same despite the period tables being materially different, and even the
   closer Grifolaroo file conflicts on rune/flake quantities.
6. **The shared acquisition chain is not live.** Canonical Neem-drupe/jug/oil
   charges, 6.5 Herblore XP, temporary target form, and independent
   sprinkle-drop transaction remain absent from AnkiScape.

## Explicit omissions

- No target sprites or Grifolic-resource icons were installed because neither
  target is runtime-certifiable.
- The hidden Magic/Ranged selector, charge/hop trigger frequency, skipped-turn
  count distribution, and neem sprinkle-drop selectors remain
  `source_blocked`; article strategy prose does not turn observations into
  exact server rolls.
- Ganodermic creatures, Fungal rodents, Infested axes, dungeon traversal, and
  the Dungeoneering resource room are outside this paired family audit.

## Required unblock

Do not activate either family until period-lineage evidence closes the five
combat levels, the conflicting visible values and selectors are reconciled,
and the canonical Neem-oil chain plus temporary Magic-to-Ranged enemy-form
transition is implemented atomically. A future high-fidelity Darkan pass may
supply that behavior; copying its current generated levels or duplicated drop
files would violate the source standard.

No design question was opened. These are source and implementation
dependencies under the 2026-07-19 closed-design rule.

## Workflow telemetry

Codex Workflows run `4c58b634-5012-4d02-93d8-8b0d2e83099d` launched one
bounded Sol-high read-only leaf. The repaired runtime created session
`019f7984-9828-7f11-bab6-dc2abf4c2e1f` and successfully executed repository
tools, so this was not a startup or provider-connection failure. The leaf did
not return its required concise report after 10 minutes and 13 tool calls; its
telemetry reached 366,360 total tokens, including 308,992 cached input tokens.
The root canceled it at `2026-07-19T08:44:17Z` to prevent a runaway review
from blocking the source queue. No leaf claim was accepted. The root
independently reproduced and verified every finding recorded above.
