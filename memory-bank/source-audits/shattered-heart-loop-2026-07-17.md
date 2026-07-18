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

## Still open for source harvest

- Enumerate and corroborate every qualifying and non-qualifying cutoff action
  for all fifteen skills.
- Resolve each rock probability and the second-rock reduction through the
  project evidence hierarchy; otherwise mark the hidden roll `source_blocked`
  and follow the provisional-calibration standard.
- Corroborate the XP formula, weekly final-pair boundary, replica progression,
  bag identity, weight, and destruction semantics against independent
  period-lineage evidence.
- Map statue and replica pieces to the existing Construction/POH contracts
  without inventing a separate location system.
