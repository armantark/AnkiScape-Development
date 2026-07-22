# Stronghold of Player Safety horizontal readiness

Date: `2026-07-22`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period reward, route, equipment, and Cockroach soldier public combat
facts are closed; hidden NPC stats and drop rates remain source-blocked.**

## Pinned period evidence

The literal wikitext was fetched through the RuneScape Wiki API and inspected,
not inferred from a current rendered page.

- `Stronghold of Player Safety`, oldid `6487359`,
  `2012-10-27T21:41:27Z`:
  <https://runescape.wiki/w/Stronghold_of_Player_Safety?oldid=6487359>
- `Safety gloves`, oldid `6081806`, `2012-08-12T22:00:03Z`:
  <https://runescape.wiki/w/Safety_gloves?oldid=6081806>
- `Misthalin Training Centre of Excellence`, oldid `6430839`,
  `2012-10-17T00:04:00Z`:
  <https://runescape.wiki/w/Misthalin_Training_Centre_of_Excellence?oldid=6430839>
- `Cockroach soldier`, oldid `6539651`,
  `2012-11-06T22:58:45Z`:
  <https://runescape.wiki/w/Cockroach_soldier?oldid=6539651>

These revisions establish:

- the route behind the jail-cell poster, through the old mugger rooms and down
  to the Cockroach soldier room;
- pulling the lever to open the jail door, climbing the rope to unlock the
  permanent surface crevice, and returning to the chest;
- non-aggressive monsters and no combat requirement for reaching the reward;
- the one-time chest package of `10,000` coins, Safety gloves, two antique
  lamps worth `500` XP each, and the Safety First emote;
- reclaiming lost Safety gloves from the chest;
- Safety gloves item ID `12629`, no attack bonuses, and defence bonuses of
  `+1` stab, `+2` slash, `+2` crush, `+1` magic, `+2` ranged, and `+1`
  Summoning;
- Cockroach soldier level `83`, `960` life points, non-aggressive behavior,
  six-tick attack speed, melee when close and ranged at distance, and maximum
  hits of `83` melee and `110` ranged; and
- crush, ranged, stab, and earth weaknesses named by the period page.

## Darkan boundary

The Darkan restoration task supplied a read-only identity handoff rather than
a new harvest. Its Stronghold spawn file identifies Cockroach soldier as NPC
`7160`, with three plane-1 placements. Its current combat definition is marked
unqualified: it has placeholder zero skills and missing animations. Its drop
table is also not dated or cache-qualified. Neither file is used to close
hidden combat stats, animations, or drop probabilities.

Darkan additionally records client/object leads for stairs `29592`/`29589`,
lever `29736` changing temporarily to `29731`, secure doors `29624`, reward
chest `29734`, Jailguard `7142`, Professor Henry `7143`, and students
`7151`–`7157`. AnkiScape does not simulate map-object routing, so these are
identity cross-references rather than runtime inputs.

## Horizontal translation

The owner-settled reconnaissance ledger classifies the Stronghold as a
one-time landmark route with optional ordinary Combat contexts. The runtime
therefore uses three review landmarks:

1. pass behind the poster and cross the mugger rooms;
2. reach the soldier room, pull the lever, and unlock the surface rope; and
3. return through the open jail door to the reward passage.

The chest and each lamp are direct actions. The two lamps independently target
any trainable skill and preserve the exact `500` XP reward. Starting a
Cockroach soldier encounter is optional after landmark two and switches to the
ordinary Combat surface. It is not a prerequisite for the chest.

Safety-glove reclaim checks inventory, equipped items, the active combat grave,
and Death's Office so it cannot duplicate a recoverable copy.

## Explicit abstractions and omissions

- The period pages do not expose the five hidden Cockroach soldier combat
  skills or a complete bonus block. The horizontal enemy uses a disclosed
  neutral `level = stat = 83` fallback for Attack, Strength, Defence, and
  Ranged, with Magic `1`. This is an AnkiScape Combat substrate abstraction,
  not a historical claim.
- The period page names drops but does not close their probabilities. The
  enemy has an empty drop table rather than an invented roll. Drop depth is
  `source_blocked`.
- The public ranged maximum of `110` is the conservative all-style runtime cap;
  the period melee maximum of `83` remains in the audit because the current
  ordinary Combat enemy schema has one maximum-hit field.
- The equipment engine has no separate Summoning-defence field. It preserves
  the five supported defence values and records the omitted `+1` Summoning
  defence in source metadata.
- The activity does not model the training-centre dialogue, map coordinates,
  rope/door object states, or a historical spawn layout. Those do not add a
  distinct AnkiScape mechanic to this horizontal slice.

## Verification map

`tests/test_stronghold_player_safety.py` covers state repair, all three route
landmarks, crevice timing, the atomic one-time chest, both independently
targetable lamps, rejected skill targets, reclaim ownership across every
recovery location, the optional Combat gate, and the period/disclosure fields
for the enemy and gloves. Shared runtime, migration, registry, cadence, undo,
Combat, and real offscreen Qt checks will be recorded here after integration
closure.
