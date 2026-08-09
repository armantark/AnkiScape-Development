# Gap Grill 17: Final Firemaking and Cooking Provenance

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Supersession: the Cooking-gauntlet numerical block below was resolved on
2026-08-09 by `cooking-gauntlets-runtime-closure-2026-08-09.md`, using the later
oldid 6572206 and the reconciled Darkan burn policy. Firemaking remains unchanged.

## Pinned period evidence

- `Barbarian Training` oldid 6476330, 2012-10-26: level-35 Otto unlock;
  strung wooden bow; explicit excluded bow families; same speed and no inherent
  advantage over a tinderbox; and literal bow-lighting level/XP table for normal
  through magic logs.
- `Cooking gauntlets` oldid 6556123, 2012-11-15: Family Crest conversion;
  non-tradeable equipped gloves; reduced fish-burning risk; 25,000-coin
  re-enchantment; free same-enchantment loss recovery; and a literal no-burn
  threshold table.
- `Cooking` oldid 6548144, 2012-11-11: range/fire burn context; listed affected
  fish and thresholds; explicit warning that the exact gauntlet bonus was based
  on player statistics rather than an official formula.
- `Family Crest` oldid 6548361, 2012-11-11: Family gauntlets reward, three
  brother enchantments, effect switching, and 25,000-coin change fee.

All wiki claims were read from literal archived wikitext with
`tools/wiki_parity.py`. Modern RS3 and OSRS behavior was not used as parity
evidence.

## Local reconstruction cross-check

- `game-main` Otto dialogue sets `learnedBarbarianFiremaking` immediately after
  the bow-on-oak instruction, while its Barbarian skills book repeats the
  strung-bow method. No live bow-on-log action is bound there.
- `game-main` defines Cooking gauntlets item 775 and its loss/examine metadata,
  but its Cooking runtime does not implement the effect.
- AnkiScape's focused Family Crest quest correctly rewards Family gauntlets and
  already records later conversion as the post-quest ability rather than
  granting all three enchanted pairs at completion.

## Evidence boundary

Bow-lighting has enough period evidence to settle its alternate-tool behavior;
the broader miniquest still owns acquisition of the learned flag. Cooking-
gauntlet conversion and equipment behavior are settled, but the two nearest
period pages conflict on affected fish and provide no authoritative intermediate
burn formula. Those numerical mechanics remain blocked on reconciled dated
evidence or high-fidelity Darkan rather than being inferred from thresholds.
