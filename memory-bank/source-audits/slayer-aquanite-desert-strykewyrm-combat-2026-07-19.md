# Slayer Aquanite and Desert-strykewyrm Combat audit — 2026-07-19

Status: **source-blocked; no Combat rows activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Aquanite and Desert strykewyrm required by
Sumona's settled assignment registry. It closes both period identities,
Slayer gates/XP, LP, attack families and visible maxima, cache identities,
target-local special shapes, named drop sets, and Darkan execution boundaries.
It does **not** add either target to `COMBAT_ENEMY_DATA`.

Both Darkan combat files explicitly say `nostats`; all five combat levels are
generated non-real fallbacks. Aquanite has no executable prayer-negating
special handler or source-ready trigger rate, and its ordinary selector
conflicts with the period Water-rune and Seaweed quantities. Desert
strykewyrm's handler conflicts with the period burrow frequency and conditional
double-hit consequence, while its ordinary selector conflicts with several
visible quantities.

Sumona therefore remains hidden and unrenormalized at **20/37**. Both families
retain `combat_target`; no readiness denominator changes.

## Aquanite period evidence

RuneScape Wiki `Aquanite`, oldid `6579278`, timestamp
`2012-11-18T19:13:51Z`, literal wikitext establishes:

- level 114, 1,250 LP, Slayer 78, and 125 Slayer XP;
- non-aggressive five-tick Magic attacks;
- a 134 ordinary maximum and 250 prayer-negating-special maximum;
- Ranged weakness and Stab preferred over Slash;
- guaranteed Big bones;
- Sumona, Duradel/Lapalok, and Kuradal assignment membership;
- no Kuradal reward gate for Sumona or Duradel/Lapalok;
- the complete named charm, rune, equipment, ammunition, seed, herb, food,
  resource, clue, bone-tertiary, spin, effigy, and unique-drop sets; and
- visible quantities including Water runes ×30–49 or ×100, Soul runes ×3–6,
  Seaweed ×3–6 noted, and Snape grass ×3 noted.

Source:
<https://runescape.wiki/w/Aquanite?oldid=6579278>.

Cutoff `Talk:Aquanite`, oldid `5512876`, timestamp
`2012-04-19T17:22:21Z`, independently reports that the special turns off
protection Prayer and hits harder than the ordinary attack. Its early
player reports converge only around an obsolete 200-LP special maximum; the
near-cutoff article's explicit 250 value is the higher-tier candidate. The
talk page contains no trigger denominator:
<https://runescape.wiki/w/Talk:Aquanite?oldid=5512876>.

The cutoff article describes a chance for the special but provides no
executable probability. No period-lineage implementation recovered here
supplies the special at all, so the hidden roll does not satisfy the
provisional-calibration requirement for two agreeing implementations.

## Desert-strykewyrm period evidence

RuneScape Wiki `Desert strykewyrm`, oldid `6530886`, timestamp
`2012-11-04T08:09:26Z`, literal wikitext establishes:

- level 130, 1,200 LP, Slayer 77, and 120 Slayer XP;
- non-aggressive six-tick Melee and magical-ranged attacks;
- approximate maxima of 120 Melee, 125 magical ranged, and 300 special;
- Slash and Ranged weaknesses;
- assignment-only mound investigation, rise, and damage eligibility;
- a burrow special which deals 300, is avoidable through movement or nearby
  obstacles, and hits twice for 600 only if the player runs over the surfacing
  wyrm;
- an observed special frequency averaging once per 15–20 attacks;
- no guaranteed drop; and
- the complete named charm, rune/talisman, equipment, seed, herb, resource,
  clue, spin, effigy, focus-sight, and rare-table sets.

Source:
<https://runescape.wiki/w/Desert_strykewyrm?oldid=6530886>.

Cutoff `Talk:Desert strykewyrm`, oldid `4665384`, timestamp
`2011-08-25T23:45:45Z`, independently corroborates assignment-only mound
activation, the rare/inaccurate non-melee attack, several named drops and
quantities, and the rare Focus sight. It supplies no complete hidden selector:
<https://runescape.wiki/w/Talk:Desert_strykewyrm?oldid=4665384>.

The settled no-position Combat contract permits movement/obstruction to become
a target-local special-risk abstraction. It does not license replacing the
period single-hit default with Darkan's unconditional double hit or inventing
hidden combat levels and drop quantities.

## Cache evidence

Rev-727 and independently dated rev-742 both contain attackable Aquanite NPC
9172. Both contain mound NPC 9464 and attackable Desert strykewyrm NPC 9465.
The baby Aquanite social-Slayer pet identities are separate and excluded.

Darkan's cache-derived bonus dump records:

- Aquanite: Stab/Slash/Crush/Magic/Ranged defence
  `30/90/90/90/0`, corroborating the period Ranged and Stab weaknesses; and
- Desert strykewyrm: Ranged attack `10` and
  Stab/Slash/Crush/Magic/Ranged defence `0/0/180/200/0`, corroborating the
  period Slash and Ranged weaknesses.

Cache definitions prove identities, options, and client bonuses, not the five
server-side combat levels.

## Executable evidence

Pinned Darkan paths and commits:

- Aquanite incomplete combat row:
  `data/npcs/combatdefs/uncategorized/aquanite (nostats).json`, commit
  `e1e71c9fb5979ba72bc66f4a251c725c8d0e1239`;
- Desert-strykewyrm incomplete combat row:
  `data/npcs/combatdefs/uncategorized/desert_strykewyrm (nostats).json`,
  commit `60c7e32436316a03b7695d245f7b68ae678c3306`;
- generated-level loader:
  `src/main/java/com/rs/game/model/entity/npc/combat/NPCCombatDefinitions.java:142-150,289-319`,
  commit `e1e71c9fb5979ba72bc66f4a251c725c8d0e1239`;
