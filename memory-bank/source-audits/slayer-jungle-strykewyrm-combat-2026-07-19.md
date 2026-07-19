# Slayer Jungle-strykewyrm Combat audit — 2026-07-19

Status: **source-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the ordinary Jungle strykewyrm required by Chaeldar's settled
assignment registry. It closes the visible period identity, Slayer/task gate,
attack families, poison consequences, tunnelling concept, drop set, cache
identity, and Darkan execution boundary. It does **not** add
`jungle_strykewyrm` to `COMBAT_ENEMY_DATA`.

Darkan explicitly names the only combat definition `nostats`, so all five
combat levels are generated and marked non-real. Its custom handler also
contradicts the cutoff record on melee poison, burrow damage, and burrow poison.
The ordinary-drop reconstruction disagrees with several visible cutoff
quantities. These are source conflicts, not open design choices.

Chaeldar therefore remains hidden at **25/34**. `jungle_strykewyrms` retains
its `combat_target` blocker. No denominator or readiness feature is changed.

## Period evidence

RuneScape Wiki `Jungle strykewyrm`, oldid `6588104`, timestamp
`2012-11-19T16:58:00Z`, literal wikitext establishes:

- level 110, 1,100 LP, Slayer 73, and 110 Slayer XP;
- attackability only while the player has a Jungle-strykewyrm assignment;
- non-aggression, poison immunity, six-tick Melee/Magic attacks, and an
  87-LP ordinary maximum;
- Ranged and Stab weaknesses;
- melee poison starting at 48 LP whenever the melee attack damages the player,
  even when protection Prayer prevents damage;
- a rarer Magic cloud which may start poison at 88 LP;
- a tunnelling special described as hitting 300 or more and starting poison at
  40–80 LP, avoidable through movement or obstruction;
- no guaranteed drop;
- the complete named charm, rune/talisman, herb, seed, equipment, resource,
  hard-clue, elite-clue, Spin-ticket, effigy, and rare-drop-table sets; and
- assignment membership for Chaeldar, Sumona, Duradel/Lapalok, and Kuradal.

Source:
<https://runescape.wiki/w/Jungle_strykewyrm?oldid=6588104>.

The same revision's infobox lists `300` as the special maximum while its body
says `300 plus`. That exact cap is therefore internally inconsistent even
before comparison with emulator code.

Cutoff `Talk:Jungle strykewyrm`, oldid `5499640`, timestamp
`2012-04-16T09:22:14Z`, corroborates 1,100 LP, 110 Slayer XP, Chaeldar
assignment, Magic attacks, obstacle suppression of the burrow, several
ordinary drops and quantities, Hexcrest rarity observations, and hard clues.
Its reports are useful corroboration but do not expose hidden selectors:
<https://runescape.wiki/w/Talk:Jungle_strykewyrm?oldid=5499640>.

The settled no-position Combat contract maps obstruction and movement to a
contextual special-attack risk rather than tile micromanagement. It does not
license invented levels, selector odds, or replacement poison values.

## Cache evidence

Rev-742, dated `2012-11-07`, contains mound NPC 9466 and attackable
`Jungle strykewyrm` NPC 9467. Darkan's cache-derived bonus dump records NPC
9467 with Magic defence `200`, Ranged defence `-60`, and zeroed remaining
attack/strength and defence bonuses. These records corroborate the identity
and visible Ranged weakness, not hidden server combat levels or special
selectors.

## Executable evidence

Pinned Darkan paths and commits:

- incomplete combat row:
  `data/npcs/combatdefs/uncategorized/jungle_strykewyrm (nostats).json`,
  commit `60c7e32436316a03b7695d245f7b68ae678c3306`;
- custom task/attack/poison/burrow handler:
  `src/main/java/com/rs/game/content/skills/slayer/npcs/Strykewyrm.kt`,
  commit `32df64ff4d6b9500d5786ec71bce2721190d20b8f`;
