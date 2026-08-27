# Glossary

Domain terms with one settled meaning each. Implementation detail stays out.

- **Anchor task** — one of the 22 diary rows that are visibly labelled "Reach
  Level X" milestones. An anchor's level threshold IS its deed, so it is the
  only diary row class whose trigger may be a level.
- **Bank Claims** — the Bank tab's inbox of pending claimable rewards. A claim
  row persists until the player claims it; it is the delivery surface for
  deferred rewards such as XP lamps.
- **Carried view** — the projection of the single item ledger that shows what
  the player carries right now (retained loot plus remaining supplies). It is
  not a second ledger; the Bank and the carried pack share one ledger.
- **Deed task** — a diary row whose completion requires a performed action. A
  level or quest prerequisite on a deed task is an access gate, never the
  trigger.
- **Translated deed** — a designed AnkiScape trigger for a deed whose literal
  form does not exist here (for example, world traversal). The curation ledger
  marks every translation, so a translation is never mistaken for a
  source-faithful trigger.
- **Curation ledger** — the reviewable per-task table (task → trigger →
  source citation → translation flag) that authorizes diary wiring. Wiring
  that bypasses the ledger is invalid.
- **Bankstanding** — the neutral Utilities state every ended session lands on.
  An automatic switch to Bankstanding notifies the player; a manual Stop does
  not.