- Desert-strykewyrm task/stomp/attack/burrow handler:
  `src/main/java/com/rs/game/content/skills/slayer/npcs/Strykewyrm.kt:47-286`,
  commit `32df64ff4d6b9500d5786ec71bce2721190d20b8f`;
- Aquanite ordinary drops:
  `data/npcs/drops/aquanite.json`, commit
  `38fdd530aa65851d6ed00d37be59459a2dc5a7e7`;
- Desert-strykewyrm ordinary drops:
  `data/npcs/drops/desert_strykewyrm.json`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- charm thresholds:
  `data/npcs/charmDrops.txt:10,50`, commit
  `3d96f2f98d05f837fa7294566a536b227eddc575`;
- Desert-strykewyrm clues:
  `src/main/java/com/rs/utils/NPCClueDrops.java:162,175`, commit
  `2b63cd96a7859df145204b0e8d96aedbc0515680`; and
- cache bonuses:
  `developer-information/npcListBonuses.txt:9174,9466-9467`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`.

Both combat JSON files agree on LP, broad style, visible ordinary maximum, and
a 59-tick respawn. Both zero every combat level. The loader fills those values
through `generateLevels(combatLevel, hitpoints / 10)` and marks
`realStats = false`; they are executable scaffolding, not recovered content.

There is no Aquanite-specific attack handler in Darkan. The generic Magic row
therefore never turns off Prayer and never produces the 250 special.

For Desert strykewyrm, Darkan's inclusive 21-way attack selector attempts
Melee for values 0–7 in range, Magic for values 8–19 plus blocked Melee
branches, and burrow only at 20. That is a nominal 1/21 burrow lead, outside
the period once-per-15–20 average. Its Desert branch also applies **two**
independent 100–300 flat hits whenever the target remains in range. The period
record instead makes one 300 hit normal and the second hit conditional on the
player running over the surfacing wyrm. Darkan's no-position result cannot be
copied as a faithful consequence.

## Drop-selector conflicts

Aquanite's non-zero Darkan rows form a 100,000-slot selector:

- ten rows receive 8,411 slots each;
- 26 rows receive 539 slots each;
- seven rows receive 267 slots each; and
- seven slots are empty.

The structure is executable but conflicts with visible period quantities.
Water runes use a continuous random ×30–100 range, producing disallowed
×50–99 values between the period ×30–49 and ×100 outputs. Seaweed uses an
unnoted ×3–500 range against period noted ×3–6. The selector also omits
period-visible Soul-rune quantities ×4–6 because its row is fixed at ×3.

Aquanite's Darkan charm thresholds `10-5-5-6` enumerate losslessly to 202
slots: 12 Gold, 3 Green, 3 Crimson, 4 Blue, and 180 empty. The period record
proves the charm family, not that distribution.

Desert strykewyrm's mixed-denominator rows enumerate losslessly to a
1,600,000-slot lead with 4,507 empty slots. The period-visible conflicts are
material:

- Potato cactus ×1–5 unnoted against ×5–10 noted;
- herbs fixed at ×1 against period ×1–4; and
- Coins ×1–200 against the period named sets beginning at ×200 and extending
  through ×4,500.

Darkan's Focus sight 1/512 lead is close to the period Adventure-log estimate
of 1/484 but does not independently close an exact rate. Its charm thresholds
`4-2-12-1` enumerate to 606
slots: 11 Gold, 5 Green, 59 Crimson, 3 Blue, and 528 empty. Darkan also
supplies hard clues at 1/128 and elite clues at 1/500; the period article
corroborates both tiers but not those exact rates.

## Blocking findings

1. **Both five-level combat rows are absent.** Darkan generates and explicitly
   marks every level non-real.
2. **Aquanite's distinctive special is missing.** There is no executable
   Prayer-off consequence and no source-ready trigger rate.
3. **Aquanite's ordinary selector conflicts with period quantities.** Water
   runes, Seaweed, and Soul runes cannot be copied faithfully.
4. **Desert burrow frequency conflicts.** Darkan's nominal 1/21 is outside the
   period once-per-15–20 observation.
5. **Desert burrow consequence conflicts.** Darkan always attempts two
   100–300 hits; the period default is one 300 hit, with two hits only for a
   positional player mistake.
6. **Desert ordinary drops conflict with period quantities.** Potato cactus,
   herbs, and Coins are directly incompatible.

## Explicit omissions and required unblock

- No target sprites, Amulet-of-ranging/Focus-sight assets, or drop icons are
  installed while neither target is runtime-certifiable.
- No Kuradal-only Aquanite reward gate is applied to Sumona.
- No baby Aquanite pet, other strykewyrm family, positional map, desert heat,
  or quest content is added.

Do not activate either family until a period-lineage source supplies the five
combat levels and reconciles the listed special/drop conflicts. Aquanite also
needs a corroborated hidden trigger roll. Desert strykewyrm needs an
owner-already-settled no-position consequence recorded with enough precision
to distinguish the default one-hit event from the avoidable double-hit error;
the implementation thread may not infer that clause from Darkan's conflicting
handler.

No new design question was opened. Under the 2026-07-19 design-closure rule,
these are source and authority dependencies, not invitations to reinterpret
the Combat contract.

## Workflow telemetry

Codex Workflows run `d6abe20b-b6ff-432b-8ebf-327218b309b9` launched two
bounded Sol-high read-only leaves on the repaired runtime. Neither provider
emitted `thread.started`; both remained at `session_id=null`, zero tokens,
zero tool calls, and no stdout/progress telemetry. The root canceled the run
after independently reproducing every recorded finding. No workflow output was
used as evidence.
