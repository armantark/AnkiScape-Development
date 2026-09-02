# Proof-binding harvest — 2026-09-01

## Scope and result

This harvest checks the three predicates named in the 2026-09-01 queue audit against
both the live action/proof seam and the pre-EOC period record. The cutoff is
`2012-11-20T00:00:00Z`.

The premise that these are all binding-only is not recovered. The live generic
Magic and Construction actions are real actions, but they are not the three
source-defined quest deeds. `data/crafting_data.py:434-456` is the
`crafting_recipes_as_dict()` serializer; it is not a Fremennik-round-shield
recipe. No source-faithful emitted event exists for any of the three predicates.

## 1. Legacy of Seergaze — emerald preparation

### Catalog predicate

- Quest ID: `legacy_of_seergaze`.
- Stage: `5`.
- Exact predicate: `Cast Enchant Level 2 Jewellery for the emerald preparations`.
- Catalog location: `data/quest_data.py:9371-9376`; the predicate is at `:9375`.

### Existing action and what it emits

`data/magic_data.py:332-348` generates the ordinary jewellery-enchant targets.
The emerald tier at `:335` generates these existing target IDs at `:348`:

- `enchant_emerald_ring`
- `enchant_emerald_necklace`
- `enchant_emerald_amulet`
- `enchant_emerald_bracelet`

They consume an ordinary `Emerald ring`, `Emerald necklace`, `Emerald amulet`,
or `Emerald bracelet`, respectively, and produce the corresponding ordinary
jewellery enchantment. After a successful Magic review,
`runtime/runtime_actions_magic.py:474-498` records the action as
`("magic", target)`. The shared post-success seam then passes that pair to the
proof store at `runtime/runtime_actions_shared.py:647-648`.

### Exact gap

The period deed is Level-2 Enchant **on an emerald sickle**, after the player
uses the emerald on the sickle. None of the four emitted emerald-jewellery
identifiers identifies that input, its `Silver sickle emerald (b)` result, or
its `Enchanted emerald sickle` result.

A proof-rule row can only match an existing event pair. Here the only relevant
existing pairs are `("magic", "enchant_emerald_ring")`,
`("magic", "enchant_emerald_necklace")`,
`("magic", "enchant_emerald_amulet")`, and
`("magic", "enchant_emerald_bracelet")`. Matching any of them would award the
quest predicate for an unrelated ordinary jewellery enchantment. No existing
emitted pair represents the documented sickle transformation.

### Period source

