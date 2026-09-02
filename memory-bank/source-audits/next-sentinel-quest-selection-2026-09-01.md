# Next sentinel quest selection — 2026-09-01

Read-only selection job. No sources were harvested, no web page opened, and no
file outside this report was written. The live census below was measured by
importing `data/quest_data.py`'s exported `QUESTS` tuple (which folds in
`generated/quest_catalog_generated.py` and every override table) and counting
stage rows whose `required_actions` contain a `Complete <Quest> stage <N>
objective` sentinel. The measurement reproduces the queue audit's live number
exactly — 680 sentinels across 133 quests — so it is the same population the
2026-09-01 audit (section 24.1 of the rulings ledger) measured.

## 1. Top 15 quests by generated sentinel count

Counted over the live `QUESTS` tuple. Counts are exact; the ordering inside the
9-band and 7-band is alphabetical, because raw sentinel count ties.

| # | Sentinels | Quest | Difficulty | Length | Startable today? |
|---|---|---|---|---|---|
| 1 | 9 | Desert Treasure | Master | Very Long | No — The Dig Site, Troll Stronghold, Death Plateau all sentinel-blocked |
| 2 | 9 | Do No Evil | Master | Very Long | No — gates on Garden of Tranquillity chain |
| 3 | 9 | Garden of Tranquillity | Intermediate | Very Long | No — Creature of Fenkenstrain sentinel-blocked |
| 4 | 9 | Mourning's End Part II | Master | Long | No — four-deep blocked chain |
| 5 | 9 | Ritual of the Mahjarrat | Grandmaster | Very Long | No — 25 prereqs, most blocked |
| 6 | 9 | The Darkness of Hallowvale | Intermediate | Very Long | No — both Myreque prereqs blocked |
| 7 | 8 | Monkey Madness | Master | Very Long | No — The Grand Tree blocked |
| 8 | 8 | Rat Catchers | Intermediate | Very Long | Yes — all four prereqs sentinel-free |
| 9 | 7 | A Clockwork Syringe | Master | Long | No — Rocking Out chain |
| 10 | 7 | A Tail of Two Cats | Intermediate | Long | Yes |
| 11 | 7 | As a First Resort | Experienced | Long | Yes — no prereqs |
| 12 | 7 | Blood Runs Deep | Master | Long | No — ten-prereq chain |
| 13 | 7 | Forgettable Tale of a Drunken Dwarf | Intermediate | Long | No — The Giant Dwarf blocked |
| 14 | 7 | Ghosts Ahoy | Intermediate | Long | Yes — The Restless Ghost already completable |
| 15 | 7 | Horror from the Deep | Experienced | Long | Yes — no prereqs |

Band sizes for context: 6 quests at 9, 2 at 8, 22 at 7. "Startable today"
means every quest in the prereq chain currently has zero sentinels, measured
over the same `QUESTS` tuple.

## 2. Scored top five, with working

Formula and term definitions are taken verbatim from section 3 (R4–R9) of
`memory-bank/handoffs/design-to-impl-rulings-2026-08-13.md`:
`priority = Reach × StageWeight × Gap × SubstrateBump × EvidenceBump`.

How I applied each term to a quest slice, with the judgment calls named:

- **Reach (R5).** Quest stages are the review-path surface, so every quest
  here is tier 3 (review-path surface = 3). Within the tier, R5 orders by the
  leverage number (transitive item and action gain); I used transitive
  dependents in the quest-prerequisite graph from `QUESTS` as the closest
  measurable proxy. A quest whose own prereq chain is still sentinel-blocked
  cannot actually be reached by a player today; that shows up in Gap, not
  Reach, since the surface tier itself is unchanged.
- **StageWeight (R6).** Early needs required level ≤ 30 *and no quest gate*.
  Mid is level 31–60 *or one short quest chain*. Late is 61+ or a deep chain.
- **Gap (R7).** A quest that is startable today and stalls on a generated
  `Complete X stage N objective` journal line is a player-visible defect (3).
  A quest whose prereq chain is still blocked is not yet visible to any
  player, so the sentinel is a defect on a live-but-unreachable mechanic (2).
  I scored no quest here 0; none is complete.
