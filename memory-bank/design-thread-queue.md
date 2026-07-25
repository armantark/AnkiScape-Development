# Design-thread queue

Status: **live queue. This file has no date. It is the one address for design
decisions that block implementation.**

## 1. Goal

The implementation sessions ship only what needs no design decision. When a
session finds a decision that the owner must make, it stops that family and adds
the decision here. The owner reads this file in the design thread and answers.

Dated records are snapshots. A reader must know the date to find them, and four
decisions stayed open for six days because of that. This file replaces the search
with one path.

## 2. Rules

1. Add one section for each decision. Give it the next number.
2. State the conflict, the options, and your recommendation. The owner must be
   able to decide without opening another file.
3. Give the exact paths of the records that disagree.
4. Name what the decision blocks. An unblocked decision can wait; a blocked
   family cannot.
5. Move a decision to section 4 when the owner answers. Keep the answer.
6. Never guess an answer to clear a row. A recorded decision is a success. An
   invented mechanic is a defect.

## 3. Open decisions

Four decisions carried forward from
`memory-bank/design-gaps-implementation-2026-07-19.md`. Each one has a
recommendation and no answer.

### 3.1 Treasure Trails clue ownership

The settled contract gives the player one clue per tier. The period sources give
one clue in total across every tier.

- Recommendation: use one clue in total, which matches the period rule.
- Records: `memory-bank/treasure-trails-design-contract-2026-07-19.md`
- Blocks: the Treasure Trails family.

### 3.2 Daily Challenges queue and reroll policy

The settled recon record gives one assigned challenge for each 240-card day. The
period game used a five-slot queue with an oldest-expiry rule.

- Recommendation: use the period five-slot queue and the oldest-expiry rule.
- Records: `memory-bank/source-audits/recon-coverage-closure-2026-07-18.md`
- Blocks: the Daily Challenges family.

### 3.3 Clan Wars free-for-all portal

The settled competitive record converts the two free-for-all portals into one
bounded team-score race. The period game had a safe portal and a dangerous
portal.

- Recommendation: keep both period portals as explicit modes.
- Records: `memory-bank/source-audits/competitive-tier-adaptations-2026-07-18.md`
- Blocks: Clan Wars. Implementation stopped rather than choose.

### 3.4 Duel Arena tournament mode

The settled competitive record requires free challenge duels and period
tournaments. Jagex removed tournament mode before the cutoff.

- Recommendation: remove Duel Tournaments from the live activity. Challenge duels
  stay. Staking stays excluded by the settled contract.
- Records: `memory-bank/source-audits/competitive-tier-adaptations-2026-07-18.md`
- Blocks: the Duel Arena family.

## 4. Answered decisions

### 4.1 Grand Exchange offer-slot count — answered 2026-07-19

The design records asked for eight player offer slots. The pre-cutoff wiki
revision gives six slots to members and two to free players.

- Answer: use six slots. Period parity wins.
- Authority: `memory-bank/grand-exchange-slot-count-supersession-2026-07-19.md`

### 4.2 Grand Exchange price buttons — answered 2026-07-25

The owner remembered the buttons as additive. The period client script compounds
off the shown price.

- Answer: use the recovered client behaviour. The owner asked for whatever the
  real game does, and the cache gives it.
- Authority: `memory-bank/source-audits/ge-offer-price-controls-2026-07-24.md`
