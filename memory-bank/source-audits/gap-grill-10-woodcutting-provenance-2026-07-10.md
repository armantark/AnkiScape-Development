# Gap Grill 10 Woodcutting Provenance — 2026-07-10

Target cutoff: 2012-11-20, immediately before EOC.

## Pinned historical evidence

- `Arctic Pine` oldid 6069429, 2012-08-09: level 54, 140.2 Woodcutting XP,
  Arctic pine logs, Neitiznot location, and 42.5 additional XP per split log.
- `Eucalyptus tree` oldid 6491980, 2012-10-28: level 58, 165 Woodcutting XP,
  Eucalyptus logs, and a Mobilising Armies banking route independent of the
  partial As a First Resort... unlock for the Oo'glog bank.
- `Cursed magic tree` oldid 6368505, 2012-10-08: level 82, 275 Woodcutting XP,
  Spirit of Summer gate, Cursed magic logs, and the paired-realm tree cycle.
- `Cursed magic logs` oldid 5742321, 2012-06-10: level-75 in-realm burning,
  Magic-log Firemaking XP, no Grand Exchange listing, tradeability, and
  automatic conversion to Magic logs when leaving the Spirit Realm.
- `Spirit Realm` oldid 6394729, 2012-10-13: Jennica's ring access and the
  cursed/ordinary Magic-tree alternation between realms.
- `Split log` oldid 5505475, 2012-04-18: one Arctic pine log becomes one
  tradeable, Grand Exchange-backed Split log at level 54 for 42.5 Woodcutting
  XP through the Neitiznot Woodcutting stump.

All facts above were read from literal archived wikitext through the MediaWiki
API. Exact success curves, tree-depletion rolls, respawn timing, and the
server-side paired-tree transition remain source-blocked pending reconciled
high-fidelity implementation evidence.

## Owner-approved product abstraction

Use a target-local Spirit Realm session rather than a world map. Preserve
Cursed magic logs while chopping or switching specifically to their Firemaking
target; convert remaining carried logs automatically on a bank run, explicit
exit, or unrelated target switch. Abstract paired-tree travel inside the target
loop and expose only a compact current-action label if multiple phases survive
the source reconciliation.

Arctic-pine splitting is a separate level-54 Woodcutting processing target. One
review consumes one carried Arctic pine log, produces one Split log, and awards
42.5 XP; chopping never auto-splits its output.

Eucalyptus chopping assumes competent use of one of the period page's documented
safe spots. Nearby wolves and ogresses do not add an ambient combat/HP roll to
the abstract Woodcutting target.
