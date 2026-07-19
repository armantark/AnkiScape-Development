# Slayer Fungal-mage Combat audit — 2026-07-19

Status: **source-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass closes the period identity, assignment gate, magic attack, infestation,
neem-oil effect, ordinary drops, charm lead, client identities, and Darkan
execution boundary for the level-120 Fungal mage. It does **not** activate
`fungal_mage` in `COMBAT_ENEMY_DATA`.

The settled Combat contract requires a complete source-backed stat row before an
enemy becomes attackable, and the settled Slayer contract requires the
distinctive kill loop plus its acquisition dependency before a family can
certify. Darkan deliberately labels this row `nostats` and generates all five
combat levels from combat level and LP at runtime. That reconstruction is not a
period value and the source standard does not permit provisional levels. The
same implementation also disagrees with the cutoff record about ordinary
Melee/Ranged resistance.

Chaeldar therefore remains hidden at **25/34** readiness. Fungal magi retain
their existing `combat_target` blocker; the already-declared `neem_oil`
readiness feature is not marked complete ahead of the target and its real
item/acquisition chain.

## Period evidence

### Fungal mage

RuneScape Wiki `Fungal mage`, oldid `6580164`, timestamp
`2012-11-19T05:48:51Z`, literal wikitext establishes:

- level 120, 1,200 LP, Slayer 1, and 120 Slayer XP;
- Magic 50 only to receive the assignment, not to kill the monster;
- non-aggressive six-tick Magic attacks with a 114-LP maximum;
- poison immunity and weakness to Magic and neem oil;
- rapid 2–3 LP infestation hits while within one square, without Prayer drain;
- complete prevention of infestation while affected by neem oil;
- severe Melee/Ranged resistance described as almost one tenth of normal
  damage, with dwarf multicannon exempt;
- about three safe hits after applying neem oil;
- guaranteed Accursed ashes and one to three Neem drupes;
- common Chaos runes ×15–40, noted Pure essence ×25, noted Snape grass ×4,
  noted Potato cactus ×1 or ×8, and noted Limpwurt root ×1–2;
- the full named seed, Gorajian mushroom, Polypore-spore, Fungal-flake,
  Spin-ticket, and ancient-effigy drop sets; and
- respawn within five seconds.

Source:
<https://runescape.wiki/w/Fungal_mage?oldid=6580164>.

Cutoff `Talk:Fungal mage`, oldid `5997258`, timestamp
`2012-07-26T21:59:21Z`, corroborates noted Limpwurt root, strong
Melee/Ranged resistance, seed-table observations, and the Potato-cactus
conflict. One report says a single noted cactus; the specialist reply says
Fungal mages consistently dropped eight and the single item likely came from
an Infested axe. The article's `1, 8` row remains the honest period
observation; it does not supply a selector weight:
<https://runescape.wiki/w/Talk:Fungal_mage?oldid=5997258>.

### Neem oil

RuneScape Wiki `Neem oil`, oldid `6548563`, timestamp
`2012-11-11T23:11:09Z`, establishes:

- one Neem drupe squished while an empty jug is present creates oil;
- one jug holds up to 2,000 stackable-in-container doses;
- `Sprinkle` automatically selects a target within six squares;
- one dose weakens maximum hit, attack rate, and defence, and disables toxic
  fungus;
- the effect lasts about 20 seconds and cannot be refreshed on the same target
  before expiry;
- applying it grants 6.5 Herblore XP; and
- applying oil can produce its own independent resource drop.

Source:
<https://runescape.wiki/w/Neem_oil?oldid=6548563>.

RuneScape Wiki `Polypore Dungeon`, oldid `6578900`, timestamp
`2012-11-18T15:10:35Z`, independently describes the universal
Melee/Ranged resistance, Magic weakness, fungal-damage ranges, neem's
immobilization/attack suppression, and the vine acquisition route:
<https://runescape.wiki/w/Polypore_Dungeon?oldid=6578900>.

The no-position Combat contract already determines the mapping principle:
proximity is contextual Combat risk rather than a tile-control minigame. It
does not supply missing levels, resistance arithmetic, or resource selectors.

## Cache evidence

Rev-742, dated `2012-11-07`, contains:

- NPC 14690, `Fungal mage`, with `Attack`;
- NPC 14691, the same attackable identity while weakened;
- item 22444, `Neem oil`, with `Sprinkle`, `Check`, `Empty`, and `Drop`;
- item 22445, `Neem drupe`, with `Squish` and `Drop`; and
- item 20266, `Accursed ashes`, with `Scatter` and `Drop`.

The cache independently corroborates the identities and interactions. As a
client configuration layer, it cannot supply server combat levels, damage
reducers, timers, or drop probabilities.

Darkan's cache-derived bonus dump records both forms with zero attack and
strength bonuses, Stab/Slash/Crush defences `60/70/50`, Ranged defence `0`,
and Magic defence changing from `-30` to `-50` while neemed. The paired CS2
rows change key 14 from `4` to `6`; this is preserved as a cache observation,
not asserted as a server attack-delay formula.

## Executable evidence

Pinned Darkan paths and commits:

- incomplete combat row:
  `data/npcs/combatdefs/uncategorized/fungal_mage (nostats).json`,
  commit `e1e71c9fb5979ba72bc66f4a251c725c8d0e1239`;