- ordinary drops:
  `data/npcs/drops/jungle_strykewyrm.json`,
  commit `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- charm thresholds:
  `data/npcs/charmDrops.txt:103`,
  commit `3d96f2f98d05f837fa7294566a536b227eddc575`;
- clue selectors:
  `src/main/java/com/rs/utils/NPCClueDrops.java:161,174`,
  commit `2b63cd96a7859df145204b0e8d96aedbc0515680`; and
- cache bonuses:
  `developer-information/npcListBonuses.txt:9468-9469`, repository root
  commit `c6fbe036b1743f4dd6067ec178332c69c3708856`.

The combat JSON agrees on 1,100 LP, an 87 maximum, passivity, and a 59-tick
respawn. It labels its broad attack style `RANGE` while the custom handler
calculates both ordinary attacks against `CombatStyle.MAGIC`. More
importantly, the JSON omits Attack, Strength, Defence, Magic, and Ranged
levels. `NPCCombatDefinitions.getDefs()` fills those omissions through
`generateLevels(combatLevel, hitpoints / 10)` and explicitly sets
`realStats = false`. They are executable fallbacks, not recovered period
values.

The handler enforces Slayer 73 and the live assignment before the mound rises
or damage can land. Its 21-way selector attempts Melee for values 0–7 when in
range, Magic for values 8–19 plus any blocked Melee branch, and burrow only at
20. No period source recovered in this pass corroborates that hidden selector.

The poison and special implementation materially conflicts with the cutoff
page:

- melee makes an independent 1-in-11 poison roll at 44 LP before calculating
  the attack, instead of applying 48-LP poison whenever a melee hit damages;
- the rare Magic cloud uses a 1-in-11 trigger and then a one-half 88-LP poison
  roll, selectors not exposed by the period page;
- burrow deals a flat random 100–300 and always applies 88-LP poison, while the
  cutoff page says 300 or more and poison starting at 40–80; and
- the no-position AnkiScape poison seam currently accepts one
  `poison_damage` plus a shared fixed NPC-attack chance. It cannot encode the
  three distinct attack-conditional poison channels without a certified
  special contract.

The Darkan ordinary-drop file is a useful item lead, not a shippable selector.
Its common rows give Coins ×1–200 against the cutoff ×200–7,844, noted Papaya
fruit ×1–3 against ×3–10, and single herbs against the cutoff ×1–4 rows. It
also adds Soul runes and several talisman/seed rows not named by the cutoff
article. Absence from a player-built table is not disproof, but the visible
quantity conflicts prevent direct adoption of the file as the complete
ordinary selector.

Darkan's charm thresholds are `6-14-3-1`. Lossless enumeration of
`CharmDrop.getCharmType()` produces a 606-slot lead: 16 Gold, 64 Green,
7 Crimson, 3 Blue, and 516 empty. The cutoff article corroborates the charm
family but not that hidden distribution. Darkan supplies hard clues at 1/128
and elite clues at 1/500; the cutoff article corroborates both clue tiers but
not either rate.

## Blocking findings

1. **Combat levels are absent.** Darkan generates all five hidden levels and
   marks them non-real. The source standard forbids promoting them.
2. **Melee poison conflicts.** The cutoff condition is 48-LP poison on a
   damaging melee hit; Darkan instead performs an independent 1-in-11,
   44-LP roll.
3. **Burrow damage and poison conflict.** Darkan's 100–300 plus fixed 88 poison
   contradicts the cutoff 300-or-more plus 40–80 poison record.
4. **The hidden attack selectors remain uncorroborated.** Darkan's 21-way
   attack selector and rare-cloud rolls are executable reconstruction values,
   not closed period values.
5. **The ordinary selector has visible quantity conflicts.** Coins, Papaya
   fruit, and herbs cannot be copied without discarding cutoff evidence.
6. **The current target schema is insufficient.** One generic
   `poison_damage` and shared poison chance cannot faithfully represent the
   attack-conditional 48/88/40–80 channels.

## Explicit omissions

- No Jungle-strykewyrm sprite, Hexcrest icon, or ordinary-drop assets were
  installed because the target is not runtime-certifiable.
- Desert and Ice strykewyrms, other Slayer-master pools, anti-poison equipment,
  and positional obstacle simulation are outside this family audit.
- The mound-rise delay, ordinary Melee/Magic selector, rare-cloud selector,
  burrow selector, exact special cap, and all uncorroborated drop/charm/clue
  rates remain `source_blocked`.

## Required unblock

Do not activate the family until a period-lineage source closes the five combat
levels and reconciles the poison/special conflicts, or a newer owner-approved
record explicitly supersedes those source obligations. The settled Combat
contract would also need an already-authorized attack-conditional poison
mapping before this distinctive loop can certify. Copying Darkan's generated
levels or conflicting handler would violate the source standard.

No design question was opened. Under the 2026-07-19 design-closure rule these
are source and implementation blockers, not invitations to reinterpret the
Slayer or Combat contracts.

## Workflow telemetry

Codex Workflows run `48f9384d-da0b-41ce-8d21-b2ac80bafbe3` launched one
narrow Sol-high read-only leaf. The provider never emitted `thread.started`;
the leaf remained at zero tokens and zero tool calls while stderr reported
`failed to refresh available models: timeout waiting for child process to
exit`. The root canceled it at `2026-07-19T08:50:09Z` after independently
reproducing the complete audit. This is the already-observed pre-session model
refresh failure signature, not evidence about the source verdict.
