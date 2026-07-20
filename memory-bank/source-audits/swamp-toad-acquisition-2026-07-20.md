# Swamp toad acquisition — 2026-07-20

## Scope

This audit closes the ordinary overworld acquisition root for `Swamp toad`
without inventing a shop, combat drop, quest gate, or wall-clock timer. It also
reconciles the existing `Swamp toad` → `Toad's legs` preparation action and
their item identities.

## Period evidence

The pinned `Swamp toad` revision is RuneScape Wiki
[oldid 6088673](https://runescape.wiki/w/Swamp_toad?oldid=6088673),
2012-08-14T01:59:26Z. Its literal wikitext establishes:

- members-only, tradeable, non-stackable, and no quest requirement;
- eighteen ground spawns in the Tree Gnome Stronghold swamp;
- full-inventory collection as a common money-making method with no skill
  requirement and quickly respawning spawns;
- rare incidental gnome attacks can be avoided by keeping auto-retaliate off;
- removing the legs replaces the toad with `Toad's legs`;
- the intact toad is the Barker toad pouch tertiary.

The pinned `Toad's legs` revision is RuneScape Wiki
[oldid 6065573](https://runescape.wiki/w/Toad%27s_legs?oldid=6065573),
2012-08-09T09:22:18Z. Its literal wikitext establishes that the item is
tradeable and non-stackable, is obtained by removing the legs from a swamp
toad, and is used for Agility potion and gnome cooking.

The existing 2011Scape action at
`game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/swamp_toad.plugin.kts`
reconciles the cache identities `2150` → `2152` and the 1:1 Remove-legs
transition.

## AnkiScape translation

`Gather swamp toads` is a zero-XP Utility / Activities gathering row. One
successful review gathers a disclosed batch of up to 28 toads, following the
period page's full-inventory collection method and the existing AnkiScape
gathering convention. It has no skill, material, or quest gate.

The rare avoidable gnome attack is not converted into ambient damage: the
period page explicitly instructs collectors to disable auto-retaliate, and the
target represents that competent safe collection method. Respawn and banking
descriptions prove the collection route but do not introduce wall-clock
gameplay.

The existing zero-XP `Remove swamp toad's legs` activity remains a batchable
1:1 conversion. Both items are non-stackable and tradeable. Distinct sprites
are pinned to pre-cutoff file revisions:

- `summoningitems/swamp_toad.png`: 2008-05-03T20:30:01Z;
- `herbloreitems/toad_s_legs.png`: 2011-11-29T20:20:05Z.

## Explicit omissions

- No Tortoise or Gnome pickpocket drop rate is inferred from the location page.
- No server-population respawn multiplier or wall-clock banking duration is
  modeled.
- Gnome cooking recipes remain owned by their existing Cooking contract.
- Big Chinchompa's Swamp toad reward remains an independent sourced route.

## Verification and UI review

- Focused logic, registry, Summoning, metadata, integration, Herblore-asset,
  reachability, and Qt row checks pass.
- Complete non-Qt discovery passes all 1,905 tests with 250 expected
  environment skips. Complete real offscreen Qt discovery also passes all
  1,905 tests with one intentional platform skip. The repository documentation
  audit passes 431 Markdown and 379 HTML files, and the test-quality audit
  reports zero hard issues across 83 test files.
- The reachability graph now contains 1,343 actions and 1,997 reachable items.
  Orphan inputs fall to 239 (96 root and 143 cascade), with 250 unresolved
  actions. `Swamp toad`, `Toad's legs`, and both Agility-potion dose routes are
  live graph paths.
- A fully quit and restarted native macOS Anki process displayed exactly one
  AnkiScape entry and one menu. The enabled `Gather swamp toads` row appeared
  in Gathering with its normalized period sprite at the same scale as adjacent
  rows; the activity was not started and the save was not mutated.
- Kimi K3 inspected the native screenshot and implementation and returned a
  ship verdict. Its only copy observations were inherited generic Utility
  tooltip wording shared by the existing flax and wool rows, not defects
  introduced by this slice.
- The required Fable taste pass remains an external QA/auth gate because the
  mandatory fresh quota probe cannot read Claude Code OAuth from macOS
  Keychain (`security` exit 51). No unverified Claude call was made. This is
  not an owner design gap.
- Results:
  `memory-bank/status-updates/swamp-toad-acquisition-results-2026-07-20.html`;
  mobile copy: `https://jzn1gbktyze8.postplan.dev`.