- [Legacy of Seergaze, oldid 6521668](https://runescape.wiki/w/Special:PermanentLink/6521668), `2012-11-02T22:17:22Z` UTC.
- Its literal historical wikitext directs the player to use an emerald on the
  sickle, then use Enchant Level 2 Jewellery on the resulting emerald sickle,
  before making the Ivandis flail. This confirms that the catalog predicate is
  the right deed, while also showing why the generic jewellery actions are not
  its proof.

## 2. In Aid of the Myreque — sapphire preparation

### Catalog predicate

- Quest ID: `in_aid_of_the_myreque`.
- Stage: `6`.
- Exact predicate: `Enchant sapphire for the Myreque preparations`.
- Catalog location: `data/quest_data.py:9220-9230`; the predicate is at `:9229`.

### Existing action and what it emits

The sapphire tier in `data/magic_data.py:332-348` is the tuple at `:334`. It
creates these ordinary jewellery target IDs at `:348`:

- `enchant_sapphire_ring`
- `enchant_sapphire_necklace`
- `enchant_sapphire_amulet`
- `enchant_sapphire_bracelet`

As with the emerald rows, successful use emits `("magic", target)` through
`runtime/runtime_actions_magic.py:474-498` and the shared proof seam at
`runtime/runtime_actions_shared.py:647-648`. Each target consumes an ordinary
sapphire jewellery item, not a Silvthrill rod.

### Exact gap

The period deed makes a `Silvthrill rod` from a silver bar, mithril bar, and
cut sapphire, then casts Enchant Level 1 Jewellery on that rod. The four
existing sapphire pairs above identify ordinary jewellery forms, not the rod
or its enchanted result. `data/magic_data.py:332-348` contains no target that
identifies the Silvthrill-rod transformation.

Thus a proof row would have to match one of the existing
`("magic", "enchant_sapphire_...")` identifiers, but no such identifier is a
valid proof of the documented deed. No existing emitted event pair can be
recorded honestly for this predicate.

### Period source

- [In Aid of the Myreque, oldid 6555220](https://runescape.wiki/w/Special:PermanentLink/6555220), `2012-11-14T12:32:46Z` UTC.
- Its literal historical wikitext says to use a silver bar, mithril bar, and
  sapphire to make a `Silvthrill rod`, then enchant it with Enchant Level 1
  Jewellery. This supplies the source-specific action boundary that the live
  sapphire jewellery targets do not have.

## 3. The Fremennik Isles — Fremennik round shield

### Catalog predicate

- Quest ID: `the_fremennik_isles`.
- Stage: `5`.
- Exact predicate: `Make a Fremennik round shield`.
- Catalog location: `data/quest_data.py:9086-9093`; the predicate is at `:9092`.

### Existing action and what it emits

There is no `CraftingRecipe` for a Fremennik round shield. The complete
`CRAFTING_RECIPES` tuple ends at `data/crafting_data.py:180-369`; the cited
`:434-456` only projects existing recipes into dictionaries.

The superficially similar live target is `round_shield` in
`data/construction_data.py:21`: a level-66 player-owned-house Construction
furnishing named `Round shield`, requiring two `Oak plank`. Successful
Construction reviews emit `("construction", "round_shield")` at
`runtime/runtime_actions_production.py:863-926`, specifically `:913-921`, and
the shared seam makes that available to proof rules at
`runtime/runtime_actions_shared.py:647-648`.

### Exact gap

The source deed is a woodcutting-stump interaction that uses two arctic pine
logs, one bronze nail, a hammer, and rope. The emitted
`("construction", "round_shield")` pair instead identifies a player-owned-house
oak-plank furnishing. It does not identify the item, materials, station, or
quest action that the period source requires.

There is no existing `("crafting", event_id)` pair for the shield, and matching
`("construction", "round_shield")` would prove the wrong action. Consequently
no existing identifier can be used for a faithful proof-rule row.

### Period source

- [The Fremennik Isles, oldid 6540919](https://runescape.wiki/w/Special:PermanentLink/6540919), `2012-11-07T09:46:34Z` UTC.
- Its literal historical wikitext states that the shield needs two arctic logs,
  a bronze nail, a hammer, and rope, and is made on the northern woodcutting
  stump by selecting `Cut-Wood` and then `Make Fremmenik Round Shield` (the
  source's spelling). It corroborates the catalog deed and excludes the
  Construction furnishing as a proof source.

## Proof-rule sufficiency

No: the existing proof-rule mechanism is not sufficient to bind these three
predicates faithfully today.

`data/quest_action_proof_data.py:11-34` defines rules solely as a mapping from
an `(event_type, event_id)` pair to prerequisite and emitted proof strings.
`logic_pure/quest_action_proofs.py:29-41` performs that exact lookup, and
`runtime/runtime_actions_shared.py:647-648` calls it only after a successful
runtime action. The mechanism can express a link once a source-faithful action
already emits its own existing pair. It cannot distinguish the generic
jewellery forms from an emerald sickle or Silvthrill rod, and it cannot
distinguish the player-owned-house `round_shield` furnishing from the
woodcutting-stump shield deed.

The missing seam for all three is therefore the source-faithful successful
action event, not a declarative proof-rule entry. This harvest does not design
or name a replacement identifier.

## What was not recovered or done

- No source-faithful existing event pair was recovered for any of the three
  predicates.
- No Darkan or cache source was needed for the deed confirmation; each is
  directly attested by a pinned pre-cutoff RuneScape Wiki revision.
- No code, catalog data, proof rule, generated output, test, generator, or
  existing file was edited. No git state-changing command was run.
