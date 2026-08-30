# Snake-hide Bush-snake acquisition audit — 2026-08-30

## Scope and verdict

This slice closes the ordinary acquisition route for `Snake hide` and its
existing Snakeskin tanning and Crafting chain. It does not merge ordinary Snake
hide with the distinct swamp-snake item.

**Verdict:** a selectable Bush snake is the smallest live translation of the
period Tai Bwo Wannai Cleanup source. The target requires completed Jungle
Potion, Woodcutting 10, and a Machete. Every kill always drops one Bones and an
unnoted quantity of 1–5 ordinary Snake hides. The period record does not state
the quantity weighting, so the executable uniform choice is registered as a
placeholder. The target uses the existing Combat persistence, answer-undo, and
target-row contracts.

## Period Wiki evidence

### Bush-snake identity, combat, and drops

The nearest pre-EOC revision is:

- RuneScape Wiki `Bush snake`, oldid `6352282`, timestamp
  `2012-10-05T16:21:41Z`:
  <https://runescape.wiki/w/Bush_snake?oldid=6352282>.

Its literal wikitext states combat level 35, 250 LP, maximum hit 38, Stab
weakness, Melee style, poison starting at 68 LP, attack speed 7, guaranteed
Bones ×1, and guaranteed Snake hide ×1–5. It also says that Bush snakes appear
while players hack jungle during Tai Bwo Wannai Cleanup.

Oldid `6352282` carries `{{beta}}`. The same complete value set and both drop
rows are present in the non-beta revision oldid `5190727`, timestamp
`2012-01-27T00:47:39Z`:
<https://runescape.wiki/w/Bush_snake?oldid=5190727>. This second oldid closes
the beta-page concern instead of treating the marked revision as sole
authority.

The Cleanup page's broad warning says that its snakes inflict 48 LP poison,
which conflicts with the Bush-snake-specific 68-LP row. The product follows the
stable NPC-specific value found in both the beta and non-beta Bush-snake
revisions. The current Combat poison model has 10-LP tiers, so it executes and
displays the nearest 70-LP opening tick. This is an explicit product
representation limit, not a claim that the historical value was 70.

### Ordinary hide identity and independent drop corroboration

- RuneScape Wiki `Snake hide`, oldid `6009794`, timestamp
  `2012-07-29T12:51:10Z`:
  <https://runescape.wiki/w/Snake_hide?oldid=6009794>.

The item page distinguishes ordinary Snake hide from `Snake hide (swamp)`. It
independently states that Bush snakes appear randomly during Tai Bwo Wannai
Cleanup and always drop 1–5 ordinary hides. It also lists Mos Le'Harmless,
Soul Wars Gamble, and Familiarisation as alternate sources.

### Cleanup access and encounter context

- RuneScape Wiki `Tai Bwo Wannai Cleanup`, oldid `6539724`, timestamp
  `2012-11-07T00:21:17Z`:
  <https://runescape.wiki/w/Tai_Bwo_Wannai_Cleanup?oldid=6539724>.
- RuneScape Wiki `Jungle Potion`, oldid `6555418`, timestamp
  `2012-11-14T16:30:32Z`:
  <https://runescape.wiki/w/Jungle_Potion?oldid=6555418>.

The Cleanup revision requires completed Jungle Potion before participation. It
requires a Machete to hack jungle and sets the minimum light-jungle requirement
at Woodcutting 10. Its monster table names Bush snake and Snake hide, while the
Jungle Potion reward section independently names access to the Cleanup
activity.

Bush snakes are random threats produced by jungle hacking in RuneScape. The
existing AnkiScape Combat selector has no world-location or random-encounter
surface. The selectable row therefore models the resulting fight and its
product, gated by the minimum sourced access requirements. It does not claim
that one review equals one jungle hack or encode an encounter frequency.

## Cache identity evidence

OpenRS2 cache revision 742 is dated `2012-11-07`, thirteen days before the EOC
cutoff. The immutable archive has SHA-256
`9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`:

