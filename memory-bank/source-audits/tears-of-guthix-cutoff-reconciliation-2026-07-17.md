# Tears of Guthix cutoff reconciliation

Date: 2026-07-17

Status: **partial; activity identity and eligibility are safe, exact
post-refresh reward magnitude remains source-blocked.**

## Conflict

[`Tears of Guthix`, oldid `6579712`](https://runescape.wiki/w/Tears_of_Guthix?oldid=6579712)
is dated 2012-11-19, but its own `Obsolete` banner says the 6 November update
changed XP and added mechanics. The body mixes the refreshed ornate bowl with
older activity prose, so its date does not make every row cutoff-correct.

The official 6 November update,
[`Tears of Guthix: Go with the Flow`](https://runescape.wiki/w/Update:Tears_of_Guthix:_Go_with_the_Flow),
proves that the cutoff activity:

- requires the Tears of Guthix quest;
- is available once per week after either one new Quest Point or 100,000 earned
  XP;
- rewards the lowest eligible skill;
- received an XP-rate refresh; and
- gained an improved bowl requiring 80 Mining and 80 Crafting, described as
  enabling up to five times the pre-update XP.

The period-adjacent
[`Ornate bowl`](https://runescape.fandom.com/wiki/Ornate_bowl) record identifies
its 6 November 2012 release and the 300-XP-per-tear cap, versus 180 for the
ordinary bowl. This is corroborating evidence rather than a substitute for a
clean pinned dependency chain.

## Safe design inputs

- recurring activity owned by Juna after its quest;
- blue tears add and green tears subtract;
- Quest Points govern available collection time, with a source cap;
- one current recurring entry plus one reserve under AnkiScape's settled
  carryover rule;
- the reward selects the eligible skill with the least XP rather than merely
  the lowest displayed level; and
- the ornate bowl is a permanent activity upgrade, not ordinary inventory
  management.

## Source-blocked before implementation

- exact post-6-November collection-rate distribution;
- exact relationship between Quest Points, collection opportunities, and the
  refreshed XP multiplier;
- whether `level × 6`, the 180/300 caps, and “up to five times” can be reconciled
  without an additional period dependency or server implementation; and
- any numeric blue/green transition model used by the review-native session.

Do not treat oldid `6579712` as a complete numeric authority. Search its talk
history, period update discussion, dated guides, and reconciled server sources
before implementation.

## Design work that can continue

The owner may settle the review-native session grammar independently: whether
one recurring entry resolves as a single payout or as several automatic
collection beats. Exact beat counts and reward magnitude remain downstream of
the source reconciliation.

Cadence reconciliation, 2026-07-17: the accepted multi-beat session is an
activity-progress route, not an XP/hour rate-limited skill. Each successful
Tears handler action advances one automatic collection beat; Again advances the
world calendar but not the session. The review-action multiplier repeats
complete activity beats, while leaving preserves the exact remaining beat
count. Exact beats per entry and tear/XP magnitude remain `source_blocked`.
