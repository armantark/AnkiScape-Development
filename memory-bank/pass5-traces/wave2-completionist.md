# Wave 2 Completionist trace

## Verifier refix — shipped predicates and provenance

- Hypothesis: Three frozen requirement rows were incorrectly latent despite exact durable owner state; the Completionist quest predicate also treated every catalog miniquest as a caper, and the Dungeoneering master cape overstated its bonus provenance.
- Change: `9d789373` (`fix: enforce shipped completionist requirements`). Player Safety now gates on the final landmark stage, Court Cases on every sanitized completed case id, and circus clothing on the full sanitized costume set. Both quest capes exclude catalog miniquests, while the frozen label keeps the source's “including capers” wording. The master cape now names the shared `items.yml` trimmed-skillcape block that actually supplies its bonuses.
- Regression evidence: the purchase path refuses the regular cape one Player Safety landmark early, and refuses the trimmed upgrade with one missing court case or circus costume. The registry tests also prove all three rows are active rather than latent.
- Test results:
  - Targeted Completionist suite: 41 tests passed.
  - Full plain lane: 3,757 tests passed, 446 skipped (`python3 run_tests.py`).
  - Full offscreen Qt lane: 3,757 tests passed, 2 skipped (`QT_QPA_PLATFORM=offscreen python run_tests.py` in `.venv-qt`).
- Simplification review: a single-pass inline review ran because the Agent tool was unavailable; it deduplicated the repeated full circus-costume fixture. No other safe reduction survived the reuse, simplification, efficiency, and altitude checks.
- Verdict: keep. Every rejected row now gates its cape from source-aligned owner state, the quest reconstruction is removed, and the provenance label matches the value's actual source.
- Open questions: none.