- **SubstrateBump (R8).** ×2 requires five or more families or call sites. A
  quest slice touches `data/quest_data.py` (or a sibling data module) plus the
  stage-action source rows; the three cleared quests (Zogre, Rum Deal, Cabin
  Fever) did not claim the bump and I found no count of five-plus call sites
  for any candidate. Scored ×1 for all five. This term is the one I could
  least verify without opening implementation lanes.
- **EvidenceBump (R9).** ×1.5 when the evidence already sits on local disk.
  All five have a frozen dossier or contract under
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/` (section 3), so all
  five take ×1.5.

| Quest | Reach | StageWeight | Gap | Bumps | Score | Working |
|---|---|---|---|---|---|---|
| Ghosts Ahoy | 3 | 2 (levels 25/20, one short quest gate) | 3 (startable today; The Restless Ghost is completable on main) | ×1.5 ev | **27** | 3 × 2 × 3 × 1 × 1.5 |
| Horror from the Deep | 3 | 2 (Agility 35, Prayer 43; no quest gate) | 3 (no prereqs, startable today) | ×1.5 ev | **27** | 3 × 2 × 3 × 1 × 1.5 |
| The Giant Dwarf | 3 | 2 (levels 12–33; no quest gate) | 3 (no prereqs, startable today) | ×1.5 ev | **27** | 3 × 2 × 3 × 1 × 1.5 |
| Garden of Tranquillity | 3 | 2 (Farming 25; two-quest chain) | 2 (chain blocked at Creature of Fenkenstrain, so not yet player-visible) | ×1.5 ev | **18** | 3 × 2 × 2 × 1 × 1.5 |
| Monkey Madness | 3 | 2 (Prayer 43; short chain) | 2 (chain blocked at The Grand Tree) | ×1.5 ev | **18** | 3 × 2 × 2 × 1 × 1.5 |

Rat Catchers scores **13.5** under my reading (Reach 3 × StageWeight 1 × Gap 3
× 1.5): it is startable today, but its gate is a four-quest chain three levels
deep, which R6 calls a deep chain (weight 1). If the design seat judges that
chain "one short quest chain" instead (weight 2), Rat Catchers jumps to 27 and
joins the lead group with 8 sentinels. I flag this as the largest scoring
uncertainty in the table.

R10 tie-break among the three 27s: sentinel counts are equal-ish (7, 7, 7),
so leverage orders them. Ghosts Ahoy has 9 transitive dependent quests (the
Wanted!/Slug Menace/While Guthix Sleeps web), against 2 each for Horror from
the Deep and The Giant Dwarf. Ghosts Ahoy goes first.

## 3. Dossier status (other project's ledger)

Read from `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/ledgers/quests.jsonl`. Every row below was read; none is inferred from
silence.

| Quest | `source_dossier` | Contract file on disk | Ledger status |
|---|---|---|---|
| Ghosts Ahoy | `memory-bank/audit/sources/ghosts-ahoy-build727-oldid-5981551.json` | No `*-target-contract.json`; a build-727 cache snapshot `openrs2-cache-727-ghosts-ahoy.json` exists, plus three source dossiers under `audit/sources/` | COMPLETE, `completion_reachable: true`, four evidence tiers E0–E2. Notes record the full route runtime-verified in their iteration 85 (model-ship route, petition route, Rune-Draw, partial hand-ins, varbit 217 = 8, 2,400 Prayer XP, Ectophial) |
| Horror from the Deep | `memory-bank/audit/evidence/static/horror-from-the-deep-target-contract.json` | Yes, plus `openrs2-cache-727-horror-from-the-deep.json` | COMPLETE, `completion_reachable: true`, E0–E2. Their iteration 104 restored server-side November 2012 behavior |
| The Giant Dwarf | `memory-bank/audit/evidence/static/the-giant-dwarf-target-contract.json` | Yes, plus `openrs2-cache-727-742-the-giant-dwarf.json` | PARTIAL |
| Garden of Tranquillity | `memory-bank/audit/evidence/static/garden-of-tranquillity-target-contract.json` | Yes, plus `openrs2-cache-727-742-garden-of-tranquillity.json` | PARTIAL[source_blocked], `completion_reachable: true` — route runtime-verified in their iteration 125, dialogue/varbit details unresolved |
| Monkey Madness | `memory-bank/audit/evidence/static/monkey-madness-target-contract.json` | Yes, plus `openrs2-cache-727-monkey-madness.json` | COMPLETE, `completion_reachable: true` |

For comparison, the three just-cleared quests (Zogre Flesh Eaters, Rum Deal,
Cabin Fever) all carried `*-target-contract.json` files, which is the pattern
the last three slices followed.

## 4. Recommendation

**Recommend: Ghosts Ahoy.**

- Highest score under the project's own formula (27, tied on arithmetic but
  first on the R5/R10 leverage tie-break: 9 transitive dependents against 2
  for the other two leaders).
- It is startable by a player today — The Restless Ghost, its only prereq, had
  its stage actions emitted on main (commit `3862ad7b`), so the wall a player
  actually hits is Ghosts Ahoy's own seven sentinels. Gap is a clean 3.
- It has the cheapest evidence picture of any candidate: a build-727 source
  dossier *plus* a final pre-EOC dossier *plus* a transcript-history file, and
  the other project's ledger records the complete route as runtime-verified
  with a closed evidence trail (E0 through E2, four entries). No target
  contract exists for it, but the dossier set is richer than the contract the
  Zogre slice used.
- Clearing it unblocks the biggest downstream web of any single quest in the
  census: the Wanted! → Slug Menace → While Guthix Sleeps line, which is the
  only path by which most of the 9-sentinel endgame quests ever become
  startable.

**Second choice: Horror from the Deep** (also 27, and effectively tied). No
prereqs at all, seven sentinels, a COMPLETE target contract on disk, and a
fully traced route. Pick it over Ghosts Ahoy if the implementer wants the
smallest possible slice with zero chain coordination; its downstream payoff
(2 dependents) is just much smaller.

The Giant Dwarf is the honest third at the same 27, with the same no-prereq
profile and a PARTIAL contract.

**What would change my mind:**

1. If the design seat rules Rat Catchers' four-quest gate a "short chain"
   (StageWeight 2), it ties the leaders at 27 with 8 sentinels and more
   player-visible payoff (Rat Pits, Wily cat) — its PARTIAL contract is also
   on disk. I scored it 13.5 only on the deep-chain reading.
2. If another agent already holds one of these slices. I checked worktrees and
   branches: `goal/q-ghost-2026-08-23` is the Restless Ghost fix (merged to
   main), `goal/q-ratcatchers-2026-08-22` holds only recorded handoff rows
   (no sentinel clearing), and no worktree named for Ghosts Ahoy, Horror from
   the Deep, or The Giant Dwarf exists. Nothing is held as of this report, but
   the orchestrator should confirm at claim time.
3. If SubstrateBump is meant to fire here. I scored ×1 for all candidates
   because I counted no five-family call sites; a quest whose stage actions
   feed five or more live families (for example Monkey Madness's greegree
   system) would gain ×2 and reshuffle the middle of the table.

## 5. Could not determine

- **SubstrateBump call-site counts (R8).** Counting families/call sites per
  candidate needs an implementation-lane pass I did not run (read-only job).
  All five carry ×1; the term is unverified, not measured-zero.
- **Whether the ledger's COMPLETE status requires a target contract.** Ghosts
  Ahoy has source dossiers but no `*-target-contract.json` under
  `audit/evidence/static/`. The Zogre, Rum Deal, and Cabin Fever slices all
  worked from target contracts. Whether the Ghosts Ahoy dossier set (build-727
  + final pre-EOC + transcript history) satisfies the claim check the same way
  is a claim-check question, not a selection one; I flag it so the harvest
  step checks it first.
- **The reachability leverage number from `tools/audit_item_reachability.py`.**
  R5 names that script's transitive-gain number as the within-tier order. I
  did not run the audit tool (it is a lane, and other agents are working);
  I used quest-graph transitive dependents as the proxy. The running order
  could differ from a true item-and-action leverage count.