- ordinary drops:
  `data/npcs/drops/fungal_mage.json`,
  commit `9b5ab68a43838c765e92d10e9b0108999dc9ed69`;
- charm thresholds:
  `data/npcs/charmDrops.txt:63`,
  commit `3d96f2f98d05f837fa7294566a536b227eddc575`;
- cache bonuses:
  `developer-information/npcListBonuses.txt:14692-14693`,
  repository root commit `c6fbe036b1743f4dd6067ec178332c69c3708856`;
- infestation and neem transformation:
  `src/main/java/com/rs/game/content/skills/slayer/npcs/PolyporeNPC.java`,
  commit `c971be5fe`; and
- drupe, charge-container, and sprinkle actions:
  `src/main/java/com/rs/game/content/world/areas/dungeons/polypore/PolyporeDungeon.kt`,
  current file lineage through commit
  `41c877c20b52be02781f45d9089f7b1033fa71dc`.

The combat JSON agrees on 1,200 LP, 114 maximum, Magic, passive aggression,
and a 59-tick respawn. It omits every combat level. In
`NPCCombatDefinitions.getDefs()`, Darkan detects that omission and calls
`generateLevels(combatLevel, hitpoints / 10)`, which fabricates equal
Attack/Strength/Defence/Ranged/Magic values from the displayed combat level.
`realStats` is explicitly set false. Those generated values are executable
fallbacks, not recovered period stats.

`PolyporeNPC` supplies a 2–3 LP infestation when the target is in melee range,
a 20-second neem transformation, one-fifth incoming Melee/Ranged damage before
neem, half outgoing Magic/Ranged damage after neem, and the cache defence-form
swap. The duration and infestation magnitude agree with the cutoff pages, but
the one-fifth reducer conflicts with the Fungal-mage page's almost-one-tenth
statement. The broader dungeon page itself says one fifth or one sixth, so the
period wiki record is internally inconsistent on this exact reducer.

The Darkan ordinary drop file has guaranteed Accursed ashes and Neem drupe
×1–3, then independent candidate rows. Its resource rows use
`751/6250`, seed rows use `219/25000`, and rare-seed rows use
`267/100000`. The cutoff article corroborates the items and quantities but
does not corroborate those hidden rates. The file also encodes only the
eight-noted Potato-cactus form and one Limpwurt root, while the cutoff article
records `1, 8` cactus and `1–2` Limpwurt root. These rows therefore remain
leads rather than a shippable selector.

Darkan charm thresholds `5-12-2-1`, losslessly enumerated through
`CharmDrop.getCharmType()`, produce a 606-slot selector: 14 Gold, 56 Green,
5 Crimson, 3 Blue, and 528 empty. The cutoff page corroborates that Fungal
mages drop charms but does not expose the hidden distribution. No Fungal-mage
row exists in Darkan's clue-drop registry, and the cutoff article names no clue
scroll; no clue channel is added or inferred.

## Blocking findings

1. **Combat levels are absent.** No period source found in this pass supplies
   Attack, Strength, Defence, Magic, and Ranged levels. Darkan explicitly marks
   its generated replacements as non-real. The pre-EOC standard forbids
   inventing levels.
2. **Resistance arithmetic conflicts.** The individual cutoff page says almost
   one tenth; the dungeon page says one fifth or one sixth; Darkan implements
   exactly one fifth. This is a concrete source conflict, not an owner-design
   choice.
3. **Ordinary drop rates and two quantities are unresolved.** Darkan's rates
   lack independent corroboration, and its Potato-cactus/Limpwurt quantities do
   not preserve the full cutoff article row.
4. **The acquisition chain is not live.** Neem oil, Neem drupe, and the
   Polypore resources exist only in generated value metadata, not as canonical
   runtime item/action identities with their jug charges, Herblore XP, and
   independent sprinkle-drop transaction. Marking `neem_oil` ready now would
   create a dead feature flag.

## Required unblock

Activate Fungal magi only after:

- a period-lineage source closes the five missing combat levels, or a newer
  owner-approved record explicitly authorizes a non-level fallback despite the
  source standard;
- the resistance conflict is resolved by period evidence or an explicit newer
  abstraction record;
- the ordinary selector is reconciled without silently dropping the cutoff
  quantity variants; and
- the canonical Neem-drupe/jug/oil acquisition and atomic sprinkle action are
  implemented with their real item identities.

No design question was opened. Under the 2026-07-19 design-closure rule, these
are source and dependency blockers; they are not invitations to reinterpret the
settled Combat or Slayer contracts.

## Workflow telemetry

Codex Workflows run `0cead6ef-4203-40dd-9a80-c9e76a9773cb` launched one
bounded Sol-high read-only leaf. Startup took more than seven minutes before
session `019f7978-6384-79b2-b825-ed3f7fe89a5a` was created. The provider then
repeatedly reported `request timed out` reconnects and never produced a token,
tool call, or result; stderr also recorded model-refresh child-process timeouts.
The root canceled the unhealthy leaf at `2026-07-19T08:32:17Z` after
independently reproducing the complete audit. This is a post-session provider
connection failure, distinct from the earlier zero-session bootstrap failure.
