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
- **Dormant task** — a deed task whose designed trigger awaits a named,
  plausible future game system. Its trigger is fully designed and recorded in
  the curation ledger; the row activates when its system lands. A dormant task
  differs from the retired "latent" stub, which had no designed trigger at
  all. A deed that can never translate must not be dormant; it is swapped or
  translated instead.
- **Translated deed** — a diary deed rebuilt for AnkiScape from a source deed
  whose literal form does not exist here (for example, world traversal). It
  keeps the source's region, family, and difficulty. In the game it carries
  its own name and sentence with no reference to the source deed; the source
  lives only in the curation ledger, which marks every translation.
- **Invented deed** — a diary deed written from scratch in the spirit of its
  region and tier, used when no honest translation of the source deed
  survives. Like a translated deed, it shows no reference to the source.
- **Curation ledger** — the reviewable per-task table (task → trigger →
  source citation → translation flag) that authorizes diary wiring. Wiring
  that bypasses the ledger is invalid.
- **Bankstanding** — the neutral Utilities state every ended session lands on.
  An automatic switch to Bankstanding notifies the player; a manual Stop does
  not.