- cache page: <https://archive.openrs2.org/caches/runescape/544>
- archive: <https://archive.openrs2.org/caches/runescape/544/disk.zip>
- local extracted cache:
  `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache`

The exact repository queries were:

```text
bash tools/query_openrs2_cache_definitions.sh '/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache' npc --id 2489 2490
bash tools/query_openrs2_cache.sh '/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache' --id 6287
```

The results identify NPCs `2489` and `2490` as level-35 `Bush snake` with an
`Attack` option. Item `6287` is `Snake hide`, model `8861`, non-stackable,
exchangeable, and has the `drop` option. A direct definition probe also reports
`attackDelay=3` for both NPCs. That client value does not match the period
article's attack speed 7 and is not treated as a server-cadence replacement;
the target uses the repeated period value 7 and records the cache conflict.

## Darkan reconstruction evidence

### Combat definition

Path:

```text
/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/bush_snake (noanims).json
```

The file was created in commit
[`6a5048b96aeeb7f594ba700d9fcc3df4a43adfd5`](https://gitlab.com/darkanrs/world-server/-/commit/6a5048b96aeeb7f594ba700d9fcc3df4a43adfd5)
and last changed for its relevant aggression fields in commit
[`14e49a561bab1441384022421d10dc03a8d837f0`](https://gitlab.com/darkanrs/world-server/-/commit/14e49a561bab1441384022421d10dc03a8d837f0).
The permanent file view is:
<https://gitlab.com/darkanrs/world-server/-/blob/14e49a561bab1441384022421d10dc03a8d837f0/data/npcs/combatdefs/uncategorized/bush_snake%20%28noanims%29.json>.

It reconstructs 250 LP, maximum hit 38, Melee style, Stab attack bonus type,
respawn delay 59, and hidden combat levels Attack 25, Strength 25, Defence 50,
Magic 1, and Ranged 1. It does not state numeric attack, defence, or strength
bonuses. The executable zero vector is therefore registered as
`combat.bush_snake_combat_bonuses` rather than presented as recovered history.

### Drop definition

Path:

```text
/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/bush_snake.json
```

The supplying commit is
[`c6fbe036b1743f4dd6067ec178332c69c3708856`](https://gitlab.com/darkanrs/world-server/-/commit/c6fbe036b1743f4dd6067ec178332c69c3708856),
with permanent file view:
<https://gitlab.com/darkanrs/world-server/-/blob/c6fbe036b1743f4dd6067ec178332c69c3708856/data/npcs/drops/bush_snake.json>.

Darkan independently reconstructs guaranteed Bones ×1 and ordinary Snake hide
item `6287` ×1. Its fixed hide quantity conflicts with both period Wiki rows,
which state an always-on range of 1–5. The period range wins. No source states
how the five quantities are weighted, so
`combat.bush_snake_hide_quantity_distribution` supplies the uniform executable
choice until a period server routine or qualified cutoff-era sample replaces
it.

## Product translation

- The target is available only after Jungle Potion completion, at Woodcutting
  10 or higher, and while a Machete is carried or equipped.
- The target uses sourced level 35, 250 LP, 38 maximum hit, Melee style,
  attack speed 7, and the Darkan hidden combat-level reconstruction.
- The sourced 68-LP poison opens at 70 LP because the shared poison engine uses
  10-LP tiers. The existing game-main-backed 4-in-10 NPC poison application
  chance remains unchanged.
- Bones ×1 is guaranteed. One always-on hide table produces an inclusive 1–5
  ordinary Snake-hide quantity with registered placeholder weighting.
- The existing `tan_snakeskin` Utility action consumes one Snake hide and 15
  Coins to produce one Snakeskin. The five existing Snakeskin armour recipes
  then close without recipe changes, for six downstream items in total.
- Combat already saves inventory mutations and snapshots review state before an
  answer. The new producer reuses those paths; Anki review undo restores the
  exact pre-review player state.

## Assets

| Asset | Source upload timestamp | Source SHA-1 | Normalized dimensions | Normalized SHA-256 |
| --- | --- | --- | --- | --- |
| `summoningitems/snake_hide.png` | `2011-03-13T13:04:58Z` | `7d7a0d0bf40b57b877c45fbed93187deac7a5f27` | 28×28 | `171eca705a3cd464933ef712c8ac3d1017ac89932b0b4bbb9de2f72a5e9657d3` |
| `combatenemies/bush_snake.png` | `2011-07-29T13:54:56Z` | `1a7e9ae59cd2c0ee81b819f19321f0504aba13a3` | 48×42 | `f9964c85d15b1b0b99154de4fcc81e2751d27ee7257e410250dc567881fb460e` |

Permanent file pages and archived source URLs:

- <https://runescape.wiki/wiki/File:Snake_hide.png>
- <https://runescape.wiki/images/archive/20140329021955%21Snake_hide.png?13c6a>
- <https://runescape.wiki/wiki/File:Snake.png>
- <https://runescape.wiki/images/archive/20240325161336%21Snake.png?826cd>

The existing ordinary-hide sprite is reused; no duplicate item asset is added.
The Bush-snake source article transcludes `File:Snake.png`, and the enemy fetch
map now records that title explicitly.

## Rejected and deferred routes

- `Snake (Mos Le'Harmless)`, oldid `6352638`, timestamp
  `2012-10-05T16:54:07Z`, proves an exact always-on one-hide producer:
  <https://runescape.wiki/w/Snake_(Mos_Le%27Harmless)?oldid=6352638>.
  `Mos Le'Harmless`, oldid `6549119`, timestamp `2012-11-12T06:14:09Z`,
  requires Cabin Fever access:
  <https://runescape.wiki/w/Mos_Le%27Harmless?oldid=6549119>.
  The live reachability closure cannot start Cabin Fever, so this historically
  valid route does not satisfy the player-finishable acquisition requirement.
- Soul Wars Gamble is not used because the period item page gives only its
  5–10 output range, not the selection probability, and the current evidence
  does not settle ordinary versus noted output identity.
- Familiarisation remains a separate shard and level-dependent reward system;
  this slice does not turn its box into a direct source.
- `Snake hide (swamp)` is a separate item identity in the period source. Its
  absence from the live item registry is follow-up work and is not repaired by
  aliasing it to item `6287`.
- A complete Tai Bwo Wannai Cleanup activity, jungle-hack success and encounter
  rolls, favour, trading sticks, and world travel remain outside this producer
  slice.

## Reachability result

The seven pinned metrics change as follows:

| Metric | Before | After |
| --- | ---: | ---: |
| Action count | 1,600 | 1,600 |
| Reachable item count | 2,217 | 2,224 |
| Orphan input count | 192 | 190 |
| Root orphan count | 40 | 39 |
| Cascade orphan count | 152 | 151 |
| Unresolved action count | 284 | 277 |
| Seed item count | 1,164 | 1,165 |

The final routes are:

```text
Snake hide -> combat:bush_snake
Snakeskin -> Utility:tan_snakeskin
Snakeskin bandana -> Crafting:leather_snakeskin_bandana
Snakeskin body -> Crafting:leather_snakeskin_body
Snakeskin boots -> Crafting:leather_snakeskin_boots
Snakeskin chaps -> Crafting:leather_snakeskin_chaps
Snakeskin vambraces -> Crafting:leather_snakeskin_vambraces
```

None of the seven family items remains in `orphan_inputs`.

## Acceptance contract

- A player must complete Jungle Potion, reach Woodcutting 10, and carry or
  equip a Machete before selecting the Bush snake.
- A real Combat kill must always produce Bones and 1–5 ordinary Snake hides.
- A real Utility reducer must tan one hide, and all five existing Snakeskin
  armour products must remain reachable.
- The ordinary item must remain item `6287`, non-stackable, tradeable, and use
  its period asset. The target must use the period Bush-snake asset.
- Combat review save and Anki answer undo must preserve and restore the exact
  inventory state.
- Reachability must name all seven routes above and keep all seven pinned
  metrics at the measured values.
- Focused data, integration, registry, reachability, placeholder, and shown
  offscreen Qt checks plus both full discovery lanes must pass before closure.
