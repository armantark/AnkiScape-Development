# Wave 2 Completionist trace

## Verifier refix — shipped predicates and provenance

Commit `1f615a2f` (`fix: enforce shipped completionist requirements`) activates the Player Safety, Court Cases, and circus-clothing requirements from durable owner state. Player Safety gates on the final landmark stage, Court Cases gates on every sanitized completed case identifier, and circus clothing gates on the full sanitized costume set. The same commit keeps catalog miniquests out of both quest-cape predicates and preserves the frozen source label, “Every quest complete, including capers.”

Commit `34560917` incorrectly folded every catalog miniquest into the Completionist quest predicate. Commit `6b65e084` (`fix: Restore the sourced Completionist quest boundary.`) reverts that fold. Both quest capes again exclude catalog miniquests because the pinned Completionist table lists its miniquest outcomes as separate requirement rows. The restored code comment cites https://runescape.wiki/index.php?oldid=6560039&action=raw, and the restored regression test proves that incomplete catalog miniquests do not fail either quest predicate.

The plain test lane ran 3,746 tests in 184.336 seconds and passed with 440 skipped tests. The exact command was `/opt/homebrew/bin/python3 run_tests.py`.

The offscreen Qt lane did not start because `.venv-qt/bin/python` does not exist in this worktree. The exact command was `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`, and the shell returned exit code 127 with `no such file or directory: .venv-qt/bin/python`. No offscreen Qt test count was measured.

The shipped predicate now matches the pinned source boundary, the row label matches that predicate, and the branch retains the active Player Safety, Court Cases, and circus-clothing gates.
