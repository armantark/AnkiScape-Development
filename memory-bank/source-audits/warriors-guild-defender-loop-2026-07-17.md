# Warriors' Guild token and defender loop at the pre-EOC cutoff

Date: 2026-07-17

Status: **source structure pinned; Casual multi-token balancing owner-settled.**

## Pinned evidence

The literal wikitext of `Warriors' Guild`, oldid `6565080`,
`2012-11-17T05:44:30Z`, establishes:

- entry requires combined Attack and Strength of at least 130, or level 99 in
  either skill;
- five activities award their own token balances: animated armour, attack
  dummies, catapult defence, shot put, and keg balance;
- Cyclops-room entry requires either at least 200 tokens from one activity or
  at least 30 from each of the five;
- single-token mode drains 20 of that token per source minute, while multi-token
  mode drains 3 from each balance;
- multi-token mode adds a small damage bonus, some noted drops, better defender
  odds, and a greater Cyclossus chance; and
- defenders progress from bronze through dragon, with each new tier through
  rune shown to Kamfreena before the next tier becomes available.

The literal wikitext of `Defenders`, oldid `6513277`,
`2012-10-31T19:13:53Z`, corroborates the tier ladder, token drain, rare Cyclops
drops, and the need to restart from the best retained lower-tier defender after
loss.

Sources:

- <https://runescape.wiki/w/Warriors%27_Guild?oldid=6565080>
- <https://runescape.wiki/w/Defenders?oldid=6513277>

Both were inspected as literal wikitext with `tools/wiki_parity.py`.

## Owner-settled AnkiScape automation

Persist all five authentic token balances. Casual automation earns toward the
multi-token threshold and rotates among the source activities according to the
current deficit. This is not a hidden five-room simulation: each successful
review resolves only the selected activity's bounded action reducer.

If one or more activities are currently unavailable, Casual uses the fastest
source-supported single-token route the player can perform. Advanced selects
the exact earning activity and chooses single-token or multi-token Cyclops-room
payment.

Showing a newly obtained defender to Kamfreena is an instantaneous explicit
command that changes the eligible drop tier; it does not consume a review.
Drop rates, token yields, XP, failure damage, armour-loss rolls, Cyclossus
behavior, and cadence conversion remain source-harvest inputs rather than owner
design questions.
