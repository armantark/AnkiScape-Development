# Curly-root Woodcutting — 2026-08-13

Cutoff: 2012-11-20, immediately before EOC.

## Shipped contract

Curly jade root is a standard selectable Woodcutting target in AnkiScape's
locationless gathering model. It requires Woodcutting 83 and a usable hatchet.
One successful review represents the period cut-and-collect sequence, awards
161.6 Woodcutting XP, and gives exactly four non-stackable, non-tradeable Curly
roots. No quest gate applies.

The branch already models Herblore Habitat Farming patches and four Habitat
Jadinko Hunter targets, but it has no general player-location or Jadinko-Lair
activity state. The Woodcutting registry, selector, cadence route, carried pack,
telemetry, item graph, persistence, and review undo already accept a contained
gathering row, so no new area or activity mechanism was added.

## Period evidence

### RuneScape Wiki

- `Curly root`, oldid `6518326`, 2012-11-02T01:24:59Z.
  - Page markers: members `Yes`, quest `No`, tradeable `No`, stackable `No`;
    no beta marker.
  - Section `Chopping & Collecting Roots`: the root is obtained by chopping
    curly jade roots inside the Jadinko Lair with Woodcutting 83.
  - The first stage awards `80.8 Woodcutting experience`; the second awards
    `80.8 woodcutting experience`, for `161.6 experience` total.
  - Quantity, verbatim: `Collecting the roots yields 4 curly roots.`
  - The same section says a curly root can straighten during chopping and that
    a fifth rapid cut fails while four earlier roots have not regrown.
- `Jadinko Lair`, oldid `6436518`, 2012-10-18T09:22:25Z.
  - Page markers: members `Yes`, `quests = None`; no beta marker.
  - Section `Getting there`: first use of the main entrance requires speaking
    to Dotmatrix.
  - Section `Requirements` → `Activity requirements`: chopping and collecting
    all Jade-root types each require Woodcutting 83.
- `Woodcutting`, oldid `6556356`, 2012-11-15T11:49:01Z, restates the row as
  level 83, 161 total XP, and 80.5 per stage. That row is rounded and internally
  inconsistent with two 80.5 stages. The item-specific oldid above supplies the
  exact 80.8 + 80.8 = 161.6 contract; the conflicting figures remain recorded
  rather than silently merged.

### OpenRS2 caches

All six dated pre-EOC caches, revs 727, 728, 729, 736, 741, and 742, contain:

- item `21350`, `Curly root`; rev 742 records it as non-stackable and
  non-exchangeable;
- NPC `13823`, `Dotmatrix`, with `Talk-to`;
- object `12290`, `Jade root (healthy)`, with `Chop`;
- object `12291`, `Jade root (mutated)`, with `Chop`.

The cache supplies client identity and options only. It does not supply XP,
quantity, success probability, straightening probability, or regrowth timing.

### Darkan

Production source reviewed with `web/*AuditProbe.kt` excluded:

- `/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-jadinko-lair-394/src/main/java/com/rs/game/content/skills/woodcutting/TreeType.java`
- `/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-jadinko-lair-394/src/main/java/com/rs/game/content/skills/woodcutting/Woodcutting.java`
- `/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-jadinko-lair-394/src/main/java/com/rs/game/content/minigames/jadinkolair/JadinkoLair.kt`

`git log -- <path>` shows `TreeType.java`'s Jadinko XP was changed by commit
`97759f4278ae6334c63d2f3f535da6037ce128b5`, which expressly restored the
rounded Woodcutting-oldid value. Darkan's XP is therefore not independent
corroboration; citing it as agreement would quote the wiki twice through a
longer path.

Darkan's `6/35` success endpoints and `72` respawn value have no restored or
independently corroborated provenance, and its production dispatcher has no
working curly/straight vine action. Those values were rejected.

`JadinkoLair.kt` commit `246906f8b68e904960de9af01ca20edf2e4a5cb8`
restores Dotmatrix introduction behavior, but it is a modern reconstruction;
the pinned wiki closes the historical access claim.

### game-main

The period-lineage tree contains item `21350`, Dotmatrix, and positively found
ordinary Woodcutting target registrations. It contains no Curly/Jade-root
Woodcutting target or handler and no success, depletion, straightening, or
regrowth values. The negative result was positive-controlled against ordinary
tree registrations and checked for multiple hits.

## Placeholder and omissions

The value-local marker `woodcutting.curly_jade_root_success_curve` uses the
shared Hunter fallback `128/256` through Woodcutting's existing review adapter.
It stands only for the unrecovered hidden success curve. It does not stand for
the sourced level, XP, output, quantity, access, or quest gate.

The implementation deliberately omits two attested behaviors that the current
locationless Woodcutting model cannot reproduce without invented math or new
area state:

- curly-to-straight transition, because no period probability survives;
- the four-unregrown-root cap and regrowth timer, because the model has no tree
  depletion/regrowth state and no period duration survives.

The route therefore always yields the sourced Curly-root bundle on a successful
review. This is an explicit simplification, not a claim that the transition and
cap did not exist.
