# Summoning training source audit (2026-07-16)

Scope: close the ordinary surface by which AnkiScape trains Summoning, without yet
claiming the complete pouch and scroll row harvest. Cutoff is 2012-11-20.

## Pinned period sources

1. **Summoning training**, oldid
   [6579264](https://runescape.wiki/w/Summoning_training?oldid=6579264),
   2012-11-18 19:01:19 UTC.
2. **Summoning pouches**, oldid
   [6438719](https://runescape.wiki/w/Summoning_pouches?oldid=6438719),
   2012-10-18 21:44:17 UTC.
3. **Summoning scrolls**, oldid
   [6520851](https://runescape.wiki/w/Summoning_scrolls?oldid=6520851),
   2012-11-02 14:16:52 UTC.
4. **Summoning**, oldid
   [6582606](https://runescape.wiki/w/Summoning?oldid=6582606),
   2012-11-19 08:49:35 UTC.
5. Darkan world server commit
   `2383a9b213bbb2de46cbc4c376ef7d6d87dba312`, especially
   `skills/summoning/Summoning.java:131-205,226-248`.
6. 2011Scape rev-667 snapshot under
   `/Users/ArmanTarkhanian1/Downloads/game-main`, especially
   `skills/summoning/summoning_crafting.plugin.kts:5-201` and
   `skills/summoning/SummoningPouchData.kt:9-90`.

The wiki revision IDs and timestamps came from the MediaWiki revisions API with
`rvstart=2012-11-20T23:59:59Z` and `rvdir=older`. Claims were checked against literal
wikitext.

## Closed source facts

- Ordinary Summoning training is primarily pouch infusion. Oldid 6579264 lines 10-15
  names the empty pouch, charm, spirit shards, and familiar-specific tertiary; oldid
  6438719 supplies level, shard, charm, tertiary, and creation-XP columns per pouch.
- Pouches are infused at a large Summoning obelisk. Period training routes repeatedly
  alternate a Bank load with travel to an obelisk and describe carrying roughly one
  inventory of tertiaries per trip (oldid 6579264 lines 404-420).
- The interface supported one, five, ten, X, and all. Both Darkan and 2011Scape preserve
  those quantities and atomically consume the per-pouch ingredients and award exact
  per-pouch XP.
- One pouch converts into ten matching scrolls at an obelisk. Oldid 6520851 line 1
  explicitly says its creation-XP column is per pouch, not per scroll; the table separately
  records scroll creation XP, use XP, and special-move-point cost.
- Oldid 6520851 line 1 awards scroll-use XP only for manual inventory activation and
  explicitly withholds it from scrolls fired automatically by enchanted headgear. That is
  a source precedent for any future truly passive auto-fire. It does not by itself define
  AnkiScape's successful-review abstraction, where an automatically resolved special still
  represents the player's foreground action.
- Wolf Whistle was optional by the cutoff. Its quest XP and starter items remain a quest
  reward when that quest exists, but completion cannot gate the skill (oldid 6579264 line
  5).
- Dungeoneering pouches and scrolls are a separate catalog. Oldid 6438719 begins a distinct
  `Dungeoneering pouches` table at literal line 1050, oldid 6520851 begins a distinct
  `Dungeoneering scrolls` table at line 155, and Darkan rejects surface pouches inside
  Daemonheim and Daemonheim pouches outside it (`Summoning.java:226-230`).
- Familiarisation, quest/activity XP, and charm acquisition are supporting routes rather
  than replacements for pouch infusion. Familiarisation already has its own contract;
  charms already enter AnkiScape through combat drop tables.

## AnkiScape translation resolved from existing patterns

The Summoning skill page has two ordinary action families: **Infuse pouches** and
**Create scrolls**. Each successful review processes one source unit: one exact pouch, or
one pouch into ten scrolls, with the sourced item transaction and XP. The carried-pack and
Bank-run system owns repeated inventory trips; the later cadence/rate pass owns the travel
cost and must not multiply the source XP. Again advances world state but performs neither
action.

The large catalog uses the shared modular target search plus source-shaped filters such as
`Only craftable` and charm family. Casual packs the chosen recipe through the ordinary
target preset; Advanced exposes the exact carried grid. Surface-world search never mixes
in Daemonheim pouches or scrolls. A future Dungeoneering implementation consumes the
separate period rows inside its own temporary-session economy.

## Still required before implementation closure

- Harvest every surface pouch and scroll row, including exceptions, alternate tertiaries,
  quest/activity gates, and exact item IDs; reconcile both emulators against the pinned
  tables.
- Audit acquisition for every charm, tertiary, empty pouch, and shard. Existing item
  presence is not proof of reachability.
- Derive Summoning's route/trip input from a sourced training rate and nominal load; keep
  the action unit and XP exact while the trip system supplies the travel burden.
- Decide whether Bogrog pouch exchange belongs in the Summoning page, Shop/service
  surfaces, or both projections of one transaction. Its sourced 70% shard return is not a
  new training recipe.
