# Shattered Heart at the pre-EOC cutoff

Date: 2026-07-17

Status: **period structure pinned; inventory, batch turn-in, and discard
behavior owner-settled; drop-rate harvest remains open.**

## Pinned evidence

The literal wikitext of `Shattered Heart`, oldid `6514590`,
`2012-11-01T02:17:31Z`, establishes:

- qualifying non-combat training may passively produce two strange rocks for
  each of fifteen skills;
- the second rock for the same skill has half the ordinary chance until the
  player receives a rock from another skill;
- without a collection bag, a rock enters inventory and may replace the item
  the skilling action would otherwise have produced when no extra slot exists;
- complete pairs are placed on Dahmaroc's museum plinth for same-skill XP equal
  to `level² - 2 × level + 100`;
- all fifteen pairs complete and explode the museum statue, awarding a replica
  piece for the player-owned-house statue;
- only the final pair is weekly gated; collecting the next statue's rocks may
  begin immediately;
- thirty museum completions finish the cosmetic POH replica, after which the
  activity and its XP rewards may continue; and
- an archaeologist can stop or restart strange-rock acquisition.

The literal wikitext of `Statue collection bag`, oldid `6134494`,
`2012-08-24T02:20:17Z`, establishes:

- Marius Giste or Barnabus Hurma supplies the optional bag;
- the bag is a non-stackable inventory item weighing 10 kg;
- a rock obtained while the bag is carried goes directly into it and therefore
  does not replace the action's ordinary output; and
- destroying the bag destroys every rock stored inside.

Sources:

- <https://runescape.wiki/w/Shattered_Heart?oldid=6514590>
- <https://runescape.wiki/w/Statue_collection_bag?oldid=6134494>

Both revisions were resolved and inspected as literal wikitext with
`tools/wiki_parity.py`. Exact per-action rock eligibility and probabilities
remain subject to the implementation-time evidence hierarchy; prose reports of
high variance do not establish a drop rate.

## Owner-settled AnkiScape behavior

Strange rocks remain real inventory pressure. Without the collection bag, an
awarded rock occupies an ordinary inventory slot and retains the source output-
replacement behavior when the action has no spare slot. The bag is never an
invisible account ledger: it must be obtained and carried, consumes one
inventory slot, weighs 10 kg, and only then catches rocks automatically.

The museum plinth exposes one instantaneous **Add all completed pairs** command.
It removes every currently complete pair, awards each pair's source-scaled skill
XP, advances the museum statue, and resolves any completion/explosion rewards as
one atomic undoable delta. It consumes no review and does not create fifteen
repetitive pair buttons.

The Activity also exposes an opt-in **Automatically discard strange rocks**
setting, disabled by default. When enabled, future rock acquisition is
suppressed before inventory mutation; implementation must not create and then
delete an item merely to reproduce the same result. Existing loose rocks and
rocks already inside the collection bag are untouched. They remain available
for the batch plinth command or an explicit destructive item action.

This setting is the compact player-facing equivalent of the source
archaeologist's stop-receiving option. Re-enabling collection affects only
future qualifying actions and never grants missed rocks retroactively.

## Implementation-time evidence resolution

Darkan has no Shattered Heart server implementation. Its readable dumps contain
only item, object, interface and enum identities. The rev-742 cache independently
matches those identities, and game-main contains only the thirty strange-rock
item constants. The executable behavior therefore uses the pinned cutoff wiki
revisions for rules and the two independent identity layers for ids and options.

Exact evidence implemented:

- fifteen non-combat skills in cache enum order: Agility, Herblore, Thieving,
  Crafting, Runecrafting, Mining, Smithing, Fishing, Cooking, Firemaking,
  Woodcutting, Fletching, Farming, Construction and Hunter;
- two rocks per skill, ids `15522` through `15551`, with the same-skill second
  rock at one-half the ordinary chance until another skill yields a rock; both
  rocks can arrive from one training action, as the pinned Strange rock revision
  states explicitly;
- museum pairs accepted in any order and paying `level² - 2 × level + 100` XP
  in their own skill at the base level when placed;
- only the fifteenth pair is gated, at seven world days from the previous
  explosion; earlier pairs and later-statue rock collection remain available;
- first completion awards 10 Kudos and item `15521` Statue plinth; building the
  plinth in a Study pays the sourced 1 Construction XP; every completion awards
  the next replica piece, ids `15552` through `15581`, until all thirty are
  earned; later completions continue to pay pair XP;
- the optional collection bag is item `19704`, catches rocks while carried, and
  destroys its contents when destroyed; and
- golden rocks are excluded. Their first wiki revision and release are in 2014,
  and no cutoff cache or emulator identity exists.

Labeled AnkiScape abstractions:

- one simulated day is the established 240-card world clock. The final-pair gate
  uses `completion_day + 7`, not a global week boundary, because the source gate
  is anchored to the day of the previous explosion;
- breadth one treats every successful action classified to an eligible awarded
  skill as qualifying. The hook follows the awarded skill rather than the
  telemetry owner, so Magic-only lectern tablets do not yield Construction rocks
  while Hunter XP from Big Chinchompa and Farming queue work remains eligible.
  Exact per-action inclusions and exclusions remain a later catalog-depth harvest;
- the flat skilling inventory has no ordinary 28-slot carried layout. When a
  loose rock and an ordinary output arrive together, the hook removes one unit
  of that action's output to preserve the sourced replacement consequence. The
  shared hook filters caller-supplied candidate outputs through canonical item
  tradeability, so untradeable outputs remain while incidental bird nests and
  gems stay outside the primary-output candidate set. A carried collection bag
  suppresses replacement. The hook runs before telemetry, achievement and Daily
  Challenge credit, so a replaced output is not later counted as though the
  player kept it; and
- the existing POH contract supplies the location layer: building the replica
  plinth requires an owned Study and consumes the sourced plinth item. No second
  house or geography system is introduced.

Source-blocked value:

- `shattered_heart.rock_chance` is one global registered placeholder. No
  recovered server routine states a base chance or per-skill rate. A global
  value is the verification standard's estimation floor and the exact one-half
  modifier remains separate, source-backed behavior. Fork 3.13 records the
  alternatives.

Deferred data depth:

- exact qualifying and excluded action ids within each of the fifteen skills;
- any authentic per-action or per-skill rock-rate table; and
- cosmetic museum examine text for the late partial-statue stages.

The article's lone stale bullet that blocks a completed skill until all other
skills are complete conflicts with its lead and the dedicated Strange rock page.
Breadth one follows the repeated halving/reacquisition rule and buffers a placed
skill's next pair for the following statue. Fork 3.14 records that reconciliation.
