# Slayer master challenges source reconnaissance — 2026-07-15

Status: **period families and stated objectives attested; source-first
hidden-roll fallback owner-set**.
Cutoff: `2012-11-20T00:00:00Z`.

## Primary period source

RuneScape Wiki, `Slayer/Challenges`, oldid `6328439`, timestamp
`2012-10-01T08:55:32Z`:
<https://runescape.wiki/w/Slayer/Challenges?oldid=6328439>.

The historical wikitext was read through the MediaWiki revisions API, not from
the current rendered page. It states that challenges were added on
`2010-04-21`; Kuradal's existing `2009-12-08` special task became her challenge.
Challenges are occasionally offered instead of a normal assignment, may be
declined without a Slayer-point penalty, count as assignments, and award their
own completion rewards.

A period-lineage Knowledge Base mirror independently says that players who
complete several consecutive tasks for a particular master have a chance to be
offered that master's optional challenge:
<https://www.2011.rs/kb/slayer_challenges>.

## Cutoff-live challenge families

| Master | Literal period objective | Stated challenge reward |
|---|---|---|
| Turael / Spria | In one basement visit: 2 level-5 goblins, 2 level-11 goblins, 1 level-13 goblin, 2 level-11 wolves, 3 level-14 wolves, and 5 level-12 minotaurs | 1,000 Slayer XP; no challenge points |
| Mazchna / Achtryn | Contact the master with an enchanted gem at fairy rings CKS, ALQ, and BKR, then kill the spawned ravenous ghoul, vampyre, and snail | 2,000 Slayer XP and 3 Slayer points |
| Vannaka | Obtain one perfect green, blue, red, and black dragon scale from qualifying baby or adult chromatic dragons, then hand in all four | 4,000 Slayer XP and 10 Slayer points |
| Chaeldar | Use experimental fungicide spray on 10 mutated zygomites, resolving its kill, enrage, or full-heal result, then report back | 10,000 Slayer XP and 25 Slayer points |
| Sumona | Defeat the Kalphite Queen while personally dealing the majority of damage | 15,000 Slayer XP and 30 Slayer points |
| Duradel / Lapalok | In one Slayer Tower trip: 21 crawling hands, 8 banshees, 9 infernal mages, 7 bloodvelds, 7 aberrant spectres, 5 gargoyles, 6 nechryaels, and 6 abyssal demons; individual kills grant no Slayer XP | 20,000 Slayer XP and 35 Slayer points |
| Kuradal | Complete the Fight Cave and slay 280 monsters there, through TzTok-Jad | 25,000 bonus Slayer XP, 37,000 total stated; no bonus challenge points |

Ordinary task-completion points may still apply separately where the historical
page says so. The table records the challenge-specific reward only.

## Cancellation and completion leads

- Accepted challenges cannot be cancelled through the Slayer reward shop in the
  period revision. Turael/Spria replacement is the stated escape hatch and
  resets the Slayer task count.
- Vannaka and Chaeldar explicitly require returning to the master after the
  objective ledger is satisfied.
- Several rows encode location continuity (`one visit`, `one trip`) that cannot
  be copied literally without adding a forbidden global-location model.
- Vannaka's perfect-scale drop chance and Chaeldar's experimental-spray outcome
  probabilities are hidden rolls and remain `source_blocked` until the emulator
  and cache/source pass is complete.

## Challenge-offer roll

The cutoff revision states only that challenges are `occasionally offered`; it
contains no numeric probability, counter formula, or exact minimum streak. The
period-lineage Knowledge Base mirror likewise says `several consecutive tasks`
for the particular master and `have the chance`, without a number.

The current wiki's `X/100` formula is not period evidence: it does not appear in
oldid `6328439`, and the current page cites a 2023 source for its eligibility
section. Until a period implementation, talk-history row, or independent dated
source closes the mechanic, both the prerequisite and hidden offer probability
remain `source_blocked`. The design still preserves the sourced shape: roll only
when requesting a new task from the chosen master; a successful roll offers the
challenge instead; declining produces an ordinary assignment without a point
penalty.

The implementation pass must make one final focused search for those two cutoff
values. If it still finds no qualifying evidence, the owner-set fallback is five
consecutive assignments for the same functional master role followed by a 10%
offer roll on each later request. An offer resets that role's counter whether
accepted or declined; changing roles breaks only this challenge sequence, not
the distinct Slayer-point streak. This is a labeled abstraction, never a period
claim, and any qualifying cutoff evidence replaces it.

## Corroboration still required before implementation

The period wiki revision closes the existence and user-visible shape of all
seven families. Exact counts, rewards, item IDs, monster membership, gates,
drop/outcome rolls, and challenge-offer probability still require Darkan,
rev-727/rev-742, game-main, or independent period corroboration under
`pre-eoc-source-verification-standard.md`.

## Open AnkiScape abstraction

The source challenges remain structurally richer than ordinary single-target
assignments. AnkiScape preserves their compound objective ledgers and flattens
only unavailable travel/location ceremony into concise status text and
review-free hand-in UI.
