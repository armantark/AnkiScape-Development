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

## Implementation harvest, 2026-07-26

Most of the "source-blocked" list above turned out to be recoverable from the
same pinned revision, which had not been read closely enough in July.

Recovered and shipped exactly as stated:

- Eligibility. `Tears of Guthix` oldid `6579712`: "Earned at least 100,000 total
  experience or one quest point since they last participated (unless they have
  never played before)", plus "Waited at least 7 days".
- Cavern timer. Same revision: "The time a player has is the player's Quest
  Points in Ticks which is 0.6 of a second", and "The maximum a player can have
  is 3 minutes", so `min(quest_points, 300)` ticks.
- XP per tear. Same revision: "Level * 6 = Xp. The experience per tear is capped
  at 180", and "capped at 300 for those who have made an ornate bowl".
- Reward skill. Same revision: "The experience is added to the skill with the
  least experience", with the Dungeoneering paragraph confirming this is least
  *experience*, not lowest level.
- Ornate bowl. `Ornate bowl` oldid `6555677`: "requiring 80 Mining and 80
  Crafting", made with a chisel, boosts not allowed, and Juna keeps the bowl.

Conflict resolved rather than averaged: the ornate-bowl article says the bowl
collects "up to five times as much experience as the regular stone bowl", which
cannot be squared with the 180/300 caps in the same period. The launch update's
"up to five times" is measured against the **pre-update** reward, which is
consistent with 180/300. The shipped values are the D&D article's caps; the
ornate article's sentence is recorded here as a period-wiki defect.

The per-tick collection rate was recovered and its placeholder retired on
2026-07-27: Darkan `TearsOfGuthix.kt:496-510` accepts only one collection update
per server tick and adds exactly one tear for blue. The green-tear roll
(`tears_of_guthix.green_tear_chance`) remains a registered placeholder. Its only
period anchor is the reported 267 tears at 316 quest points. AnkiScape has no
positional layer for a player to dodge a green stream with, so the green catch
is necessarily a hidden roll here.

AnkiScape abstractions, neither of them period claims: one answered card is six
game ticks of cavern time (design-thread queue 3.2), and up to two weekly visits
bank under `simulation-time-boundary-2026-07-16.md` Decision 2.

Cadence reconciliation, 2026-07-17: the accepted multi-beat session is an
activity-progress route, not an XP/hour rate-limited skill. Each successful
Tears handler action advances one automatic collection beat; Again advances the
world calendar but not the session. The review-action multiplier repeats
complete activity beats, while leaving preserves the exact remaining beat
count. Exact beats per entry and tear/XP magnitude remain `source_blocked`.
